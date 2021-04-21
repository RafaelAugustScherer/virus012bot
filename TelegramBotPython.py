import json
import requests
from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import time
import urllib
import re

TOKEN = "1596955182:AAFoljqh85kZCd7p7jlfGmDRVX3RxW3Zvc0"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)


#obtem a url, ou seja usa o bot que voces criaram, de acordo com o token
def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content

def get_price(coin, coin2):
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    parameters = {
        'symbol': coin,
        'convert': coin2
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': 'b8f0262e-c07f-40b2-abd7-0e3780d0522b',
    }
    session = Session()
    session.headers.update(headers)
    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)
        if (data['status']['error_code'] != 0):
            return "Ops, erro na conversão! Verifique se o formato está como CRYPTO/FIAT e não FIAT/CRYPTO"
        else:
            price = str(round(data['data'][coin]['quote'][coin2]['price'], 2))
            return "1 " + coin + " = " + price + " " + coin2
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)

#recebe o objeto json retornado da API
def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js

#tempo para buscar a url a partir do momento que o bot rodar, retorna objeto json
def get_updates(offset=None):
    url = URL + "getUpdates"
    if offset:
        url += "?offset={}".format(offset)
    js = get_json_from_url(url)
    return js

#cria uma lista com todo mundo a ser respondido
def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)

#prepara a construção da mensagem
def construct_message(updates):
    for update in updates["result"]:
        text = update["message"]["text"]
        chat = update["message"]["chat"]["id"]
        nome = update["message"]["chat"]["first_name"]
        if (text == "Olá!"):
            text = "Olá " + nome + "! Tudo bem?"
        elif (text == "help"):
            text = "Você quis dizer /help? Caso contrário isso deve ajudar : https://www.reddit.com/r/cute/"
        elif (text == "music"):
            text = "Ok, saca só essa playlist: https://music.youtube.com/playlist?list=PLG9hZs0y-_kNhYhDzn52pl6iR-eHaLen5"
        elif (text == "secret"):
            text = "Gosta de segredos?\n" \
                   "Me diga o nome de um projeto lendário cujas cores tema eram preto e branco e teve a duração de 1 ano completo. Caso acertar, lhe contarei uma curiosidade sobre mim (bot)."
        elif (re.match('market \w{3,4}/\w{3,4}', text)):
            coins = re.findall('\w{3,4}', text)
            coins = list(map(str.upper, coins))
            text = get_price(coins[1], coins[2])
        else:
            text = "Tente um desses comandos:\n" \
                   "- Olá!\n" \
                   "- help\n" \
                   "- music\n" \
                   "- market btc/brl\n" \
                   "- secret"
        send_message(text, chat)

#evita que o bot responda duas vezes a mesma mensagem
def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)

#envia a mensagem formada em echo_all
def send_message(text, chat_id):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    get_url(url)


def main():
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            construct_message(updates)
        time.sleep(0.5)


if __name__ == '__main__':
    main()