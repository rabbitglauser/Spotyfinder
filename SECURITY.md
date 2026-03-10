# Security Policy

## Supported Versions

The following versions of Spotyfinder are currently supported with security updates:

| Version | Supported          |
| ------- | ------------------ |
| latest (main branch) | ✅ Yes |
| older branches       | ❌ No  |

## Reporting a Vulnerability

If you discover a security vulnerability in Spotyfinder, please **do not** open a public GitHub issue. Instead, report it responsibly by following these steps:

1. **Open a [GitHub Security Advisory](https://github.com/rabbitglauser/Spotyfinder/security/advisories/new)** — this allows you to report the vulnerability privately.
2. Provide a clear description of the vulnerability, including:
   - Steps to reproduce
   - Potential impact
   - Any suggested fix (optional but appreciated)

## Response Timeline

- **Acknowledgement:** Within 3 business days of receiving your report.
- **Assessment:** Within 7 business days we will assess the severity and impact.
- **Resolution:** We aim to release a fix within 30 days for critical vulnerabilities.

## Security Best Practices for Contributors

When contributing to Spotyfinder, please follow these security guidelines:

- Never commit secrets, API keys, or credentials to the repository.
- Sanitize all user inputs on both the frontend and backend.
- Keep dependencies up to date and review security advisories.
- Use parameterized queries or ORM methods to prevent SQL injection.
- Follow the principle of least privilege when handling data.

## Data & Privacy

Spotyfinder uses the Spotify API to provide music recommendations. We do not store your Spotify credentials. Any data processed is used solely to generate recommendations and is not shared with third parties.

For more information, see the [README](./README.md).
