# Deployment auf teth (Docker + Cron)

## 1. Lokalen MTA einrichten

Beispiel mit Postfix:

```bash
sudo dnf install -y postfix    # bzw. apt install postfix
sudo systemctl enable --now postfix
echo "Testmail" | mail -s "Test" du@example.com
```

Hinweise:
- Viele Provider blocken eingehenden Port-25-Traffic von Consumer-IPs;
  in dem Fall einen Smarthost in Postfix konfigurieren (`relayhost = ...`).
- Damit die Mails nicht im Spam landen: SPF/DKIM für `raptus.com` setzen
  bzw. `EMAIL_FROM` auf eine Adresse mit gültigem Reverse-DNS legen.

## 2. Image bauen

```bash
cd /opt/snb-leitzins-monitor    # oder wo das Repo liegt
sudo docker build -t snb-leitzins:latest .
```

## 3. Manuell testen

`EMAIL_TO` ist Pflicht (kein Default mehr im Code):

```bash
sudo docker run --rm --network=host -e EMAIL_TO=du@example.com snb-leitzins:latest
```

`--network=host` erlaubt dem Container, den Postfix auf `localhost:25`
des Hosts zu erreichen. Mail im Postfach prüfen.

## 4. Crontab-Eintrag

Als root (`sudo crontab -e`) eintragen - läuft jeden 5. des Monats um 08:00.
`EMAIL_TO` muss gesetzt werden:

```
0 8 5 * * /usr/bin/docker run --rm --network=host -e EMAIL_TO=du@example.com snb-leitzins:latest >> /var/log/snb-leitzins.log 2>&1
```

Wer mehrere Variablen pflegen will, kann sie in eine Datei legen
(`/etc/snb-leitzins.env`, `chmod 600`) und im Cron-Befehl
`--env-file /etc/snb-leitzins.env` statt `-e ...` verwenden.

## 5. Update / Rebuild

Nach Code-Änderungen:

```bash
cd /opt/snb-leitzins-monitor && git pull && sudo docker build -t snb-leitzins:latest .
```

## Troubleshooting

| Problem | Check |
|---|---|
| Keine Mail | `/var/log/snb-leitzins.log`, dann `journalctl -u postfix` / `mailq` |
| Cron läuft nicht | `grep CRON /var/log/syslog` bzw. `journalctl -u cron` |
| `Connection refused` auf SMTP | Postfix läuft? `ss -tlnp \| grep :25` |
| HTTP-Fehler beim SNB-Abruf | URL im Browser testen |
