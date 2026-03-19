Ausgangslage


Die aktuelle docker-compose.yml enthält nur eine grundlegende Konfiguration der Services.

Für eine praktikable lokale Entwicklungsumgebung sollten jedoch zusätzliche Einstellungen definiert werden, z. B. für das Neustartverhalten, Abhängigkeiten zwischen Services und Umgebungsvariablen.


Ziel

Passen Sie Ihre Compose-Konfiguration so an, dass folgende Punkte erfüllt sind:



Definieren Sie eine restart-Policy für alle Services.

Verwenden Sie depends_on, um sinnvolle Abhängigkeiten zwischen den Services festzulegen.

Konfigurieren Sie Environment-Variablen über .env Dateien.

.env Dateien werden normalerweise NICHT committet. In diesem Projekt ist es Pflicht.


Zusätzliche Anforderung

Ergänzen Sie mindestens ein weiteres sinnvolles Service-Attribut aus der offiziellen Docker Compose Referenz: https://docs.docker.com/reference/compose-file/services/





Erforderliche Git Commits

Git Commit Message: Task 4: "Improve Docker Compose"

enthält nur:

docker/docker-compose.yml

.env.dev 