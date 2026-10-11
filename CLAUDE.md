# Radio Geburtstag

Baukasten für personalisierte Geburtstags-Radiobeiträge: Nachrichten vom Tag der Geburt als Sprechtext, vertont in Google AI Studio, ausgeliefert als Mini-Landingpage mit Player (GitHub Pages, Link oder QR-Code).

## Ablauf für eine neue Person

1. **Eingaben erfragen** (falls nicht genannt): Vorname, Geburtsdatum, Präferenzen/Hobbys, Name des Schenkenden.
2. **Ordner anlegen**: `personen/<vorname>/meta.json`
   ```json
   {"vorname": "Hubert", "geburtsdatum": "1978-10-14", "praeferenzen": ["Fußball"], "von": "Dominic"}
   ```
3. **Recherche** zum Geburtstag (Regeln unten), danach **Sprechtext** nach `personen/<vorname>/sprechtext.txt` schreiben.
4. **Dominic vertont** den Text in Google AI Studio und legt die MP3 oder WAV in `personen/<vorname>/` ab (oder lädt sie im Chat hoch).
5. **Bauen**: `python3 bauen.py <vorname>` erzeugt `docs/<slug>/` (Seite + `radio.mp3`) und, wenn in `projekt.json` eine `basis_url` steht, `personen/<vorname>/qr.svg` und `qr.png`.
6. **Veröffentlichen**: `docs/` committen und pushen, GitHub Pages auf den Ordner `/docs` des Branches stellen.

Der `slug` (Ordnername im Link) wird beim ersten Bau zufällig erzeugt und in `meta.json` gespeichert. Er bleibt bei Neubauten gleich, damit verschickte Links gültig bleiben.

## Regeln für die Recherche

- Jede Tatsache im Sprechtext muss mit einer Quelle belegt sein, die das **konkrete Datum** nennt. Undatierte Monatsübersichten (zum Beispiel Wikipedia „Oktober 1978“) reichen nicht. Das Datum über eine zweite Quelle gegenprüfen.
- Sport nach Präferenz: Spieltag, Ergebnisse, Torschützen, Zuschauer aus dem DFB-Datencenter (`datencenter.dfb.de`) oder vergleichbaren Archiven. **Achtung:** Die „Blitztabelle“-Seiten von sportschau.de zeigen die Endtabelle der Saison, nicht den Stand am Spieltag.
- Charts: Vor September 1978 erschienen die deutschen Charts nur zweimal im Monat (1. und 15.), danach wöchentlich. Passende Ausgabe zum Datum nehmen und nicht pauschal „Nummer 1 am Tag“ behaupten.
- Preise nur als Jahresdurchschnitt nennen und so benennen (zum Beispiel Superbenzin).
- Wetter nur, wenn eine Quelle zum Tag vorliegt. Sonst ehrlich als unbekannt lassen und als Pointe nutzen.
- Blick in die Zukunft („Er wird später …“) ist erlaubt und wirkt gut, muss aber ebenso belegt sein.
- Keine Liedtexte, keine längeren Zitate aus Artikeln.

## Regeln für den Sprechtext

- Länge: etwa 350 bis 450 Wörter, das sind zwei bis drei Minuten.
- Aufbau: Begrüßung mit Vornamen und Datum, Sport (Präferenz), Musik, Preise und Politik, Weltnachrichten, Wetter, Schluss mit Glückwunsch und „Ein Geschenk von …“.
- Fürs Vorlesen schreiben: Zahlen und Jahreszahlen als Wörter („neunzehnhundertachtundsiebzig“), Spielstände als „vier zu eins“, keine Klammern, keine Abkürzungen, kurze Sätze.
- Absätze durch Leerzeilen trennen. Daraus macht `bauen.py` die lesbare Textfassung auf der Seite.
- Ton: warm, mit leichtem Schmunzeln, wie ein Radiosprecher der Zeit. Nur Fakten, die belegt sind.

## Hinweis zum Vertonen (Google AI Studio)

Stil-Anweisung zum Mitgeben: „Sprich wie ein erfahrener Radiosprecher der Siebzigerjahre: warm, souverän, ruhiges Tempo, bei den Pointen mit hörbarem Schmunzeln.“ Eine ruhige, tiefere Stimme passt gut. Vor dem Bauen einmal komplett anhören und Aussprache von Namen prüfen.

## Datenschutz

- Die Seite enthält Vorname und Geburtsdatum der Person. In einem öffentlichen Repository ist sie für jeden erreichbar, der den Link kennt. Deshalb: zufälliger `slug`, `noindex` auf der Seite, und `personen/` steht in `.gitignore`, damit Rohdaten nicht ins Repo wandern.
- Vor dem Veröffentlichen kurz abwägen, ob die Person damit einverstanden wäre.

## Technik

- `vorlage/index.html`: Seite mit Platzhaltern (`{{NAME}}`), eine Datei ohne externe Abhängigkeiten und ohne Schriften von Drittservern. Die Skala zeigt die Jahre, die Nadel steht auf dem Tag der Geburt.
- `bauen.py`: füllt die Vorlage, wandelt Audio mit ffmpeg in eine schlanke Mono-MP3 um, erzeugt QR-Codes mit `segno` (`pip install segno`).
