import os
import asyncio
import nest_asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

# Applica la patch di nest_asyncio
nest_asyncio.apply()

# Carica le variabili d'ambiente dal file .env
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Risponde al comando /start."""
    await update.message.reply_text('Ciao! Sono G35, il tuo assistente personale. Come posso aiutarti oggi?')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Risponde al comando /help."""
    await update.message.reply_text('Puoi chiedermi di fare diverse cose, come accendere le luci o fornire informazioni.')

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Risponde ai messaggi dell'utente."""
    user_message = update.message.text
    await update.message.reply_text(f"Hai detto: {user_message}")

async def main():
    """Avvia il bot."""
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    await application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
