# Outlook setup

1. entra.microsoft.com: App registrations, new, accounts in any org directory + personal accounts.
2. Authentication: enable **public client / device code flow**.
3. API permissions (delegated): `Mail.Read`, `Mail.ReadWrite`. Do **not** add `Mail.Send`.
4. `set MS_CLIENT_ID=<application id>` then `draftbox login-outlook`.
5. Work/school accounts may need admin consent.
