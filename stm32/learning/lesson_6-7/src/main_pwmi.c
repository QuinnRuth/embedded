/**
 * @file    main_pwmi.c
 * @brief   Lesson 6-7: PWMI Mode Frequency & Duty Cycle Measurement
 * @note    Demonstrates TIM3 PWMI mode on PA6 (CH1) and PA7 (CH2)
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
 *   - OLED shows "Duty: xx%"
 *   - PWM from TIM2 provides test signal
 *   - TIM3 measures both frequency and duty cycle
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
    OLED_ShowString(2, 1, "Duty:00%");

    /* Test signal from TIM2 */
    PWM_SetPrescaler(720 - 1);
    PWM_SetCompare1(50);

    while (1)
    {
        OLED_ShowNum(1, 6, IC_GetFreq(), 5);
        OLED_ShowNum(2, 6, IC_GetDuty(), 2);
    }
}
