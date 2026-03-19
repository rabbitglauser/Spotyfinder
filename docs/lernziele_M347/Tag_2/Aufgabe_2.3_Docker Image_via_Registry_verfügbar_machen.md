Ziel

Ein eigenes Docker Image wird in ein öffentliches Container-Registry hochgeladen und kann von dort wieder heruntergeladen werden.

Für diese Aufgabe spielt es noch keine Rolle, welches Image Sie pushen.

Ausblick:  
Später müssen alle Images (Aufgaben 2.1, 2.2) auf einer Registry hochgeladen werden.  
Vorteil: so können Sie ihre Docker Images im Team schneller verteilen.
Warum schneller?



Voraussetzungen

Ein gebautes Docker-Image, z.B.: hello-world-demo

Ein Account bei Docker Hub: https://hub.docker.com/






Anleitung: Push zu Docker Hub

(1) Login im Terminal

docker login



(2) Image taggen

docker tag hello-world-demo <yourname>/hello-world-demo:latest


<yourname> durch den Docker-Hub-Username ersetzen: 




(3) Image pushen

docker push <yourname>/hello-world-demo:latest





Testing


(1) Image aus Registry ziehen

docker pull <yourname>/hello-world-demo:latest


(2) Container starten

docker run --name my-hello-world <yourname>/hello-world-demo:latest


Abgabe:  
Im README.md Link auf Registry posten.



Erforderliche Git Commits


Git Message "Task 2: Docker Registry Documentation":

Im README.md wird die Webpage ihres Docker Images dokumentiert.  
Beispiel für Webpage: https://hub.docker.com/r/lfogmxch/hello-world-demo/tags

Abschnitt # Local Development


Alternative Registries

Falls Docker Hub nicht verfügbar ist, können alternativ verwendet werden:

GitHub Container Registry (GHCR)

GitLab Container Registry

Azure Container Registry

Google Artifact Registry

Hinweis: Für alternative Registries gibt es keinen offiziellen Support.