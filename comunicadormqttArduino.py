import paho.mqtt.client as mqtt
import json
import time
import random
import serial
import threading
import sys

# Configuração do MQTT
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "estacionamento/vagas"
CLIENT_ID = f"python-estacionamento-{random.randint(0, 1000)}"

# Configuração da porta serial
SERIAL_PORT = "COM3"
SERIAL_BAUD = 9600

# Total de vagas no estacionamento
TOTAL_VAGAS = 6

# Variável global para armazenar os status das vagas
vagas_status = [0] * TOTAL_VAGAS  # Inicialmente todas as vagas estão livres (0)
ultimo_valor_com3 = None  # Armazena o último valor numérico lido da COM3

# Função para imprimir mensagens de debug com timestamp
def debug_print(message):
    timestamp = time.strftime("%H:%M:%S", time.localtime())
    print(f"[{timestamp}] DEBUG: {message}")

# Função de callback quando a conexão for estabelecida
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        debug_print(f"Conectado ao broker MQTT: {MQTT_BROKER}")
    else:
        debug_print(f"Falha na conexão ao broker. Código de retorno: {rc}")

# Função para ler o valor do sensor Arduino
def ler_sensor_arduino():
    global vagas_status, ultimo_valor_com3

    debug_print(f"Iniciando leitura da porta serial {SERIAL_PORT} para a vaga 3")

    try:
        ser = serial.Serial(SERIAL_PORT, SERIAL_BAUD, timeout=0.1)
        time.sleep(2)
        debug_print(f"✅ COM3 conectada com sucesso! Baud rate: {SERIAL_BAUD}")

        buffer = ""

        while True:
            try:
                if ser.in_waiting > 0:
                    linha = ser.readline().decode(errors='ignore').strip()
                    debug_print(f"Linha lida: '{linha}'")

                    if linha.startswith("Distancia"):
                        partes = linha.split()

                        if len(partes) == 2:
                            try:
                                valor = int(partes[1])
                                ultimo_valor_com3 = valor
                                debug_print(f"Valor de distância lido da COM3: {valor}")

                                status_anterior = vagas_status[3]
                                vagas_status[3] = 1 if valor < 10 else 0

                                if status_anterior != vagas_status[3]:
                                    status_texto = "OCUPADA" if vagas_status[3] == 1 else "LIVRE"
                                    debug_print(f"⚠️ MUDANÇA DE STATUS DA VAGA 3: {status_texto} (valor={valor})")
                                else:
                                    status_texto = "ocupada" if vagas_status[3] == 1 else "livre"
                                    debug_print(f"Vaga 3 continua {status_texto} (valor={valor})")

                            except ValueError:
                                debug_print(f"⚠️ ERRO: Não foi possível converter '{partes[1]}' para inteiro")

            except Exception as e:
                debug_print(f"⚠️ ERRO na leitura da porta serial: {e}")
                time.sleep(1)

            time.sleep(0.2)

    except serial.SerialException as e:
        debug_print(f"❌ ERRO FATAL: Não foi possível abrir a porta serial {SERIAL_PORT}: {e}")
        debug_print(f"Simulando valores para a vaga 3...")

        while True:
            valor = random.randint(0, 20)
            ultimo_valor_com3 = valor
            vagas_status[3] = 1 if valor < 10 else 0
            status_texto = "OCUPADA" if vagas_status[3] == 1 else "LIVRE"
            debug_print(f"[SIMULAÇÃO] Vaga 3: {status_texto} (valor simulado={valor})")
            time.sleep(5)



# Função para simular as outras vagas (exceto a vaga 3)
def simular_outras_vagas():
    global vagas_status
    
    debug_print("Iniciando simulação das outras vagas")
    
    while True:
        for i in range(TOTAL_VAGAS):
            if i != 3:
                status_anterior = vagas_status[i]
                vagas_status[i] = random.randint(0, 1)
                
                if status_anterior != vagas_status[i]:
                    status_texto = "OCUPADA" if vagas_status[i] == 1 else "LIVRE"
                    debug_print(f"Vaga {i}: mudou para {status_texto}")
        
        debug_print("Simulação das outras vagas concluída")
        time.sleep(40)  # Simula a cada 40 segundos

# Função para publicar o status das vagas
def publicar_vagas(client):
    global vagas_status, ultimo_valor_com3
    
    debug_print("Iniciando publicação no tópico MQTT")
    
    while True:
        # Exibe o estado atual das vagas
        vagas_texto = []
        for i, status in enumerate(vagas_status):
            texto = "OCUPADA" if status == 1 else "LIVRE"
            vagas_texto.append(f"Vaga {i}: {texto}")
        
        debug_print("Estado atual das vagas:")
        debug_print(" | ".join(vagas_texto))
        
        # Inclui o valor numérico da COM3 no payload, se disponível
        payload = {
            "vagas": vagas_status,
            "vaga3_valor_com3": ultimo_valor_com3 if ultimo_valor_com3 is not None else "N/A"
        }
        
        payload_json = json.dumps(payload)
        
        debug_print(f"Publicando no tópico MQTT: {MQTT_TOPIC}")
        client.publish(MQTT_TOPIC, payload_json)
        debug_print(f"✅ Publicado com sucesso: {payload_json}")
        
        time.sleep(3)  # Publica a cada 3 segundos

def main():
    debug_print("=== SISTEMA DE MONITORAMENTO DE ESTACIONAMENTO ===")
    debug_print(f"Broker MQTT: {MQTT_BROKER}:{MQTT_PORT}")
    debug_print(f"Tópico: {MQTT_TOPIC}")
    debug_print(f"Porta Serial Arduino: {SERIAL_PORT} @ {SERIAL_BAUD} baud")
    debug_print(f"Cliente ID: {CLIENT_ID}")
    debug_print("============================================")
    
    try:
        debug_print("Iniciando cliente MQTT...")
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, CLIENT_ID)
        client.on_connect = on_connect
        
        debug_print(f"Conectando ao broker MQTT {MQTT_BROKER}...")
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        
        client.loop_start()
        debug_print("Loop MQTT iniciado")
        
        # Thread para ler o sensor do Arduino (vaga 3)
        debug_print("Iniciando thread de leitura do Arduino...")
        arduino_thread = threading.Thread(target=ler_sensor_arduino)
        arduino_thread.daemon = True
        arduino_thread.start()
        
        # Thread para simular as outras vagas
        debug_print("Iniciando thread de simulação das outras vagas...")
        simulacao_thread = threading.Thread(target=simular_outras_vagas)
        simulacao_thread.daemon = True
        simulacao_thread.start()
        
        # Thread para publicar os dados
        debug_print("Iniciando thread de publicação MQTT...")
        publicar_thread = threading.Thread(target=publicar_vagas, args=(client,))
        publicar_thread.daemon = True
        publicar_thread.start()
        
        # Mantém o programa rodando
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        debug_print("Programa interrompido pelo usuário")
    except Exception as e:
        debug_print(f"❌ ERRO FATAL: {e}")
        debug_print(f"Tipo de erro: {type(e).__name__}")
        import traceback
        debug_print(traceback.format_exc())
    finally:
        debug_print("Encerrando cliente MQTT...")
        try:
            client.loop_stop()
            client.disconnect()
            debug_print("Cliente MQTT desconectado")
        except:
            pass
        debug_print("Programa encerrado")

if __name__ == "__main__":
    main()