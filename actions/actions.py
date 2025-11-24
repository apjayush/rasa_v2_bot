from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import httpx

BACKEND_SLOT_URL = "http://localhost:8000/available-slots"
BACKEND_BOOK_URL = "http://localhost:8000/book-slot"

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

        # Convert slots to WhatsApp-compatible button IDs
        buttons = []
        for slot in slots:
            slot_id = slot.replace(" ", "").replace(":", "_")   # "10:00 AM" -> "10_00AM"
            slot_id = f"slot_{slot_id}"                        # "slot_10_00AM"

            buttons.append({
                "title": slot, 
                "payload": slot_id     # CLEAN payload for WhatsApp
            })

        # Send message back to user
        dispatcher.utter_message(
            text="Available slots for today:",
            buttons=buttons
        )

        return []
    

class ActionStoreSlot(Action):
    def name(self):
        return "action_store_slot"

    def run(self, dispatcher, tracker, domain):
        # Example: "slot_10_00AM"
        raw = tracker.latest_message.get("text")

        if not raw:
            return []

        # Remove "slot_" prefix
        raw = raw.replace("slot_", "")     # "10_00AM"

        # Extract AM/PM
        ampm = raw[-2:]                    # "AM" or "PM"

        # Extract time part
        time_part = raw[:-2]               # "10_00"

        # Convert "10_00" → "10:00"
        time_part = time_part.replace("_", ":")

        # Make final readable time: "10:00 AM"
        readable_time = f"{time_part} {ampm}"

        # Save to Rasa slot
        return [SlotSet("chosen_slot", readable_time)]


class ActionStoreName(Action):
    def name(self):
        return "action_store_name"

    def run(self, dispatcher, tracker, domain):
        # The entire user message is treated as name
        name = tracker.latest_message.get("text")

        # Clean name (optional)
        name = name.strip()

        return [SlotSet("user_name", name)]
    


class ActionBookAppointment(Action):
    def name(self):
        return "action_book_appointment"

    async def run(self, dispatcher, tracker, domain):
        name = tracker.get_slot("user_name")
        slot = tracker.get_slot("chosen_slot")
        phone = tracker.sender_id

        payload = {
            "name": name,
            "slot": slot,
            "phone": phone
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(BACKEND_BOOK_URL, json=payload)

        # Confirmation to user
        dispatcher.utter_message(
            text=f"Thanks {name}! Your appointment is booked for {slot}."
        )

        return []

