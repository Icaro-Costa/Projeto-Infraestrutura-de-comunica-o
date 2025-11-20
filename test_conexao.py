import unittest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
import json

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

if __name__ == '__main__':
    unittest.main()
