Ziel

Die Infrastruktur der Anwendung läuft containerisiert und die Datenbank enthält Testdaten.


Anforderungen / Inhalt

Es existiert eine docker-compose.yml (docker/docker-compose.yml)

Services:

database (offizielles Image, kein eigenes Dockerfile)

backend (build aus backend/)

frontend (build aus frontend/)

Datenbank:

persistentes Volume

Initialisierung über SQL-Skript (Datei: docker/init.sql)

mindestens 1 Tabelle

Testdaten

Abhängigkeiten korrekt konfiguriert
(Backend startet erst, wenn die DB verfügbar ist)
Hinweis: je nach dem, mit welchem Backend Framework ihr arbeitet, braucht das zusätzlichen Code im docker-compose.yml


Erfolgskriterium

docker compose up startet alle Container

DB läuft stabil und enthält Testdaten



Erforderliche Git Commits

Git Message: "Task 3: Compose"

Enthält nur docker/docker-compose.yml

Git Message: "Task 3: Database Seed"

Enthält nur Datenbank-Initialisierung

Enthält nur docker/init.sql

Git Message: "Task 3: Documentation Compose"

Enthält nur README.md

Neuer Abschnitt:  # Local Development with Compose

Hinweis: Den Abschnitt # Local Development aus den Aufgaben 2.1 und 2.2 könnt ihr unverändert drin lassen. Braucht es an sich nicht mehr.



Vorlage README.md



# Local Development with Compose

## Build

- `docker compose --build ..`

## Run

- `docker compose up ..` 
  