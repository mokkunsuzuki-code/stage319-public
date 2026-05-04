# REMEDA Stage319

AI vulnerabilities → Verification → Proof URL

REMEDA converts AI-detected vulnerabilities into verifiable, reproducible proof.

## What you can do

- Generate API keys
- Submit AI vulnerability results
- Get verification decisions
- Generate proof URLs
- Measure trust score

## Live API

https://stage302.onrender.com/api/health

## Example

```bash
curl -X POST https://stage302.onrender.com/api/keys

curl -X POST https://stage302.onrender.com/api/verify \
  -H "x-api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"ai_result":"SQL Injection detected","confidence":0.92}'
Flow

AI vulnerability result
→ API key
→ Verification
→ Proof JSON
→ Proof URL

Why this matters

AI outputs are not trustworthy by default.

REMEDA makes them:

Verifiable
Reproducible
Measurable
Architecture

Public Layer (this repo)
→ Core API (private)
→ Proof URL

Stage

319 Public

License

MIT License (c) 2025 Motohiro Suzuki