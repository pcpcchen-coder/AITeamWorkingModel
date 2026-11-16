/* 主機端單元測試 — 虛構範例（fictional）。以主機 C 編譯器建置，不需任何目標板或設備。 */
#include <stdio.h>
#include <stdlib.h>

#include "analog_config.h"
#include "ntc.h"
#include "ntc_table_data.h"

static int failures = 0;

#define CHECK(cond, ...)                                  \
    do {                                                  \
        if (!(cond)) {                                    \
            failures++;                                   \
            printf("FAIL %s:%d: ", __FILE__, __LINE__);   \
            printf(__VA_ARGS__);                          \
            printf("\n");                                 \
        }                                                 \
    } while (0)

static void test_table_is_strictly_decreasing(void)
{
    for (unsigned i = 1; i < NTC_TABLE_LEN; i++) {
        CHECK(NTC_TABLE[i].adc < NTC_TABLE[i - 1].adc, "table[%u] not decreasing", i);
        CHECK(NTC_TABLE[i].decic > NTC_TABLE[i - 1].decic, "temps not increasing at %u", i);
    }
}

static void test_table_points_map_exactly(void)
{
    for (unsigned i = 0; i < NTC_TABLE_LEN; i++) {
        int16_t t = ntc_adc_to_decic(NTC_TABLE[i].adc);
        CHECK(t == NTC_TABLE[i].decic, "point %u: got %d want %d", i, t, NTC_TABLE[i].decic);
    }
}

static void test_25c_is_mid_scale(void)
{
    /* 上拉 = R25 時，25°C 位於量程中點 */
    int16_t t = ntc_adc_to_decic((uint16_t)((AN_ADC_MAX + 1u) / 2u));
    CHECK(abs(t - 250) <= 1, "mid-scale: got %d want 250±1", t);
}

static void test_interpolation_is_monotonic(void)
{
    int16_t prev = ntc_adc_to_decic(NTC_TABLE[0].adc);
    for (uint32_t adc = NTC_TABLE[0].adc; adc-- > NTC_TABLE[NTC_TABLE_LEN - 1].adc;) {
        int16_t t = ntc_adc_to_decic((uint16_t)adc);
        CHECK(t >= prev, "non-monotonic at adc=%u", (unsigned)adc);
        prev = t;
    }
}

static void test_out_of_range_clamps_known_limitation(void)
{
    /* 記錄現況：超出範圍回傳端點值（docs/12 §6.2 的 F1；WP-003 返工時處理） */
    CHECK(ntc_adc_to_decic((uint16_t)AN_ADC_MAX) == NTC_TABLE[0].decic, "open-circuit clamp");
    CHECK(ntc_adc_to_decic(0u) == NTC_TABLE[NTC_TABLE_LEN - 1].decic, "short-circuit clamp");
}

int main(void)
{
    test_table_is_strictly_decreasing();
    test_table_points_map_exactly();
    test_25c_is_mid_scale();
    test_interpolation_is_monotonic();
    test_out_of_range_clamps_known_limitation();
    if (failures) {
        printf("%d check(s) failed\n", failures);
        return 1;
    }
    printf("fw host tests: all checks passed\n");
    return 0;
}
