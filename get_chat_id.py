"""
Script para obtener tu Chat ID de Telegram
"""
from telegram import Bot
import asyncio

async def get_chat_id():
    # Tu token de bot
    token = "8302860071:AAHuj9YWPUU-c_tmn_SM_kqV5qHgcEeE-MM"
    bot = Bot(token=token)
    
    print("=" * 50)
    print("🔍 Obteniendo tu Chat ID de Telegram")
    print("=" * 50)
    print("\nPASOS:")
    print("1. Abre Telegram")
    print("2. Busca tu bot y envíale un mensaje (cualquiera)")
    print("3. Ejecuta este script nuevamente\n")
    
    try:
        # Obtener actualizaciones
        updates = await bot.get_updates()
        
        if not updates:
            print("⚠️ No hay mensajes nuevos.")
            print("   Envía un mensaje a tu bot y vuelve a ejecutar este script.\n")
            return
        
        # Mostrar todos los chat IDs encontrados
        print("✅ Chat IDs encontrados:\n")
        seen_ids = set()
        for update in updates:
            if update.message:
                chat_id = update.message.chat.id
                username = update.message.chat.username or "Sin username"
                first_name = update.message.chat.first_name or "Sin nombre"
                
                if chat_id not in seen_ids:
                    print(f"📱 Chat ID: {chat_id}")
                    print(f"   Usuario: {first_name} (@{username})")
                    print(f"   Último mensaje: {update.message.text}\n")
                    seen_ids.add(chat_id)
        
        if seen_ids:
            print("=" * 50)
            print("📝 Copia uno de estos Chat IDs y pégalo en .env")
            print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(get_chat_id())
