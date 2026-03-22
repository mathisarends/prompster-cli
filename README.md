# Prompster-CLI

**Create your own Hitster card deck — powered by AI and Spotify.**

Prompster is a CLI tool that helps you build custom Hitster card decks. Just describe the vibe or theme you want, and Prompster finds matching songs on Spotify, generates QR codes, and builds a print-ready PDF.

---

## What the cards look like

<p align="center">
  <img src="static/page_front.png" width="380" alt="Front side — QR codes to scan">
  &nbsp;&nbsp;&nbsp;
  <img src="static/page_back.png" width="380" alt="Back side — song, artist and year">
</p>

**Front:** Each card has a QR code that links directly to the song on Spotify.
**Back:** Artist, song title, and release year — in colorful designs.

Print double-sided, cut them out, and start playing.

---

## Installation

> Requires [Python 3.14+](https://www.python.org/downloads/) and [uv](https://docs.astral.sh/uv/getting-started/installation/)

```bash
# Clone the repository
git clone https://github.com/dein-user/hitster-cli.git
cd hitster-cli

# Install
uv sync
```

### Spotify setup

Prompster needs access to the Spotify API to search for songs and create playlists.

1. Create an app in the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Set the redirect URI to: `http://localhost:8888/callback`
3. Create a `.env` file in the project folder:

```env
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
```

---

## Usage

```bash
prompster
```

This starts the interactive console:

```
  ██████╗ ██████╗  ██████╗ ███╗   ███╗██████╗ ███████╗████████╗███████╗██████╗
  ██╔══██╗██╔══██╗██╔═══██╗████╗ ████║██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔══██╗
  ██████╔╝██████╔╝██║   ██║██╔████╔██║██████╔╝███████╗   ██║   █████╗  ██████╔╝
  ██╔═══╝ ██╔══██╗██║   ██║██║╚██╔╝██║██╔═══╝ ╚════██║   ██║   ██╔══╝  ██╔══██╗
  ██║     ██║  ██║╚██████╔╝██║ ╚═╝ ██║██║     ███████║   ██║   ███████╗██║  ██║
  ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚═╝     ╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝

  Tell me your vibe — I'll build the deck.

❯ I want a 90s Eurodance deck!
```

Just describe what kind of deck you want — Prompster takes care of the rest:

1. Finds matching songs on Spotify
2. Creates a playlist in your Spotify account
3. Generates a print-ready PDF with QR codes and card backs

### Commands

| Command  | Description             |
| -------- | ----------------------- |
| `/help`  | Show available commands |
| `/reset` | Reset the conversation  |
| `/exit`  | Exit Prompster          |

---

## Printing

1. Open the generated PDF (`hitster-deck.pdf`)
2. Print **double-sided** (flip on short edge)
3. Cut the cards along the crop marks
4. Done — have fun playing!
