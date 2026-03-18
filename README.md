<h1 align="center">
  <img src="https://github.com/user-attachments/assets/b3ec80d2-1758-48ee-aa55-fa262de131ec" width="200px" alt="logo">
  <p>Spotyfinder</p>
</h1>


Spotyfinder helps users discover better Spotify recommendations through a custom algorithm and machine learning.

---

## Website

[![Live Demo](https://img.shields.io/badge/Live-Demo-brightgreen?style=for-the-badge)](https://spotyfinder.netlify.app/)

## Technologies

- <img src="https://skillicons.dev/icons?i=react" alt="React" height="40" /> **Frontend:** React, TypeScript, Tailwind CSS, Next.js
- <img src="https://skillicons.dev/icons?i=py" alt="Python" height="40" /> **Backend:** Python
- <img src="https://skillicons.dev/icons?i=sqlite" alt="SQLite" height="40" /> **Database:** SQLite

 ---

## Project Links

[![ChatGPT Context](https://img.shields.io/badge/ChatGPT-Context-74aa9c?style=for-the-badge&logo=openai&logoColor=white)](https://chatgpt.com/share/699ec2be-a860-8012-ab46-2b494bf7e957)
[![Figma Mockup](https://img.shields.io/badge/Figma-Mockup-F24E1E?style=for-the-badge&logo=figma&logoColor=white)](https://github.com/rabbitglauser/Spotyfinder/tree/main/docs/Frontend_mockup)
[![ERD Diagram](https://img.shields.io/badge/ERD-Database_Diagram-0ea5e9?style=for-the-badge&logo=databricks&logoColor=white)](https://dbdiagram.io/home)
[![Notion](https://img.shields.io/badge/Notion-Project_Page-000000?style=for-the-badge&logo=notion&logoColor=white)](https://www.notion.so/Project-31119db87e2b80e19b4afe2d9371ae73)
[![Exportify](https://img.shields.io/badge/Exportify-Open-1DB954?style=for-the-badge&logo=spotify&logoColor=white)](https://exportify.net/)
## How to get started using Docker :)

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
