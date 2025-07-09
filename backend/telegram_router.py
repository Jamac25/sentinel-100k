from backend.intent_engine import IntentEngine
from backend.ai_action_bridge import AIActionBridge

intent_engine = IntentEngine()
ai_bridge = AIActionBridge()

def handle_message(user_id: str, message: str) -> str:
    intent = intent_engine.detect_intent(message)
    params = intent_engine.extract_parameters(message, intent)
    return ai_bridge.execute(user_id, intent, params) 