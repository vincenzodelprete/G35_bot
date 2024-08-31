# G35 Telegram Bot

Questo progetto implementa un bot Telegram che supporta l'elaborazione di messaggi di testo e audio. Il bot utilizza la libreria `python-telegram-bot` per interfacciarsi con l'API di Telegram, `Spacy` per l'elaborazione del linguaggio naturale e `Vosk` per la trascrizione dell'audio.

## Caratteristiche principali

- **Gestione dei Messaggi di Testo**: Il bot può analizzare e rispondere ai messaggi di testo usando Spacy per l'analisi grammaticale.
- **Gestione dei Messaggi Audio**: Il bot può trascrivere messaggi vocali utilizzando Vosk, e processare il testo risultante con Spacy.
- **Asincronismo**: Le operazioni di elaborazione sono implementate in modo asincrono per migliorare le performance.

## Struttura del Codice

- `Config`: Singleton per gestire la configurazione del bot.
- `Command`: Interfaccia di base per i comandi del bot.
- `TextCommand` e `AudioCommand`: Implementazioni concrete per gestire i messaggi di testo e audio.
- `CommandFactory`: Factory per selezionare il comando appropriato basato sull'input ricevuto.
- `TelegramBot`: Classe principale che gestisce l'interazione con l'API di Telegram.

## Note di Design

- **Command Interface**: Definisce un contratto comune per tutti i comandi, facilitando l'estensibilità.
- **CommandFactory**: Centralizza la logica di selezione del comando, semplificando l'aggiunta di nuovi tipi di comandi.
- **Asincronismo**: Le operazioni più pesanti, come l'elaborazione del testo e la conversione dei file audio, sono implementate in modo asincrono.

## Requisiti

- Python 3.7+
- Librerie: `python-telegram-bot`, `spacy`, `vosk`, `aiohttp`, `dotenv`

## Istruzioni per l'installazione

1. Clona il repository
2. Crea e attiva un ambiente virtuale
3. Installa le dipendenze con `pip install -r requirements.txt`
4. Configura le variabili d'ambiente in un file `.env`
5. Avvia il bot con `python g35j.py`

## Contributi

Sentiti libero di fare fork di questo progetto e di proporre modifiche tramite pull request. Assicurati di includere test appropriati per qualsiasi nuova funzionalità o correzione di bug.