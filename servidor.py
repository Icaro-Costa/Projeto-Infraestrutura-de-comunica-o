# Importa bibliotecas de conexao e threads
import socket
import threading

HOST = '127.0.0.1' 
PORTA = 12345

# Lista para armazenar conexoes de clientes
clientes = []

# Funcao para lidar com cada cliente conectado
def handle_client(conn, ender):
    print(f"[NOVA CONEXAO] {ender} conectado.")
    clientes.append(conn)
    
    try:
        while True:
            # Recebe mensagem do cliente
            mensagem = conn.recv(1024)
            if not mensagem:
                break
            
            # Reenvia a mensagem para todos os outros clientes
            broadcast(mensagem, conn)
    
    except ConnectionResetError:
        print(f"[DESCONECTADO] {ender} desconectou abruptamente.")
    
    finally:
        # Limpa a conexao
        if conn in clientes:
            clientes.remove(conn)
        conn.close()
        print(f"[CONEXAO FECHADA] {ender}.")

# Funcao para enviar mensagem a todos
def broadcast(mensagem, conexao_origem):
    for cliente_conn in clientes:
        # Nao envia a mensagem de volta para quem enviou
        if cliente_conn != conexao_origem:
            try:
                cliente_conn.send(mensagem)
            except socket.error:
                # Remove o cliente se houver erro ao enviar
                if cliente_conn in clientes:
                    clientes.remove(cliente_conn)
                cliente_conn.close()

# Funcao principal do servidor
def iniciar_servidor():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind((HOST, PORTA))
    servidor.listen()
    print(f"[ESCUTANDO] Servidor escutando em {HOST}:{PORTA}...")

    while True:
        # Aceita novas conexoes
        conn, ender = servidor.accept()
        
        # Cria uma nova thread para cada cliente
        thread_cliente = threading.Thread(target=handle_client, args=(conn, ender))
        thread_cliente.start()

if __name__ == "__main__":
    iniciar_servidor()
