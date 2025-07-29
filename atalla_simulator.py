import socketserver
import threading
import random
import string
import time

# --- Configuración del Servidor ---
HOST, PORT = "localhost", 9999

# --- Lógica de Simulación de Comandos Atalla ---
# (Las funciones handle_command_* y generate_hex no cambian y se mantienen igual)
def generate_hex(length):
    """Genera una cadena hexadecimal aleatoria de la longitud especificada."""
    return ''.join(random.choice('0123456789ABCDEF') for _ in range(length))

def handle_command_93(data):
    """Simula el Comando 93."""
    print("-> Recibido Comando 93: Generar Número Aleatorio")
    error_code = "00"
    random_number = generate_hex(16)
    response = f"<A3#{error_code}{random_number}>"
    print(f"<- Enviando Respuesta: {response}")
    return response

def handle_command_30(data):
    """Simula el Comando 30."""
    print("-> Recibido Comando 30: Encriptar PIN Formato ANSI 0")
    error_code = "00"
    encrypted_pin_block = generate_hex(16)
    response = f"<40#{error_code}{encrypted_pin_block}>"
    print(f"<- Enviando Respuesta: {response}")
    return response

def handle_command_37(data):
    """Simula el Comando 37."""
    print("-> Recibido Comando 37: Cambio de PIN IBM3624")
    error_code = "00"
    response = f"<47#{error_code}>"
    print(f"<- Enviando Respuesta: {response}")
    return response

def handle_command_32(data):
    """Simula el Comando 32."""
    print("-> Recibido Comando 32: Verificar PIN IBM3624")
    error_code = "00" # '00' significa PIN Válido
    response = f"<42#{error_code}>"
    print(f"<- Enviando Respuesta: {response}")
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
    Ahora lee en un bucle hasta encontrar '>' seguido de un Enter ('\n').
    """
    def handle(self):
        print(f"\nConexión recibida de {self.client_address[0]}")
        
        full_data_bytes = b''
        while True:
            chunk = self.request.recv(1024)
            if not chunk:
                break
            full_data_bytes += chunk
            # --- LÍNEA MODIFICADA ---
            # Ahora el bucle se rompe solo si encuentra '>' Y un carácter de nueva línea '\n'.
            if b'>' in full_data_bytes and b'\n' in full_data_bytes:
                break
        
        if not full_data_bytes:
            print("<- Conexión cerrada por el cliente sin enviar datos.")
            return

        data = full_data_bytes.decode('utf-8').strip()
        print(f"Datos recibidos: {data}")

        response = None
        for command_key, handler_func in COMMAND_MAP.items():
            if command_key in data:
                response = handler_func(data)
                break
        
        if response:
            self.request.sendall(response.encode('utf-8'))
        else:
            print("<- Comando no reconocido o no simulado. No se envió respuesta.")


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

if __name__ == "__main__":
    print("--- Simulador de Atalla HSM (Versión Final) ---")
    print(f"Iniciando servidor en {HOST}:{PORT}")
    print("Esperando conexiones... (Los mensajes deben terminar con '>' y luego Enter)")
    print("Comandos simulados: 93, 30, 37, 32")
    print("Presiona Ctrl+C para detener el servidor.")

    server = ThreadedTCPServer((HOST, PORT), AtallaTCPHandler)
    server.serve_forever()