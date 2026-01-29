#!/usr/bin/env python
"""
Bot de Telegram interactivo con autenticación por keys
"""
import asyncio
import logging
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
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

# Estado de usuarios esperando key
users_waiting_key = set()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja el comando /start"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    username = update.effective_user.username
    
    # Verificar si ya tiene acceso
    auth_info = is_user_authorized(user_id)
    
    if auth_info:
        # Usuario ya autorizado
        remaining = auth_info['remaining']
        days = remaining.days
        hours = remaining.seconds // 3600
        
        if days > 0:
            time_str = f"{days} día(s) y {hours} hora(s)"
        else:
            time_str = f"{hours} hora(s)"
        
        await update.message.reply_text(
            f"✅ <b>¡Ya tienes acceso activo!</b>\n\n"
            f"⏱️ Tiempo restante: <b>{time_str}</b>\n\n"
            f"📊 Recibirás las señales de trading automáticamente.",
            parse_mode='HTML'
        )
    else:
        # Solicitar key
        users_waiting_key.add(user_id)
        await update.message.reply_text(
            "🔐 <b>Bienvenido al Bot de Señales de Trading</b>\n\n"
            "Para acceder, necesitas una <b>clave de acceso</b>.\n\n"
            "📝 Por favor, ingresa tu clave:",
            parse_mode='HTML'
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja mensajes de texto (principalmente para recibir keys)"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    username = update.effective_user.username
    text = update.message.text.strip().upper()
    
    # Verificar si usuario está esperando ingresar una key
    if user_id in users_waiting_key:
        # Intentar validar y activar la key
        key_info = validate_key(text)
        
        if key_info:
            # Activar la key
            result = activate_key(text, user_id, chat_id, username)
            
            if result:
                users_waiting_key.discard(user_id)
                
                await update.message.reply_text(
                    f"✅ <b>¡Acceso Activado!</b>\n\n"
                    f"⏱️ Duración: <b>{result['duration_label']}</b>\n"
                    f"📅 Expira: <b>{result['expires_at'].strftime('%d/%m/%Y %H:%M')}</b>\n\n"
                    f"📊 A partir de ahora recibirás las señales de trading automáticamente.\n\n"
                    f"¡Buena suerte! 🚀",
                    parse_mode='HTML'
                )
                logger.info(f"✅ Usuario {user_id} activó acceso hasta {result['expires_at']}")
            else:
                await update.message.reply_text(
                    "❌ <b>Error al activar la clave.</b>\n\n"
                    "Por favor, intenta de nuevo o contacta al administrador.",
                    parse_mode='HTML'
                )
        else:
            await update.message.reply_text(
                "❌ <b>Clave inválida o ya utilizada.</b>\n\n"
                "Por favor, verifica tu clave e intenta de nuevo.\n"
                "Si no tienes una clave, contacta al administrador.",
                parse_mode='HTML'
            )
    else:
        # Usuario no autenticado intentando usar el bot
        auth_info = is_user_authorized(user_id)
        
        if not auth_info:
            users_waiting_key.add(user_id)
            await update.message.reply_text(
                "🔒 <b>Acceso Requerido</b>\n\n"
                "No tienes una suscripción activa.\n\n"
                "📝 Por favor, ingresa tu clave de acceso:",
                parse_mode='HTML'
            )
        else:
            # Usuario autorizado, mostrar info
            remaining = auth_info['remaining']
            days = remaining.days
            hours = remaining.seconds // 3600
            
            if days > 0:
                time_str = f"{days} día(s) y {hours} hora(s)"
            else:
                time_str = f"{hours} hora(s)"
            
            await update.message.reply_text(
                f"ℹ️ <b>Estado de tu Suscripción</b>\n\n"
                f"✅ Acceso activo\n"
                f"⏱️ Tiempo restante: <b>{time_str}</b>\n\n"
                f"📊 Recibirás las señales automáticamente.",
                parse_mode='HTML'
            )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Muestra el estado de la suscripción"""
    user_id = update.effective_user.id
    
    auth_info = is_user_authorized(user_id)
    
    if auth_info:
        remaining = auth_info['remaining']
        days = remaining.days
        hours = remaining.seconds // 3600
        minutes = (remaining.seconds % 3600) // 60
        
        if days > 0:
            time_str = f"{days} día(s), {hours} hora(s)"
        elif hours > 0:
            time_str = f"{hours} hora(s), {minutes} minuto(s)"
        else:
            time_str = f"{minutes} minuto(s)"
        
        await update.message.reply_text(
            f"📊 <b>Estado de tu Suscripción</b>\n\n"
            f"✅ Estado: <b>Activo</b>\n"
            f"⏱️ Tiempo restante: <b>{time_str}</b>\n"
            f"📅 Expira: <b>{auth_info['expires_at'].strftime('%d/%m/%Y %H:%M')}</b>",
            parse_mode='HTML'
        )
    else:
        users_waiting_key.add(user_id)
        await update.message.reply_text(
            "🔒 <b>Sin Acceso Activo</b>\n\n"
            "No tienes una suscripción activa.\n\n"
            "📝 Por favor, ingresa tu clave de acceso:",
            parse_mode='HTML'
        )


async def send_signal_to_users(bot: Bot, message: str):
    """Envía una señal a todos los usuarios autorizados"""
    # Limpiar usuarios expirados primero
    cleanup_expired()
    
    # Obtener usuarios autorizados
    chat_ids = get_authorized_chat_ids()
    
    if not chat_ids:
        logger.warning("⚠️ No hay usuarios autorizados para enviar señales")
        return 0
    
    sent_count = 0
    for chat_id in chat_ids:
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode='HTML'
            )
            sent_count += 1
        except Exception as e:
            logger.error(f"❌ Error enviando a {chat_id}: {e}")
    
    logger.info(f"📤 Señal enviada a {sent_count}/{len(chat_ids)} usuarios")
    return sent_count


def main():
    """Función principal del bot"""
    if not Config.TELEGRAM_BOT_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN no configurado en .env")
        return
    
    # Crear la aplicación
    app = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
    
    # Agregar handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Iniciar el bot
    logger.info("🤖 Bot de Telegram iniciado")
    logger.info("📡 Esperando conexiones...")
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
