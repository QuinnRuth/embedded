/**
 * @file LED闪烁.cpp
 * @brief STM32 GPIO输出模式实践 - 控制单个LED闪烁
 * @author (你的名字)
 * @date 2025-09-10
 * @note 本程序基于STM32F10x标准库，演示了如何配置并使用一个GPIO引脚
 *       作为推挽输出，驱动一个LED灯以1Hz的频率闪烁。
 */

#include "stm32f10x.h" // 包含所有STM32F10x系列外设的定义

// --- 延时函数 ---
// 在没有配置系统定时器（如SysTick）的早期学习阶段，
// 使用简单的软件循环来实现延时是一种常见做法。
// 注意：这种延时的精确度受编译器优化和系统主频影响。
void Delay_ms(uint32_t nms)
{
	uint32_t i, j;
	for (i = 0; i < nms; i++)
	{
		for (j = 0; j < 7200; j++); // 在72MHz主频下，这个内循环大致消耗1ms
	}
}

/**
 * @brief  主函数，程序从这里开始执行
 * @param  None
 * @retval int 永远不会返回
 */
int main(void)
{
	/****************************************************************
	 * 步骤 1: 开启外设时钟
	 * 笔记知识点: [GPIO在STM32中的位置]
	 * - 所有外设都像独立的模块，默认处于关闭状态以节省功耗。
	 * - 使用任何外设前，必须先通过RCC(Reset and Clock Control)为其提供时钟。
	 * - GPIOA, GPIOB等端口挂载在高速APB2总线上。
	 ****************************************************************/
	RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA, ENABLE);

	/****************************************************************
	 * 步骤 2: 初始化GPIO引脚
	 * 笔记知识点: [8种工作模式] & [推挽输出]
	 ****************************************************************/
	GPIO_InitTypeDef GPIO_InitStructure; // 定义一个GPIO初始化结构体变量

	// 配置引脚PA0
	GPIO_InitStructure.GPIO_Pin = GPIO_Pin_0;
	
	// 配置工作模式为推挽输出 (Push-Pull Output)
	// 笔记知识点: [P-MOS和N-MOS晶体管] & [推挽输出特性]
	// - 推挽输出由P-MOS和N-MOS互补对构成。
	// - 能够强力地主动输出高电平(Push)和低电平(Pull)。
	// - 驱动能力强，速度快，是驱动LED这类负载最理想的模式。
	GPIO_InitStructure.GPIO_Mode = GPIO_Mode_Out_PP;

	// 配置引脚输出速度为50MHz (最高)
	GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;

	// 调用库函数，将上述配置写入到GPIOA的寄存器中
	GPIO_Init(GPIOA, &GPIO_InitStructure);
	
	/****************************************************************
	 * 步骤 3: 进入无限循环，控制LED闪烁
	 * 笔记知识点: [位设置/清除寄存器(BSRR)]
	 ****************************************************************/
	while (1)
	{
		// --- 点亮LED ---
		// 假设LED的负极连接到PA0，正极通过限流电阻接到3.3V (灌电流模式)。
		// 此时，需要PA0输出低电平(0V)，才能形成电位差，点亮LED。
		// 使用GPIO_ResetBits函数来输出低电平。
		// 笔记知识点: [BSRR]
		// - GPIO_ResetBits()函数向BSRR寄存器的高16位(BR0-BR15)写入1。
		// - 这是一个原子操作，能安全、高效地将对应ODR位置0，不会影响其他位。
		GPIO_ResetBits(GPIOA, GPIO_Pin_0);
		Delay_ms(500); // 延时500毫秒

		// --- 熄灭LED ---
		// PA0输出高电平(3.3V)，与电源电压相同，没有电位差，LED熄灭。
		// 使用GPIO_SetBits函数来输出高电平。
		// 笔记知识点: [BSRR]
		// - GPIO_SetBits()函数向BSRR寄存器的低16位(BS0-BS15)写入1。
		// - 同样是原子操作，安全地将对应ODR位置1。
		GPIO_SetBits(GPIOA, GPIO_Pin_0);
		Delay_ms(500); // 延时500毫秒
	}
}