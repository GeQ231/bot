# Usa l'immagine di base Python 3.12
FROM python:3.12-slim

# Installa ffmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Imposta la cartella di lavoro nel container
WORKDIR /app

# Copia i file del progetto nella cartella di lavoro
COPY . /app

# Installa le dipendenze (assicurati di avere un requirements.txt)
RUN pip install --no-cache-dir -r requirements.txt

# Comando per avviare il bot
CMD ["python", "bot.py"]
