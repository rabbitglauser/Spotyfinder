Ziel

Ein statisches Frontend wird in einem Docker-Container ausgeführt und ist über den Browser erreichbar.

Aufgabe

Ihr erstellt ein kleines Frontend (HTML/CSS, JS) und dockerisiert es so, dass es lokal im Browser aufrufbar ist.


Anforderungen

Frontend läuft in genau einem Container

Mindestens eine Seite:

index.html

CSS (extern oder inline)

Frontend ist nach dem Start über http://localhost erreichbar (Port frei wählbar)

Keine Verbindung zum Backend notwendig



Umsetzung: 2 Optionen (ihr wählt eine)

Option A – Einfach (Static Server)

Ihr verwendet einen sehr einfachen Webserver im Container (z. B. Python http.server, Node serve, …).

Vorteil: schnell, wenig Konfiguration

Nachteil: weniger „produktionsnah“

Beispiele für passende Server:

Python: python -m http.server

Node: serve -s

ähnliche Minimal-Webserver sind erlaubt



Option B - Empfohlen (Nginx)

Ihr nutzt Nginx als Webserver und liefert die statischen Dateien darüber aus.

Warum besser: Nginx ist der Standard für das Ausliefern statischer Inhalte (robust, schnell, realistisch für Deployment).





Erforderliche Git Commits


Git Message "Task 2: Frontend"

Statisches Frontend gemäss eurem Konzept aus Aufgabe 1

Beliebig viele Dateien, im Ordner /frontend/src

Git Message "Task 2: Frontend Dockerfile":

Enthält nur Dockerfile, im Ordner /frontend/

Git Message "Task 2: Documentation":

Enthält nur README.md

Gemäss Vorlage, korrekte Commands und vollständige localhost URLs angeben



Vorlage README.md



# Local Development

## Build

- Backend: `docker build ..`

- Frontend: `docker build ..`

## Run

- Backend: `docker run ..`

  Open in Browser: localhost

- Frontend: `docker run ..`

  Open in Browser: localhost   

 