# 韌體主機端建置 — 虛構範例（fictional）。只用主機 C 編譯器；不連接任何目標板或設備。
CC      ?= cc
CFLAGS  ?= -std=c99 -O2 -Wall -Wextra -Werror -pedantic
BUILD   := build
INC     := -Iinclude

.PHONY: test size clean

$(BUILD)/test_ntc: tests/test_ntc.c src/ntc.c include/ntc.h include/ntc_table_data.h include/analog_config.h | $(BUILD)
	$(CC) $(CFLAGS) $(INC) -o $@ tests/test_ntc.c src/ntc.c

$(BUILD)/ntc.o: src/ntc.c include/ntc.h include/ntc_table_data.h | $(BUILD)
	$(CC) $(CFLAGS) $(INC) -c -o $@ src/ntc.c

$(BUILD):
	mkdir -p $(BUILD)

test: $(BUILD)/test_ntc
	./$(BUILD)/test_ntc

# 主機端物件大小（示意；真實目標的 Flash／RAM 用量需目標工具鏈，屬選用配方）
size: $(BUILD)/ntc.o
	size $(BUILD)/ntc.o

clean:
	rm -rf $(BUILD)
