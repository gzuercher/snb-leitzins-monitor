# Deployment auf teth (Docker Compose + Cron)

Dieser Stack folgt der `~/scripts/`-Konvention auf teth:
- Repo geklont nach `/opt/stacks/snb-leitzins-monitor/` (Compose-File und
  Source liegen zusammen).
- `.skip-update` Marker -> `update-stacks.sh` ueberspringt diesen Stack
  (lokales Image, kein Registry-Pull).
- Service in Compose-Profile `scheduled` -> `docker compose up -d`
  startet ihn nicht. Trigger erfolgt explizit per Cron.

## 1. Lokalen MTA voraussetzen

Postfix laeuft bereits auf teth (`127.0.0.1:25`). Falls nicht:

```bash
sudo dnf install -y postfix
sudo systemctl enable --now postfix
echo "Testmail" | mail -s "Test" du@example.com
```

## 2. Stack installieren

```bash
sudo mkdir -p /opt/stacks
sudo chown gzuercher:gzuercher /opt/stacks
cd /opt/stacks
git clone https://github.com/gzuercher/snb-leitzins-monitor.git
cd snb-leitzins-monitor
cp .env.example .env
$EDITOR .env                  # EMAIL_TO eintragen
docker compose --profile scheduled build
```

## 3. Manuell testen

```bash
cd /opt/stacks/snb-leitzins-monitor
docker compose --profile scheduled run --rm snb-leitzins
```

Mail im Postfach pruefen.

## 4. Cron-Eintrag (User-Crontab)

`crontab -e` als User `gzuercher`:

```
MAILTO=gzuercher@raptus.com

# SNB Leitzins Monitor: jeden 5. des Monats um 08:00.
# Erfolgs-Output landet im Logfile (kein Mail-Spam an MAILTO);
# bei Fehler reicht cron Stderr durch -> Mail an MAILTO.
0 8 5 * * cd /opt/stacks/snb-leitzins-monitor && docker compose --profile scheduled run --rm snb-leitzins >>$HOME/scripts/logs/snb-leitzins.log 2>&1 || tail -n 30 $HOME/scripts/logs/snb-leitzins.log >&2
```

## 5. Updates

Code-Aenderungen aus dem Git-Repo holen und Image neu bauen
(`update-stacks.sh` macht das *nicht* fuer diesen Stack):

```bash
cd /opt/stacks/snb-leitzins-monitor
git pull
docker compose --profile scheduled build
```

## Troubleshooting

| Problem | Check |
|---|---|
| Keine Mail | `~/scripts/logs/snb-leitzins.log`, `mailq`, `journalctl -u postfix` |
| Cron laeuft nicht | `journalctl -u crond --since "1 hour ago"` |
| `EMAIL_TO ist nicht gesetzt` | `.env` vorhanden? `docker compose config` zeigt geladene Vars |
| Image fehlt | `docker compose --profile scheduled build` im Stack-Dir |
| `WARN: No services to build` | `--profile scheduled` vergessen |
