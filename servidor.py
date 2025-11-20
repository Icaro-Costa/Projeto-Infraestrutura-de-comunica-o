import asyncio
import websockets
import json

# Dicionario para armazenar {websocket: username}
clientes = {}


# Funcao para enviar mensagem a todos os clientes
# O parametro websocket_origem e opcional
async def broadcast(mensagem, websocket_origem=None):
    # Converte a mensagem em string JSON para envio
    msg_json = json.dumps(mensagem)

    conexoes = list(clientes.keys())
    tarefas_envio = []

    for websocket in conexoes:
        if websocket != websocket_origem:
            try:
                tarefas_envio.append(websocket.send(msg_json))
            except Exception as e:
                print(f"[ERRO DE ENVIO] Falha ao enviar para cliente: {e}")

    if tarefas_envio:
        await asyncio.gather(*tarefas_envio, return_exceptions=True)


# Funcao principal para lidar com cada conexao de cliente
async def handler(websocket):
    username = "Desconhecido"

    try:
        # 1. Espera a primeira mensagem (Handshake) com o nome de usuario
        primeira_msg_raw = await websocket.recv()
        data = json.loads(primeira_msg_raw)

        # Verifica se e a mensagem de handshake esperada
        if data.get("type") == "handshake":
            username = data.get("username", "Desconhecido").strip()

            if not username or username == "Desconhecido":
                print("[ERRO DE CONEXAO] Nome de usuario invalido. Fechando.")
                return

            # Adiciona o cliente ao dicionario
            clientes[websocket] = username
            print(f"[NOVA CONEXAO] {username} conectado ({len(clientes)} total).")

            # 2. Funcionalidade Secundaria: Envia notificacao de entrada
            msg_entrada = {"sender": "SISTEMA", "text": f"***{username} entrou no chat!***"}
            await broadcast(msg_entrada)
        else:
            print("[ERRO DE CONEXAO] Protocolo inicial invalido. Fechando.")
            return

        # Loop principal para receber mensagens de chat
        async for mensagem_raw in websocket:
            # Espera que a mensagem seja um JSON: {"type": "chat", "text": "Mensagem"}
            try:
                data = json.loads(mensagem_raw)
                text = data.get("text", "")

                if text:
                    # Broadcast da mensagem de chat
                    mensagem_broadcast = {"sender": username, "text": text}
                    await broadcast(mensagem_broadcast, websocket)
                    print(f"[{username}] {text}")

            except json.JSONDecodeError:
                print(f"[ERRO] Mensagem invalida recebida de {username}: {mensagem_raw}")

    except websockets.exceptions.ConnectionClosedOK:
        print(f"[DESCONECTADO] {username} desconectou normalmente.")
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"[ERRO DE CONEXAO] {username} desconectou abruptamente. Codigo: {e.code}")
    except Exception as e:
        print(f"[ERRO GERAL] Erro na conexao com {username}: {e}")
    finally:
        # 3. Limpa a conexao e notifica a saida
        if websocket in clientes:
            del clientes[websocket]
            print(f"[CONEXAO FECHADA] {username} saiu. ({len(clientes)} restantes).")

            # Funcionalidade Secundaria: Envia notificacao de saida
            msg_saida = {"sender": "SISTEMA", "text": f"***{username} saiu do chat.***"}
            await broadcast(msg_saida)


# Funcao principal do servidor
async def iniciar_servidor():
    HOST = '127.0.0.1'
    PORTA = 9000

    try:
        # Use o 'handler' que tem dois argumentos (websocket, path)
        # origins=None permite conexoes de qualquer origem (necessario para rodar html localmente)
        async with websockets.serve(handler, HOST, PORTA, origins=None):
            print(f"[ESCUTANDO] Servidor WebSocket escutando em ws://{HOST}:{PORTA}...")
            await asyncio.Future()
    except OSError as e:
        print(f"[ERRO FATAL] Nao foi possivel iniciar o servidor na porta {PORTA}: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(iniciar_servidor())
    except KeyboardInterrupt:
        print("\nServidor encerrado manualmente.")
    except Exception as e:
        print(f"Erro ao rodar o servidor: {e}")
