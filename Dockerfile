FROM python:3.12-slim

WORKDIR /app
COPY main.py .

# Keine Dependencies - Standardbibliothek reicht.
ENTRYPOINT ["python3", "/app/main.py"]
