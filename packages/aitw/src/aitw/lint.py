"""``aitw lint`` — schema and cross-reference checks (docs/13 K0).

Deterministic by construction (invariant I1): files are discovered in sorted
order, issues are sorted before output, and nothing depends on time, network
or randomness. No model is ever called.

Scope of this module (K0): JSON Schema validation, cross references, ID and
directory naming, autonomy/gate/review-tier compatibility, and unfilled
template placeholders in front matter. Label rules L1–L6 (K1), packet
narrative checks (K3) and Gate logic (K2a) are intentionally not here.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

from . import frontmatter, schemas, yamlio

# --------------------------------------------------------------------------- issues


@dataclass(frozen=True, order=True)
class Issue:
    file: str  # repo-relative POSIX path
    field: str  # dotted/indexed path inside the file, or "-" for the whole file
    code: str  # stable machine code, e.g. "schema.required"
    reason: str  # 中文：哪裡錯
    fix: str  # 中文：怎麼修
    parse_error: bool = False

    def as_dict(self) -> dict:
        return {"file": self.file, "field": self.field, "code": self.code,
                "reason": self.reason, "fix": self.fix}


@dataclass
class LintResult:
    issues: list[Issue]
    files_checked: int

    @property
    def ok(self) -> bool:
        return not self.issues

    @property
    def exit_code(self) -> int:
        if any(i.parse_error for i in self.issues):
            return 2
        return 1 if self.issues else 0


# --------------------------------------------------------------------------- helpers

PLACEHOLDER = re.compile(r"<[^<>\n]+>")

# docs/09 §3 + docs/10 §3–§5 (union; see PR notes on the 09/10 difference for A3).
AUTONOMY_GATES = {"A3": {"G0", "G1"}, "A2": {"G1", "G2"}, "A1": {"G3"}, "A0": {"G2", "G3"}}
EXECUTOR_AUTONOMY = {"ai": {"A2", "A3"}, "human": {"A0", "A1"}, "pair": {"A0", "A1", "A2", "A3"}}
DEFAULT_TIER = {"G0": "R1", "G1": "R2", "G2": "R2", "G3": "R3"}
TIER_RANK = {"R1": 1, "R2": 2, "R3": 3}


def _field(path) -> str:
    out = ""
    for part in path:
        if isinstance(part, int):
            out += f"[{part}]"
        else:
            out += f".{part}" if out else str(part)
    return out or "-"


def _schema_fix(err, doc: str) -> tuple[str, str, str]:
    """Translate a jsonschema error into (code, reason, fix)."""
    v = err.validator
    if v == "required":
        missing = re.findall(r"'([^']+)' is a required property", err.message)
        name = missing[0] if missing else "?"
        return ("schema.required", f"缺少必填欄位 '{name}'",
                f"加上欄位 '{name}'（規格見 {doc}；可參考 kit/templates/ 的樣板）")
    if v == "enum":
        allowed = "、".join("null" if x is None else str(x) for x in err.validator_value)
        return ("schema.enum", f"值 {err.instance!r} 不在允許的列舉內", f"改為下列其中之一：{allowed}")
    if v == "const":
        return ("schema.const", f"值 {err.instance!r} 不符合規則（必須為 {err.validator_value!r}）",
                f"改為 {err.validator_value!r}（規格見 {doc}）")
    if v == "pattern":
        return ("schema.pattern", f"值 {err.instance!r} 格式不符（需符合 {err.validator_value}）",
                "依命名規則修正（見 docs/11 §3：M-NNN、WP-NNN、EV-<WP號>-NN、DR-NNN）")
    if v == "additionalProperties":
        extra = re.findall(r"'([^']+)' (?:was|were) unexpected", err.message)
        names = extra[0] if extra else err.message
        return ("schema.unknown_field", f"未知欄位：{names}", f"確認拼字或移除該欄位（允許的欄位見 {doc}）")
    if v == "type":
        return ("schema.type", f"型別錯誤：{err.instance!r} 應為 {err.validator_value}",
                f"改成 {err.validator_value} 型別（規格見 {doc}）")
    if v in ("minItems", "maxItems"):
        return (f"schema.{v}", f"項目數量不符：{err.message}", f"調整清單長度（規格見 {doc}）")
    if v in ("anyOf", "oneOf"):
        return ("schema.any_of", f"不符合任何允許的形式：{err.message}", f"依 {doc} 的規則擇一填寫")
    return (f"schema.{v}", err.message, f"依 {doc} 修正")


class _Repo:
    """Loaded view of a project repository (docs/11 §3 layout)."""

    def __init__(self, root: Path):
        self.root = root
        self.issues: list[Issue] = []
        self.files_checked = 0
        self.config: dict | None = None
        self.policy: dict | None = None
        self.requirement_ids: set[str] = set()
        self.missions: dict[str, tuple[Path, dict]] = {}
        self.wps: dict[str, tuple[Path, dict]] = {}

    # -- issue helpers
    def rel(self, path: Path) -> str:
        return path.relative_to(self.root).as_posix()

    def add(self, path: Path, field: str, code: str, reason: str, fix: str, parse: bool = False) -> None:
        self.issues.append(Issue(self.rel(path), field, code, reason, fix, parse))

    # -- loading
    def load(self, path: Path, schema: str, markdown: bool) -> dict | None:
        self.files_checked += 1
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            self.add(path, "-", "file.unreadable", f"無法讀取檔案：{exc}", "確認檔案存在且為 UTF-8 文字", True)
            return None
        if markdown:
            try:
                text = frontmatter.split(text).front_matter
            except frontmatter.FrontMatterError as exc:
                self.add(path, "-", "file.front_matter", str(exc),
                         "檔案第一行需為 '---'，其後為 YAML 欄位，再以一行 '---' 結束（見 kit/templates/）", True)
                return None
        try:
            data = yamlio.load(text)
        except yamlio.DuplicateKeyError as exc:
            key = re.findall(r"duplicate key '?([^'\s]+)'?", str(exc.problem))
            line = exc.problem_mark.line + 1 if exc.problem_mark else "?"
            self.add(path, key[0] if key else "-", "yaml.duplicate_key",
                     f"YAML 鍵重複（第 {line} 行附近）：{exc.problem}", "刪除或合併重複的鍵；同一層只能出現一次", True)
            return None
        except yaml.YAMLError as exc:
            mark = getattr(exc, "problem_mark", None)
            where = f"第 {mark.line + 1} 行" if mark else "未知位置"
            self.add(path, "-", "yaml.syntax", f"YAML 語法錯誤（{where}）：{getattr(exc, 'problem', exc)}",
                     "修正縮排、冒號或引號；可先用 YAML 檢查工具確認", True)
            return None
        if not isinstance(data, dict):
            self.add(path, "-", "yaml.not_mapping", "內容不是 YAML 對應表（key: value）",
                     "改為 key: value 形式（見 kit/templates/ 的樣板）", True)
            return None
        doc = schemas.load_schema(schema).get("x-doc", "docs/11 §4")
        for err in sorted(schemas.validator(schema).iter_errors(data),
                          key=lambda e: (_field(e.absolute_path), e.validator, e.message)):
            code, reason, fix = _schema_fix(err, doc)
            self.add(path, _field(err.absolute_path), code, reason, fix)
        self._placeholders(path, data, [])
        return data

    def _placeholders(self, path: Path, node, trail: list) -> None:
        if isinstance(node, dict):
            for k in sorted(node, key=str):
                self._placeholders(path, node[k], [*trail, k])
        elif isinstance(node, list):
            for i, v in enumerate(node):
                self._placeholders(path, v, [*trail, i])
        elif isinstance(node, str) and PLACEHOLDER.search(node):
            self.add(path, _field(trail), "template.placeholder",
                     f"樣板空格未填：{PLACEHOLDER.search(node).group(0)}",
                     "以實際內容取代 <…>；若此欄屬於人類決定（例如 owner），請由人類填寫")


def _sorted_dirs(path: Path, pattern: str) -> list[Path]:
    return sorted((p for p in path.glob(pattern) if p.is_dir()), key=lambda p: p.name)


def _check_dir_name(repo: _Repo, path: Path, file_id: str | None, kind: str) -> None:
    if not isinstance(file_id, str):
        return
    name = path.parent.name
    if name != file_id and not name.startswith(file_id + "-"):
        repo.add(path, "id", f"{kind}.dir_mismatch",
                 f"目錄名稱 '{name}' 與 id '{file_id}' 不一致",
                 f"將目錄改名為 '{file_id}-<slug>'，或修正 id（見 docs/11 §3 命名規則）")


def _find_cycles(graph: dict[str, list[str]]) -> list[list[str]]:
    """Return each elementary cycle once, rotated to start at its smallest node."""
    cycles: set[tuple[str, ...]] = set()
    state: dict[str, int] = {}
    stack: list[str] = []

    def visit(node: str) -> None:
        state[node] = 1
        stack.append(node)
        for nxt in sorted(graph.get(node, [])):
            if nxt not in graph:
                continue
            if state.get(nxt) == 1:
                cyc = stack[stack.index(nxt):]
                i = cyc.index(min(cyc))
                cycles.add(tuple(cyc[i:] + cyc[:i]))
            elif state.get(nxt) is None:
                visit(nxt)
        stack.pop()
        state[node] = 2

    for n in sorted(graph):
        if state.get(n) is None:
            visit(n)
    return [list(c) for c in sorted(cycles)]


# --------------------------------------------------------------------------- main entry


def lint_repo(root: Path) -> LintResult:
    root = root.resolve()
    repo = _Repo(root)

    # Project-level files (optional; `aitw init` creates them).
    cfg = root / ".aiteam" / "config.yaml"
    if cfg.is_file():
        repo.config = repo.load(cfg, "config", markdown=False)
        if repo.config:
            _check_config(repo, cfg, repo.config)
    pol = root / ".aiteam" / "policy.yaml"
    if pol.is_file():
        repo.policy = repo.load(pol, "policy", markdown=False)
    req = root / "knowledge" / "requirements.yaml"
    if req.is_file():
        data = repo.load(req, "requirements", markdown=False)
        if data:
            seen: set[str] = set()
            for i, r in enumerate(data.get("requirements") or []):
                rid = r.get("id") if isinstance(r, dict) else None
                if isinstance(rid, str):
                    if rid in seen:
                        repo.add(req, f"requirements[{i}].id", "id.duplicate", f"需求編號重複：{rid}",
                                 "每個需求編號只能出現一次")
                    seen.add(rid)
            repo.requirement_ids = seen

    # Missions and work packages.
    wp_files: list[tuple[Path, dict]] = []
    for mdir in _sorted_dirs(root / "work" / "missions", "*"):
        mfile = mdir / "mission.md"
        if not mfile.is_file():
            repo.files_checked += 1
            repo.add(mdir / "mission.md", "-", "mission.missing", f"Mission 目錄 '{mdir.name}' 沒有 mission.md",
                     "依 kit/templates/mission.md 建立 mission.md，或移除空目錄", True)
            continue
        mdata = repo.load(mfile, "mission", markdown=True)
        if mdata is None:
            continue
        mid = mdata.get("id")
        _check_dir_name(repo, mfile, mid, "mission")
        if isinstance(mid, str):
            if mid in repo.missions:
                repo.add(mfile, "id", "id.duplicate",
                         f"Mission 編號重複：{mid} 也出現在 {repo.rel(repo.missions[mid][0])}",
                         "Mission 編號需在 repo 內唯一遞增；改用下一個未使用的編號")
            else:
                repo.missions[mid] = (mfile, mdata)
        for wdir in _sorted_dirs(mdir / "wp", "*"):
            wfile = wdir / "wp.md"
            if not wfile.is_file():
                repo.files_checked += 1
                repo.add(wfile, "-", "wp.missing", f"工作包目錄 '{wdir.name}' 沒有 wp.md",
                         "依 kit/templates/wp.md 建立 wp.md，或移除空目錄", True)
                continue
            wdata = repo.load(wfile, "wp", markdown=True)
            if wdata is None:
                continue
            wdata.setdefault("__mission_dir_id", mid)
            wp_files.append((wfile, wdata))

    for wfile, wdata in wp_files:
        wid = wdata.get("id")
        _check_dir_name(repo, wfile, wid, "wp")
        if isinstance(wid, str):
            if wid in repo.wps:
                repo.add(wfile, "id", "id.duplicate",
                         f"工作包編號重複：{wid} 也出現在 {repo.rel(repo.wps[wid][0])}",
                         "WP 編號需在 repo 內唯一遞增（docs/11 §3）；改用下一個未使用的編號")
            else:
                repo.wps[wid] = (wfile, wdata)

    for wfile, wdata in wp_files:
        _check_wp(repo, wfile, wdata)
        _check_wp_artifacts(repo, wfile, wdata)

    graph = {w: [d for d in (data.get("depends_on") or []) if isinstance(d, str)]
             for w, (_, data) in repo.wps.items()}
    for cyc in _find_cycles(graph):
        first = repo.wps[cyc[0]][0]
        chain = " → ".join([*cyc, cyc[0]])
        repo.add(first, "depends_on", "wp.dependency_cycle", f"相依成環：{chain}",
                 "移除其中一個相依，或把共同部分拆成新的工作包，使相依關係無環")

    issues = sorted(set(repo.issues))
    return LintResult(issues=issues, files_checked=repo.files_checked)


def _check_config(repo: _Repo, path: Path, cfg: dict) -> None:
    handles: dict[str, int] = {}
    for i, person in enumerate(cfg.get("people") or []):
        h = person.get("handle") if isinstance(person, dict) else None
        if isinstance(h, str):
            if h in handles:
                repo.add(path, f"people[{i}].handle", "id.duplicate", f"人員帳號重複：{h}", "每個帳號只登錄一次")
            handles[h] = i
    ids = (cfg.get("agents") or {}).get("identities") or []
    for j, ident in enumerate(ids):
        if ident in handles:
            repo.add(path, f"agents.identities[{j}]", "config.agent_is_person",
                     f"'{ident}' 同時登錄為人員與 Agent 身份",
                     "Agent 必須使用獨立的機器身份（docs/11 §9.1）；從其中一邊移除")


def _check_wp(repo: _Repo, wfile: Path, w: dict) -> None:
    mission = w.get("mission")
    dir_mid = w.pop("__mission_dir_id", None)
    if isinstance(mission, str):
        if mission not in repo.missions:
            repo.add(wfile, "mission", "ref.mission", f"引用不存在的 Mission：{mission}",
                     "改為已存在的 Mission 編號，或先建立該 Mission")
        elif isinstance(dir_mid, str) and mission != dir_mid:
            repo.add(wfile, "mission", "ref.mission_dir",
                     f"wp.md 的 mission 為 {mission}，但檔案位於 {dir_mid} 的目錄下",
                     "把工作包移到所屬 Mission 的 wp/ 目錄，或修正 mission 欄位")

    wid = w.get("id")
    for i, dep in enumerate(w.get("depends_on") or []):
        if not isinstance(dep, str):
            continue
        if dep == wid:
            repo.add(wfile, f"depends_on[{i}]", "wp.self_dependency", "工作包不可相依自己", "移除這個相依項目")
        elif dep not in repo.wps:
            repo.add(wfile, f"depends_on[{i}]", "ref.wp", f"引用不存在的工作包：{dep}",
                     "改為已存在的 WP 編號，或先建立該工作包（Plan PR）")

    allowed_sat = set(repo.requirement_ids)
    if isinstance(mission, str) and mission in repo.missions:
        allowed_sat |= {s.get("id") for s in repo.missions[mission][1].get("success") or [] if isinstance(s, dict)}
    for i, sat in enumerate(w.get("satisfies") or []):
        if isinstance(sat, str) and sat not in allowed_sat:
            repo.add(wfile, f"satisfies[{i}]", "ref.requirement", f"引用不存在的需求編號：{sat}",
                     "改為 knowledge/requirements.yaml 中的需求編號，或所屬 Mission 的 success 編號")

    seen_ac: set[str] = set()
    for i, ac in enumerate(w.get("acceptance") or []):
        aid = ac.get("id") if isinstance(ac, dict) else None
        if isinstance(aid, str):
            if aid in seen_ac:
                repo.add(wfile, f"acceptance[{i}].id", "id.duplicate", f"驗收條件編號重複：{aid}",
                         "同一工作包內 AC 編號需唯一")
            seen_ac.add(aid)

    autonomy, gate, executor, tier = w.get("autonomy"), w.get("gate"), w.get("executor"), w.get("review_tier")
    if autonomy in AUTONOMY_GATES and gate in DEFAULT_TIER and gate not in AUTONOMY_GATES[autonomy]:
        allowed = "、".join(sorted(AUTONOMY_GATES[autonomy]))
        repo.add(wfile, "gate", "wp.autonomy_gate", f"自主度 {autonomy} 與 Gate {gate} 不相容",
                 f"{autonomy} 對應的 Gate 為 {allowed}（docs/09 §3、docs/10）；調整自主度或 Gate")
    if executor in EXECUTOR_AUTONOMY and autonomy in AUTONOMY_GATES and autonomy not in EXECUTOR_AUTONOMY[executor]:
        allowed = "、".join(sorted(EXECUTOR_AUTONOMY[executor]))
        repo.add(wfile, "autonomy", "wp.executor_autonomy", f"執行者 {executor} 與自主度 {autonomy} 不相容",
                 f"executor={executor} 時自主度應為 {allowed}（實體動作由人執行：A1／A0）")
    if gate in DEFAULT_TIER and tier in TIER_RANK:
        minimum = DEFAULT_TIER[gate]
        if repo.policy:
            minimum = ((repo.policy.get("gates") or {}).get(gate) or {}).get("review_tier", minimum)
        if minimum in TIER_RANK and TIER_RANK[tier] < TIER_RANK[minimum]:
            repo.add(wfile, "review_tier", "wp.review_tier", f"審查層級 {tier} 低於 Gate {gate} 的預設 {minimum}",
                     f"把 review_tier 調為 {minimum} 或更高（docs/11 §4.1）")


def _wp_number(wid: str) -> str | None:
    m = re.fullmatch(r"WP-(\d{3,})", wid or "")
    return m.group(1) if m else None


def _check_wp_artifacts(repo: _Repo, wfile: Path, w: dict) -> None:
    wid = w.get("id") if isinstance(w.get("id"), str) else None
    wdir = wfile.parent
    ac_ids = {a.get("id") for a in w.get("acceptance") or [] if isinstance(a, dict)}

    def check_wp_field(path: Path, data: dict) -> None:
        if wid and data.get("wp") not in (None, wid):
            repo.add(path, "wp", "ref.wp_dir", f"wp 欄位為 {data.get('wp')}，但檔案位於 {wid} 的目錄下",
                     f"把 wp 改為 {wid}，或把檔案移到正確的工作包目錄")

    evidence_ids: set[str] = set()
    manifest = wdir / "evidence" / "manifest.yaml"
    if manifest.is_file():
        data = repo.load(manifest, "evidence-manifest", markdown=False)
        if data:
            check_wp_field(manifest, data)
            num = _wp_number(wid) if wid else None
            for i, item in enumerate(data.get("items") or []):
                if not isinstance(item, dict):
                    continue
                eid = item.get("id")
                if isinstance(eid, str):
                    if eid in evidence_ids:
                        repo.add(manifest, f"items[{i}].id", "id.duplicate", f"證據編號重複：{eid}",
                                 "證據只增不改：重跑請使用新編號（docs/11 §7.1）")
                    evidence_ids.add(eid)
                    m = re.fullmatch(r"EV-(\d{3,})-\d{2,}", eid)
                    if num and m and m.group(1) != num:
                        repo.add(manifest, f"items[{i}].id", "evidence.id_wp_mismatch",
                                 f"證據編號 {eid} 與工作包 {wid} 不一致", f"編號格式為 EV-{num}-NN（docs/11 §3）")
                ac = item.get("ac")
                if isinstance(ac, str) and ac not in ac_ids:
                    repo.add(manifest, f"items[{i}].ac", "ref.acceptance", f"引用不存在的驗收條件：{ac}",
                             f"改為 {wid or '該工作包'} 的 acceptance 中存在的 AC 編號")

    for pfile in sorted((wdir / "review").glob("packet-r*.md")):
        data = repo.load(pfile, "review-packet", markdown=True)
        if not data:
            continue
        check_wp_field(pfile, data)
        for i, claim in enumerate(data.get("claims") or []):
            for j, ev in enumerate((claim or {}).get("evidence") or []):
                if isinstance(ev, str) and ev.startswith("EV-") and ev not in evidence_ids:
                    repo.add(pfile, f"claims[{i}].evidence[{j}]", "ref.evidence", f"引用不存在的證據編號：{ev}",
                             "改為 evidence/manifest.yaml 中存在的證據編號，或先留證")
        for j, q in enumerate(data.get("questions") or []):
            if isinstance(q, str) and not (wdir / "decisions" / f"{q}.md").is_file():
                repo.add(pfile, f"questions[{j}]", "ref.decision", f"引用不存在的決策請求：{q}",
                         "改為 decisions/ 中存在的 DR 編號，或先建立該決策請求")

    for vfile in sorted((wdir / "review").glob("verification-r*.md")):
        data = repo.load(vfile, "verification-report", markdown=True)
        if not data:
            continue
        check_wp_field(vfile, data)
        for ac in sorted((data.get("criteria") or {}).keys()):
            if ac not in ac_ids:
                repo.add(vfile, f"criteria.{ac}", "ref.acceptance", f"引用不存在的驗收條件：{ac}",
                         f"改為 {wid or '該工作包'} 的 acceptance 中存在的 AC 編號")

    for dfile in sorted((wdir / "decisions").glob("DR-*.md")):
        data = repo.load(dfile, "decision-request", markdown=True)
        if not data:
            continue
        check_wp_field(dfile, data)
        did = data.get("id")
        if isinstance(did, str) and dfile.stem != did:
            repo.add(dfile, "id", "decision.file_mismatch", f"檔名 '{dfile.name}' 與 id '{did}' 不一致",
                     f"將檔案命名為 {did}.md")
        for i, b in enumerate(data.get("blocks") or []):
            if isinstance(b, str) and b not in repo.wps:
                repo.add(dfile, f"blocks[{i}]", "ref.wp", f"引用不存在的工作包：{b}", "改為已存在的 WP 編號")
        opt_ids = {o.get("id") for o in data.get("options") or [] if isinstance(o, dict)}
        rec = (data.get("recommendation") or {}).get("option")
        if isinstance(rec, str) and rec not in opt_ids:
            repo.add(dfile, "recommendation.option", "ref.option", f"建議選項 {rec} 不在 options 中",
                     "改為 options 中存在的選項編號")

    htr = wdir / "human-task-record.md"
    if htr.is_file():
        data = repo.load(htr, "human-task-record", markdown=True)
        if data:
            check_wp_field(htr, data)
