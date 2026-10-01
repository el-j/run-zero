# GitHub Actions Billing Panel Setup HOWTO

This guide configures the RunZero dashboard's Actions minutes panel so it can read real usage from GitHub billing APIs.

## 1. Choose Your Billing Scope

- Personal account tracking: set `OWNER=<your-username>` and keep `ORG=` empty.
- Organization tracking: set `ORG=<your-org>`.

RunZero uses these endpoints:

- Personal owner mode: `GET /users/{owner}/settings/billing/actions`
- Organization mode: `GET /orgs/{org}/settings/billing/actions`

## 2. Create a Token with Correct Permissions

Use a Personal Access Token and place it in `.env` as `ACCESS_TOKEN=...`.

Minimum practical access:

- Required for runner lifecycle and queue discovery:
- Classic PAT: `repo` (plus org administration scope when managing org runners).
- Required for Actions minutes panel:
- Token must be allowed to read billing for the target account/org.

If billing access is missing, the panel intentionally shows an error status instead of fake numbers.

## 3. Update .env

```env
ACCESS_TOKEN=ghp_xxx
OWNER=your-username
# ORG=your-org-name

# Optional: refresh cadence for minutes panel in seconds
ACTIONS_BILLING_REFRESH_INTERVAL=300
```

## 4. Restart and Verify

```bash
docker compose build autoscaler
make restart
```

Open dashboard: `http://localhost:49505`

Check panel: `GitHub Actions Minutes`

- `Billing synced from GitHub.` means permissions are correct.
- If it shows `Billing unavailable`, update token permissions and restart.

## 5. API-level Verification (Optional)

```bash
curl -sS http://localhost:49505/api/status | python3 -c 'import sys, json; d=json.load(sys.stdin); print(json.dumps(d.get("github", {}).get("actions_billing", {}), indent=2))'
```

Expected fields when successful:

- `scope_type`
- `scope_name`
- `included_minutes`
- `total_minutes_used`
- `total_paid_minutes_used`
- `minutes_remaining`
- `status: ok`
