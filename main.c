//
// Included Files
//
#include "driverlib.h"
#include "device.h"
#include "board.h"
#include "math.h"
#include "scicomm.h"

//
// Definições de Tamanho
//
#define TAM_BUFFER_DAC 200
#define TAM_BUFFER_ADC 100

//
// Variáveis Globais 
// (Alocadas na RAM e iniciadas com zero para evitar lixo de memória na primeira execução)
//
volatile uint16_t dac_buffer[TAM_BUFFER_DAC] = {0};
volatile uint16_t adc_buffer[TAM_BUFFER_ADC] = {0};
volatile float gain = 1.0f; // Mexe na amplitude da senoide via Debug
volatile Protocol_Header_t g_prot_header = {CMD_NONE, 0};

//
// Main
//
void main(void)
{
    // Device Initialization
    Device_init();

    // Initializes PIE and clears PIE registers. Disables CPU interrupts.
    Interrupt_initModule();
    
    // Initializes the PIE vector table with pointers to ISRs
    Interrupt_initVectorTable();

    Board_init();

    // Enable Global Interrupt (INTM) and realtime interrupt (DBGM)
    EINT;
    ERTM;

    while(1)
    {
        if (g_prot_header.cmd != CMD_NONE)
        {
            switch (g_prot_header.cmd)
            {
                case CMD_RECEIVE_VECTOR:
                    // 1. Pausa o Timer do DAC para não gerar formas de onda deformadas
                    // Obs: Verifique se o nome gerado pelo seu SysConfig é myCPUTIMER1_BASE ou CPUTIMER1_BASE
                    CPUTimer_stopTimer(myCPUTIMER1_BASE); 

                    // 2. Recebe os dados e atualiza o dac_buffer
                    protocolReceiveVector(SCI0_BASE, (uint16_t*)dac_buffer, g_prot_header.data_len / 2);

                    // 3. Retoma o Timer do DAC com a nova onda
                    CPUTimer_startTimer(myCPUTIMER1_BASE);
                    break;

                case CMD_SEND_VECTOR:
                    // 1. Pausa o Timer do ADC para "congelar" a amostragem
                    CPUTimer_stopTimer(myCPUTIMER0_BASE);

                    // 2. Envia a foto estática do adc_buffer via SCI
                    protocolSendVector(SCI0_BASE, (uint16_t*)adc_buffer, TAM_BUFFER_ADC);

                    // 3. Retoma o Timer do ADC para continuar amostrando
                    CPUTimer_startTimer(myCPUTIMER0_BASE);
                    break;
            }

            // Limpa status de interrupção e reseta comando
            SCI_clearInterruptStatus(SCI0_BASE, SCI_INT_RXFF);
            g_prot_header.cmd = CMD_NONE;
        }
    }
}

// 
// Rotina de Interrupção do ADC (Disparada pelo fim da conversão)
//
__interrupt void INT_ADC0_1_ISR(void)  
{
    static uint16_t cnt_adc = 0; 
    
    adc_buffer[cnt_adc] = ADC_readResult(ADC0_RESULT_BASE, ADC0_SOC0);
    cnt_adc = (cnt_adc + 1) % TAM_BUFFER_ADC;
    
    ADC_clearInterruptStatus(ADC0_BASE, ADC_INT_NUMBER1);
    Interrupt_clearACKGroup(INT_ADC0_1_INTERRUPT_ACK_GROUP);
}

// 
// Rotina de Interrupção do DAC (Disparada pelo Timer 1)
//
__interrupt void INT_myCPUTIMER1_ISR(void)
{
    static uint16_t cnt_dac = 0;
    
    DAC_setShadowValue(DAC0_BASE, (uint16_t) (gain * dac_buffer[cnt_dac]));
    cnt_dac = (cnt_dac + 1) % TAM_BUFFER_DAC; 
}

// 
// Rotina de Interrupção da SCI (Recepção do Cabeçalho)
//
__interrupt void INT_SCI0_RX_ISR(void)
{
    uint16_t header[PROTOCOL_HEADER_SIZE];
    uint16_t cmd;

    // Lê apenas os 3 bytes do cabeçalho
    SCI_readCharArray(SCI0_BASE, header, PROTOCOL_HEADER_SIZE);
    
    cmd = header[0];
    g_prot_header.data_len = header[1] | (header[2] << 8);
    g_prot_header.cmd = (cmd < CMD_COUNT) ? (SCI_Command_e)cmd : CMD_NONE;

    Interrupt_clearACKGroup(INT_SCI0_RX_INTERRUPT_ACK_GROUP);
}