/**
 * @file    Motor.c
 * @brief   DC Motor Control with L298N Driver
 * @note    Uses TIM2 Channel 3 on PA2 for PWM speed control
 *
 * Hardware Connection:
 *   - ENA (PWM) -> PA2
 *   - IN1 -> PA4
 *   - IN2 -> PA5
 */

#include "stm32f10x.h"
#include "PWM.h"

/**
 * @brief  Initialize motor control pins
 */
void Motor_Init(void)
{
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA, ENABLE);

    GPIO_InitTypeDef GPIO_InitStructure;
    GPIO_InitStructure.GPIO_Mode = GPIO_Mode_Out_PP;
    GPIO_InitStructure.GPIO_Pin = GPIO_Pin_4 | GPIO_Pin_5;
    GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
    GPIO_Init(GPIOA, &GPIO_InitStructure);

    PWM_Init();
}

/**
 * @brief  Set motor speed
 * @param  Speed: -100 to 100
 *           >0: forward
 *           <0: reverse
 */
void Motor_SetSpeed(int8_t Speed)
{
    if (Speed >= 0)
    {
        GPIO_SetBits(GPIOA, GPIO_Pin_4);
        GPIO_ResetBits(GPIOA, GPIO_Pin_5);
        PWM_SetCompare3(Speed);
    }
    else
    {
        GPIO_ResetBits(GPIOA, GPIO_Pin_4);
        GPIO_SetBits(GPIOA, GPIO_Pin_5);
        PWM_SetCompare3(-Speed);
    }
}
