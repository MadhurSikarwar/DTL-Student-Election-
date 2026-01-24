# Security Policy

## Supported Versions

The following versions of the DTL Student Election project are currently supported with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

If you discover a security issue in this project, please follow these steps:

### 1. Contact the Maintainer

Send an email to **madhurrishis.is24@rvce.edu.in** (or open a private security advisory on GitHub's "Security" tab) with a clear description of the vulnerability, including:
- A brief summary of the issue.
- Steps to reproduce or a proof‑of‑concept (if safe to share).
- The affected component(s) and version(s).

### 2. Confidentiality

Do not publicly disclose the vulnerability until it has been resolved. Keep any details you share confidential and limit distribution to the project maintainers.

### 3. Response Timeline

- **Acknowledgement:** We will acknowledge receipt of your report within **2 business days**.
- **Investigation & Fix:** We aim to investigate, develop a fix, and release a patched version within **30 calendar days** for critical and high‑severity issues. Lower‑severity issues will be addressed as part of the regular release cycle.

### 4. Updates

We will keep you informed of progress at regular intervals (at least once a week) and will let you know when a fix has been deployed.

### 5. Credit (Optional)

If you wish to be credited for the discovery, let us know. We will acknowledge contributors in the release notes, unless you prefer to remain anonymous.

### 6. Disposition

- **Accepted:** If the vulnerability is confirmed, we will issue a security advisory and update the version table above.
- **Declined:** If the report is a false positive or not a security issue, we will explain the reasoning and close the report.

---

## Security Best Practices

When deploying this application:
1. Never commit `.env` or `firebase_credentials.json` to version control.
2. Use strong, unique values for `FLASK_SECRET_KEY` and `ADMIN_PRIVATE_KEY`.
3. Restrict `ALLOWED_ADMIN_EMAIL` to authorized administrators only.
4. Deploy behind HTTPS in production.
5. Regularly update dependencies to patch known vulnerabilities.

Thank you for helping keep **DTL Student Election** secure!
