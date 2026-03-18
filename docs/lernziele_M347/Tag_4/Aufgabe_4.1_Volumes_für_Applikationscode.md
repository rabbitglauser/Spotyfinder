Ausgangslage

Bisher wird der Anwendungscode beim Bauen des Images mit COPY . . in den Container übernommen.


Das hat in der lokalen Entwicklung einen Nachteil:

Bei jeder Änderung am Code müssen Sie das Image neu bauen und den Container neu erstellen.


Das ist für die Entwicklung unpraktisch.


Ziel

Richten Sie die Container so ein, dass der Anwendungscode in der lokalen Entwicklung per Volume in den Container gemountet wird.

Achten Sie darauf, dass die Images weiterhin korrekt gebuildet werden können.

Development mit Volume-Mount

Passen Sie Ihre Compose-Konfiguration für die lokale Entwicklung so an, dass:

der Anwendungscode vom Host in den Container gemountet wird

Änderungen am Code ohne Neubau des Images wirksam werden

die Anwendung weiterhin korrekt startet


Verwenden Sie dafür Volumes.



Erforderliche Git Commits

Git Message: "Task 4: Code Volumes"

Enthält nur docker/docker-compose.yml 

 