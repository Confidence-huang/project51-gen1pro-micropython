#ifndef APP_LED_H
#define APP_LED_H

#include "stm32f4xx_hal.h"

void AppLed_Run(UART_HandleTypeDef *console);
void AppLed_RxComplete(UART_HandleTypeDef *uart);
void AppLed_RxError(UART_HandleTypeDef *uart);

#endif
