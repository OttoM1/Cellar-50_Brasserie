# Cellar50 Brasserie

> blind wine tasting

Paper scorecards belong in the 1990s :D

## What is this?

- interactive full-stack mockup of a private web application originally built + delivered for a brasserie client.
- the production version lives and runs a proprietary wine catalog, this repo works as a functional reference implementation.
- UX pipeline: the host starts up a private room and guests get in with a 4-letter room code.
- tasting pipeline: visuals - nose - palate - structure - guess - score.

## The Actual Production Stack

Client dep is a full-stack setup; no React, also a server rendered HTML, it is more than enough to keep the UI fast and responsiv; the tasting wizard powered by GSAP motion.

### Backend:

- is powered by FastAPI behind nginx, async req and structured json.
- Redis holds session tokens.
- PostgreSQL is instead of SQLite (which is used in this mockup version).

### Active layer:

- WebSockets (room codes will expire and events get archived not deleted)

### Auth / ops:

- email/Oauth)
- wine library is manageable through internal admin surface

(docker compose locally)

## Stack in this mockup repo

What stayed the same for this mockup repo:

- Jinja2 page blocks, scss tokens, GSAP, vanilla client utils
- Same UX pipeline; in the prod stack I just added more persistence/concurrency and the catalog is not hardcoded

```
  scaffold/        jinja templates
 styles/            scss src
 components.css     compiled output
  interface.js       pure vanilla js shared client utils
 backend/server.py  flask and SQLite
```

Everything else is server-rendered HTML

## features

- Tasting wizard: tasting step flow (gsap anims)
- Server: room codes and wine list builder
- Cheat sheet: slide panel to help quide less experienced tasters
- Discover: searchable catalog library (not client's own catalog in this mockup)
- Cellar: journal and horizontal stat cards
- Tasting summary: avrg scores per wine when the event is done

UX bits: custom alert modal, toast notifs, mobile bottom nav...

## full repo tree

```
Cellar-50_Brasserie/
├── backend/
│   └── server.py
├── scaffold/
├── static/
├── styles/
│   ├── main.scss
│   ├── _variables.scss
│   ├── _mixins.scss
│   └── pages/
├── components.css
├── interface.js
├── package.json
└── requirements.txt
```

Public template. Fork it, break it, ship your own app :)
