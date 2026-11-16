/* 產生檔，請勿手改 — 虛構範例資料（fictional）。
 * 來源：knowledge/interfaces/analog.yaml version 1
 * 產生：python examples/bms-ntc-demo/fw/tools/gen_ntc_table.py
 * 上拉 10000 Ω、R25 10000 Ω、Beta 3435 K、ADC 12 bit；每 5°C 一點。
 * ADC 讀值隨溫度上升而遞減（NTC 接地端）。
 */
#ifndef NTC_TABLE_DATA_H
#define NTC_TABLE_DATA_H

#define NTC_TABLE_LEN 26

static const ntc_point_t NTC_TABLE[NTC_TABLE_LEN] = {
    {3936,  -400},
    {3882,  -350},
    {3813,  -300},
    {3729,  -250},
    {3627,  -200},
    {3507,  -150},
    {3368,  -100},
    {3210,   -50},
    {3037,     0},
    {2850,    50},
    {2654,   100},
    {2451,   150},
    {2248,   200},
    {2048,   250},
    {1854,   300},
    {1669,   350},
    {1496,   400},
    {1337,   450},
    {1191,   500},
    {1059,   550},
    { 940,   600},
    { 834,   650},
    { 740,   700},
    { 657,   750},
    { 584,   800},
    { 519,   850},
};

#endif /* NTC_TABLE_DATA_H */
