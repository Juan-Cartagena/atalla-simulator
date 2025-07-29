import socketserver
import threading
import random
import string

# --- Configuración del Servidor ---
HOST, PORT = "localhost", 9999

# --- Lógica de Simulación de Comandos Atalla ---

def generate_hex(length):
    """Genera una cadena hexadecimal aleatoria de la longitud especificada."""
    return ''.join(random.choice('0123456789ABCDEF') for _ in range(length))

def handle_command_93(data):
    """
    Simula GenerateRandomNumberWS (Comando 93).
    Respuesta esperada: Un header, código de error '00' (éxito) y un número aleatorio.
    El formato de respuesta real puede variar, esto es una simulación plausible.
    """
    print("-> Recibido Comando 93: Generar Número Aleatorio")
    error_code = "00"
    random_number = generate_hex(16) # Simulamos un número aleatorio de 16 caracteres hexadecimales
    response = f"<A3#{error_code}{random_number}"
    print(f"<- Enviando Respuesta: {response}")
    return response

def handle_command_30(data):
    """
    Simula EncryptPinANSIFormat0WS (Comando 30).
    Respuesta esperada: Un header, código de error '00' (éxito) y un PIN block encriptado.
    """
    print("-> Recibido Comando 30: Encriptar PIN Formato ANSI 0")
    error_code = "00"
    encrypted_pin_block = generate_hex(16) # Un PIN block simulado
    response = f"<40#{error_code}{encrypted_pin_block}"
    print(f"<- Enviando Respuesta: {response}")
    return response

def handle_command_37(data):
    """
    Simula PinChangeIBM3624WS (Comando 37).
    Respuesta esperada: Un header y un código de error '00' (éxito).
    """
    print("-> Recibido Comando 37: Cambio de PIN IBM3624")
    error_code = "00"
    response = f"<47#{error_code}"
    print(f"<- Enviando Respuesta: {response}")
    return response

def handle_command_32(data):
    """
    Simula VerifyPinIBM3624WS (Comando 32).
    Respuesta esperada: Un header y un código de error '00' (PIN válido).
    """
    print("-> Recibido Comando 32: Verificar PIN IBM3624")
    # Para pruebas, se puede simular un PIN inválido cambiando el código de error.
    # '01' podría ser PIN inválido, por ejemplo.
    error_code = "00" # '00' significa PIN Válido
    response = f"<42#{error_code}"
    print(f"<- Enviando Respuesta: {response}")
    return response

# Mapeo de comandos a funciones. Usamos 'in' para buscar el comando en el request.
# Esto es más flexible que una coincidencia exacta.
COMMAND_MAP = {
    "<93#": handle_command_93,
    "<30#": handle_command_30,
    "<37#": handle_command_37,
    "<32#": handle_command_32,
}

class AtallaTCPHandler(socketserver.BaseRequestHandler):
    """
    El manejador de peticiones para el servidor.
    Se instancia una vez por cada conexión al servidor.
    """

    def handle(self):
        # self.request es el socket TCP conectado al cliente
        data = self.request.recv(1024).strip().decode('utf-8')
        print(f"\nConexión recibida de {self.client_address[0]}")
        print(f"Datos recibidos: {data}")

        response = None
        # Busca qué función de manejo de comandos usar
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
    print("--- Simulador de Atalla HSM ---")
    print(f"Iniciando servidor en {HOST}:{PORT}")
    print("Esperando conexiones...")
    print("Comandos simulados: 93, 30, 37, 32")
    print("Presiona Ctrl+C para detener el servidor.")

    # Usamos un servidor con hilos para manejar múltiples conexiones si es necesario
    server = ThreadedTCPServer((HOST, PORT), AtallaTCPHandler)
    
    # Activar el servidor; continuará ejecutándose hasta que lo interrumpas con Ctrl+C
    server.serve_forever()
