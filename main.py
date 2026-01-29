#!/usr/bin/env python
"""
Scalping Engine V2 - Punto de entrada unificado
Ejecuta el bot de Telegram y el scanner en un solo proceso
"""
import sys
import threading
import asyncio
import logging
import time

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_scanner():
    """Ejecuta el scanner de criptomonedas"""
    from scanner import CryptoScanner
    
    logger.info("📊 Iniciando Scanner...")
    time.sleep(3)  # Esperar a que el bot inicie primero
    
    scanner = CryptoScanner()
    scanner.start()


def run_telegram_bot():
    """Ejecuta el bot de Telegram"""
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters
    from config import Config
    from bot_telegram import start_command, status_command, handle_message
    
    logger.info("🤖 Iniciando Bot de Telegram...")
    
    if not Config.TELEGRAM_BOT_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN no configurado")
        return
    
    # Crear aplicación
    app = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
    
    # Agregar handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("✅ Bot de Telegram listo")
    
    # Correr el bot
    app.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """Función principal - ejecuta ambos servicios"""
    print("""
    ╔══════════════════════════════════════════════════════╗
    ║     SCALPING ENGINE V2 + TELEGRAM BOT                ║
    ║     Sistema Unificado de Señales                     ║
    ╚══════════════════════════════════════════════════════╝
    """)
    
    # Crear hilos
    scanner_thread = threading.Thread(target=run_scanner, name="Scanner", daemon=True)
    bot_thread = threading.Thread(target=run_telegram_bot, name="TelegramBot")
    
    try:
        # Iniciar el scanner en segundo plano
        scanner_thread.start()
        logger.info("✅ Thread del Scanner iniciado")
        
        # El bot de Telegram corre en el hilo principal
        # (telegram-python-bot requiere el hilo principal para señales)
        run_telegram_bot()
        
    except KeyboardInterrupt:
        logger.info("\n⛔ Deteniendo servicios...")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
    finally:
        logger.info("👋 Scalping Engine V2 detenido")


if __name__ == "__main__":
    main()
