# Two Bots Chatting (OpenAI SDK)

A command line app where two bots, Alice and Bob, talk to each other. The first message is seeded, then the bots reply in turn for a fixed number of iterations. It uses the OpenAI Python SDK, so it works with any OpenAI-compatible provider (Groq, Gemini, OpenRouter, or a local Ollama).

## How it works

- Alice opens with the seed message.
- Bob replies, then Alice, and so on for `NUM_ITERATIONS` replies.
- Each bot has its own system prompt (personality) and sees the conversation from its own point of view: its own lines are sent as `assistant` messages, the other bot's lines as `user` messages.
- Failed requests are retried (rate limits, timeouts, empty replies).
- The full conversation is saved to `chat_<timestamp>.txt`.

## Requirements

- Linux with Python 3.9+
- An API key from a free provider (or a working local Ollama install)

## Setup

```bash
mkdir -p ~/bot_chat && cd ~/bot_chat
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

`requirements.txt`:

```
openai
python-dotenv
```

## Configuration (`.env`)

Create a file named `.env` in the project folder:

```
API_KEY=PASTE_YOUR_API_KEY_HERE
BASE_URL=https://api.groq.com/openai/v1
MODEL=PASTE_MODEL_NAME_HERE

NUM_ITERATIONS=8
SEED_MESSAGE=Hi! I think pineapple absolutely belongs on pizza. Change my mind.
```

| Variable | Meaning |
|---|---|
| `API_KEY` | Your provider's API key |
| `BASE_URL` | The provider's OpenAI-compatible endpoint |
| `MODEL` | Exact model ID your account can use |
| `NUM_ITERATIONS` | Number of replies after the seed message |
| `SEED_MESSAGE` | The opening line from the first bot |

Do not use quotes or spaces around the `=`.

### Provider settings

| Provider | BASE_URL | Where to get a key |
|---|---|---|
| Groq | `https://api.groq.com/openai/v1` | https://console.groq.com |
| Gemini | `https://generativelanguage.googleapis.com/v1beta/openai/` | https://aistudio.google.com |
| OpenRouter | `https://openrouter.ai/api/v1` | https://openrouter.ai (use a model ending in `:free`) |
| Ollama (local) | `http://localhost:11434/v1` | no key needed, set `API_KEY=ollama` |

### Finding a valid model name

Model names change over time. List the models your key can use:

```bash
curl -s https://api.groq.com/openai/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY" \
  | grep -o '"id":"[^"]*"'
```

Pick a chat model and paste its ID into `MODEL=`. Skip names containing `whisper`, `guard`, `tts` or `orpheus`.

## Run

```bash
source venv/bin/activate
python bot_chat.py
```

## Example output

```
Model: <your model> | Iterations: 8
======================================================================

[Alice] (seed): Hi! I think pineapple absolutely belongs on pizza. Change my mind.

[Bob] (1/8): <reply>

[Alice] (2/8): <reply>
...
Done: 8/8 replies generated.
Transcript saved to chat_20261009_153000.txt
```

## Customizing

- Change the bots' personalities in the `BOTS` dictionary in `bot_chat.py`.
- Change the length of the chat with `NUM_ITERATIONS` in `.env`.

## Troubleshooting

| Problem | Fix |
|---|---|
| `404 model_not_found` | The model name is wrong or retired. List models (see above) and update `MODEL`. |
| `401` / authentication error | The API key is wrong. Regenerate it and check for stray spaces or quotes in `.env`. |
| Rate limit messages | The script waits and retries automatically. A smaller model usually has higher free limits. |
| Chat stops early | Read the printed error line. It shows the reason (rate limit, timeout, etc.). |

## Security

Never commit your `.env` file. Add it to `.gitignore`:

```bash
echo ".env" >> .gitignore
echo "venv/" >> .gitignore
```

## Project structure

```
bot_chat/
├── bot_chat.py
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```
