#!/usr/bin/env python3
"""Baut aus personen/<name>/ eine fertige Mini-Landingpage in docs/<slug>/.

Aufruf:   python3 bauen.py hubert
Benötigt: personen/<name>/meta.json, sprechtext.txt und eine Audiodatei (mp3, wav, m4a oder ogg).
Ergebnis: docs/<slug>/index.html + radio.mp3 (für GitHub Pages) und, wenn projekt.json
          eine basis_url enthält, personen/<name>/qr.svg und qr.png.
"""
import argparse
import html
import json
import secrets
import shutil
import string
import subprocess
import sys
from datetime import date
from pathlib import Path

WOCHENTAGE = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
MONATE = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August",
          "September", "Oktober", "November", "Dezember"]
AUDIO_ENDUNGEN = (".mp3", ".wav", ".m4a", ".ogg")


def fehler(text):
    print(f"Fehler: {text}", file=sys.stderr)
    sys.exit(1)


def lade_json(pfad):
    try:
        return json.loads(pfad.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fehler(f"{pfad} fehlt.")
    except json.JSONDecodeError as e:
        fehler(f"{pfad} ist kein gültiges JSON: {e}")


def js_string(wert):
    """JSON-String, der sicher in ein <script> eingebettet werden kann."""
    return json.dumps(wert, ensure_ascii=False).replace("</", "<\\/")


def finde_audio(ordner):
    kandidaten = sorted(p for p in ordner.iterdir() if p.suffix.lower() in AUDIO_ENDUNGEN)
    if not kandidaten:
        fehler(f"Keine Audiodatei in {ordner} gefunden (erlaubt: {', '.join(AUDIO_ENDUNGEN)}).")
    # Bei mehreren Dateien gewinnt die zuletzt geänderte.
    return max(kandidaten, key=lambda p: p.stat().st_mtime)


def audio_nach_mp3(quelle, ziel):
    """WAV & Co. werden zu einer schlanken Mono-MP3 (Sprache) umgewandelt, wenn ffmpeg da ist."""
    if quelle.suffix.lower() == ".mp3":
        shutil.copyfile(quelle, ziel)
        return "unverändert kopiert"
    if shutil.which("ffmpeg"):
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(quelle),
               "-ac", "1", "-codec:a", "libmp3lame", "-b:a", "96k", str(ziel)]
        if subprocess.run(cmd).returncode == 0:
            return "mit ffmpeg zu MP3 (mono, 96 kbit/s) umgewandelt"
        fehler("ffmpeg konnte die Audiodatei nicht umwandeln.")
    # Ohne ffmpeg: Originalformat behalten, Endung anpassen.
    return None


def neuer_slug(vorname):
    rein = "".join(c for c in vorname.lower() if c.isalnum()) or "radio"
    zufall = "".join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(6))
    return f"{rein}-{zufall}"


def sprechtext_html(text):
    absaetze = [a.strip() for a in text.replace("\r\n", "\n").split("\n\n") if a.strip()]
    return "\n".join(f"      <p>{html.escape(a)}</p>" for a in absaetze)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("person", help="Ordnername unter personen/, z. B. hubert")
    ap.add_argument("--basis-url", help="überschreibt basis_url aus projekt.json")
    args = ap.parse_args()

    wurzel = Path(__file__).resolve().parent
    ordner = wurzel / "personen" / args.person
    if not ordner.is_dir():
        fehler(f"{ordner} existiert nicht.")

    meta_pfad = ordner / "meta.json"
    meta = lade_json(meta_pfad)
    projekt = lade_json(wurzel / "projekt.json") if (wurzel / "projekt.json").exists() else {}

    for pflicht in ("vorname", "geburtsdatum"):
        if not meta.get(pflicht):
            fehler(f"'{pflicht}' fehlt in {meta_pfad}.")
    try:
        geb = date.fromisoformat(meta["geburtsdatum"])
    except ValueError:
        fehler("'geburtsdatum' muss das Format JJJJ-MM-TT haben, z. B. 1978-10-14.")

    text_pfad = ordner / "sprechtext.txt"
    if not text_pfad.exists():
        fehler(f"{text_pfad} fehlt.")
    sprechtext = text_pfad.read_text(encoding="utf-8")

    audio_quelle = finde_audio(ordner)

    # Der Slug bleibt stabil, damit ein verschickter Link/QR-Code nach einem Neubau weiter gilt.
    slug = meta.get("slug")
    if not slug:
        slug = neuer_slug(meta["vorname"])
        meta["slug"] = slug
        meta_pfad.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    vorname = meta["vorname"]
    von = meta.get("von", "").strip()
    wochentag = WOCHENTAGE[geb.weekday()]
    datum_lang = f"{geb.day}. {MONATE[geb.month - 1]} {geb.year}"
    tage_im_jahr = 366 if (geb.year % 4 == 0 and (geb.year % 100 != 0 or geb.year % 400 == 0)) else 365
    jahresanteil = (geb.timetuple().tm_yday - 1) / tage_im_jahr

    ausgabe = wurzel / "docs" / slug
    ausgabe.mkdir(parents=True, exist_ok=True)

    audio_name = "radio.mp3"
    notiz = audio_nach_mp3(audio_quelle, ausgabe / audio_name)
    if notiz is None:  # kein ffmpeg, kein MP3
        audio_name = "radio" + audio_quelle.suffix.lower()
        shutil.copyfile(audio_quelle, ausgabe / audio_name)
        notiz = "ohne Umwandlung kopiert (ffmpeg nicht gefunden, Datei kann groß sein)"

    titel = f"Radio {vorname}"
    ersetzungen = {
        "TITEL": html.escape(titel),
        "SENDER": html.escape(titel),
        "BESCHREIBUNG": html.escape(f"Die Nachrichten vom {datum_lang}, nur für {vorname}."),
        "WOCHENTAG": html.escape(wochentag),
        "DATUM_LANG": html.escape(datum_lang),
        "DATUM_KURZ": f"{geb.day}.{geb.month}.{geb.year}",
        "JAHR": str(geb.year),
        "JAHRESANTEIL": f"{jahresanteil:.4f}",
        "UNTERTITEL": html.escape(meta.get("untertitel") or "Die Nachrichten von dem Tag, an dem du geboren wurdest."),
        "AUDIO": audio_name,
        "SPRECHTEXT": sprechtext_html(sprechtext),
        "GESCHENK": html.escape(f"Ein Geschenk von {von}." if von else "Ein Geschenk."),
        "HINWEIS": html.escape(meta.get("hinweis") or "Die Stimme ist KI-generiert, die Fakten stammen aus öffentlichen Quellen."),
        "MEDIA_TITEL_JSON": js_string(titel),
        "MEDIA_KUENSTLER_JSON": js_string(f"Ein Geschenk von {von}" if von else "Ein Geschenk"),
    }

    seite = (wurzel / "vorlage" / "index.html").read_text(encoding="utf-8")
    for schluessel, wert in ersetzungen.items():
        seite = seite.replace("{{" + schluessel + "}}", wert)
    if "{{" in seite:
        fehler("In der Vorlage ist ein Platzhalter übrig geblieben.")
    (ausgabe / "index.html").write_text(seite, encoding="utf-8")

    # Neutrale Startseite, damit docs/ nichts über die Personen verrät; Jekyll aus.
    docs = wurzel / "docs"
    (docs / ".nojekyll").touch()
    start = docs / "index.html"
    if not start.exists():
        start.write_text('<!doctype html><meta charset="utf-8"><meta name="robots" content="noindex">'
                         "<title>Radio</title>\n", encoding="utf-8")

    print(f"Seite:  {ausgabe / 'index.html'}")
    print(f"Audio:  {ausgabe / audio_name} ({notiz}, {(ausgabe / audio_name).stat().st_size / 1e6:.1f} MB)")

    basis = (args.basis_url or projekt.get("basis_url") or "").rstrip("/")
    if basis:
        link = f"{basis}/{slug}/"
        import segno
        qr = segno.make(link, error="m")
        qr.save(ordner / "qr.svg", scale=10, border=4)
        qr.save(ordner / "qr.png", scale=12, border=4)
        print(f"Link:   {link}")
        print(f"QR:     {ordner / 'qr.svg'} und qr.png")
    else:
        print("Link:   noch offen. Trage in projekt.json die basis_url ein, z. B.")
        print('        {"basis_url": "https://DEIN-GITHUB-NAME.github.io/DEIN-REPO/"} und starte den Bau erneut.')


if __name__ == "__main__":
    main()
