# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Projekt

Standalone Python-Script (Standardbibliothek only), das den SNB-Leitzins als CSV
abruft und per lokalem MTA (Postfix o.ä. auf `localhost:25`) eine Vergleichs-Mail
verschickt. Deployment: Docker-Image, getriggert via Cron auf dem Linux-Host
(`docker run --rm --network=host`). Privates Projekt, MIT-lizenziert,
öffentliches GitHub-Repo.

## Architektur

- `main.py` - alles drin: `fetch_letzte_zwei_zinsen()` (urllib + csv) liest die
  SNB-CSV (`https://data.snb.ch/api/cube/snboffzisa/data/csv/de?dimSel=D0(LZ)`,
  3 Header-Zeilen, `;`-getrennt). `baue_mail()` baut multipart HTML+text.
  `main()` versendet via `smtplib.SMTP(SMTP_HOST, SMTP_PORT)` ohne Auth.
- Konfig per Env-Var mit Defaults: `EMAIL_TO`, `EMAIL_FROM`, `SMTP_HOST=localhost`,
  `SMTP_PORT=25`.
- `Dockerfile`: `python:3.12-slim`, kopiert `main.py`, ENTRYPOINT ruft Script.
  Keine `pip install`-Schritte (keine Dependencies).
- `docker-compose.yml`: Service `snb-leitzins` mit `build: .`,
  `network_mode: host` (für Postfix auf 127.0.0.1:25), `env_file: .env`,
  `profiles: ["scheduled"]` — Profil verhindert Auto-Start durch
  `~/scripts/update-stacks.sh`.
- `.skip-update`: Marker für `~/scripts/update-stacks.sh` (lokales Image,
  kein Registry-Pull).
- Trigger: User-Crontab-Eintrag (`0 8 5 * * cd /opt/stacks/... && docker
  compose --profile scheduled run --rm snb-leitzins`).
- `requirements.txt` ist absichtlich leer.

## Lokal testen

```bash
python3 main.py    # benötigt erreichbaren SMTP auf localhost:25
```

Für Versand-Test ohne MTA: `python3 -m smtpd -c DebuggingServer -n localhost:1025`
in einem zweiten Terminal, dann `SMTP_PORT=1025 python3 main.py`.

## Konventionen

User-facing Strings, Kommentare und Doku in Deutsch - bei Edits Sprache beibehalten.
