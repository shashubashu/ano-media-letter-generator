# Making this live for the HR team

The tool is now a small web app (`streamlit_app.py`) instead of a script you
run yourself: pick a letter type, fill in the fields, click Generate,
download the PDF. Anyone with the link (and the password, see below) can use
it — no Python install needed on their end.

**Before you put this anywhere reachable by more than you:** these letters
carry salary, addresses and other personal data. Don't deploy this to a
public URL without at least the password gate turned on (below), and prefer
one of the private-hosting options if you can.

## 0. Try it on your own machine first

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```
Opens at `http://localhost:8501`. Confirm the flow end-to-end before
deploying anywhere.

## 1. Turn on the password gate

The app checks for a secret called `HR_PASSWORD`. Locally, create
`.streamlit/secrets.toml` (already in `.gitignore` — never commit this file):
```toml
HR_PASSWORD = "choose-a-shared-password"
```
Share that password with HR staff out of band (Slack DM, not email). This is
a *shared team password*, not individual logins — good enough to keep the
tool off search engines and casual stumbling, not a real access-control
system. See "Better access control" below if you want per-person logins.

## 2. Pick where it runs

### Option A — Streamlit Community Cloud (fastest, free)
Good for: getting this in front of HR this week, low/no ops effort.
Not good for: guaranteed data persistence (see note below), full data
privacy control (Streamlit's infra, not yours).

1. Push this folder to a **private** GitHub repo.
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in, "New app",
   point it at the repo and `streamlit_app.py`.
3. In the app's Settings → Secrets, paste the same `HR_PASSWORD = "..."` line.
4. Deploy. You get a `https://<something>.streamlit.app` URL — share that
   plus the password with HR.

**Persistence caveat:** the serial-number counter and the generation log
(`data/serial_counter.json`, `data/generation_log.csv`) live on local disk.
Community Cloud can wipe local disk on redeploy/restart. The Ref. No.
serial field is always editable by hand, so this doesn't block anyone — it
just means the auto-suggested next number might occasionally be wrong after
a redeploy and someone needs to type the correct one. If you want this to
never happen, see "Durable serial numbers" below.

### Option B — Render or Railway (recommended for real use)
Good for: an always-on private URL, a real persistent disk, still cheap
($5–7/month), your own custom domain if you want one.

1. Push the folder to GitHub (private repo is fine, these platforms support
   private repos).
2. Render: New → Web Service → connect the repo. Build command
   `pip install -r requirements.txt`, start command
   `streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0`.
   Railway: similar — it auto-detects Python and lets you set the start
   command the same way.
3. Attach a small persistent disk mounted at `/opt/render/project/src/data`
   (Render) or the equivalent volume mount (Railway) so the counter/log
   survive restarts.
4. Add `HR_PASSWORD` as an environment variable, and in `streamlit_app.py`
   change `st.secrets.get(...)` to also fall back to `os environ.get("HR_PASSWORD")`
   if you'd rather not use a `secrets.toml` on this platform.
5. Both platforms give you HTTPS automatically.

### Option C — Your own server / VPS
Good for: full control, if AnO already has a server or you want everything
on infrastructure you fully own.

1. Copy the folder to the server, `pip install -r requirements.txt` inside a
   virtualenv.
2. Run it under a process manager so it survives reboots, e.g. systemd:
   ```ini
   # /etc/systemd/system/hr-letters.service
   [Unit]
   After=network.target
   [Service]
   WorkingDirectory=/opt/hr-letters
   ExecStart=/opt/hr-letters/venv/bin/streamlit run streamlit_app.py --server.port 8501
   Restart=always
   [Install]
   WantedBy=multi-user.target
   ```
3. Put nginx (or Caddy) in front of it for HTTPS + optionally nginx's own
   `auth_basic` login as a second layer on top of the app's password gate.
4. If the server is only reachable over your office/company VPN, you can
   skip the password gate entirely and rely on network access as the
   control — simplest and often the safest option for an internal HR tool.

## 3. Durable serial numbers (optional upgrade)

If sequential Ref. No. numbering must never skip/repeat across restarts,
swap `SerialCounter` in `hr_helpers.py` for something backed by shared,
durable storage instead of a local JSON file — a Google Sheet (via
`gspread`, handy since it also gives HR a familiar place to eyeball the
running count) or a small hosted database (Supabase/Postgres, SQLite on
Render's persistent disk). The rest of the app is unaffected either way —
`SerialCounter` is the only class that would need to change.

## 4. Better access control (optional upgrade)

The shared-password gate is fine to start. If you want individual logins
(so you know *which* HR person generated a given letter, not just what they
typed into "Your name"), options in increasing effort:
- `streamlit-authenticator` (a small pip package) for named username/password
  logins stored in a config file.
- Google OAuth via `st.login()` (Streamlit's built-in auth, needs a Google
  Cloud OAuth client) restricted to `@anomedia.in`/your company domain.
- Put the whole app behind your company's existing SSO (Okta/Google
  Workspace) at the reverse-proxy level if you self-host (Option C).

## 5. Backups

`output/` fills up with every PDF ever generated, and `data/generation_log.csv`
is your audit trail. On a host with persistent disk, back both up
periodically (even a daily copy to a private Google Drive folder is fine for
a company this size).
