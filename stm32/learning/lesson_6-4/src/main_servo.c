/**
 * @file    main_servo.c
 * @brief   Lesson 6-4: PWM Servo Control
 * @note    Demonstrates servo control using TIM2 Channel 2 on PA1
 *
 * Hardware Connections:
 *   Servo Motor (SG90):
 *     - Signal -> PA1
 *     - VCC -> 5V
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
 *   - Press Key1 to rotate servo by 30 degrees
 *   - Cycles: 0 -> 30 -> 60 -> ... -> 180 -> 0
 *   - OLED shows current angle
 */

#include "stm32f10x.h"
#include "Delay.h"
#include "OLED.h"
#include "Servo.h"
#include "Key.h"

uint8_t KeyNum = 0;
float Angle = 0;

int main(void)
{
    OLED_Init();
    Servo_Init();
    Key_Init();

    OLED_ShowString(1, 1, "Angle:");

    while (1)
    {
        KeyNum = Key_GetNum();
        if (KeyNum == 1)
        {
            Angle += 30;
            if (Angle > 180)
            {
                Angle = 0;
            }
        }
        Servo_SetAngle(Angle);
        OLED_ShowNum(1, 7, (uint16_t)Angle, 3);
    }
}
