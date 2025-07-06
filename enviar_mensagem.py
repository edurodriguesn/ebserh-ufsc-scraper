import os
from dotenv import load_dotenv
import requests

load_dotenv()

# Configurações
TOKEN_BOT = os.getenv('TOKEN_BOT')
CHAT_ID = os.getenv('CHAT_ID')

def enviar_telegram(conteudo):
    mensagem_telegram = formatar_mensagem(conteudo)
    return dispatch(mensagem_telegram)

def formatar_mensagem(link):
    # Formata a mensagem para o Telegram
    mensagem_telegram = "NOVAS CONVOCAÇÕES ENCONTRADAS:\n"
    for link in link:
        mensagem_telegram += f"<a href='{link}'>{link}</a>\n"
    return mensagem_telegram

def dispatch(mensagem):
    # Envia a mensagem para o Telegram
    url = f"https://api.telegram.org/bot{TOKEN_BOT}/sendMessage"
    params = {"chat_id": CHAT_ID, "text": mensagem, "parse_mode": "HTML"}
    requests.get(url, params=params)