# Importa a biblioteca de conexao
import socket

# Define o IP (localhost) e a Porta
HOST = '127.0.0.1' 
PORTA = 12345

# Cria o objeto socket
servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.bind((HOST, PORTA))
servidor.listen()

print(f"Servidor escutando em {HOST}:{PORTA}...")

# Aceita a conexao do cliente
conn, ender = servidor.accept()
print(f"Conectado por {ender}")

# Apenas envia uma mensagem de boas-vindas e fecha
conn.send("Conectado ao servidor!".encode('utf-8'))
conn.close()
servidor.close()
print("Conexao fechada.")
