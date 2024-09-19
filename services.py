import requests
import sett
import json
import time

def datos_bus(text):
	url = f"https://api.montevideo.gub.uy/transporteRest/siguientesParada/{text}"

	try:
		headers = {'User-Agent': 'Mozilla/5.0'}
		response = requests.get(url, headers=headers)

		if response.status_code == 200:
			data = response.json()
			resultados = [] 
			for bus in data:
				hora = bus['minutos']
				destino = bus['destino']
				linea = bus['linea']
				p_actual = bus['parada_actual']
				d_bus = f"Línea: {linea}\nDestino: {destino}\nAhora mismo va por: {p_actual}\nTiempo estimado: {hora}"
				print(d_bus)
				resultados.append(d_bus)
			return resultados
		else:
			print("Error al hacer la solicitud. Código de estado:", response.status_code)

	except Exception as e:
		print("Error:", e)


def obtener_Mensaje_whatsapp(message):
	if 'type' not in message :
		text = 'mensaje no reconocido'
		return text

	typeMessage = message['type']
	if typeMessage == 'text':
		text = message['text']['body']
	elif typeMessage == 'button':
		text = message['button']['text']
	elif typeMessage == 'interactive' and message['interactive']['type'] == 'list_reply':
		text = message['interactive']['list_reply']['title']
	elif typeMessage == 'interactive' and message['interactive']['type'] == 'button_reply':
		text = message['interactive']['button_reply']['title']
	else:
		text = 'mensaje no procesado'
	
	
	return text

def enviar_Mensaje_whatsapp(data):
	try:
		whatsapp_token = sett.whatsapp_token
		whatsapp_url = sett.whatsapp_url
		headers = {'Content-Type': 'application/json',
				   'Authorization': 'Bearer ' + whatsapp_token}
		print("se envia ", data)
		response = requests.post(whatsapp_url, 
								 headers=headers, 
								 data=data)
		
		if response.status_code == 200:
			return 'mensaje enviado', 200
		else:
			return 'error al enviar mensaje', response.status_code
	except Exception as e:
		return e,403
	
def text_Message(number,text):
	data = json.dumps(
			{
				"messaging_product": "whatsapp",	
				"recipient_type": "individual",
				"to": number,
				"type": "text",
				"text": {
					"body": text
				}
			}
	)
	return data

def buttonReply_Message(number, options, body, footer, sedd,messageId):
	buttons = []
	for i, option in enumerate(options):
		buttons.append(
			{
				"type": "reply",
				"reply": {
					"id": sedd + "_btn_" + str(i+1),
					"title": option
				}
			}
		)

	data = json.dumps(
		{
			"messaging_product": "whatsapp",
			"recipient_type": "individual",
			"to": number,
			"type": "interactive",
			"interactive": {
				"type": "button",
				"body": {
					"text": body
				},
				"footer": {
					"text": footer
				},
				"action": {
					"buttons": buttons
				}
			}
		}
	)
	return data

def listReply_Message(number, options, body, footer, sedd,messageId):
	rows = []
	for i, option in enumerate(options):
		rows.append(
			{
				"id": sedd + "_row_" + str(i+1),
				"title": option,
				"description": ""
			}
		)

	data = json.dumps(
		{
			"messaging_product": "whatsapp",
			"recipient_type": "individual",
			"to": number,
			"type": "interactive",
			"interactive": {
				"type": "list",
				"body": {
					"text": body
				},
				"footer": {
					"text": footer
				},
				"action": {
					"button": "Ver Opciones",
					"sections": [
						{
							"title": "Secciones",
							"rows": rows
						}
					]
				}
			}
		}
	)
	return data

def document_Message(number, url, caption, filename):
	data = json.dumps(
		{
			"messaging_product": "whatsapp",
			"recipient_type": "individual",
			"to": number,
			"type": "document",
			"document": {
				"link": url,
				"caption": caption,
				"filename": filename
			}
		}
	)
	return data

def sticker_Message(number, sticker_id):
	data = json.dumps(
		{
			"messaging_product": "whatsapp",
			"recipient_type": "individual",
			"to": number,
			"type": "sticker",
			"sticker": {
				"id": sticker_id
			}
		}
	)
	return data

def get_media_id(media_name , media_type):
	media_id = ""
	if media_type == "sticker":
		media_id = sett.stickers.get(media_name, None)
	#elif media_type == "image":
	#	media_id = sett.images.get(media_name, None)
	#elif media_type == "video":
	#	media_id = sett.videos.get(media_name, None)
	#elif media_type == "audio":
	#	media_id = sett.audio.get(media_name, None)
	return media_id

def replyReaction_Message(number, messageId, emoji):
	data = json.dumps(
		{
			"messaging_product": "whatsapp",
			"recipient_type": "individual",
			"to": number,
			"type": "reaction",
			"reaction": {
				"message_id": messageId,
				"emoji": emoji
			}
		}
	)
	return data

def replyText_Message(number, messageId, text):
	data = json.dumps(
		{
			"messaging_product": "whatsapp",
			"recipient_type": "individual",
			"to": number,
			"context": { "message_id": messageId },
			"type": "text",
			"text": {
				"body": text
			}
		}
	)
	return data

def markRead_Message(messageId):
	data = json.dumps(
		{
			"messaging_product": "whatsapp",
			"status": "read",
			"message_id":  messageId
		}
	)
	return data

def administrar_chatbot(text,number, messageId, name):
	text = text.lower() #mensaje que envio el usuario
	list = []
	print("mensaje del usuario: ",text)

	markRead = markRead_Message(messageId)
	list.append(markRead)
	time.sleep(2)

	if text != "":
		resultados = datos_bus(text)
		for resultado in resultados:
			body = resultado
			footer = "Opensitoo"
			options = [text]

			replyButtonData = buttonReply_Message(number, options, body, footer, "sed1",messageId)
			replyReaction = replyReaction_Message(number, messageId, "🫡")
			list.append(replyReaction)
			list.append(replyButtonData)
	elif "servicios" in text:
		body = "Tenemos varias áreas de consulta para elegir. ¿Cuál de estos servicios te gustaría explorar?"
		footer = "Equipo Bigdateros"
		options = ["Analítica Avanzada", "Migración Cloud", "Inteligencia de Negocio"]

		listReplyData = listReply_Message(number, options, body, footer, "sed2",messageId)
		sticker = sticker_Message(number, get_media_id("perro_traje", "sticker"))

		list.append(listReplyData)
		list.append(sticker)

	else :
		data = text_Message(number,"Lo siento, no entendí lo que dijiste. ¿Quieres que te ayude con alguna de estas opciones?")
		list.append(data)

	for item in list:
		enviar_Mensaje_whatsapp(item)

#al parecer para mexico, whatsapp agrega 521 como prefijo en lugar de 52,
# este codigo soluciona ese inconveniente.
def replace_start(s):
	number = s[3:]
	if s.startswith("521"):
		return "52" + number
	elif s.startswith("549"):
		return "54" + number
	else:
		return s
		
