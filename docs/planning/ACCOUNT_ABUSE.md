# Signup, login, and email transition

## Local pilot limits

Each signup POST consumes one of eight attempts per client address and one of 100 sitewide attempts in a 15-minute window. Each login POST consumes one of 30 attempts per address and 12 per submitted public name in the same window. A blocked request gets HTTP 429, a generic retry message, and `Retry-After`; the application does not validate the submitted password or create an account for that request. These limits apply to successful attempts too, to prevent concurrent submissions from escaping the count. They can temporarily slow a shared network or a frequently used account; the sitewide cap is deliberately modest for the local pilot and must be reviewed before public launch.

The counters live in PostgreSQL. Each bucket is serialized with a transaction-scoped advisory lock, including its first insert, so multiple web workers share the same count. Database keys are HMACs using `DJANGO_SECRET_KEY`; raw addresses and submitted names are not stored in the bucket table. The secret must stay private. Rotating it resets effective limits.

Run `python manage.py prune_auth_attempts` at least daily once deployed. It deletes buckets after their 15-minute window expires. Until a scheduled job exists, records remain in the database beyond expiry, although they no longer count against requests. The command is manual in the local pilot. Do not log raw submitted names or client addresses for this feature.

## Client addresses behind Cloudflared

By default, the app uses the direct `REMOTE_ADDR` and ignores forwarded address headers. On the intended VPS, configure a stable, private direct peer for Cloudflared or a reverse proxy, then put only that peer's exact IP in `TRUSTED_PROXY_IPS` (comma-separated). Only from that peer does the app use a valid single `CF-Connecting-IP` address. Do not add public client ranges or trust `X-Forwarded-For`. Restrict origin access to the trusted peer. Verify this path with real deployment networking before public signup; if all requests arrive with one address, the per-address limit will affect everyone.

## Verified email decision

Email remains optional during the local pilot. A typed address alone is not proof of control and does not prevent signup spam. The public-launch decision is to require verified email for **new** accounts, once outbound delivery, one-use expiring verification tokens, bounce handling, recovery, and resend limits are built and tested. Existing accounts with blank email may continue to sign in, host, and join outings during a notified transition period; prompt them to add and verify an address, without fabricating one or suddenly locking them out. Any later restriction on those accounts requires a separate product decision and advance notice. Tighten stored-data constraints only after migration metrics show the transition is complete. Password recovery remains unavailable until this flow exists.
