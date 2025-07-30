import socketserver
import threading
import random
import string
import time

"""Uso del Simulador:
1. Ejecuta este script para iniciar el servidor.
2. Conéctate al servidor usando un cliente TCP (por ejemplo, telnet o netcat). telnet localhost 9999
3. Envía comandos en el formato <XX#...> donde XX es el código del comando. <93#D#6#>
4. El servidor responderá con una simulación de la respuesta esperada.
5. Puedes enviar múltiples comandos sin cerrar la conexión, el servidor mantendrá la conexión abierta.
6. Para detener el servidor, presiona Ctrl+C en la consola donde se está ejecutando"""

# --- Configuración del Servidor ---
HOST, PORT = "localhost", 9999

# --- Lógica de Simulación de Comandos Atalla ---
# (Las funciones no cambian)
def generate_hex(length):
    """Genera una cadena hexadecimal aleatoria de la longitud especificada."""
    return ''.join(random.choice('0123456789ABCDEF') for _ in range(length))

def generate_dec(length):
    """Genera una cadena decimal aleatoria de la longitud especificada."""
    return ''.join(random.choice('0123456789') for _ in range(length))

def handle_command_93(data):
    """Simula el Comando 93."""
    print("-> Recibido Comando 93: Generar Número Aleatorio")
    error_code = "00"
    random_number = generate_dec(6)
    response = f"<A3#{error_code}#{random_number}#>" # Se añade \n para limpiar el buffer del cliente
    print(f"<- Enviando Respuesta: {response.strip()}")
    return response

def handle_command_30(data):
    """Simula el Comando 30."""
    print("-> Recibido Comando 30: Encriptar PIN Formato ANSI 0")
    error_code = "00"
    encrypted_pin_block = generate_hex(16)
    response = f"<40#{error_code}{encrypted_pin_block}#>"
    print(f"<- Enviando Respuesta: {response.strip()}")
    return response

def handle_command_37(data):
    """Simula el Comando 37."""
    print("-> Recibido Comando 37: Cambio de PIN IBM3624")
    error_code = "00"
    response = f"<47#{error_code}#>"
    print(f"<- Enviando Respuesta: {response.strip()}")
    return response

def handle_command_32(data):
    """Simula el Comando 32."""
    print("-> Recibido Comando 32: Verificar PIN IBM3624")
    error_code = "00" # '00' significa PIN Válido
    response = f"<42#{error_code}#>"
    print(f"<- Enviando Respuesta: {response.strip()}")
    return response

# Mapeo de comandos a funciones.
COMMAND_MAP = {
    "<93#": handle_command_93,
    "<30#": handle_command_30,
    "<37#": handle_command_37,
    "<32#": handle_command_32,
}

class AtallaTCPHandler(socketserver.BaseRequestHandler):
    """
    El manejador de peticiones para el servidor.
    <<< MODIFICACIÓN PRINCIPAL >>>
    El método handle ahora contiene un bucle infinito para procesar
    múltiples comandos sin cerrar la conexión.
    """
    def handle(self):
        print(f"\n✅ Conexión persistente establecida con {self.client_address[0]}")
        
        # <<< BUCLE PARA MANTENER LA CONEXIÓN ABIERTA >>>
        while True:
            full_data_bytes = b''
            # Bucle interno para leer una trama completa (terminada en > y Enter)
            while True:
                try:
                    chunk = self.request.recv(1024)
                    # Si el cliente cierra la conexión, chunk estará vacío
                    if not chunk:
                        break
                    full_data_bytes += chunk
                    # La trama termina con '>' y un salto de línea
                    if b'>' in full_data_bytes and b'\n' in full_data_bytes:
                        break
                except ConnectionResetError:
                    chunk = b'' # Forzar salida si la conexión se resetea
                    break
            
            # Si no se recibieron datos, el cliente se desconectó.
            # Salimos del bucle principal para cerrar el manejador.
            if not full_data_bytes:
                print(f"❌ Cliente {self.client_address[0]} se ha desconectado.")
                break

            data = full_data_bytes.decode('utf-8').strip()
            # El servidor muestra en su consola lo que recibió.
            print(f"Datos recibidos de {self.client_address[0]}: {data}")

            response = None
            for command_key, handler_func in COMMAND_MAP.items():
                if command_key in data:
                    response = handler_func(data)
                    break
            
            if response:
                self.request.sendall((response + '\n\r').encode('utf-8'))
            else:
                error_msg = "<- Comando no reconocido o no simulado. No se envió respuesta.\n"
                print(error_msg.strip())
                self.request.sendall(error_msg.encode('utf-8'))


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

if __name__ == "__main__":
    print("--- Simulador de Atalla HSM (Conexión Persistente) ---")
    print(f"Iniciando servidor en {HOST}:{PORT}")
    print("Esperando conexiones... (Los mensajes deben terminar con '>' y luego Enter)")
    print("Comandos simulados: 93, 30, 37, 32")
    print("Presiona Ctrl+C para detener el servidor.")

    # Permite reutilizar la dirección para evitar errores de "Address already in use"
    socketserver.TCPServer.allow_reuse_address = True
    server = ThreadedTCPServer((HOST, PORT), AtallaTCPHandler)
    server.serve_forever()