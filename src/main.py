from fastapi import FastAPI, Request
from discord_notifier import send_discord_message
from proxmox_utils import get_proxmox_report
import os

app = FastAPI()

@app.post("/proxmox-status")
async def ping(request: Request):
    payload = await request.json()
    user = payload.get("user", "unknown")
    device = payload.get("device", "unknown")

    report = get_proxmox_report()
    message = f"🟢 {user} logged into `{device}`\n\n{report}"
    send_discord_message(message)

    return {"status": "ok", "posted": True}
