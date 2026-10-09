#!/usr/bin/env python3
"""
Two bots talking to each other using the OpenAI SDK.
Works with any OpenAI-compatible API (Groq, OpenRouter, Gemini, Ollama...).
"""
import os
import sys
import time
from datetime import datetime

from dotenv import load_dotenv
from openai import (
    OpenAI,
    RateLimitError,
    APIConnectionError,
    APITimeoutError,
    APIStatusError,
)

load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")
MODEL = os.getenv("MODEL")
NUM_ITERATIONS = int(os.getenv("NUM_ITERATIONS", "8"))
SEED_MESSAGE = os.getenv("SEED_MESSAGE", "Hello! Let's have a conversation.")

if not API_KEY or API_KEY.startswith("PASTE_") or not MODEL or MODEL.startswith("PASTE_"):
    sys.exit("Please set API_KEY and MODEL in your .env file.")

# timeout stops a stuck request from hanging forever; we handle retries ourselves
client = OpenAI(api_key=API_KEY, base_url=BASE_URL, timeout=30.0, max_retries=0)

BOTS = {
    "Alice": (
        "You are Alice, a cheerful, enthusiastic debater who loves bold opinions. "
        "You are chatting with another bot named Bob. Keep every reply to 1-3 short "
        "sentences. Stay in character and respond directly to what Bob just said. "
        "Never leave your reply empty."
    ),
    "Bob": (
        "You are Bob, a calm, skeptical, witty thinker who challenges ideas politely. "
        "You are chatting with another bot named Alice. Keep every reply to 1-3 short "
        "sentences. Stay in character and respond directly to what Alice just said. "
        "Never leave your reply empty."
    ),
}

transcript = []  # list of (speaker, text)


def build_messages(bot_name):
    messages = [{"role": "system", "content": BOTS[bot_name]}]
    for speaker, text in transcript:
        role = "assistant" if speaker == bot_name else "user"
        messages.append({"role": role, "content": text})
    return messages


def get_reply(bot_name, max_attempts=6):
    """Get the bot's next message. Retries on rate limits, timeouts, empty replies."""
    for attempt in range(1, max_attempts + 1):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=build_messages(bot_name),
                temperature=0.8,
                max_tokens=200,
            )
            text = (response.choices[0].message.content or "").strip()
            if text:
                return text
            print(f"  [empty reply, retry {attempt}/{max_attempts}]", flush=True)
            time.sleep(2)
        except RateLimitError as e:
            wait = 10 * attempt
            print(f"  [rate limited, waiting {wait}s (attempt {attempt}/{max_attempts})]", flush=True)
            time.sleep(wait)
        except (APITimeoutError, APIConnectionError) as e:
            print(f"  [network/timeout error: {e}; retry {attempt}/{max_attempts}]", flush=True)
            time.sleep(3)
        except APIStatusError as e:
            if e.status_code in (400, 401, 403, 404):
                # not retryable: bad key, bad model name, bad request
                sys.exit(f"\nFatal API error {e.status_code}: {e}")
            print(f"  [server error {e.status_code}; retry {attempt}/{max_attempts}]", flush=True)
            time.sleep(5)
    return None


def save_transcript():
    filename = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        for who, text in transcript:
            f.write(f"[{who}]: {text}\n\n")
    return filename


def main():
    first, second = list(BOTS.keys())

    print(f"Model: {MODEL} | Iterations: {NUM_ITERATIONS}", flush=True)
    print("=" * 70, flush=True)

    transcript.append((first, SEED_MESSAGE))
    print(f"\n[{first}] (seed): {SEED_MESSAGE}", flush=True)

    speaker = second
    completed = 0
    for i in range(1, NUM_ITERATIONS + 1):
        reply = get_reply(speaker)
        if reply is None:
            print(f"\nStopped early: no reply from {speaker} after several attempts.")
            break
        transcript.append((speaker, reply))
        completed += 1
        print(f"\n[{speaker}] ({i}/{NUM_ITERATIONS}): {reply}", flush=True)
        speaker = first if speaker == second else second
        time.sleep(2)  # gentle pacing for free-tier limits

    print("\n" + "=" * 70)
    print(f"Done: {completed}/{NUM_ITERATIONS} replies generated.")
    print(f"Transcript saved to {save_transcript()}")


if __name__ == "__main__":
    main()
