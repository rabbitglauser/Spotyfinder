Ausgangslage und Ziel
In produktiven Umgebungen (Cloud Provider) können Sie docker-compose.yml nicht verwenden.  
Das Ziel ist, dass ihre eigenen Docker Images  (Frontend, Backend) auf einer Registry verfügbar sind, am besten so, dass Sie die Aktualisierung der Images möglichst automatisieren können.

(1) Builden und Publishen
Publishen Sie ihre beiden Docker Images (Frontend, Backend) auf DockerHub.  
Machen Sie dies einmalig, und testen Sie, ob es funktioniert.  
Erstellen Sie dann ein Script (z.B. build-and-push.sh), das beide Images buildet und published. Muss kein Bash Script sein, Make File oder etwas ähnliches geht auch.


(2) Automatisierung mit GitLab
Automatisierung via GitLab Pipeline:  
Immer wenn in den main branch gepusht wird, werden die Images erstellt und published.  
Hinweis: wenn das zu schwierig ist, können Sie diesen Schritt auslassen.




Erforderliche Git Commits

Git Message: "Task 4: Build and publish images"

Enthält eine Datei (z.B. build-and-push.sh)

Git Message: "Task 4: GitLab Pipeline"

Enthält nur.gitlab-ci.yml

Git Message: "Task 4: Documentation"

Enthält nur README.md

Beschreiben Sie kurz, wie in ihrem Projekt ihre Images auf DockerHub aktualisiert werden.

Neuer Abschnitt:

# Deployment

## Build and publish images 