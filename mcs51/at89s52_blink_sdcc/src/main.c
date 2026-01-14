#include <8052.h>
#include <stdint.h>

#ifndef FOSC_HZ
#define FOSC_HZ 11059200UL
#endif

#ifndef LED_ACTIVE_LOW
#define LED_ACTIVE_LOW 1
#endif

#define TICKS_PER_MS (FOSC_HZ / 12UL / 1000UL)
#define TIMER0_RELOAD (65536UL - TICKS_PER_MS)
#define TH0_RELOAD ((uint8_t)((TIMER0_RELOAD >> 8) & 0xFF))
#define TL0_RELOAD ((uint8_t)(TIMER0_RELOAD & 0xFF))

#ifndef LED_PIN
#define LED_PIN P1_0
#endif

static void timer0_init(void) {
  TMOD = (TMOD & 0xF0) | 0x01;
  TR0 = 0;
  TF0 = 0;
}

static void delay_ms(uint16_t ms) {
  while (ms--) {
    TH0 = TH0_RELOAD;
    TL0 = TL0_RELOAD;
    TR0 = 1;
    while (!TF0) {
    }
    TR0 = 0;
    TF0 = 0;
  }
}

void main(void) {
  timer0_init();
  LED_PIN = (LED_ACTIVE_LOW ? 1 : 0);

  while (1) {
    LED_PIN = !LED_PIN;
    delay_ms(500);
  }
}
