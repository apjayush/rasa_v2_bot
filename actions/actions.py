from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import httpx

BACKEND_SLOT_URL = "http://localhost:8000/available-slots"

class ActionFetchSlots(Action):
    def name(self) -> Text:
        return "action_fetch_slots"

    async def run(self,
                  dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Call backend to get slots
        async with httpx.AsyncClient() as client:
            response = await client.get(BACKEND_SLOT_URL)
            slots = response.json().get("slots", [])

        # Convert slots to Rasa buttons
        buttons = []
        for slot in slots:
            buttons.append({
                "title": slot,  # visible on WhatsApp button
                "payload": f"/slot_selected{{\"slot\": \"{slot}\"}}"
            })

        # Send message back to user
        dispatcher.utter_message(
            text="Available slots for today:",
            buttons=buttons
        )

        return []
