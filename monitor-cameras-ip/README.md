# Monitor de Câmeras IP

Sistema em Python para monitorar câmeras de segurança por endereço IP e identificar quando ficam ONLINE ou OFFLINE.

## Recursos da Versão 1.0

- Cadastro de câmera por NVR
- Canal
- Nome da câmera
- Endereço IP
- Local de instalação
- Monitoramento automático por ping
- Status ONLINE / OFFLINE
- Registro da data e hora da mudança de status
- Histórico de quedas e retornos
- Filtro por NVR
- Banco de dados SQLite automático
- Interface gráfica para Windows

## Estrutura

- NVR 1
- NVR 2
- NVR 3
- NVR 4

Cada NVR pode ser usado para organizar até 32 canais ou mais.

## Como executar

1. Instale Python 3.
2. Extraia a pasta do projeto.
3. Abra o terminal dentro da pasta.
4. Execute:

```bash
python app.py
```

No Windows também pode ser:

```bash
py app.py
```

## Observação sobre monitoramento

O sistema utiliza `ping` para verificar se o IP responde na rede.

Algumas câmeras ou redes podem bloquear ping mesmo quando a câmera está funcionando. Em versões futuras podemos adicionar verificação por porta TCP, RTSP ou HTTP.

## Autor

Projeto Monitor de Câmeras IP
