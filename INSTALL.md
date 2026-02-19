# INSTALLATION GUIDE (v1000000 ZERO)

## 1. Quick Install (Termux)
Run this single command to install everything:
```bash
pkg update -y && pkg install python git -y && git clone https://github.com/YourRepo/NazhanBots && cd NazhanBots && bash setup.sh
```

## 2. Requirements
- **Android**: 8.0+
- **Termux**: Latest Version (F-Droid Recommended)
- **Termux:API**: App installed from PlayStore/F-Droid (Required for Voice & Battery)

## 3. How to Run
- **Normal Mode**: `python main.py`
- **Server Mode (24/7)**: `bash start_server.sh`
- **Hunter Mode**: `python main.py --hunter`

## 4. Troubleshooting
- **No Voice?** Install `Termux:API` app and run `pkg install termux-api`.
- **Bot Crashes?** Check `logs/error.log`.
- **Battery Drain?** The bot automatically pauses at 20% battery.

## 5. Features (God Mode)
- **Skynet**: Auto-manages the bot.
- **Swarm**: Shares targets with other bots via Telegram.
- **Chaos**: Mimics human errors to bypass firewalls.
- **Immortal**: Auto-restarts if killed by Android.

*System Architect: NazhanBots AI*
