from fastapi import APIRouter, Request
from backend.telegram_router import handle_message

router = APIRouter()

@router.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    user_id = str(data['message']['chat']['id'])
    message = data['message']['text']
    response = handle_message(user_id, message)
    return {"ok": True, "response": response} 