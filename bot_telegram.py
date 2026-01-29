#!/usr/bin/env python
"""
Bot de Telegram con autenticación por keys y menú interactivo
"""
import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    CallbackQueryHandler, filters, ContextTypes
)
from config import Config
from keys_manager import (
    is_user_authorized, 
    validate_key, 
    activate_key, 
    get_authorized_chat_ids,
    cleanup_expired
)

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Estado de usuarios
users_waiting_key = set()


def get_main_menu():
    """Retorna el menú principal"""
    keyboard = [
        [InlineKeyboardButton("📊 Analizar Moneda", callback_data='analyze')],
        [InlineKeyboardButton("📈 Ver Top Señales", callback_data='top_signals')],
        [InlineKeyboardButton("⏱️ Mi Suscripción", callback_data='status')],
    ]
    return InlineKeyboardMarkup(keyboard)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja el comando /start"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    username = update.effective_user.username
    
    # Verificar si ya tiene acceso
    auth_info = is_user_authorized(user_id)
    
    if auth_info:
        # Usuario autorizado - mostrar menú
        remaining = auth_info['remaining']
        days = remaining.days
        hours = remaining.seconds // 3600
        
        if days > 0:
            time_str = f"{days}d {hours}h"
        else:
            time_str = f"{hours}h"
        
        await update.message.reply_text(
            f"🤖 <b>Bot de Señales Futures</b>\n\n"
            f"✅ Acceso activo: <b>{time_str}</b> restantes\n\n"
            f"Selecciona una opción:",
            parse_mode='HTML',
            reply_markup=get_main_menu()
        )
    else:
        # Solicitar key
        users_waiting_key.add(user_id)
        await update.message.reply_text(
            "🔐 <b>Bot de Señales Futures</b>\n\n"
            "Para acceder necesitas una clave.\n\n"
            "📝 Ingresa tu clave de acceso:",
            parse_mode='HTML'
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja mensajes de texto"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    username = update.effective_user.username
    text = update.message.text.strip().upper()
    
    # Verificar si está esperando key
    if user_id in users_waiting_key:
        key_info = validate_key(text)
        
        if key_info:
            result = activate_key(text, user_id, chat_id, username)
            
            if result:
                users_waiting_key.discard(user_id)
                
                await update.message.reply_text(
                    f"✅ <b>¡Acceso Activado!</b>\n\n"
                    f"⏱️ Duración: <b>{result['duration_label']}</b>\n"
                    f"📅 Expira: <b>{result['expires_at'].strftime('%d/%m/%Y %H:%M')}</b>\n\n"
                    f"🚀 Recibirás señales automáticamente.\n\n"
                    f"Selecciona una opción:",
                    parse_mode='HTML',
                    reply_markup=get_main_menu()
                )
                logger.info(f"✅ Usuario {user_id} activó acceso")
            else:
                await update.message.reply_text(
                    "❌ Error al activar. Intenta de nuevo.",
                    parse_mode='HTML'
                )
        else:
            await update.message.reply_text(
                "❌ <b>Clave inválida o ya usada.</b>\n\n"
                "Verifica tu clave e intenta de nuevo:",
                parse_mode='HTML'
            )
        return
    
    # Usuario no autenticado
    auth_info = is_user_authorized(user_id)
    
    if not auth_info:
        users_waiting_key.add(user_id)
        await update.message.reply_text(
            "🔒 <b>Acceso Requerido</b>\n\n"
            "📝 Ingresa tu clave de acceso:",
            parse_mode='HTML'
        )
    else:
        # Usuario autenticado queriendo analizar moneda
        # Buscar si escribió un símbolo
        symbol = text.replace('$', '').replace('/', '').upper()
        if not symbol.endswith('USDT'):
            symbol = symbol + 'USDT'
        
        await update.message.reply_text(
            f"🔍 Analizando <b>{symbol}</b>...\n\n"
            f"⏳ Por favor espera...",
            parse_mode='HTML'
        )
        
        # TODO: Integrar análisis real aquí
        await asyncio.sleep(2)
        
        await update.message.reply_text(
            f"📊 <b>Análisis de {symbol}</b>\n\n"
            f"⚠️ El modelo de IA está en entrenamiento.\n"
            f"Las señales automáticas llegarán pronto.",
            parse_mode='HTML',
            reply_markup=get_main_menu()
        )


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja los callbacks de los botones"""
    query = update.callback_query
    user_id = query.from_user.id
    
    await query.answer()
    
    # Verificar autorización
    auth_info = is_user_authorized(user_id)
    if not auth_info:
        await query.edit_message_text(
            "🔒 Tu acceso expiró.\n\n"
            "📝 Ingresa una nueva clave:",
            parse_mode='HTML'
        )
        users_waiting_key.add(user_id)
        return
    
    if query.data == 'analyze':
        await query.edit_message_text(
            "📊 <b>Analizar Moneda</b>\n\n"
            "Escribe el símbolo de la moneda.\n"
            "Ejemplo: <code>BTC</code> o <code>ETHUSDT</code>",
            parse_mode='HTML'
        )
    
    elif query.data == 'top_signals':
        await query.edit_message_text(
            "📈 <b>Top Señales Recientes</b>\n\n"
            "⏳ El modelo está en entrenamiento.\n"
            "Las señales llegarán automáticamente.",
            parse_mode='HTML',
            reply_markup=get_main_menu()
        )
    
    elif query.data == 'status':
        remaining = auth_info['remaining']
        days = remaining.days
        hours = remaining.seconds // 3600
        
        if days > 0:
            time_str = f"{days} día(s), {hours} hora(s)"
        else:
            time_str = f"{hours} hora(s)"
        
        await query.edit_message_text(
            f"⏱️ <b>Tu Suscripción</b>\n\n"
            f"✅ Estado: Activo\n"
            f"⏱️ Tiempo restante: <b>{time_str}</b>\n"
            f"📅 Expira: <b>{auth_info['expires_at'].strftime('%d/%m/%Y %H:%M')}</b>",
            parse_mode='HTML',
            reply_markup=get_main_menu()
        )
    
    elif query.data == 'menu':
        await query.edit_message_text(
            "🤖 <b>Menú Principal</b>\n\n"
            "Selecciona una opción:",
            parse_mode='HTML',
            reply_markup=get_main_menu()
        )


async def send_signal_to_users(bot, message: str):
    """Envía una señal a todos los usuarios autorizados"""
    cleanup_expired()
    chat_ids = get_authorized_chat_ids()
    
    if not chat_ids:
        logger.warning("⚠️ No hay usuarios autorizados")
        return 0
    
    sent = 0
    for chat_id in chat_ids:
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode='HTML'
            )
            sent += 1
        except Exception as e:
            logger.error(f"❌ Error enviando a {chat_id}: {e}")
    
    logger.info(f"📤 Señal enviada a {sent}/{len(chat_ids)} usuarios")
    return sent


def main():
    """Función principal del bot"""
    if not Config.TELEGRAM_BOT_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN no configurado")
        return
    
    app = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
    
    # Handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("menu", start_command))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("🤖 Bot de Telegram iniciado")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
