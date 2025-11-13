# Importa bibliotecas assincronas e de websocket
import asyncio
import websockets
import json

# Set para armazenar conexoes de clientes (WebSockets)
clientes = set()

# Funcao para enviar mensagem a todos os clientes
async def broadcast(mensagem, websocket_origem):
    # Converte a mensagem em string JSON para envio
    msg_json = json.dumps(mensagem)
    # Cria lista de tarefas de envio assincrono
    tarefas_envio = []
    
    for websocket in clientes:
        # Nao envia de volta para quem enviou
        if websocket != websocket_origem:
            tarefas_envio.append(websocket.send(msg_json))
    
    # Executa os envios em paralelo
    if tarefas_envio:
        await asyncio.gather(*tarefas_envio)

# Funcao principal para lidar com cada conexao de cliente
async def handler(websocket, path):
    clientes.add(websocket) # Adiciona novo cliente
    print(f"[NOVA CONEXAO] Cliente conectado ({len(clientes)} total).")
    
    try:
        # Loop para receber mensagens do cliente
        async for mensagem_raw in websocket:
            # Espera que a mensagem seja um JSON: {"sender": "Nome", "text": "Mensagem"}
            try:
                data = json.loads(mensagem_raw)
                sender = data.get("sender", "Desconhecido")
                text = data.get("text", "")
                
                if text:
                    mensagem_broadcast = {"sender": sender, "text": text}
                    await broadcast(mensagem_broadcast, websocket)
                    print(f"[{sender}] {text}")
                    
            except json.JSONDecodeError:
                print(f"[ERRO] Mensagem invalida recebida: {mensagem_raw}")

    except websockets.exceptions.ConnectionClosedOK:
        print(f"[DESCONECTADO] Cliente desconectou normalmente.")
    except Exception as e:
        print(f"[ERRO] Erro na conexao: {e}")
    finally:
        # Remove a conexao ao desconectar
        if websocket in clientes:
            clientes.remove(websocket)
        print(f"[CONEXAO FECHADA] Cliente desconectou ({len(clientes)} restantes).")

# Funcao principal do servidor
async def iniciar_servidor():
    HOST = '127.0.0.1' 
    PORTA = 8765 # Porta padrao para websockets
    
    # Inicia o servidor websocket
    async with websockets.serve(handler, HOST, PORTA):
        print(f"[ESCUTANDO] Servidor WebSocket escutando em ws://{HOST}:{PORTA}...")
        # Mantem o servidor rodando para sempre
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(iniciar_servidor())
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
