# NexaDev-Bot
# NexaDev Bot

Bot Discord per la community NexaDev con sistema di ticket e gestione progetti.

## Setup

1. Clona il repository
2. Installa le dipendenze: `pip install -r requirements.txt`
3. Crea il file `.env` con le variabili d'ambiente
4. Esegui: `python main.py`

## Comandi

- `/setup_verify` - Setup sistema verifica
- `/setup_tickets` - Setup sistema ticket  
- `/status <nome> <modalità>` - Aggiorna status progetto

## Variabili d'Ambiente

- `DISCORD_TOKEN` - Token del bot Discord
- `GUILD_ID` - ID del server
- `TICKET_CHANNEL_ID` - ID canale ticket
- `VERIFY_CHANNEL_ID` - ID canale verifica
- `STATUS_CHANNEL_ID` - ID canale status
- `STAFF_ROLE_ID` - ID ruolo staff
