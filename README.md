# SNB Leitzins Monitor

Kleines Python-Script, das einmal pro Monat den aktuellen Leitzins der
Schweizerischen Nationalbank (SNB) abruft und per E-Mail verschickt - inkl.
Vergleich zum Vormonat und farblicher Markierung bei Änderungen.

Läuft als Docker-Compose-Stack, getriggert von Cron auf einem Linux-Host.
Mailversand über lokalen MTA (z.B. Postfix). Keine externen Dienste, keine
Cloud, keine Python-Dependencies ausserhalb der Standardbibliothek.

## Funktionen

- Monatlicher Versand am 5. des Monats um 08:00 Uhr
- Aktueller Wert + Vormonat im Vergleich
- HTML-Mail mit roter Markierung bei Zinsänderung
- Plain-Text-Alternative für Mail-Clients ohne HTML

## Voraussetzungen

- Linux-Host mit Docker (inkl. Compose-Plugin) und Cron
- Lokaler MTA, der Mails nach extern zustellen kann (Postfix, msmtp, ...)

## Installation

Siehe [DEPLOYMENT.md](DEPLOYMENT.md). Kurz:

```bash
git clone https://github.com/gzuercher/snb-leitzins-monitor.git
cd snb-leitzins-monitor
cp .env.example .env && $EDITOR .env   # EMAIL_TO setzen
docker compose build
# Cron (User-Crontab):
# 0 8 5 * * cd /opt/stacks/snb-leitzins-monitor && docker compose --profile scheduled run --rm snb-leitzins
```

## Konfiguration

`EMAIL_TO` ist Pflicht (Environment-Variable, kein Default im Code).
`EMAIL_FROM`, `SMTP_HOST`, `SMTP_PORT` haben Defaults und sind optional
überschreibbar - siehe `.env.example`.

## Datenquelle

[Schweizerische Nationalbank Data Portal](https://data.snb.ch/api/cube/snboffzisa/data/csv/de?dimSel=D0(LZ))

## Lizenz

MIT - siehe [LICENSE](LICENSE).
