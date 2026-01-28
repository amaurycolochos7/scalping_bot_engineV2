import requests
import json

TOKEN = "8302860071:AAHuj9YWPUU-c_tmn_SM_kqV5qHgcEeE-MM"
url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"

print("Obteniendo mensajes del bot...\n")

response = requests.get(url)
data = response.json()

if data.get('ok'):
    if data.get('result'):
        print("=" * 60)
        print("CHAT IDs ENCONTRADOS:")
        print("=" * 60)
        
        for update in data['result']:
            if 'message' in update:
                chat = update['message']['chat']
                chat_id = chat['id']
                first_name = chat.get('first_name', 'Sin nombre')
                username = chat.get('username', 'Sin username')
                text = update['message'].get('text', '')
                
                print(f"\nChat ID: {chat_id}")
                print(f"Nombre: {first_name}")
                print(f"Username: @{username}")
                print(f"Mensaje: {text}")
        
        print("\n" + "=" * 60)
        print("IMPORTANTE: Copia el Chat ID de arriba")
        print("=" * 60)
    else:
        print("No se encontraron mensajes")
else:
    print(f"Error: {data}")
