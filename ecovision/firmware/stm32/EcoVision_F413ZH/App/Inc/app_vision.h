#ifndef APP_VISION_H
#define APP_VISION_H
#include "main.h"
void AppVision_Run(UART_HandleTypeDef *uart);
void AppVision_RxComplete(UART_HandleTypeDef *uart);
void AppVision_RxError(UART_HandleTypeDef *uart);
void AppVision_Rehandshake(void);
#endif
