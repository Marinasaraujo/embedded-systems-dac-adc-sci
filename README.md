# Projeto de Síntese e Amostragem de Forma de Onda (DAC/ADC) no TMS320F28379D

Este projeto demonstra a síntese de uma forma de onda senoidal utilizando o Digital-to-Analog Converter (DAC) e a amostragem dessa mesma onda utilizando o Analog-to-Digital Converter (ADC) em um microcontrolador Texas Instruments TMS320F28379D. A temporização para a geração e amostragem da onda é controlada pelos CPU Timers do dispositivo.

## Funcionalidades

* **Geração de Forma de Onda Senoidal:** Utiliza o DAC integrado para sintetizar uma onda senoidal configurável.
* **Amostragem de Forma de Onda:** Utiliza o ADC integrado para amostrar a forma de onda gerada (ou qualquer sinal analógico conectado à entrada do ADC).
* **Sincronização de Timers:** Os CPU Timers são configurados para controlar a taxa de atualização do DAC e a taxa de amostragem do ADC.
* **Geração Automática do Buffer DAC:** Um script Python é fornecido para gerar o array de valores do DAC automaticamente, facilitando a alteração dos parâmetros da onda.

## Requisitos de Hardware

* Placa de desenvolvimento com o microcontrolador **TMS320F28379D** (ex: LaunchPad F28379D).
* Conexões físicas entre a saída do DAC e a entrada do ADC (para testar o loopback).

## Requisitos de Software

* **Code Composer Studio (CCS)** v20.x ou superior (IDE da Texas Instruments).
* **C2000Ware SDK** (Pacote de software da TI para microcontroladores C2000).
* **Python 3.11+** (para o script de geração do buffer DAC).


