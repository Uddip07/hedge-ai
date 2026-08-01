# Security Policy

## 🔒 Supported Versions

Only the latest release version on the `main` branch is actively supported with security updates.

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1.0 | :x:                |

---

## 🚨 Reporting a Vulnerability

The maintainers of the **Indian AI Hedge Fund Platform** take security vulnerabilities seriously.

If you discover a security vulnerability or potential security risk in this project (e.g. secret leakage, unsafe serialization, prompt injection, or broker credential exposure):

1. **Do NOT open a public GitHub issue.**
2. Report the vulnerability privately to the project security maintainers by emailing `uddip07@users.noreply.github.com` or creating a [GitHub Private Vulnerability Report](https://github.com/Uddip07/indian-hedge-fund-ai/security/advisories/new).
3. Include the following details in your report:
   - Type of vulnerability (e.g., secret leakage, unsafe deserialization, authorization breach)
   - Detailed step-by-step instructions to reproduce the issue
   - Proof of concept payload or code snippet (if applicable)
   - Potential impact of the vulnerability

---

## 🛡️ Security Response Timeline

- **Initial Response**: Within 48 hours of receipt of the vulnerability report.
- **Triage & Status Update**: Within 5 business days detailing the planned fix.
- **Patch Release**: Released as a hotfix PR following private patch verification.

---

## 🔑 Security Principles

As mandated by `PROJECT_CONSTITUTION.md`:
1. **Zero Secret Hardcoding**: Secrets, passwords, API keys, and private keys MUST NEVER be committed to source control.
2. **Environment Configuration**: Runtime credentials must be supplied strictly via secure environment variables.
3. **Input Validation**: All external inputs (APIs, broker ticks, file uploads) must be validated before reaching domain entities.
4. **Safe Serialization**: Unsafe deserialization functions (`pickle`, `eval`) are strictly forbidden.
