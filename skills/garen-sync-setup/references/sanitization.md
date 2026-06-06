# Sanitization — mandatory before writing/sharing memories

Memories live in a private synced repo but get **pasted into web LLMs** (Gemini/ChatGPT/Claude.ai),
so treat them as if they could leak. Redact before writing `6-integrated/memories.md`.

## Redact (never include the actual value)

| Category | Examples | Rule |
|----------|----------|------|
| Device serial numbers | S/N, IMEI, motherboard/SSD serials | Drop entirely |
| Public / routable IPs | WAN IP, any non-RFC1918 IPv4/IPv6 | Drop or replace with role ("home WAN") |
| MAC addresses | `aa:bb:cc:dd:ee:ff` | Drop entirely |
| Secrets | API keys, tokens, `BOT_TOKEN` values, passwords, SOPS/age keys | Drop the value; may keep "uses a BOT_TOKEN" as a fact |
| Personal IDs of others | real Telegram chat/user IDs, phone numbers, full names of private contacts | Redact to a role/alias (e.g. "primary userbot", "contact A") |
| Exact street address / unit | full postal address | Keep only city-level ("Tokyo apartment") |

## Keep (useful, low-risk)

- Hardware models & capacities (CPU/GPU/RAM/SSD models, NAS model).
- Private LAN topology at the **role** level (e.g. "OpenWRT is the router, PVE on the 192.168.1.x LAN").
  RFC1918 addresses are non-routable; in a private repo they're acceptable, but **generalize host
  enumeration** (prefer "PVE and OpenWRT on 192.168.1.x" over listing every host's last octet) unless
  the user asks to keep specifics.
- Architecture decisions, service names, roles, software versions.

## Verification grep battery

Run all of these against the final `memories.md`. Each should report CLEAN / no matches
(except the keyword check, which may legitimately match a redacted-value mention like "uses a BOT_TOKEN").

```bash
cd ~/sync-setup/6-integrated

# Public (non-RFC1918) IPv4 — must be none
grep -nE '\b([0-9]{1,3}\.){3}[0-9]{1,3}\b' memories.md \
  | grep -vE '192\.168\.|10\.|172\.(1[6-9]|2[0-9]|3[01])\.' || echo "CLEAN: no public IPs"

# MAC addresses — must be none
grep -nE '([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}' memories.md || echo "CLEAN: no MACs"

# Secret/serial keywords — review each hit; values must be absent
grep -niE 'serial|s/n|imei|token|api[_-]?key|password|secret|age1[a-z0-9]' memories.md \
  || echo "CLEAN: no secret keywords"

# Long digit runs that look like phone numbers / chat IDs — review each hit
grep -nE '[0-9]{9,}' memories.md || echo "CLEAN: no long numeric IDs"
```

## If a hit is found

Don't silently delete user data. Surface it: quote the line, say why it's flagged, and ask whether to
redact, generalize, or keep. Pre-existing leaks (already in memories from earlier rounds) count too —
flag them even if this run didn't introduce them.
