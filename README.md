<h1 align="center">
  <img src="https://github.com/user-attachments/assets/b463580a-e199-4e4d-8fb1-075991fa46e0" width="200px" alt="logo">
  <p>Spotyfinder</p>
</h1>


Spotifinder helps everyone find better Spotify recommendations than Spotify itself by using an algorithm and machine learning.

---

## technologies
- database: MySQL Lite 
- backend: python
- frontend: React, TypeScript, tailwind and next js

 ---

 ## Links!
 - chatGPT context(https://chatgpt.com/share/699ec2be-a860-8012-ab46-2b494bf7e957)
 - Figma docs/frontend_mockup
 - ERD diagram https://dbdiagram.io/home
 - Notion https://www.notion.so/Project-31119db87e2b80e19b4afe2d9371ae73
 - Exportify https://exportify.net/

## How to start the project using Docker

From the repo root:

DEV
```
docker compose -f docker/compose.dev.yml up --build
```
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
  
PROD
```
docker compose -f docker/compose.prod.yml up --build
```
- Website: http://localhost:8080

start container
```
docker compose -f docker/compose.dev.yml up
```

stop container
```
docker compose -f docker/compose.dev.yml down
```


If Port 3000 is already used, use following command in POWERSHELL to find the process using port 3000 and KILL IT:
```Powershell
Stop-Process -Id (Get-NetTCPConnection -LocalPort 3000 -State Listen).OwningProcess -Force
```
