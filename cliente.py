# Importa bibliotecas de conexao e threads
import socket
import threading
import sys

HOST = '127.0.0.1' 
PORTA = 12345

# Funcao para receber mensagens do servidor
def receber_mensagens(cliente_socket):
    while True:
        try:
            mensagem = cliente_socket.recv(1024).decode('utf-8')
            if not mensagem:
                print("\n[SERVIDOR] Servidor fechou a conexao.")
                break
            print(f"\nMensagem recebida: {mensagem}")
        
        except ConnectionResetError:
            print("\n[ERRO] Conexao perdida com o servidor.")
            break
        except Exception as e:
            print(f"Erro ao receber: {e}")
            break
    
    cliente_socket.close()

# Funcao para enviar mensagens ao servidor
def enviar_mensagens(cliente_socket):
    while True:
        try:
            # Le input do usuario
            mensagem = input()
            if mensagem.lower() == 'sair':
                break
                
            cliente_socket.send(mensagem.encode('utf-8'))
        
        except (EOFError, KeyboardInterrupt):
            print("\nSaindo...")
            break
        except Exception as e:
            print(f"Erro ao enviar: {e}")
            break
            
    cliente_socket.close()
    sys.exit() # Forca o encerramento do programa

# --- Main ---
cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    cliente.connect((HOST, PORTA))
    print(f"Conectado ao servidor em {HOST}:{PORTA}. Digite 'sair' para fechar.")
    
    # Inicia thread para receber mensagens
    thread_receber = threading.Thread(target=receber_mensagens, args=(cliente,))
    thread_receber.daemon = True # Permite fechar o programa
    thread_receber.start()

    # Inicia loop principal para enviar mensagens
    enviar_mensagens(cliente)

except ConnectionRefusedError:
    print("O servidor nao esta online ou recusou a conexao.")
except Exception as e:
    print(f"Erro ao conectar: {e}")
finally:
    if cliente.fileno() != -1: # Verifica se o socket ainda esta aberto
        cliente.close()
    print("Conexao fechada.")
