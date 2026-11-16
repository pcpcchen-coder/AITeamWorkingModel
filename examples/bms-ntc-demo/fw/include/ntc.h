/* NTC 溫度換算介面 — 虛構範例（fictional）。 */
#ifndef NTC_H
#define NTC_H

#include <stdint.h>

typedef struct {
    uint16_t adc;    /* ADC 讀值 */
    int16_t decic;   /* 溫度，0.1°C */
} ntc_point_t;

/* 把 ADC 讀值換算為 0.1°C 單位的溫度（查表 + 線性內插）。
 * 已知限制（刻意保留，對應 docs/12 §6.2 的 Validator 發現 F1）：
 * 讀值超出表格範圍（例：NTC 斷線或短路）時回傳表格端點溫度，不回報故障。
 */
int16_t ntc_adc_to_decic(uint16_t adc);

#endif /* NTC_H */
