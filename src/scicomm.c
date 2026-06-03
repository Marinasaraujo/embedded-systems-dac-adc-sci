/*
 * scicomm.c
 *
 *  Created on: 13 de jun de 2025
 *      Author: Guilherme M�rcio Soares
 */
#include "board.h"
#include "device.h"
#include "scicomm.h"

void protocolReceiveVector(unsigned int sci_base, volatile uint16_t *vector, uint16_t length)
{
    uint16_t buffer[INT_SIZE]; 
    // Percorre o tamanho total do vetor
    for (uint16_t i = 0; i < length; i++)
    {
        // Lê os próximos 2 bytes da serial (bloqueia até receber)
        SCI_readCharArray(sci_base, buffer, INT_SIZE);
        vector[i] = buffer[0] | (buffer[1] << 8U);
    }
}

void protocolSendVector(unsigned int sci_base, volatile uint16_t *vector, uint16_t length)
{
    uint16_t txBuf[INT_SIZE];

    // Percorre o vetor de dados do ADC
    for (uint16_t i = 0; i < length; i++)
    {
        // Quebra cada amostra de 16 bits em 2 bytes separados
        txBuf[0] = (uint16_t)(vector[i] & 0x00FF);
        txBuf[1] = (uint16_t)((vector[i] >> 8U) & 0x00FF);

        // Envia o par de bytes pela serial
        SCI_writeCharArray(sci_base, txBuf, INT_SIZE);
    }
}