"""
Script simplificado para obtener Chat ID
"""
import requests

TOKEN = "8302860071:AAHuj9YWPUU-c_tmn_SM_kqV5qHgcEeE-MM"

print("=" * 50)
print("🔍 Obteniendo actualizaciones del bot...")
print("=" * 50)

url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"

try:
    response = requests.get(url)
    data = response.json()
    
    if not data.get('ok'):
        print(f"❌ Error: {data}")
    elif not data.get('result'):
        print("\n⚠️ No hay mensajes.")
        print("\n📝 PASOS:")
        print("1. Abre Telegram")
        print("2. Busca el bot con este token")
        print("3. Envía cualquier mensaje (ej: /start)")
        print("4. Ejecuta este script nuevamente\n")
    else:
        print("\n✅ Chat IDs encontrados:\n")
        seen = set()
        for update in data['result']:
            if 'message' in update:
                msg = update['message']
                chat_id = msg['chat']['id']
                username = msg['chat'].get('username', 'Sin username')
                first_name = msg['chat'].get('first_name', 'Sin nombre')
                text = msg.get('text', '')
                
                if chat_id not in seen:
                    print(f"📱 Chat ID: {chat_id}")
                    print(f"   Usuario: {first_name} (@{username})")
                    print(f"   Mensaje: {text}")
                    print()
                    seen.add(chat_id)
        
        if seen:
            print("=" * 50)
            print("📝 Copia este Chat ID y pégalo en .env:")
            print(f"   TELEGRAM_CHAT_ID={list(seen)[0]}")
            print("=" * 50)

except Exception as e:
    print(f"❌ Error: {e}")
