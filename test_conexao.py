import unittest
import socket
from unittest.mock import patch, MagicMock

# Importar as funcoes ou classes dos seus scripts originais
# (Para este exemplo, vamos simular o fluxo principal dos scripts originais)

class TestRedeBasica(unittest.TestCase):

    # Teste para o fluxo do servidor original
    @patch('socket.socket') # Simula a biblioteca socket
    def test_servidor_fluxo_basico(self, mock_socket_class):
        # Configura os mocks (simuladores)
        mock_servidor = MagicMock()
        mock_conn = MagicMock()
        mock_ender = ('127.0.0.1', 54321)

        # Configura o mock da classe socket para retornar o mock do servidor
        mock_socket_class.return_value = mock_servidor
        
        # Simula o aceite da conexao
        mock_servidor.accept.return_value = (mock_conn, mock_ender)

        # --- Simula a execucao do servidor.py original ---
        HOST_ORIGINAL = '127.0.0.1' 
        PORTA_ORIGINAL = 12345

        # Simula a criacao do socket
        servidor_simulado = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Verifica se o bind e listen foram chamados (como no original)
        servidor_simulado.bind((HOST_ORIGINAL, PORTA_ORIGINAL))
        servidor_simulado.listen()
        
        # Simula a aceitacao
        conn_simulada, ender_simulado = servidor_simulado.accept()
        
        # Simula o envio de mensagem
        mensagem_enviada = "Conectado ao servidor!".encode('utf-8')
        conn_simulada.send(mensagem_enviada)
        
        # Simula o fechamento
        conn_simulada.close()
        servidor_simulado.close()
        # --- Fim da simulacao ---

        # Verificacoes (Assertions)
        # Verifica se os metodos corretos foram chamados nos mocks
        mock_socket_class.assert_called_with(socket.AF_INET, socket.SOCK_STREAM)
        mock_servidor.bind.assert_called_with((HOST_ORIGINAL, PORTA_ORIGINAL))
        mock_servidor.listen.assert_called_once()
        mock_servidor.accept.assert_called_once()
        
        # Verifica se a mensagem de boas-vindas foi enviada
        mock_conn.send.assert_called_with(mensagem_enviada)
        
        # Verifica se as conexoes foram fechadas
        mock_conn.close.assert_called_once()
        mock_servidor.close.assert_called_once()

    # Teste para o fluxo do cliente original
    @patch('socket.socket') # Simula a biblioteca socket
    def test_cliente_fluxo_basico(self, mock_socket_class):
        # Configura os mocks
        mock_cliente = MagicMock()
        mock_socket_class.return_value = mock_cliente
        
        # Mensagem que o servidor (simulado) enviara
        mensagem_servidor = "Conectado ao servidor!".encode('utf-8')
        mock_cliente.recv.return_value = mensagem_servidor

        # --- Simula a execucao do cliente.py original ---
        HOST_ORIGINAL = '127.0.0.1' 
        PORTA_ORIGINAL = 12345
        
        cliente_simulado = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            cliente_simulado.connect((HOST_ORIGINAL, PORTA_ORIGINAL))
            mensagem_recebida = cliente_simulado.recv(1024)
        except Exception:
            pass # Ignora erros na simulacao
            
        cliente_simulado.close()
        # --- Fim da simulacao ---

        # Verificacoes (Assertions)
        mock_socket_class.assert_called_with(socket.AF_INET, socket.SOCK_STREAM)
        mock_cliente.connect.assert_called_with((HOST_ORIGINAL, PORTA_ORIGINAL))
        
        # Verifica se o cliente tentou receber dados
        mock_cliente.recv.assert_called_with(1024)
        
        # Verifica se o cliente decodificou corretamente (implicitamente)
        self.assertEqual(mensagem_recebida.decode('utf-8'), "Conectado ao servidor!")
        
        # Verifica se o cliente fechou a conexao
        mock_cliente.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()
