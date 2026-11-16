/* NTC 溫度換算：查表 + 線性內插 — 虛構範例（fictional）。 */
#include "ntc.h"
#include "ntc_table_data.h"

int16_t ntc_adc_to_decic(uint16_t adc)
{
    /* 表格依 ADC 遞減排列：index 0 = 最低溫（最大讀值）。 */
    if (adc >= NTC_TABLE[0].adc) {
        return NTC_TABLE[0].decic;                    /* 已知限制：不回報故障 */
    }
    if (adc <= NTC_TABLE[NTC_TABLE_LEN - 1].adc) {
        return NTC_TABLE[NTC_TABLE_LEN - 1].decic;    /* 已知限制：不回報故障 */
    }
    unsigned lo = 0u, hi = NTC_TABLE_LEN - 1u;        /* 不變式：table[lo].adc > adc > table[hi].adc */
    while (hi - lo > 1u) {
        unsigned mid = (lo + hi) / 2u;
        if (NTC_TABLE[mid].adc > adc) {
            lo = mid;
        } else {
            hi = mid;
        }
    }
    const int32_t a0 = NTC_TABLE[lo].adc, a1 = NTC_TABLE[hi].adc;
    const int32_t t0 = NTC_TABLE[lo].decic, t1 = NTC_TABLE[hi].decic;
    const int32_t num = (t1 - t0) * (a0 - (int32_t)adc);
    const int32_t den = a0 - a1;
    return (int16_t)(t0 + (num + den / 2) / den);     /* 四捨五入 */
}
