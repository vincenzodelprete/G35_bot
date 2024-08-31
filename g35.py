import logging
import os
import asyncio
import subprocess
import json
import vosk
import spacy
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv

# Configurazione Singleton per gestire le configurazioni globali del bot
class Config:
    _instance = None

    @staticmethod
    def get_instance():
        """Metodo statico per ottenere l'istanza singleton di Config."""
        if Config._instance is None:
            Config()
        return Config._instance

    def __init__(self):
        """Inizializza il singleton Config e carica le variabili d'ambiente."""
        if Config._instance is not None:
            raise Exception("Questa classe è un singleton!")
        else:
            load_dotenv()
            self.telegram_token = os.getenv("TELEGRAM_TOKEN")
            self.vosk_model_path = os.getenv("VOSK_MODEL_PATH")
            Config._instance = self

# Interfaccia Command per implementare il pattern Command
class Command:
    async def execute(self, update: Update, context):
        """Metodo da implementare per eseguire un comando."""
        raise NotImplementedError("Questo metodo dovrebbe essere implementato nelle sottoclassi")

# Comando concreto per gestire i messaggi di testo
class TextCommand(Command):
    def __init__(self):
        """Inizializza il comando di testo caricando il modello Spacy per l'analisi linguistica."""
        self.nlp = spacy.load("it_core_news_sm")

    async def execute(self, update: Update, context):
        """Esegue il comando di elaborazione del testo."""
        user_text = update.message.text
        logging.info(f"Received text message: {user_text}")

        # Elaborazione del testo con Spacy
        doc = await self.process_text_async(user_text)
        processed_text = [(token.text, token.pos_, token.dep_) for token in doc]
        logging.info(f"Processed text with Spacy: {processed_text}")

        response = f"Analisi del testo: {processed_text}"

        # Invia il risultato in chat
        try:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=response)
        except Exception as e:
            logging.error(f"Errore durante l'invio del messaggio: {e}")

    async def process_text_async(self, user_text):
        """Elabora il testo in modo asincrono utilizzando Spacy."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.nlp, user_text)

# Comando concreto per gestire i messaggi vocali
class AudioCommand(Command):
    def __init__(self):
        """Inizializza il comando audio caricando il modello Vosk e Spacy."""
        self.model_path = Config.get_instance().vosk_model_path
        self.model = vosk.Model(self.model_path)
        self.nlp = spacy.load("it_core_news_sm")

    async def execute(self, update: Update, context):
        """Esegue il comando di elaborazione dell'audio."""
        try:
            file = await context.bot.get_file(update.message.voice.file_id)
            file_path = os.path.join("downloads", file.file_unique_id + ".oga")
            wav_path = file_path.replace(".oga", ".wav")

            await self.download_file(file, file_path)
            logging.info(f"File audio scaricato: {file_path}")

            await self.convert_to_wav(file_path, wav_path)
            logging.info(f"File convertito in WAV: {wav_path}")

            transcript = await self.transcribe_audio_async(wav_path)
            logging.info(f"Trascrizione completata: {transcript}")

            doc = await self.process_text_async(transcript['text'])
            processed_text = [(token.text, token.pos_, token.dep_) for token in doc]
            logging.info(f"Processed text with Spacy: {processed_text}")

            response = f"Analisi del testo: {processed_text}"

            await context.bot.send_message(chat_id=update.effective_chat.id, text=response)
        except Exception as e:
            logging.error(f"Errore durante l'elaborazione dell'audio: {e}")
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Errore durante l'elaborazione dell'audio.")

    async def download_file(self, file, file_path):
        """Scarica il file audio dal server Telegram."""
        await file.download_to_drive(file_path)

    async def convert_to_wav(self, input_path, output_path):
        """Converte il file audio da OGA a WAV utilizzando FFmpeg."""
        convert_command = f"ffmpeg -i {input_path} -ar 16000 -ac 1 {output_path}"
        process = await asyncio.create_subprocess_shell(
            convert_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            logging.error(f"Errore durante la conversione in WAV: {stderr.decode('utf-8')}")
            raise Exception("Errore durante la conversione dell'audio.")

    async def transcribe_audio_async(self, wav_path):
        """Trascrive l'audio in modo asincrono utilizzando Vosk."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.transcribe_audio, wav_path)

    def transcribe_audio(self, wav_path):
        """Trascrive l'audio utilizzando Vosk."""
        with open(wav_path, "rb") as audio_file:
            rec = vosk.KaldiRecognizer(self.model, 16000)
            rec.SetWords(True)
            rec.AcceptWaveform(audio_file.read())
            return json.loads(rec.FinalResult())

    async def process_text_async(self, text):
        """Elabora il testo trascritto in modo asincrono utilizzando Spacy."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.nlp, text)

# Factory per creare i comandi appropriati in base al tipo di messaggio ricevuto
class CommandFactory:
    @staticmethod
    def get_command(update: Update) -> Command:
        """Ritorna il comando appropriato in base al tipo di messaggio ricevuto."""
        if update.message.text:
            return TextCommand()
        elif update.message.voice or update.message.audio:
            return AudioCommand()
        else:
            return None

# Invocatore: Applicazione del Bot Telegram
class TelegramBot:
    def __init__(self, config: Config):
        """Inizializza il bot Telegram con la configurazione fornita."""
        self.config = config
        self.application = ApplicationBuilder().token(config.telegram_token).build()

    def start(self):
        """Avvia il bot, aggiungendo i gestori di comando e messaggio."""
        start_handler = CommandHandler('start', self.handle_start)
        self.application.add_handler(start_handler)

        message_handler = MessageHandler(filters.ALL, self.handle_message)
        self.application.add_handler(message_handler)

        logging.info("Bot is running...")
        self.application.run_polling()

    async def handle_start(self, update: Update, context):
        """Gestisce il comando /start inviato dagli utenti."""
        await update.message.reply_text("Hello! Send me a message or an audio file.")

    async def handle_message(self, update: Update, context):
        """Gestisce tutti i messaggi ricevuti e li instrada al comando appropriato."""
        command = CommandFactory.get_command(update)
        if command:
            await command.execute(update, context)
        else:
            logging.warning("Received unsupported message type")

# Punto di ingresso dell'applicazione
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    config = Config.get_instance()
    bot = TelegramBot(config)
    bot.start()