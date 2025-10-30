# Importa a biblioteca de conexao
import socket

# Define o IP (do servidor) e a Porta
HOST = '127.0.0.1' 
PORTA = 12345

# Cria o objeto socket do cliente
cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Tenta se conectar ao IP e Porta do servidor
    cliente.connect((HOST, PORTA))
    print(f"Conectado ao servidor em {HOST}:{PORTA}")

    # Apenas recebe a mensagem de boas-vindas
    mensagem = cliente.recv(1024).decode('utf-8')
    print(f"Mensagem do Servidor: {mensagem}")

except ConnectionRefusedError:
    print("O servidor nao esta online ou recusou a conexao.")

# Fecha a conexao
cliente.close()
print("Conexao fechada.")
