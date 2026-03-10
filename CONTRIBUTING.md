# Contributing to Spotyfinder

Thank you for your interest in contributing to Spotyfinder! This document explains how to set up a development environment and contribute code. For a general project overview and Docker usage, see the [README](README.md).

---

## Table of Contents

- [Getting Started](#getting-started)
- [Branching Strategy](#branching-strategy)
- [Making Changes](#making-changes)
- [Pull Request Process](#pull-request-process)
- [Code Style](#code-style)
- [Reporting Issues](#reporting-issues)

---

## Getting Started

1. **Fork** the repository on GitHub.
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/<your-username>/Spotyfinder.git
   cd Spotyfinder
   ```
3. Set the upstream remote so you can pull in future updates:
   ```bash
   git remote add upstream https://github.com/rabbitglauser/Spotyfinder.git
   ```
4. Start the dev environment as described in the [README](README.md) and confirm the app runs before making any changes.

---

## Branching Strategy

- Always create a new branch from the latest `main`:
  ```bash
  git checkout main
  git pull upstream main
  git checkout -b feature/your-feature-name
  ```
- Use descriptive branch names that reflect the work being done:
  - `feature/add-recommendation-engine`
  - `fix/login-redirect-bug`
  - `docs/update-readme`
- **Never** commit directly to `main`.

---

## Making Changes

1. Make your changes in small, focused commits.
2. Write clear commit messages that describe *what* and *why*:
   ```
   feat: add song similarity scoring algorithm
   fix: correct API endpoint for playlist fetch
   docs: clarify setup steps in README
   ```
3. Run linting and tests before pushing:
   - **Backend:**
     ```bash
     cd backend
     pip install -r requirements-test.txt
     pytest
     ```
   - **Frontend:**
     ```bash
     cd frontend
     pnpm lint
     ```

---

## Pull Request Process

1. Push your branch to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
2. Open a **Pull Request** against the `main` branch of the upstream repository.
3. Fill in the PR description explaining:
   - What the change does
   - Why it is needed
   - Any relevant screenshots or test output
4. Request a review from at least one team member.
5. Address any review feedback before merging.
6. PRs are merged only after approval — do not merge your own PR without a review.

---

## Code Style

### Frontend (TypeScript / React)

- Follow the existing ESLint configuration (`eslint.config.mjs`).
- Use **TypeScript** types; avoid `any`.
- Use **Tailwind CSS** utility classes for styling.
- Keep components small and single-purpose.

### Backend (Python)

- Follow [PEP 8](https://peps.python.org/pep-0008/) conventions.
- Use type hints for all function signatures.
- Keep route handlers thin — put business logic in separate modules.

---

## Reporting Issues

- Use GitHub Issues to report bugs or request features.
- Check existing issues first to avoid duplicates.
- Include steps to reproduce, expected behavior, and actual behavior when reporting a bug.

---

We appreciate every contribution, big or small. Happy coding! 🎵
