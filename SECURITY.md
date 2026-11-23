# Security policy

## Supported versions

Only the default branch (`main`) is supported. There are no releases or published packages.

## Reporting a vulnerability

Report it privately through GitHub: open the repository's **Security** tab and choose **Report a vulnerability** (private vulnerability reporting). Do not open a public issue for a vulnerability.

Include what you did, what you expected and what happened, and the commit you tested. The server is designed to listen on `127.0.0.1` only, to reject writes from another origin, and to never build a filesystem path from an HTTP value; reports that break those rules are the most useful. Only the scaffold exists, with no product behaviour, so reports are about the plan in `docs/PROJECT-PLAN.md` until the first tickets land.
