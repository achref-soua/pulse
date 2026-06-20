# Security Policy

## Supported Versions

Only the latest release receives security fixes.

| Version | Supported |
|---------|-----------|
| Latest  | ✓         |
| Older   | ✗         |

## Reporting a Vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Email **achref.soua@outlook.com** with:

- A clear description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested remediation (if any)

You will receive an acknowledgement within 72 hours. Confirmed vulnerabilities
will be addressed and released as a patch version within 14 days for critical
issues, or included in the next scheduled release for lower-severity issues.

We ask that you follow responsible disclosure and give us reasonable time to
address the issue before any public disclosure.

## Scope

This is an educational/demo platform on **synthetic data** and is not intended
for production clinical use. However, security vulnerabilities in the
authentication, RBAC, data isolation, or API layers are in scope.

## Out of Scope

- Vulnerabilities requiring physical access to the deployment machine
- Social engineering attacks
- Issues in third-party dependencies (report those upstream)
