import os
import wave
import json
import vosk
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv

# Carica le variabili d'ambiente
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  
VOSK_MODEL_PATH = os.getenv("VOSK_MODEL_PATH")

# Inizializza il modello Vosk
model = vosk.Model(VOSK_MODEL_PATH)

async def start(update: Update, context):
    await update.message.reply_text('Ciao! Inviami un messaggio di testo o un audio, e lo elaborerò per te.')

async def handle_text(update: Update, context):
    user_text = update.message.text
    # Qui puoi aggiungere la logica che già hai per gestire il testo, per esempio inviare a GPT o eseguire comandi
    response = f"Hai detto: {user_text}"
    await update.message.reply_text(response)

async def handle_audio(update: Update, context):
    try:
        # Scarica il file audio
        file = await context.bot.get_file(update.message.voice.file_id if update.message.voice else update.message.audio.file_id)
        file_path = os.path.join("downloads", f"{file.file_id}.oga")
        await file.download_to_drive(file_path)
        
        # Converti il file .oga in .wav
        wav_path = file_path.replace('.oga', '.wav')
        convert_to_wav(file_path, wav_path)
        
        # Trascrivi l'audio con Vosk
        transcription = transcribe_audio(wav_path)
        
        # Invia la trascrizione all'utente
        await update.message.reply_text(f"Trascrizione: {transcription}")
        
    except Exception as e:
        await update.message.reply_text(f"Si è verificato un errore durante l'elaborazione dell'audio: {str(e)}")
    
    finally:
        # Rimuovi i file temporanei
        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists(wav_path):
            os.remove(wav_path)

def convert_to_wav(input_path, output_path):
    """Converte un file audio da .oga a .wav utilizzando ffmpeg."""
    try:
        command = f"ffmpeg -i {input_path} -ar 16000 -ac 1 {output_path}"
        subprocess.run(command, shell=True, check=True)
        print(f"File convertito con successo: {output_path}")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Errore durante la conversione dell'audio: {str(e)}")

def transcribe_audio(file_path):
    """Trascrive l'audio utilizzando il modello Vosk."""
    with wave.open(file_path, "rb") as wf:
        rec = vosk.KaldiRecognizer(model, wf.getframerate())
        
        transcription = []
        
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                result = rec.Result()
                transcription.append(json.loads(result).get('text', ''))
        
        transcription.append(json.loads(rec.FinalResult()).get('text', ''))
        
    return ' '.join(transcription)

if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    start_handler = CommandHandler('start', start)
    text_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)
    audio_handler = MessageHandler(filters.VOICE | filters.AUDIO, handle_audio)
    
    application.add_handler(start_handler)
    application.add_handler(text_handler)
    application.add_handler(audio_handler)
    
    print("Bot in esecuzione...")
    application.run_polling()
