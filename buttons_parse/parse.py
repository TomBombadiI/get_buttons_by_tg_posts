import configparser
import json

from telethon.sync import TelegramClient
from telethon import connection

# для корректного переноса времени сообщений в json
from datetime import date, datetime

# классы для работы с каналами
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch

# класс для работы с сообщениями
from telethon.tl.functions.messages import GetHistoryRequest

# Считываем учетные данные
config = configparser.ConfigParser()
config.read("config.ini")

# Присваиваем значения внутренним переменным
api_id   = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']
username = config['Telegram']['username']

client = TelegramClient(username, api_id, api_hash, system_version="4.16.30-vxCUSTOM", device_model="vxCUSTOM", lang_code="ru", app_version="4.16.30")

client.start()

async def dump_all_messages(channel):
	"""Записывает json-файл с информацией о всех сообщениях канала/чата"""
	offset_msg = 0    # номер записи, с которой начинается считывание
	limit_msg = 100   # максимальное число записей, передаваемых за один раз

	all_messages = []   # список всех сообщений
	total_messages = 0
	total_count_limit = 0  # поменяйте это значение, если вам нужны не все сообщения

	class DateTimeEncoder(json.JSONEncoder):
		'''Класс для сериализации записи дат в JSON'''
		def default(self, o):
			if isinstance(o, datetime):
				return o.isoformat()
			if isinstance(o, bytes):
				return list(o)
			return json.JSONEncoder.default(self, o)

	while True:
		history = await client(GetHistoryRequest(
			peer=channel,
			offset_id=offset_msg,
			offset_date=None, add_offset=0,
			limit=limit_msg, max_id=0, min_id=0,
			hash=0))
		if not history.messages:
			break
		messages = history.messages
		for message in messages:
			all_messages.append(message.to_dict())
		offset_msg = messages[len(messages) - 1].id
		total_messages = len(all_messages)
		if total_count_limit != 0 and total_messages >= total_count_limit:
			break

	return all_messages

def get_url_buttons(data):

    models = []

    for message in data:
        if 'message' in message.keys():
            id = message['id']
            text = message['message']

            model_name = text.split('\n')[0]

            if model_name not in models and len(model_name)>0 and id!=3 and "прайс" not in model_name.lower():
                models.append((model_name, f'https://t.me/Apple_Prices/{id}'))

    models.reverse()
    s = ''
    s += f"{models[0][0]} - {models[0][1]}\n"
    for i in range(1, len(models), 2):
        s += f"{models[i][0]} - {models[i][1]}"
        if i+1 < len(models):
            s += f" | {models[i+1][0]} - {models[i+1][1]}\n" 

    return s

async def main():
	url = '@Apple_Prices'
	channel = await client.get_entity(url)
	messages = await dump_all_messages(channel)
	print(get_url_buttons(messages))
	input("Нажмите любую кнопку для выхода...")

with client:
	client.loop.run_until_complete(main())