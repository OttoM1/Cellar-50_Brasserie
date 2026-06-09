## start server

```
git clone https://github.com/OttoM1/Cellar-50_Brasserie.git
cd Cellar-50_Brasserie

# python side
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
python3 backend/server.py

# styles (components.css is pre built)
npm install
npm run watch:css
npm run build:css
```

Opens http://127.0.0.1:5000

- Host an event from Tasting, share the code, rate some wines :)

## env

var: CELLAR50_SECRET, dev fallback, flask session login
var: PORT, bind port 5000

## api surface

methods and paths:
`POST` | `/create_event`  
| `POST` | `/join_event`  
`POST` | `/save_tasting`  
| `GET` | `/discover?type=&q=`

---

## css workflow

Source lives in styles/. Partials: @use from main.scss

- Build:

```
npm run build:css
```

Edit SCSS, compile, refresh.

- Do not hand-edit the components.css file, unlike I did... easy merge conflicts.

## license

Public template. Fork it, break it, ship your own app =)
