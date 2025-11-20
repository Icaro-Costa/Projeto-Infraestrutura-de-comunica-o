import unittest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
import json
import websockets

class TestRedeWebSocket(unittest.IsolatedAsyncioTestCase):

    # Teste para o fluxo do servidor (mantido similar, mas adaptado se necessario)
    # Como o servidor usa websockets, o teste idealmente usaria AsyncMock
    @patch('websockets.serve')
    async def test_servidor_inicio(self, mock_serve):
        # Importa aqui para evitar erro se nao tiver as libs
        try:
            from servidor import iniciar_servidor
        except ImportError:
            self.skipTest("servidor.py nao encontrado ou com erro de importacao")

        # Mock do serve para nao travar
        mock_serve.return_value.__aenter__.return_value = MagicMock()
        
        # Executa a funcao (vai rodar e parar no await Future se nao mockarmos o Future)
        # Para teste simples, apenas verificamos se chamou o serve
        with patch('asyncio.Future', new_callable=AsyncMock) as mock_future:
            # Faz o future retornar imediatamente para nao travar o teste
            mock_future.return_value = None 
            
            try:
                await iniciar_servidor()
            except Exception:
                pass # Ignora erros de cancelamento ou parada forçada

            # Verifica se tentou iniciar o servidor na porta 9000
            args, _ = mock_serve.call_args
            self.assertEqual(args[1], '127.0.0.1')
            self.assertEqual(args[2], 9000)

    # Teste para o fluxo do cliente (NOVO)
    @patch('websockets.connect')
    @patch('builtins.input')
    async def test_cliente_fluxo_basico(self, mock_input, mock_connect):
        # Importa o main do cliente
        try:
            from cliente import main
        except ImportError:
            self.skipTest("cliente.py nao encontrado ou com erro de importacao")

        # Configura inputs do usuario: Username -> Mensagem -> Sair
        mock_input.side_effect = ["Tester", "Ola Mundo", "sair"]

        # Configura o Mock do WebSocket
        mock_ws = AsyncMock()
        mock_connect.return_value.__aenter__.return_value = mock_ws
        
        # Simula recebimento de mensagens (async generator)
        # O cliente espera mensagens. Vamos simular uma mensagem de boas vindas e depois nada
        async def message_generator():
            yield json.dumps({"sender": "SISTEMA", "text": "Bem vindo"})
            # Fica "esperando" (na pratica o teste vai acabar quando o input mandar sair)
            while True:
                await asyncio.sleep(0.1)

        mock_ws.__aiter__.side_effect = message_generator

        # Executa o cliente
        await main()

        # Verificacoes
        # 1. Verifica se conectou na URI correta
        mock_connect.assert_called_with("ws://127.0.0.1:9000")

        # 2. Verifica se enviou o handshake
        expected_handshake = json.dumps({"type": "handshake", "username": "Tester"})
        mock_ws.send.assert_any_call(expected_handshake)

        # 3. Verifica se enviou a mensagem de chat
        expected_chat = json.dumps({"type": "chat", "text": "Ola Mundo"})
        mock_ws.send.assert_any_call(expected_chat)

    # Teste: Cliente lidando com desconexao do servidor
    @patch('websockets.connect')
    @patch('builtins.input')
    async def test_cliente_desconexao_servidor(self, mock_input, mock_connect):
        try:
            from cliente import main
        except ImportError:
            self.skipTest("cliente.py nao encontrado")

        # Usuario entra, tenta mandar msg, mas servidor cai
        mock_input.side_effect = ["Tester", "Msg 1", "sair"]

        mock_ws = AsyncMock()
        mock_connect.return_value.__aenter__.return_value = mock_ws

        # Simula servidor fechando conexao abruptamente
        async def message_generator_error():
            yield json.dumps({"sender": "SISTEMA", "text": "Bem vindo"})
            raise websockets.exceptions.ConnectionClosed(1000, "Normal Closure")

        mock_ws.__aiter__.side_effect = message_generator_error

        # Executa cliente (nao deve dar crash/sys.exit)
        await main()
        
        # Se chegou aqui sem erro, o teste passou (pois removemos sys.exit)
        mock_connect.assert_called()

    # Teste: Servidor Broadcast
    async def test_servidor_broadcast(self):
        try:
            from servidor import broadcast, clientes
        except ImportError:
            self.skipTest("servidor.py nao encontrado")

        # Limpa clientes anteriores
        clientes.clear()

        # Cria mocks de websockets
        ws1 = AsyncMock()
        ws2 = AsyncMock()
        ws3 = AsyncMock()

        # Adiciona ao dicionario de clientes
        clientes[ws1] = "User1"
        clientes[ws2] = "User2"
        clientes[ws3] = "User3"

        msg = {"sender": "User1", "text": "Ola"}
        
        # Broadcast vindo de ws1 (nao deve enviar para ws1)
        await broadcast(msg, websocket_origem=ws1)

        # Verifica envios
        ws1.send.assert_not_called()
        ws2.send.assert_called_once()
        ws3.send.assert_called_once()
        
        # Verifica conteudo enviado (json string)
        expected_json = json.dumps(msg)
        ws2.send.assert_called_with(expected_json)
        ws3.send.assert_called_with(expected_json)

    # Teste: Servidor Handshake (Logica do Handler)
    @patch('servidor.broadcast')
    async def test_servidor_handshake(self, mock_broadcast):
        try:
            from servidor import handler, clientes
        except ImportError:
            self.skipTest("servidor.py nao encontrado")
            
        clientes.clear()
        
        mock_ws = AsyncMock()
        
        # Simula fluxo: Handshake -> Chat -> Fechar
        
        # Configura o recv para o handshake inicial
        mock_ws.recv.return_value = json.dumps({"type": "handshake", "username": "NovoUser"})
        
        # Configura o iterador para mensagens de chat subsequentes
        async def ws_iter():
            yield json.dumps({"type": "chat", "text": "Ola Servidor"})
            # Para o loop
        
        mock_ws.__aiter__.side_effect = ws_iter
        
        # Executa handler
        await handler(mock_ws)
        
        # Verifica se chamou broadcast de entrada
        # O handler chama broadcast com msg_entrada
        args, _ = mock_broadcast.call_args_list[0] # Primeira chamada
        msg_enviada = args[0]
        self.assertEqual(msg_enviada['sender'], 'SISTEMA')
        self.assertIn('NovoUser entrou', msg_enviada['text'])
        
        # Verifica se removeu ao final (pois o iterador acabou, saindo do loop)
        self.assertNotIn(mock_ws, clientes)

if __name__ == '__main__':
    unittest.main()
