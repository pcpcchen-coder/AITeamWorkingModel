/* 類比鏈常數 — 虛構範例資料（fictional）。
 * 必須與 knowledge/interfaces/analog.yaml 一致（正本在 ICD；一致性檢查見工單 K5）。
 */
#ifndef ANALOG_CONFIG_H
#define ANALOG_CONFIG_H

#define AN_PULLUP_OHM   10000u
#define AN_NTC_R25_OHM  10000u
#define AN_NTC_BETA_K   3435u
#define AN_ADC_BITS     12u
#define AN_ADC_MAX      ((1u << AN_ADC_BITS) - 1u)

#endif /* ANALOG_CONFIG_H */
