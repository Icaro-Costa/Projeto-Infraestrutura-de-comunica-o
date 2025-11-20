# Chat Simples com WebSockets

Este projeto implementa um sistema de chat em tempo real utilizando a arquitetura cliente-servidor com WebSockets. Ele permite que múltiplos usuários se conectem e troquem mensagens instantaneamente, seja através de um terminal Python ou de uma interface Web.

## 🚀 Funcionalidades

- **Comunicação em Tempo Real**: Mensagens são entregues instantaneamente para todos os usuários conectados.
- **Múltiplos Clientes**: Suporte para clientes Python (terminal) e Web (navegador) simultaneamente.
- **Broadcast**: Mensagens enviadas por um usuário são retransmitidas para todos os outros.
- **Notificações do Sistema**: Avisos automáticos quando usuários entram ou saem do chat.
- **Identificação**: Usuários escolhem um nome (username) ao entrar.

## 🛠️ Tecnologias Utilizadas

- **Linguagem**: Python 3.x
- **Bibliotecas Python**:
    - `asyncio`: Para gerenciamento de I/O assíncrono.
    - `websockets`: Para implementação do protocolo WebSocket.
- **Frontend**:
    - HTML5, CSS3 (Design Moderno).
    - JavaScript (WebSocket API nativa).

## 📋 Pré-requisitos

Para rodar o servidor e o cliente Python, você precisa ter o Python 3 instalado e a biblioteca `websockets`.

```bash
pip install websockets
```

## 🏃‍♂️ Como Rodar

### 1. Iniciar o Servidor

O servidor é o coração do chat. Ele deve estar rodando para que os clientes possam se conectar.

```bash
python3 servidor.py
```
*O servidor iniciará na porta 9000 (ws://127.0.0.1:9000).*

### 2. Conectar com Cliente Python

Abra um novo terminal e execute:

```bash
python3 cliente.py
```
*Siga as instruções para digitar seu nome de usuário e começar a conversar.*

### 3. Conectar com Cliente Web

Basta abrir o arquivo `main.html` no seu navegador preferido (Chrome, Firefox, Safari, etc.).

*Digite seu nome, verifique se o host/porta estão corretos (padrão: 127.0.0.1:9000) e clique em "Conectar".*

## 📂 Estrutura do Projeto

- **`servidor.py`**: Código do servidor WebSocket. Gerencia conexões, recebe mensagens e faz o broadcast para todos os clientes.
- **`cliente.py`**: Cliente de terminal em Python. Usa `asyncio` para enviar e receber mensagens simultaneamente.
- **`main.html`**: Interface gráfica Web para o chat.
- **`test_conexao.py`**: Testes automatizados para verificar a conectividade e o fluxo de mensagens.

## 🧪 Testes

Para verificar se tudo está funcionando corretamente, você pode rodar os testes automatizados:

```bash
python3 test_conexao.py
```
