# Ellis — a virtual wellbeing companion

Ellis is a single self-contained web page (`ellis.html`). It has a calm 3D
avatar in a lagoon scene, speaks and listens with your browser's built-in
voice features, can optionally read your expression through your camera,
and holds a conversation using a free AI chat service of your choice.

There is no build step and no server required to try it. Everything —
HTML, CSS, JavaScript and the on-page logic — lives in that one file.

## What it does

- **Calm 3D scene and avatar** — built with Three.js, loaded from a CDN.
- **Speech in and out** — your browser's Speech Recognition (listening)
  and Speech Synthesis (speaking) APIs. No audio is uploaded by Ellis
  itself for this part, though your browser's recognition engine may
  process audio on its own servers (this varies by browser).
- **Conversation** — Ellis can talk to any OpenAI-compatible chat API
  (Groq, Google Gemini, OpenRouter, Mistral, a local Ollama install, or
  your own endpoint). Several of these have a free tier. If no AI
  service is connected, or a reply fails, Ellis falls back to a built-in,
  rule-based reply engine so the page still works end to end.
- **Optional camera** — off by default. If you turn it on, your
  expression is read locally in your browser (face-api.js, loaded from a
  CDN the first time you enable it) and only a short mood word (like
  "worried") is used, never raw video or images, unless the on-device
  reader fails to load, in which case a single still frame is sent to
  Claude as a fallback.
- **End-of-session feedback** — a short feedback box adjusts Ellis's
  pace, tone and voice for the next session, saved only in your
  browser's local storage.
- **Safety net** — messages that mention self-harm or danger trigger a
  visible support message pointing to real-world help.

Ellis is a prototype and companion, **not** a licensed therapist, and
does not replace professional care.

## Quick start

1. Download `ellis.html` (and this `README.md`) from this repository, or
   clone it — see **Push to GitHub** below.
2. Open `ellis.html` directly in a modern desktop browser (Chrome or
   Edge work best for speech features). No server is required.
3. Click **Begin session**.
4. Optional: open **Voice and camera** in the top right to:
   - Pick a voice, and adjust speed/pitch.
   - Turn the camera on (your browser will ask for permission).
   - Connect a free AI chat service under **Conversation engine** (see
     below). Without this, Ellis still works using its built-in replies.

### Connecting a free AI service (recommended)

Open **Voice and camera → Conversation engine**, pick a service, and
paste a free API key:

| Service | Notes |
|---|---|
| **Groq** | Fast, generous free tier. Get a key at console.groq.com/keys |
| **Google Gemini** | Free tier on Flash models. Get a key at aistudio.google.com/apikey |
| **OpenRouter** | Free models (`:free` suffix), small daily limit. Get a key at openrouter.ai/keys |
| **Mistral** | Free mode. Get a key at console.mistral.ai |
| **Ollama (local)** | Fully free and private, runs on your own computer. No key needed, but you must start Ollama with `OLLAMA_ORIGINS=*` so the browser page is allowed to connect to it. |

Press **Test connection** after entering a key to confirm it works.
Free tiers change their rate limits and available model names over
time — if a test fails with "model not found", check the provider's
current model list and update the **Model** field.

**Note:** the API key is stored only in your own browser (and only if
you tick "Remember the key on this device"). Anyone who opens your copy
of the file in their own browser could read it from the page's local
storage/settings. For a real product serving other people, move the API
call to a small backend server you control, so the key never reaches
the browser. This file is a client-only prototype.

## Browser requirements

- A recent version of Chrome or Edge is recommended for Speech
  Recognition. Firefox and Safari have partial or no support for it;
  typing still works everywhere.
- An internet connection is needed to load the 3D library, fonts, the
  optional camera emotion model, and to reach any AI service you
  connect. Without internet, the avatar and most features won't load.
- The camera and microphone both require the user's explicit browser
  permission, requested only if those features are turned on.

## File structure

```
.
├── ellis.html   # the entire app — open this in a browser
└── README.md    # this file
```

## Push to GitHub

If you don't already have a repository:

```bash
# 1. Create a new folder and put ellis.html and README.md inside it
mkdir ellis && cd ellis
# (copy ellis.html and README.md into this folder)

# 2. Initialize git and make the first commit
git init
git add ellis.html README.md
git commit -m "Add Ellis virtual companion prototype"

# 3. Create a new empty repository on github.com (no README, no .gitignore),
#    then connect it and push
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

If you already have a repository cloned locally:

```bash
cd your-repo
# copy ellis.html and README.md into the folder
git add ellis.html README.md
git commit -m "Add Ellis virtual companion prototype"
git push
```

### Optional: enable GitHub Pages

Since `ellis.html` is a self-contained static file, you can host it for
free with GitHub Pages:

1. In your GitHub repository, go to **Settings → Pages**.
2. Under **Build and deployment**, set **Source** to "Deploy from a
   branch", branch `main`, folder `/ (root)`.
3. Save. GitHub will publish the page at
   `https://<your-username>.github.io/<your-repo>/ellis.html`.

Do **not** commit any API key into the repository. The key is meant to
be entered by each person in their own browser session, not stored in
the code.

## Known limitations

- Replies from the built-in fallback engine are simpler and more
  repetitive than a connected AI service.
- The camera-based emotion reading is a rough signal (broad categories
  like happy, sad, angry) and is treated by Ellis only as a gentle cue,
  never a stated fact.
- This is a prototype for exploration and learning, not a reviewed or
  clinically validated tool.
