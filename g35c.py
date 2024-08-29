import os
import asyncio
import logging
import nest_asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

# Applica la patch di nest_asyncio
nest_asyncio.apply()

# Carica le variabili d'ambiente dal file .env
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Configurazione del logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Risponde al comando /start."""
    logger.info(f"Comando /start ricevuto da {update.effective_user.username}")
    await update.message.reply_text('Ciao! Sono G35, il tuo assistente personale. Come posso aiutarti oggi?')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Risponde al comando /help."""
    logger.info(f"Comando /help ricevuto da {update.effective_user.username}")
    await update.message.reply_text('Puoi chiedermi di fare diverse cose, come accendere le luci o fornire informazioni.')

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Risponde ai messaggi dell'utente."""
    user_message = update.message.text
    logger.info(f"Messaggio ricevuto da {update.effective_user.username}: {user_message}")
    await update.message.reply_text(f"Hai detto: {user_message}")

async def shutdown(application):
    """Gestisce la chiusura del bot."""
    logger.info("Avvio la chiusura del bot...")
    await application.shutdown()
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [task.cancel() for task in tasks]

    logger.info("Aspettando che le attività in corso terminino...")
    await asyncio.gather(*tasks, return_exceptions=True)

async def main():
    """Avvia il bot."""
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    try:
        logger.info("Bot avviato e in ascolto per i comandi.")
        await application.run_polling()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Ricevuto segnale di interruzione, avvio la chiusura...")
        await shutdown(application)
    finally:
        logger.info("Bot chiuso correttamente.")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot interrotto manualmente.")
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
