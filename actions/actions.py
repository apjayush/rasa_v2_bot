from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import httpx
import asyncio
# from vehicle_data.vehicle_info import VEHICLE_DATA
# from ./ import VEHICLE_DATA

BACKEND_SLOT_URL = "http://localhost:8000/available-slots"
BACKEND_BOOK_URL = "http://localhost:8000/book-slot"
BACKEND_SEND_LIST_URL = "http://localhost:8000/send-list"
BACKEND_SEND_BROCHURE_URL = "http://localhost:8000/send-brochure"
BACKEND_BOOK_TEST_RIDE_URL = "http://localhost:8000/book-test-ride"
BACKEND_SEND_MESSAGE_URL = "http://localhost:8000/send-message"
BACKEND_NOTIFY_AGENT_URL = "http://localhost:8000/notify-agent"
BACKEND_SEND_IMAGE_URL = "http://localhost:8000/send-image"
BACKEND_LEAD_UPDATE_URL = "http://localhost:8000/update_lead"

VEHICLE_DATA = {
    # ---------------- APACHE SERIES ----------------
    "apache_rtr_160_4v": {
        "name": "Apache RTR 160 4V",
        "specs": (
            "🏍️ *Apache RTR 160 4V*\n\n"
            "⚙️ *Engine:* 159.7cc, Oil-cooled\n"
            "💨 *Power:* 17.55 PS\n"
            "🔧 *Torque:* 14.73 Nm\n"
            "⚖️ *Weight:* 138 kg\n"
            "⛽ *Fuel Tank:* 12 Litres\n"
        ),
        "image_url": "https://api.incoweb.in/media/templates/rtr1604v.jpg",
        "ex_showroom_price": 113190
    },

    "apache_rtr_160_2v": {
        "name": "Apache RTR 160 2V",
        "specs": (
            "🏍️ *Apache RTR 160 2V*\n\n"
            "⚙️ *Engine:* 159.7cc, Air-cooled\n"
            "💨 *Power:* 15.2 PS\n"
            "🔧 *Torque:* 13.1 Nm\n"
            "⚖️ *Weight:* 138 kg\n"
            "⛽ *Fuel Tank:* 12 Litres\n"
        ),
        "image_url": "https://api.incoweb.in/media/templates/rtr1602v.jpg",
        "ex_showroom_price": 101890
    },

    "apache_200_4v": {
        "name": "Apache RTR 200 4V",
        "specs": (
            "🏍️ *Apache RTR 200 4V*\n\n"
            "⚙️ *Engine:* 197.75cc, Oil-cooled\n"
            "💨 *Power:* 20.82 PS\n"
            "🔧 *Torque:* 16.8 Nm\n"
            "⚖️ *Weight:* 153 kg\n"
            "⛽ *Fuel Tank:* 12 Litres\n"
        ),
        "image_url": "https://api.incoweb.in/media/templates/rtr2004v.jpg",
        "ex_showroom_price": 141990
    },

    "tvs_ntorq_125": {
        "name": "TVS Ntorq 125",
        "specs": (
            "🛵 *TVS Ntorq 125*\n\n"
            "⚙️ *Engine:* 124.8cc, Air-cooled\n"
            "💨 *Power:* 9.4 PS\n"
            "🔧 *Torque:* 10.5 Nm\n"
            "⚖️ *Weight:* 118 kg\n"
            "⛽ *Fuel Tank:* 5.8 Litres\n"
        ),
        "image_url": "https://api.incoweb.in/media/templates/ntorq_125.jpg",
        "ex_showroom_price": 86900
    },

    "tvs_jupiter": {
        "name": "TVS Jupiter",
        "specs": (
            "🛵 *TVS Jupiter*\n\n"
            "⚙️ *Engine:* 109.7cc, Air-cooled\n"
            "💨 *Power:* 7.8 PS\n"
            "🔧 *Torque:* 8.4 Nm\n"
            "⚖️ *Weight:* 116 kg\n"
            "⛽ *Fuel Tank:* 6.5 Litres\n"
        ),
        "image_url": "https://api.incoweb.in/media/templates/jupiter.jpg",
        "ex_showroom_price": 76150
    },

    "tvs_ronin_bike": {
        "name": "TVS Ronin",
        "specs": (
            "🏍️ *TVS Ronin*\n\n"
            "⚙️ *Engine:* 223cc, Oil-cooled\n"
            "💨 *Power:* 20.5 PS\n"
            "🔧 *Torque:* 19.93 Nm\n"
            "⚖️ *Weight:* 161 kg\n"
            "⛽ *Fuel Tank:* 12 Litres\n"
        ),
        "image_url": "https://api.incoweb.in/media/templates/ronin.jpg",
        "ex_showroom_price": 125690
    },

    "apache_rtr_310": {
        "name": "Apache RTR 310",
        "specs": (
            "🏍️ *Apache RTR 310*\n\n"
            "⚙️ *Engine:* 312.2cc, Liquid-cooled\n"
            "💨 *Power:* 34 PS\n"
            "🔧 *Torque:* 27.3 Nm\n"
            "⚖️ *Weight:* 169 kg\n"
            "⛽ *Fuel Tank:* 11 Litres\n"
        ),
        "image_url": "https://api.incoweb.in/media/templates/rtr310.jpg",
        "ex_showroom_price": 221240
    },
}



class ActionStoreName(Action):
    def name(self) -> str:
        return "action_store_name"

    async def run(self, dispatcher, tracker: Tracker, domain):

        # 1️⃣ Extract name entity (ONLY correct way)
        name = next(tracker.get_latest_entity_values("name"), None)
        print("📝 Extracted name:", name)

        if not name:
            print("❌ Name entity missing, aborting store")
            return []

        name = name.strip()

        # 2️⃣ Resolve phone safely
        phone = (
            tracker.latest_message.get("metadata", {}).get("phone")
            or tracker.get_slot("phone")
            or tracker.sender_id
        )

        print("📞 Phone resolved as:", phone)

        if not phone:
            print("❌ Phone missing, aborting")
            return []

        # 3️⃣ Update lead via backend
        update_payload = {
            "phone": phone,
            "updates": {
                "name": name
            }
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    BACKEND_LEAD_UPDATE_URL,
                    json=update_payload
                )
                if resp.status_code != 200:
                    print("❌ Lead update failed:", resp.text)
        except Exception as e:
            print("❌ Error updating lead:", e)

        # 4️⃣ Send acknowledgment
        message_payload = {
            "to": phone,
            "message": f"Nice to meet you, {name}! 😊"
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                await client.post(BACKEND_SEND_MESSAGE_URL, json=message_payload)
        except Exception as e:
            print("❌ Error sending acknowledgment:", e)

        # 5️⃣ Set slot so next actions know name exists
        return [SlotSet("user_name", name)]


class ActionGreetUser(Action):
    def name(self) -> Text:
        return "action_greet_user"

    async def run(
        self,
        dispatcher,   # intentionally unused
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # 1️⃣ Get phone number (metadata FIRST, sender_id fallback)
        phone_number = (
            tracker.latest_message.get("metadata", {}).get("phone")
            or tracker.sender_id
        )

        print("-" * 100)
        print("📞 Phone resolved as:", phone_number)
        print("-" * 100)

        if not phone_number:
            print("❌ Phone not found")
            return []

        # 2️⃣ Call backend to send WhatsApp message
        payload = {
            "to": phone_number,
            "message": "Hi 👋 Welcome to TVS Motors — Built to Perform 🏍️"
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                await client.post(BACKEND_SEND_MESSAGE_URL, json=payload)
            print("✅ Greeting sent via backend")
        except Exception as e:
            print(f"❌ Error sending greeting: {e}")

        # 3️⃣ Store phone in slot (still useful)
        return [SlotSet("phone", phone_number)]



class ActionAskName(Action):
    def name(self) -> Text:
        return "action_ask_name"

    async def run(
        self,
        dispatcher,   # intentionally unused
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        # 1️⃣ Resolve phone number (metadata → sender_id)
        phone_number = (
            tracker.latest_message.get("metadata", {}).get("phone")
            or tracker.sender_id
        )

        if not phone_number:
            print("❌ Phone not found")
            return []

        # 2️⃣ Ask for user's name via backend
        payload = {
            "to": phone_number,
            "message": "Before we continue, may I know your name?"
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                await client.post(BACKEND_SEND_MESSAGE_URL, json=payload)
            print("✅ Name request sent successfully")
        except Exception as e:
            print(f"❌ Error asking for name: {e}")

        # 3️⃣ No slot update yet (name not known)
        return []



class ActionSendBrochure(Action):
    def name(self) -> Text:
        return "action_send_brochure"

    async def run(self,
                  dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get user's phone number
        phone_number = tracker.sender_id
        
        # Check if user has selected a vehicle
        chosen_vehicle = tracker.get_slot("chosen_vehicle")

        print("chosen vehicle:", chosen_vehicle)

        # Brochure URLs (You need to host these PDFs on a public server or cloud storage)
        brochure_data = {
            "Apache RTR 160": {
                "pdf_url": "https://www.tvsmotor.com/tvs-apache/-/media/Brand-Pages/Apache/Brochure/TVS-Apache-RTR-160-Brochure_V4.pdf",
                "filename": "TVS_Apache_RTR_160_Brochure.pdf",
                "caption": "📄 TVS Apache RTR 160 - Complete Brochure"
            },
            "Apache 200 4V": {
                "pdf_url": "https://www.tvsmotor.com/tvs-apache/-/media/Brand-Pages/Apache/Brochure/Apache-200-4V-BLUE-Leaflet.pdf",
                "filename": "TVS_Apache_200_4V_Brochure.pdf",
                "caption": "📄 TVS Apache 200 4V - Complete Brochure"
            },
            "TVS Jupiter": {
                "pdf_url": "https://www.tvsmotor.com/tvs-jupiter-125/-/media/Brand-Pages/TVS-N282/TVS-Jupiter-125-Brochure.pdf",
                "filename": "TVS_Jupiter_Brochure.pdf",
                "caption": "📄 TVS Jupiter - Complete Brochure"
            },
            "TVS Ronin": {
                "pdf_url": "https://www.tvsmotor.com/-/media/Feature/AfterAprilPdf/TVS-Ronin.pdf",
                "filename": "TVS_Ronin_Brochure.pdf",
                "caption": "📄 TVS Ronin - Complete Brochure"
            }
        }
        
        # If user has selected a specific vehicle, send that brochure
        if chosen_vehicle and chosen_vehicle in brochure_data:
            brochure = brochure_data[chosen_vehicle]
            
            payload = {
                "to": phone_number,
                "pdf_url": brochure["pdf_url"],
                "filename": brochure["filename"],
                "caption": brochure["caption"]
            }
            
            try:
                print("Reached brochure sending part")
                async with httpx.AsyncClient() as client:
                    response = await client.post(BACKEND_SEND_BROCHURE_URL, json=payload)
                    response.raise_for_status()
                
                dispatcher.utter_message(
                    text=f"✅ {chosen_vehicle} brochure has been sent!"
                )
            except Exception as e:
                print(f"❌ Error sending brochure: {e}")
                dispatcher.utter_message(
                    text="Sorry, I couldn't send the brochure at the moment. Please try again later."
                )
        
        else:
            # If no vehicle selected, show all brochures as options
            sections = [
                {
                    "title": "📚 Select vehicle",
                    "rows": [
                        {
                            "id": "apache_rtr_160",
                            "title": "Apache RTR 160",
                            "description": "Get the brochure"
                        },
                        {
                            "id": "apache_200_4v",
                            "title": "Apache 200 4V",
                            "description": "Get the brochure"
                        },
                        {
                            "id": "tvs_jupiter",
                            "title": "TVS Jupiter",
                            "description": "Get the brochure"
                        },
                        {
                            "id": "tvs_ronin_bike",
                            "title": "TVS Ronin",
                            "description": "Get the brochure"
                        }
                    ]
                }
            ]
            
            payload = {
                "to": phone_number,
                "header": "Select a Vehicle",
                "body": "📚 Please select a vehicle to receive its brochure:",
                "button_text": "Choose",
                "sections": sections
            }
            
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(BACKEND_SEND_LIST_URL, json=payload)
                    response.raise_for_status()
            except Exception as e:
                print(f"❌ Error sending brochure options: {e}")
                dispatcher.utter_message(text="Sorry, couldn't load brochure options.")
        
        return []


class ActionGreetWithMenu(Action):
    def name(self) -> Text:
        return "action_greet_with_menu"

    async def run(self,
                  dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        print("🎯 ActionGreetWithMenu TRIGGERED!")
        phone_number = tracker.sender_id
        user_name = tracker.get_slot("user_name")
        
        # Personalized greeting
        greeting = f"Hi, {user_name}!" if user_name else "Hi there! 😊"

        # Prepare vehicle selection menu with all 4 vehicles
        sections = [
            {
                "title": "🏍️ Our Vehicle Collection",
                "rows": [
                    {
                        "id": "apache_rtr_160_2v",
                        "title": "Apache RTR 160",
                        
                    },
                    {
                        "id": "apache_200_4v",
                        "title": "Apache 200 4V",
                       
                    },
                    {
                        "id": "tvs_ntorq_125",
                        "title": "TVS Ntorq 125",
                        
                    },
                    {
                        "id": "tvs_jupiter",
                        "title": "TVS Jupiter",
                        
                    },
                    {
                        "id": "tvs_ronin_bike",
                        "title": "TVS Ronin",
                        
                    },
                    {
                        "id": "apache_rtr_310",
                        "title": "Apache RTR 310",
                        
                    }
                ]
            }
        ]
        
        payload = {
            "to": phone_number,
            "body": f"{greeting}\n\nSelect the model you're interested in:",
            "button_text": "Select Vehicle",
            "sections": sections
        }
        
        try:
            print("🚀 Sending vehicle menu via backend...")
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(BACKEND_SEND_LIST_URL, json=payload)
                response.raise_for_status()
            
            print("✅ Vehicle menu sent successfully")
        
        except Exception as e:
            print(f"❌ Error sending vehicle menu: {e}")
            # Send error message via API instead of dispatcher
            error_payload = {
                "to": phone_number,
                "message": "Sorry, couldn't load vehicle menu. How can I assist you?"
            }
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    await client.post(BACKEND_SEND_MESSAGE_URL, json=error_payload)
            except Exception as inner_e:
                print(f"❌ Fallback error message also failed: {inner_e}")
        
        return []


class ActionTalkToAgent(Action):
    def name(self) -> Text:
        return "action_talk_to_agent"

    async def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get customer details
        customer_phone = tracker.sender_id
        customer_name = tracker.get_slot("user_name") or "Customer"
        
        # Agent phone number
        agent_phone = "918529750269"
        
        # Payload for customer message
        customer_payload = {
            "to": customer_phone,
            "message": "Connecting you to our agent. Please hold on..."
        }
        
        # Payload for agent notification
        agent_payload = {
            "agent_phone": agent_phone,
            "customer_name": customer_name,
            "customer_phone": customer_phone
        }
        
        try:
            # Send message to customer via FastAPI
            print("📤 Sending contact info to customer via FastAPI...")
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(BACKEND_SEND_MESSAGE_URL, json=customer_payload)
                response.raise_for_status()
            print("✅ Contact info sent to customer")
            
            # Notify agent via FastAPI
            print("📢 Notifying agent via FastAPI...")
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(BACKEND_NOTIFY_AGENT_URL, json=agent_payload)
                response.raise_for_status()
            print("✅ Agent notified successfully")
        
        except Exception as e:
            print(f"❌ Error in talk to agent action: {e}")
            # Send error via API
            error_payload = {
                "to": customer_phone,
                "text": "Sorry, couldn't connect to agent at the moment. Please try again."
            }
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    await client.post(BACKEND_SEND_MESSAGE_URL, json=error_payload)
            except Exception as inner_e:
                print(f"❌ Fallback error message also failed: {inner_e}")
        
        return []
    
    

class ActionStoreVehicleChoice(Action):
    def name(self) -> Text:
        return "action_store_vehicle_choice"

    async def run(self,
                  dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        phone_number = tracker.sender_id
        user_message = tracker.latest_message.get('text', '').lower().strip()
        vehicle_id = user_message if user_message in VEHICLE_DATA else None

        print(100*"-")
        print("Vehicle ID:", vehicle_id)
        print(100*"-")
        
        if not vehicle_id:
            error_payload = {
                "to": phone_number,
                "message": "Sorry, I couldn't identify the vehicle."
            }
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    await client.post(BACKEND_SEND_MESSAGE_URL, json=error_payload)
            except Exception as e:
                print(f"❌ Error sending error message: {e}")
            return []

        vehicle_name = VEHICLE_DATA[vehicle_id]['name']
        vehicle_image = VEHICLE_DATA[vehicle_id]['image_url']

        # Send only the image first
        image_payload = {
            "to": phone_number,
            "image_url": vehicle_image,
            # "caption": f"🏍️ {vehicle_name}"
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                await client.post(BACKEND_SEND_IMAGE_URL, json=image_payload)
            print(f"✅ Sent image for {vehicle_name}")
        except Exception as e:
            print(f"❌ Error sending image: {e}")
        
        # Store the vehicle choice
        return [SlotSet("chosen_vehicle", vehicle_name)]


class ActionShowVehicleDetails(Action):
    def name(self) -> Text:
        return "action_show_vehicle_details"

    async def run(self,
                  dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        phone_number = tracker.sender_id
        chosen_vehicle = tracker.get_slot("chosen_vehicle")
        
        if not chosen_vehicle:
            return []
        
        # Find vehicle ID from name
        vehicle_id = None
        for vid, vdata in VEHICLE_DATA.items():
            if vdata["name"] == chosen_vehicle:
                vehicle_id = vid
                break
        
        if not vehicle_id:
            return []
        
        vehicle_spec = VEHICLE_DATA[vehicle_id]['specs']
        
        # Send specs
        message_payload = {
            "to": phone_number,
            "message": vehicle_spec
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                await client.post(BACKEND_SEND_MESSAGE_URL, json=message_payload)
            print(f"✅ Sent specs for {chosen_vehicle}")
        except Exception as e:
            print(f"❌ Error sending specs: {e}")
        
        # Send action options
        sections = [
            {
                "title": f"{chosen_vehicle}?",
                "rows": [
                    {
                        "id": "get_brochure",
                        "title": "📄 Get Brochure",
                        "description": "Get brochure"
                    },
                    {
                        "id": "book_test_ride",
                        "title": "🏍️ Book Test Ride",
                        "description": "Book test ride"
                    },
                    {
                        "id": "get_price_or_EMI",
                        "title": "💰 Get Price/EMI",
                        "description": "Know price/EMI"
                    }
                ]
            }
        ]
        
        button_payload = {
            "to": phone_number,
            "body": f"What would you like to do with {chosen_vehicle}?",
            "button_text": "Choose Action",
            "sections": sections
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(BACKEND_SEND_LIST_URL, json=button_payload)
                response.raise_for_status()
            print(f"✅ Sent action options for {chosen_vehicle}")
        except Exception as e:
            print(f"❌ Error sending options: {e}")
        
        return []
    

class ActionAskPincode(Action):
    def name(self) -> Text:
        return "action_ask_pincode"

    async def run(self,
                  dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # ✅ Get phone from metadata first (consistent with other actions)
        phone_number = (
            tracker.latest_message.get("metadata", {}).get("phone")
            or tracker.get_slot("phone")
            or tracker.sender_id
        )
        
        print(f"📞 Phone resolved as: {phone_number}")
        
        if not phone_number:
            print("❌ Phone not found, aborting")
            return []
        
        chosen_vehicle = tracker.get_slot("chosen_vehicle")
        
        # Ask for pincode
        message = f"To show you the on-road price and EMI options for *{chosen_vehicle}*, please share your pincode. 📍"
        
        payload = {
            "to": phone_number,
            "message": message
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                await client.post(BACKEND_SEND_MESSAGE_URL, json=payload)
            print(f"✅ Asked for pincode for {chosen_vehicle}")
        except Exception as e:
            print(f"❌ Error asking for pincode: {e}")
        
        return []
    


class ActionStorePincodeAndShowPricing(Action):
    def name(self) -> Text:
        return "action_store_pincode_and_show_pricing"

    async def run(self,
                  dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # 1️⃣ Extract pincode entity (same pattern as name)
        pincode = next(tracker.get_latest_entity_values("pincode"), None)

        print(100*"-")
        print(100*"-")
        print(f"Extracted pincode entity: {pincode}")
        print(100*"-")
        
        # Fallback: if no entity, try to extract from text (6 digits)
        if not pincode:
            user_message = tracker.latest_message.get('text', '').strip()
            # Simple validation: 6 digits
            if user_message.isdigit() and len(user_message) == 6:
                pincode = user_message
        
        print(f"📍 Extracted pincode: {pincode}")
        
        if not pincode:
            # 2️⃣ Resolve phone number
            phone = (
                tracker.latest_message.get("metadata", {}).get("phone")
                or tracker.get_slot("phone")
                or tracker.sender_id
            )
            
            error_payload = {
                "to": phone,
                "message": "Please enter a valid 6-digit pincode. 📍"
            }
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    await client.post(BACKEND_SEND_MESSAGE_URL, json=error_payload)
            except Exception as e:
                print(f"❌ Error sending pincode error: {e}")
            return []
        
        # Validate pincode format
        if not pincode.isdigit() or len(pincode) != 6:
            phone = (
                tracker.latest_message.get("metadata", {}).get("phone")
                or tracker.get_slot("phone")
                or tracker.sender_id
            )
            
            error_payload = {
                "to": phone,
                "message": "Please enter a valid 6-digit pincode. 📍"
            }
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    await client.post(BACKEND_SEND_MESSAGE_URL, json=error_payload)
            except Exception as e:
                print(f"❌ Error sending validation error: {e}")
            return []
        
        # 3️⃣ Resolve phone number (after validation)
        phone = (
            tracker.latest_message.get("metadata", {}).get("phone")
            or tracker.get_slot("phone")
            or tracker.sender_id
        )
        
        print(f"📞 Phone resolved as: {phone}")
        
        if not phone:
            print("❌ Phone missing, aborting")
            return []
        
        chosen_vehicle = tracker.get_slot("chosen_vehicle")
        
        # 4️⃣ Update lead via backend (same pattern as name storage)
        update_payload = {
            "phone": phone,
            "updates": {
                "pincode": pincode
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    BACKEND_LEAD_UPDATE_URL,
                    json=update_payload
                )
                if resp.status_code != 200:
                    print(f"❌ Lead update failed: {resp.text}")
                else:
                    print(f"✅ Pincode {pincode} stored in lead for {phone}")
        except Exception as e:
            print(f"❌ Error updating lead with pincode: {e}")
        
        # 5️⃣ Get ex-showroom price from VEHICLE_DATA
        ex_showroom_price = None
        for vid, vdata in VEHICLE_DATA.items():
            if vdata["name"] == chosen_vehicle:
                ex_showroom_price = vdata.get("ex_showroom_price")
                break

        if not ex_showroom_price:
            print(f"❌ Ex-showroom price not found for {chosen_vehicle}")
            ex_showroom_price = 115000  # Fallback

        # Format price (convert to L for lakhs if > 100000)
        if ex_showroom_price >= 100000:
            formatted_price = f"₹{ex_showroom_price // 100000}.{ex_showroom_price % 100000 // 10000}L"
        else:
            formatted_price = f"₹{ex_showroom_price:,}"

        # 6️⃣ Send pricing message with dynamic price
        pricing_message = f"""
        Thanks for sharing your pincode!
        The ex-showroom price of **{chosen_vehicle}** starts from **{formatted_price}**.
        Our TVS sales executive will contact you shortly with the **best on-road price & EMI options** available for your area.
        """.strip()

        payload = {
            "to": phone,
            "message": pricing_message
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                await client.post(BACKEND_SEND_MESSAGE_URL, json=payload)
            print(f"✅ Sent pricing info for {chosen_vehicle}")
        except Exception as e:
            print(f"❌ Error sending pricing: {e}")

        # 7️⃣ Set slot so pincode is available for future actions
        return [SlotSet("pincode", pincode)]