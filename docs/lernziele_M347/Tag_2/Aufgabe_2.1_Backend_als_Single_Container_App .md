Ziel

Ein einfaches Backend wird in einem Docker-Container ausgeführt und ist über den Browser erreichbar.

  

Aufgabe

Ihr dockerisiert ein kleines Backend (z. B. Node.js, Python oder Java).

Anforderungen

Backend läuft in genau einem Container

Mindestens ein HTTP-Endpoint, z. B.: GET /api/hello → "Hello World" oder JSON-Ausgabe

Backend ist nach dem Start über http://localhost erreichbar

  

Was ihr dafür braucht

1. Ein Backend

Beispiel:

Node.js (Express)

Python (Flask)

Java (Spring Boot)

  

2. Ein Dockerfile

Das Dockerfile beschreibt:

welches Basis-Image verwendet wird

wie der Code in den Container kommt

wie das Backend gestartet wird

  

3. Image bauen

  

docker build -t backend-demo .

erstellt ein Docker-Image

backend-demo = Name des Images

  

4. Container starten

  

docker run -p 3000:3000 backend-demo

startet einen Container aus dem Image

-p verbindet Container-Port → localhost-Port

  

Ergebnis (Erfolgskriterium)

Container läuft

Browser oder curl liefert eine Antwort:

  

Beispiel: http://localhost:3000/api/hello



  

Ablage in Git:

Legt eure Dateien genau so ab:

  

backend/

├─ Dockerfile

├─ src/                (Source Code fürs Backend)



Erstellen Sie anschliessend eine Anleitung wie Sie ihren Docker Container starten im README.md und testen Sie die Anleitung in ihrer Gruppe.  
Ziel: Alle Gruppenmitglieder können den Backend Container auf ihrem Computer starten.





Erforderliche Git Commits


Git Message "Task 2: Backend"

1-4 Endpoints gemäss ihrem Konzept aus Aufgabe 1.

Beliebig viele Dateien, im Ordner /backend/src

Git Message "Task 2: Backend Dockerfile":

Enthält nur Dockerfile, im Ordner /backend

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

 