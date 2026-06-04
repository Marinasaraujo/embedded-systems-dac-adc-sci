import serial
import struct
import time
import numpy as np
import matplotlib.pyplot as plt

SERIAL_PORT = 'COM11'
BAUD_RATE = 115200

CMD_RECEIVE_VECTOR = 1 # PC envia vetor para o DAC do 28379D
CMD_SEND_VECTOR    = 2 # PC pede o vetor do ADC para o 28379D

# Parâmetros alteraveis do sistema 
NUM_PONTOS_DAC = 200        # Numero de amostras enviadas ao DAC
FREQ_ATUALIZACAO_DAC = 5000 # Taxa de atualizacao do DAC em Hz (Timer 1)
FREQ_FUNDAMENTAL = 60       # Frequencia fundamental em Hz
AMP_FUNDAMENTAL = 0.8       # Amplitude da fundamental (0.0 a 1.0)

PRESENCA_HARMONICA = False
FREQ1_HARMONICA = 600        
AMP1_HARMONICA = 0.1         # Amplitude da harmonica (0.0 a 1.0)
FREQ2_HARMONICA = 6000       
AMP2_HARMONICA = 0.01         

NUM_PONTOS_ADC = 200        # Tamanho do buffer configurado no C (TAM_BUFFER_ADC)
TAXA_AMOSTRAGEM_ADC = 5000 # Taxa de amostragem do ADC em Hz (Timer 0)


def main():
    print("--- Gerador de Funções e Analisador de Dados SCI ---")
    
    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=3) as ser:
            print(f"Porta serial {SERIAL_PORT} aberta a {BAUD_RATE} bps.")
            time.sleep(1)
            ser.flushInput()

            while True:
                print("\n----- MENU -----")
                print("1. Sintetizar e Enviar Forma de Onda (DAC)")
                print("2. Adquirir e Analisar Sinal (ADC)")
                print("0. Sair")
                
                choice = input("Escolha uma opcao: ")

                if choice == '1':
                    send_vector(ser)
                elif choice == '2':
                    receive_vector(ser)
                elif choice == '0':
                    print("Encerrando.")
                    break
                else:
                    print("Opcao invalida.")

    except serial.SerialException as e:
        print(f"\nERRO: Nao foi possivel abrir a porta serial '{SERIAL_PORT}'.\nDetalhe: {e}")

def send_vector(ser_connection):
    """
    Gera a onda parametrizada, empacota e envia via SCI.
    """
    try:
        # Geração do eixo do tempo
        # O tempo total de um ciclo de buffer depende do número de pontos e da taxa do DAC
        tempo_total = NUM_PONTOS_DAC / FREQ_ATUALIZACAO_DAC
        tempo = np.linspace(0, tempo_total, NUM_PONTOS_DAC, endpoint=False)
        
        # Geração da Onda 
        onda_fund = AMP_FUNDAMENTAL * np.sin(2 * np.pi * FREQ_FUNDAMENTAL * tempo)
        onda1_harm = 0
        onda2_harm = 0
        if PRESENCA_HARMONICA:
            onda1_harm = AMP1_HARMONICA * np.sin(2 * np.pi * FREQ1_HARMONICA * tempo)
            onda2_harm = AMP2_HARMONICA * np.sin(2 * np.pi * FREQ2_HARMONICA * tempo)
            
        onda_composta = onda_fund + onda1_harm + onda2_harm
        
        # Normalização para o DAC (12 bits: 0 a 4095)
        # Limita a amplitude para não exceder 1.0 ou -1.0
        onda_composta = np.clip(onda_composta, -1.0, 1.0)
        onda_discreta = 2047 * onda_composta + 2048
        forma_onda_int = onda_discreta.astype(int).tolist()

        # Empacotamento
        tamanho_payload_bytes = len(forma_onda_int) * 2 
        formato = f'<Bh{len(forma_onda_int)}h'
        packet_to_send = struct.pack(formato, CMD_RECEIVE_VECTOR, tamanho_payload_bytes, *forma_onda_int)
        
        # Envio
        ser_connection.write(packet_to_send)
        print(f"\nVetor de {NUM_PONTOS_DAC} pontos enviado com sucesso ({len(packet_to_send)} bytes).")

        # Plot
        plt.figure("Sinal Enviado (Python)", figsize=(8, 3))
        plt.plot(tempo, forma_onda_int, marker='.', linestyle='-', color='b')
        plt.title("Sinal Gerado para o DAC")
        plt.xlabel("Tempo (s)")
        plt.ylabel("Amplitude (ADC Cts)")
        plt.grid(True)
        plt.show()

    except Exception as e:
        print(f"Erro no envio: {e}")

def receive_vector(ser_connection):
    """
    Solicita o vetor de amostras ao microcontrolador, recebe e plota no tempo e frequência (FFT).
    """
    try:
        ser_connection.flushInput()
        
        # Solicita o envio do vetor
        request_packet = struct.pack('<Bh', CMD_SEND_VECTOR, 0)
        ser_connection.write(request_packet)
        print(f"\nSolicitando vetor de {NUM_PONTOS_ADC} amostras do ADC...")

        # Aguarda a resposta (NUM_PONTOS_ADC * 2 bytes)
        bytes_esperados = NUM_PONTOS_ADC * 2
        response_data = ser_connection.read(bytes_esperados)

        if not response_data or len(response_data) < bytes_esperados:
            print(f"ERRO: Timeout. Recebeu {len(response_data)} de {bytes_esperados} bytes.")
            return

        # Desempacotamento dinâmico
        formato_recepcao = f'<{NUM_PONTOS_ADC}h'
        vetor_adc = struct.unpack(formato_recepcao, response_data)
        vetor_adc = np.array(vetor_adc)
        
        print("Vetor recebido com sucesso. Processando gráficos...")

        # Processamento: Eixo do tempo
        tempo_total = NUM_PONTOS_ADC / TAXA_AMOSTRAGEM_ADC
        tempo = np.linspace(0, tempo_total, NUM_PONTOS_ADC, endpoint=False)

        # Processamento: FFT (Domínio da Frequência)
        # Remove a componente DC (média) para a FFT não ser dominada pelo offset do ADC
        vetor_sem_dc = vetor_adc - np.mean(vetor_adc)
        
        fft_valores = np.fft.fft(vetor_sem_dc)
        fft_amplitudes = 2.0 / NUM_PONTOS_ADC * np.abs(fft_valores[0:NUM_PONTOS_ADC//2])
        frequencias_eixo = np.fft.fftfreq(NUM_PONTOS_ADC, 1.0/TAXA_AMOSTRAGEM_ADC)[0:NUM_PONTOS_ADC//2]

        # Plotagem Subplots (Tempo e Frequência)
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        fig.suptitle("Análise do Sinal Adquirido do ADC")

        # Gráfico no Tempo
        ax1.plot(tempo, vetor_adc, color='g', marker='.')
        ax1.set_title("Domínio do Tempo")
        ax1.set_xlabel("Tempo (s)")
        ax1.set_ylabel("Amplitude (ADC Cts)")
        ax1.grid(True)

        # Gráfico na Frequência (FFT)
        ax2.plot(frequencias_eixo, fft_amplitudes, color='r')
        ax2.set_title("Domínio da Frequência (FFT)")
        ax2.set_xlabel("Frequência (Hz)")
        ax2.set_ylabel("Magnitude")
        ax2.grid(True)

        ax2.set_xlim(0, TAXA_AMOSTRAGEM_ADC / 2) 

        plt.tight_layout()
        plt.show()

    except Exception as e:
        print(f"Erro na recepção: {e}")

if __name__ == "__main__":
    main()