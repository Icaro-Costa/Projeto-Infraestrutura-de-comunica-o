import asyncio
import websockets
import json
import sys
import threading

# Configurações do Servidor
HOST = '127.0.0.1'
PORTA = 9000 # Porta do servidor WebSocket (verifique servidor.py)
URI = f"ws://{HOST}:{PORTA}"

async def receber_mensagens(websocket):
    """
    Corrotina para receber mensagens do servidor.
    """
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                sender = data.get("sender", "Desconhecido")
                text = data.get("text", "")
                
                # Formata a mensagem para exibição
                if sender == "SISTEMA":
                    print(f"\n[SISTEMA] {text}")
                else:
                    print(f"\n[{sender}] {text}")
                    
                # Re-imprime o prompt para o usuário não se perder
                print("> ", end="", flush=True)
                
            except json.JSONDecodeError:
                print(f"\n[ERRO] Mensagem inválida recebida: {message}")
    except websockets.exceptions.ConnectionClosed:
        print("\n[DESCONECTADO] Conexão fechada pelo servidor.")
        return # Retorna para encerrar a task graciosamente
    except Exception as e:
        print(f"\n[ERRO] Erro na recepção: {e}")
        return

async def enviar_mensagens(websocket, username):
    """
    Corrotina para ler input do usuário e enviar para o servidor.
    Usa run_in_executor para não bloquear o loop de eventos com input().
    """
    loop = asyncio.get_running_loop()
    
    print(f"Conectado como {username}. Digite suas mensagens (ou 'sair' para fechar).")
    print("> ", end="", flush=True)

    while True:
        # Executa input() em uma thread separada para não bloquear o asyncio
        mensagem = await loop.run_in_executor(None, input)
        
        if mensagem.strip().lower() == 'sair':
            print("Saindo...")
            await websocket.close()
            break
            
        if mensagem.strip():
            payload = {
                "type": "chat",
                "text": mensagem
            }
            await websocket.send(json.dumps(payload))
            print("> ", end="", flush=True)

async def main():
    print(f"Tentando conectar a {URI}...")
    try:
        async with websockets.connect(URI) as websocket:
            print("Conexão estabelecida!")
            
            # 1. Handshake
            username = input("Digite seu nome de usuário: ").strip()
            while not username:
                 username = input("Nome inválido. Digite seu nome de usuário: ").strip()

            handshake = {
                "type": "handshake",
                "username": username
            }
            await websocket.send(json.dumps(handshake))
            
            # Cria as tarefas de enviar e receber
            task_receber = asyncio.create_task(receber_mensagens(websocket))
            task_enviar = asyncio.create_task(enviar_mensagens(websocket, username))
            
            # Aguarda que uma das tarefas termine (geralmente enviar termina com 'sair')
            done, pending = await asyncio.wait(
                [task_receber, task_enviar],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # Cancela a tarefa pendente (se enviar terminou, cancela receber)
            for task in pending:
                task.cancel()
                
    except ConnectionRefusedError:
        print(f"Não foi possível conectar a {URI}. O servidor está rodando?")
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nPrograma encerrado.")
