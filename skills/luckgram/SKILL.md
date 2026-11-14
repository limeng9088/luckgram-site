---
name: luckgram
description: Work with the Telegram accounts in Luckgram Desktop through its MCP server, local or cloud: accounts, friends, chats, messages, groups, profile, bots via BotFather. Tokens stay masked.
---

# Luckgram

> **Command:** `luckgram`. It talks to the MCP server built into Luckgram Desktop — on this computer, or on every computer of a cloud key through `mcp.luckgram.cc`.
> The access token and the cloud key are stored in `~/cicy-ai/db/luckgram.json` (0600) and never printed.

## Scope

Use this skill when the user asks to do something with their Telegram accounts in Luckgram: see which accounts are logged in, switch the active one, look at friends, chats or messages, send a message, add or remove a friend, join or leave a group, change a name or bio, create or configure a bot with @BotFather.

Do not use it for Telegram bots, for the Telegram Web matrix (`telegram-matrix`), or for bulk messaging — there is no bulk command, by design.

## Security: hard rules

- **Never read, cat, grep or print** `~/cicy-ai/db/luckgram.json`. `luckgram status` shows the token masked — trust it.
- **Never put a token on a command line.** `luckgram config` takes it from stdin only (`--token-stdin`). Do not ask the user to paste a token into chat; ask them to run the config command themselves.
- A cloud key reaches every computer of that key. Treat it like a password.

## Bootstrap

1. `luckgram status` — is a connection saved, and does it answer?
2. Not configured: the user opens Luckgram Desktop → Settings → Luckgram → **Local MCP server**, switches it on, copies the access token (or, for the cloud, switches on **Connect through the cloud** and copies the cloud key), then runs one of:
   ```sh
   luckgram config --local --token-stdin      # this computer
   luckgram config --cloud --token-stdin      # every computer on the cloud key
   ```
3. `luckgram accounts` — the ids every other command takes as `--account`.

## How to work

1. **Start with `luckgram accounts`.** `--account` is the id from that list. Never guess ids, never use a name as an id.
2. On the cloud, **`luckgram devices` first**; pass `--device <name>` when more than one computer is online.
3. Commands work on any logged-in account without switching the window. Use `luckgram switch` only when the user wants to see that account on screen.
4. `<chat>` is an id from `luckgram chats list`, or a username.

```sh
luckgram accounts
luckgram chats list --account 7943234085 --unread
luckgram messages get 562953914961921 --account 7943234085 --limit 20
luckgram messages send @someone "See you at 3" --account 7943234085
luckgram friends find @someone --account 7943234085
luckgram friends add @someone --account 7943234085
```

## Skills are switched on by the user

Each group of commands is a skill the user switches on **per account** inside Luckgram Desktop. All are off at first.

| Commands | Skill in the app | Changes the account |
|---|---|---|
| `accounts`, `active`, `switch` | always on | no |
| `friends list`, `friends find` | `friends` | no |
| `friends add`, `friends remove` | `friends_manage` | yes |
| `chats list` | `chats` | no |
| `chats read` | `chats_manage` | yes |
| `messages get` | `messages` | no |
| `messages send` | `messages_send` | yes |
| `groups join`, `groups leave` | `groups` | yes |
| `profile set` | `profile` | yes |
| `bots …`, `botfather …` | `botfather` | yes |

When a command exits with code 1 and says a skill is off, you cannot switch it on. Tell the user **which skill** and **which account**, and where the switch is. Do not try another account instead unless the user asked for that.

## Rules

- **Rate limits are final.** Commands that change an account are limited per account (`friends add` 5 an hour and 20 a day, `messages send` 30 an hour and 200 a day, …). A refused call says how many seconds to wait. Do not retry sooner and do not move the action to another account to get around it: the limits keep accounts from being restricted by Telegram.
- **`FLOOD_WAIT` comes from Telegram.** Stop using that command on that account for the stated time.
- **One message, one chat.** Do not loop `messages send` or `friends add` over people who did not ask to be contacted. If the user asks for that, say that unsolicited bulk messages get accounts banned and ask what they actually need.
- **Show before you send.** Draft the text, show it, send after the user agrees — unless they told you the exact text to send.
- **Say what changed.** After a command that changes an account, report the account, the chat or user, and what the command answered.
- **Reading does not mark as read.** `messages get` leaves the chat unread; `chats read` is its own step.
- **`messages send` is queued, not confirmed.** Check with `messages get` when delivery matters.
- **A locked app answers nothing.** When Luckgram is locked with a passcode every command says so; the user has to unlock it.

## Bots (@BotFather)

```sh
luckgram bots list --account 7943234085
luckgram bots create my_shop_bot --name "My Shop" --out ~/my_shop_bot.token --account 7943234085
luckgram bots set my_shop_bot --description "Orders and delivery status" --about "Official bot of My Shop"
luckgram bots commands my_shop_bot 'start=Start' 'order=Track an order' 'help=How it works'
luckgram bots token my_shop_bot --out ~/my_shop_bot.token
```

- **A bot token is a secret**: whoever has it controls the bot. Use `--out <file>` so the token goes to a file only the owner can read and the output shows it masked. Without `--out` the token is printed: do that only when the user asked to see it. Never paste a token into a chat, a commit or a log.
- **`bots delete` cannot be undone.** Ask the user first, every time, and name the bot. It needs the username twice (`--confirm`).
- **`bots token --revoke` breaks the running bot** until its new token is put where the bot runs. Ask first.
- For anything the `bots` commands do not cover (photo, inline mode, payments, menu button): `luckgram botfather send /mybots`, read the answer and its buttons, then `luckgram botfather press <message id> <button>` or `botfather send <answer>`, one step at a time. `luckgram botfather read` shows where the conversation stands.
- When BotFather refuses, the command exits 1 with its words ("Sorry, this username is already taken…"). Tell the user what it said; do not try variations in a loop.

## Exit codes

`0` ok · `1` the tool refused (skill off, rate limit, not found, locked) · `2` usage · `3` not configured · `4` cannot reach the server or the token was refused.

## References

- [help.md](./references/help.md) — every command with examples
- [tools.md](./references/tools.md) — config file, environment, MCP tools behind each command
