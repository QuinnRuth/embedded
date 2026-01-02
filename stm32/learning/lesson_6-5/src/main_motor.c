/**
 * @file    main_motor.c
 * @brief   Lesson 6-5: PWM DC Motor Control
 * @note    Demonstrates DC motor speed control using TIM2 Channel 3 on PA2
 *
 * Hardware Connections:
 *   DC Motor Driver (L298N or similar):
 *     - ENA (PWM) -> PA2
 *     - IN1 -> PA4
 *     - IN2 -> PA5
 *     - GND -> GND
 *
 *   OLED Display (4-pin I2C):
 *     - SCL -> PB8
 *     - SDA -> PB9
 *     - VCC -> 3.3V
 *     - GND -> GND
 *
 *   Key Pin:
 *     - Key1 -> PB1
 *
 * Expected Behavior:
 *   - Press Key1 to cycle speed: 0 -> 20 -> 40 -> ... -> 100 -> -100
 *   - Positive values: forward rotation
 *   - Negative values: reverse rotation
 *   - OLED shows current speed
 */

#include "stm32f10x.h"
#include "Delay.h"
#include "OLED.h"
#include "Motor.h"
#include "Key.h"

uint8_t KeyNum = 0;
int8_t Speed = 0;

int main(void)
{
    OLED_Init();
    Motor_Init();
    Key_Init();

    OLED_ShowString(1, 1, "Speed:");

    while (1)
    {
        KeyNum = Key_GetNum();
        if (KeyNum == 1)
        {
            Speed += 20;
            if (Speed > 100)
            {
                Speed = -100;
            }
        }
        Motor_SetSpeed(Speed);
        OLED_ShowSignedNum(1, 7, Speed, 3);
    }
}
