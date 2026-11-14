---
name: luckgram
description: Work with the Telegram accounts in Luckgram Desktop through its MCP server (local or cloud) - list and switch accounts, friends, chats, messages, groups, profile. Use when the user asks to do something with their Telegram / Luckgram accounts and a "luckgram" or "luckgram-cloud" MCP server is connected.
---

# Luckgram

Luckgram Desktop exposes the Telegram accounts logged in on a computer as MCP tools. This skill is the way to use them well.

## Before anything else

1. Call `list_accounts`. Every other tool takes `account`: the `id` from this list, as a string. Do not guess ids and do not use names as ids.
2. On the cloud server (`luckgram-cloud`) call `list_devices` first. Every tool then also takes `device` (the id or the name of a computer). With one computer online it may be left out.
3. Tools work on any logged-in account without switching the window. Call `switch_account` only when the user wants to see that account on screen.

## Skills are switched on by the user

Tools are grouped into skills, switched on per account inside Luckgram Desktop (Settings → Luckgram → Local MCP server). All are off at first.

| Skill | Tools | Changes the account |
|---|---|---|
| (always on) | `list_accounts`, `get_active_account`, `switch_account` | no |
| `friends` | `list_friends`, `find_user` | no |
| `friends_manage` | `add_friend`, `remove_friend` | yes |
| `chats` | `list_chats` | no |
| `chats_manage` | `mark_chat_read` | yes |
| `messages` | `get_messages` | no |
| `messages_send` | `send_message` | yes |
| `groups` | `join_chat`, `leave_chat` | yes |
| `profile` | `update_profile` | yes |

When a call answers that a skill is off for an account, you cannot switch it on. Tell the user which skill and which account, and where the switch is. Do not try another account instead unless the user asked for that.

## Rules

- **Rate limits are final.** Tools that change something are limited per account (for example `add_friend` 5 an hour and 20 a day, `send_message` 30 an hour and 200 a day). A refused call says how many seconds to wait. Do not retry sooner, and do not move the same action to another account to get around the limit: the limits protect accounts from being restricted by Telegram.
- **`FLOOD_WAIT` comes from Telegram.** Stop using that tool on that account for the stated time.
- **One message, one chat.** There is no bulk tool. Do not loop `send_message` or `add_friend` over a list of people who did not ask to be contacted. If the user asks for that, explain that unsolicited bulk messages get accounts banned and ask what they actually need.
- **Say what you did.** After any tool that changes an account, tell the user which account, which chat or user, and the result the tool returned.
- **Reading does not mark as read.** `get_messages` leaves the chat unread. Use `mark_chat_read` only when the user wants that.
- **`send_message` is queued, not confirmed.** It answers `queued: true` when the app accepted it. A failure shows in the chat like for a message typed by hand; check with `get_messages` when delivery matters.
- **A locked app answers nothing.** When Luckgram is locked with a passcode every tool says so; the user has to unlock it.

## Typical flows

**Check what is unread everywhere**: `list_accounts` → for each account with the `chats` skill, `list_chats` with `unread_only: true` → summarize by account. Skip accounts whose skill is off and list them at the end.

**Reply in a chat**: `list_chats` (find the chat `id`) → `get_messages` with `chat` → draft the reply and show it to the user → `send_message` after they agree → report.

**Add a contact**: `find_user` by username or phone → show who was found → `add_friend` with the `user_id` → report `added` or `already_friend`.

## Setup, for the user

- Local: Settings → Luckgram → Local MCP server → switch on → Copy client config.
- Cloud: the same page → Connect through the cloud → Copy cloud client config. Other computers join with "Use the cloud key of another computer".
- Details: https://luckgram.cc/mcp/ and https://luckgram.cc/skills/
