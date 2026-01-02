/**
 * @file    main_ic.c
 * @brief   Lesson 6-6: Input Capture Frequency Measurement
 * @note    Demonstrates TIM3 input capture mode on PA6 (CH1)
 *
 * Hardware Connections:
 *   PWM Signal Source (for testing):
 *     - PWM Output -> PA0 (from TIM2)
 *     - PWM Input (for capture) -> PA6 (to TIM3 CH1)
 *
 *   OLED Display (4-pin I2C):
 *     - SCL -> PB8
 *     - SDA -> PB9
 *     - VCC -> 3.3V
 *     - GND -> GND
 *
 * Expected Behavior:
 *   - OLED shows "Freq: xxxxx Hz"
 *   - PWM from TIM2 provides test signal
 *   - TIM3 measures input frequency
 */

#include "stm32f10x.h"
#include "Delay.h"
#include "OLED.h"
#include "PWM.h"
#include "IC.h"

int main(void)
{
    OLED_Init();
    PWM_Init();
    IC_Init();

    OLED_ShowString(1, 1, "Freq:00000Hz");

    /* Test signal from TIM2 */
    PWM_SetPrescaler(720 - 1);
    PWM_SetCompare1(50);

    while (1)
    {
        OLED_ShowNum(1, 6, IC_GetFreq(), 5);
    }
}
