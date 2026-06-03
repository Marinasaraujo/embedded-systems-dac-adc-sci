/*
 * scicomm.h
 *
 *  Created on: 13 de jun de 2025
 *      Author: Guilherme M�rcio Soares
 */

#ifndef SRC_SCICOMM_H_
#define SRC_SCICOMM_H_

#include <stdint.h>

#define INT_SIZE 2U
#define PROTOCOL_HEADER_SIZE 3U

typedef enum
{
    CMD_NONE = 0,
    CMD_RECEIVE_VECTOR, // 1 
    CMD_SEND_VECTOR,    // 2
    CMD_COUNT
} SCI_Command_e;

typedef struct
{
    SCI_Command_e cmd;
    uint16_t data_len;
} Protocol_Header_t;


void protocolReceiveVector(unsigned int sci_base, volatile uint16_t *vector, uint16_t length);
void protocolSendVector(unsigned int sci_base, volatile uint16_t *vector, uint16_t length);

#endif /* SRC_SCICOMM_H_ */