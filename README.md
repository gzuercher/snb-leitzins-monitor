# SNB Leitzins Monitor

Kleines Python-Script, das einmal pro Monat den aktuellen Leitzins der
Schweizerischen Nationalbank (SNB) abruft und per E-Mail verschickt - inkl.
Vergleich zum Vormonat und farblicher Markierung bei Änderungen.

Läuft als Docker-Container, getriggert von Cron auf einem Linux-Host.
Mailversand über lokalen MTA (z.B. Postfix). Keine externen Dienste, keine
Cloud, keine Python-Dependencies ausserhalb der Standardbibliothek.

## Funktionen

- Monatlicher Versand am 5. des Monats um 08:00 Uhr
- Aktueller Wert + Vormonat im Vergleich
- HTML-Mail mit roter Markierung bei Zinsänderung
- Plain-Text-Alternative für Mail-Clients ohne HTML

## Voraussetzungen

- Linux-Host mit Docker und Cron
- Lokaler MTA, der Mails nach extern zustellen kann (Postfix, msmtp, ...)

## Installation

Siehe [DEPLOYMENT.md](DEPLOYMENT.md).

Schnellversion:

```bash
sudo docker build -t snb-leitzins:latest .
# in sudo crontab -e (EMAIL_TO ist Pflicht):
# 0 8 5 * * /usr/bin/docker run --rm --network=host -e EMAIL_TO=du@example.com snb-leitzins:latest
```

## Konfiguration

`EMAIL_TO` ist Pflicht (Environment-Variable, kein Default im Code).
`EMAIL_FROM`, `SMTP_HOST`, `SMTP_PORT` haben Defaults und sind optional
überschreibbar - siehe `.env.example`.

## Datenquelle

[Schweizerische Nationalbank Data Portal](https://data.snb.ch/api/cube/snboffzisa/data/csv/de?dimSel=D0(LZ))

## Lizenz

MIT - siehe [LICENSE](LICENSE).
