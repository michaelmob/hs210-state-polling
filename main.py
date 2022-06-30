from datetime import datetime
from asyncio import run, sleep
from requests import get as get_request
from kasa import SmartPlug

from os import getenv
from dotenv import load_dotenv

"""
Send message via Telegram bot.
"""
def send_message(token, chat_id, content):
  get_request(
    f"https://api.telegram.org/bot{token}/sendMessage?" +
    f"chat_id={chat_id}&text={content}", timeout=10)


"""
On device state change event.
"""
def on_change(name, state, notify=True):
  on_or_off = "ON" if state else "OFF"
  content = f"{name} turned {on_or_off}"
  if notify:
    send_message(BOT_TOKEN, CHAT_ID, content)
  print(f"{content} at {datetime.today()}")


"""
Main loop.
Connects to SmartPlug and polls for state.

Requires environment variables:
  * DEVICE_HOST=
  * BOT_TOKEN=
  * CHAT_ID=
"""
async def main_loop():
  plug = SmartPlug(DEVICE_HOST)
  
  # get initial state
  await plug.update()
  plug.was_on = plug.is_on
  print(f"--- CONNECTED TO {DEVICE_HOST} ---")
  on_change(plug.alias, plug.is_on, notify=False)

  # poll for state changes
  while True:
    await plug.update()
    if plug.is_on != plug.was_on:
      plug.was_on = plug.is_on
      on_change(plug.is_on)
    await sleep(1)


if __name__ == "__main__":
  load_dotenv()

  DEVICE_HOST = getenv("DEVICE_HOST")
  BOT_TOKEN = getenv("TELEGRAM_BOT_TOKEN")
  CHAT_ID = getenv("TELEGRAM_CHAT_ID")

  if not DEVICE_HOST: print("Missing DEVICE_HOST environment variable.")
  if not BOT_TOKEN: print("Missing BOT_TOKEN environment variable.")
  if not CHAT_ID: print("Missing CHAT_ID environment variable.")

  run(main_loop())
