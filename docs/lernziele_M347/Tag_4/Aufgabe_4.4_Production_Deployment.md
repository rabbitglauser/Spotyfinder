Aufgabe: Deployment einer Web-Applikation


Stellen Sie Ihre Applikation als öffentlich erreichbare Website bereit.

Verwenden Sie dafür einen beliebigen Cloud-Provider (z. B. Railway, wie in der Demo gezeigt => Demo https://railway.com/).


Anforderungen:

Die Applikation muss im Web öffentlich erreichbar sein.

Für das Deployment müssen dieselben Docker-Images verwendet werden wie in der Produktion.

Der Cloud-Provider kann frei gewählt werden.
Vorschlag: Railway.


Hinweis:

In realen Projekten werden häufig mehrere Dockerfiles bzw. unterschiedliche Images für Development und Produktion verwendet, zum Beispiel:

backend/Dockerfile.dev

backend/Dockerfile.production

Für diese Projektarbeit ist das nicht erforderlich.



Warum werden in der Praxis häufig separate Dockerfiles oder Images für Development und Produktion verwendet?





Erforderliche Git Commits

Git Message: "Task 4: Documentation"

Enthält nur README.md

Beschreiben Sie kurz, , welche Schritte notwendig sind, um eine lokale Änderung der Applikation auf der veröffentlichten Website zu deployen.

Fügen Sie die URLs ihrer Website hinzu.  
Beispiel:  
Backend: https://node-db-demo-production.up.railway.app/
Frontend: https://my-nginx-demo-production-2cc0.up.railway.app/


Neuer Abschnitt:

# Deployment

## Cloud deployment 