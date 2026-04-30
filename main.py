#!/usr/bin/env python3
"""Monatliche Überwachung des SNB-Leitzinses mit E-Mail-Benachrichtigung."""

import csv
import os
import smtplib
import sys
import urllib.request
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SNB_URL = "https://data.snb.ch/api/cube/snboffzisa/data/csv/de?dimSel=D0(LZ)"
EMAIL_TO = os.environ.get("EMAIL_TO")
EMAIL_FROM = os.environ.get("EMAIL_FROM", "noreply@raptus.com")
SMTP_HOST = os.environ.get("SMTP_HOST", "localhost")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "25"))


def fetch_letzte_zwei_zinsen():
    with urllib.request.urlopen(SNB_URL, timeout=30) as resp:
        text = resp.read().decode("utf-8")

    # SNB-CSV: 3 Header-Zeilen, dann ;-getrennt mit Spalten Date;Value
    lines = text.splitlines()[3:]
    reader = csv.DictReader(lines, delimiter=";", quotechar='"')
    rows = [r for r in reader if r.get("Value")]
    if len(rows) < 2:
        raise RuntimeError("SNB-CSV enthält weniger als zwei Datenzeilen")

    aktuell, vormonat = rows[-1], rows[-2]
    return (
        aktuell["Date"], float(aktuell["Value"]),
        vormonat["Date"], float(vormonat["Value"]),
    )


def baue_mail(aktuelles_datum, aktueller_zins, vormonats_datum, vormonats_zins):
    hat_geaendert = aktueller_zins != vormonats_zins
    differenz = aktueller_zins - vormonats_zins

    if hat_geaendert:
        aenderung_html = f'<span style="color: red; font-weight: bold;">ÄNDERUNG: {differenz:+.2f}%</span>'
        zins_farbe = "red"
    else:
        aenderung_html = '<span style="color: green;">Keine Änderung</span>'
        zins_farbe = "black"

    generiert = datetime.now().strftime("%d.%m.%Y %H:%M")

    html = f"""<html><body style="font-family: Arial, sans-serif;">
    <h2>SNB Leitzins Monitoring</h2>
    <table style="border-collapse: collapse; margin: 20px 0;">
        <tr>
            <td style="padding: 10px; font-weight: bold;">Aktueller Monat:</td>
            <td style="padding: 10px;">{aktuelles_datum}</td>
            <td style="padding: 10px; font-size: 18px; color: {zins_farbe}; font-weight: bold;">{aktueller_zins}%</td>
        </tr>
        <tr style="background-color: #f0f0f0;">
            <td style="padding: 10px; font-weight: bold;">Vormonat:</td>
            <td style="padding: 10px;">{vormonats_datum}</td>
            <td style="padding: 10px;">{vormonats_zins}%</td>
        </tr>
    </table>
    <p><strong>Status:</strong> {aenderung_html}</p>
    <hr style="margin: 30px 0; border: none; border-top: 1px solid #ccc;">
    <p style="font-size: 12px; color: #666;">
        Automatische Benachrichtigung | Datenquelle: SNB Data Portal<br>
        Generiert am: {generiert} Uhr
    </p>
    </body></html>"""

    text = (
        f"SNB Leitzins Monitoring\n\n"
        f"Aktueller Monat: {aktuelles_datum} - {aktueller_zins}%\n"
        f"Vormonat: {vormonats_datum} - {vormonats_zins}%\n\n"
        f"Status: {'ÄNDERUNG ERKANNT!' if hat_geaendert else 'Keine Änderung'}\n\n"
        f"---\nAutomatische Benachrichtigung | Datenquelle: SNB Data Portal\n"
        f"Generiert am: {generiert} Uhr\n"
    )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"SNB Leitzins {aktuelles_datum}: {aktueller_zins}%"
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg.attach(MIMEText(text, "plain"))
    msg.attach(MIMEText(html, "html"))
    return msg


def main():
    if not EMAIL_TO:
        raise RuntimeError("EMAIL_TO ist nicht gesetzt (Environment-Variable erforderlich)")

    aktuelles_datum, aktueller_zins, vormonats_datum, vormonats_zins = fetch_letzte_zwei_zinsen()
    msg = baue_mail(aktuelles_datum, aktueller_zins, vormonats_datum, vormonats_zins)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
        server.send_message(msg)

    print(
        f"OK: {aktuelles_datum}={aktueller_zins}% (vormonat {vormonats_datum}={vormonats_zins}%) "
        f"-> {EMAIL_TO}"
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Fehler beim SNB-Monitoring: {e}", file=sys.stderr)
        sys.exit(1)
