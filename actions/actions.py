from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import httpx

BACKEND_SLOT_URL = "http://localhost:8000/available-slots"
BACKEND_BOOK_URL = "http://localhost:8000/book-slot"
BACKEND_SEND_LIST_URL = "http://localhost:8000/send-list"
BACKEND_SEND_BROCHURE_URL = "http://localhost:8000/send-brochure"
BACKEND_BOOK_TEST_RIDE_URL = "http://localhost:8000/book-test-ride"
BACKEND_SEND_MESSAGE_URL = "http://localhost:8000/send-message"
BACKEND_NOTIFY_AGENT_URL = "http://localhost:8000/notify-agent"


VEHICLE_DATA = {
    "apache_rtr_160": {
        "name": "Apache RTR 160",
        "specs": """
🏍️ *Apache RTR 160*

⚙️ *Engine:* 159.7cc, Oil-cooled
💪 *Power:* 17.55 PS @ 9250 rpm
⚡ *Torque:* 14.73 Nm @ 7250 rpm
📊 *Mileage:* 45-50 km/l
⚖️ *Weight:* 139 kg
💰 *Price:* ₹1,15,000 onwards

✨ *Key Features:*
• Race-tuned Fuel Injection
• SmartXonnect Bluetooth
• LED Headlamp with DRL
• Single Channel ABS

🎨 *Available Colors:*
Racing Red, Matte Black, Pearl White
        """,
        "brochure_url": "https://www.tvsmotor.com/tvs-apache/-/media/Brand-Pages/Apache/Brochure/TVS-Apache-RTR-160-Brochure_V4.pdf"
    },
    "apache_200_4v": {
        "name": "Apache 200 4V",
        "specs": """
🏍️ *Apache 200 4V*

⚙️ *Engine:* 197.75cc, Oil-cooled
💪 *Power:* 20.82 PS @ 9000 rpm
⚡ *Torque:* 17.25 Nm @ 7250 rpm
📊 *Mileage:* 38-42 km/l
⚖️ *Weight:* 152 kg
💰 *Price:* ₹1,42,000 onwards

✨ *Key Features:*
• 4-Valve Engine Technology
• Dual Channel ABS
• 3 Riding Modes (Sport, Urban, Rain)
• GTT (Glide Through Traffic)
• Smartphone Connectivity

🎨 *Available Colors:*
Knight Black, Racing Red, Pearl White
        """,
        "brochure_url": "https://www.tvsmotor.com/tvs-apache/-/media/Brand-Pages/Apache/Brochure/TVS-Apache-200-4V-Brochure_V4.pdf"
    },
    "tvs_jupiter": {
        "name": "TVS Jupiter",
        "specs": """
🛵 *TVS Jupiter*

⚙️ *Engine:* 109.7cc, Air-cooled
💪 *Power:* 7.88 PS @ 7500 rpm
⚡ *Torque:* 8.8 Nm @ 5500 rpm
📊 *Mileage:* 62 km/l
⚖️ *Weight:* 108 kg
💰 *Price:* ₹73,000 onwards

✨ *Key Features:*
• Econometer for fuel efficiency
• LED Headlamp
• USB Charger
• 33L Under Seat Storage
• External Fuel Filler Cap

🎨 *Available Colors:*
Titanium Grey, Starlight Blue, Volcano Red
        """,
        "brochure_url": "https://www.tvsmotor.com/tvs-jupiter/-/media/Brand-Pages/Jupiter/Brochure/TVS-Jupiter-Brochure_V4.pdf"
    },
    "tvs_ronin": {
        "name": "TVS Ronin",
        "specs": """
🏍️ *TVS Ronin*

⚙️ *Engine:* 225.9cc, Oil-cooled
💪 *Power:* 20.4 PS @ 7750 rpm
⚡ *Torque:* 19.93 Nm @ 3750 rpm
📊 *Mileage:* 35-38 km/l
⚖️ *Weight:* 159 kg
💰 *Price:* ₹1,49,000 onwards

✨ *Key Features:*
• 3 Riding Modes (Urban, Roll, Rain)
• Dual Channel ABS
• TFT Display with Bluetooth
• Cruise Control
• LED Lighting
• Inverted Front Suspension

🎨 *Available Colors:*
Stargaze Black, Canyon Copper, Tornado Grey
        """,
        "brochure_url": "https://www.tvsmotor.com/tvs-ronin/-/media/Brand-Pages/Ronin/Brochure/TVS-Ronin-Brochure_V4.pdf"
    }
}


class ActionStoreName(Action):
    def name(self):
        return "action_store_name"

    def run(self, dispatcher, tracker, domain):
        # The entire user message is treated as name
        name = tracker.latest_message.get("text")

        # Clean name (optional)
        name = name.strip()

        return [SlotSet("user_name", name)]
    
class ActionShowVehicleList(Action):
    def name(self) -> Text:
        return "action_show_vehicle_list"

    async def run(self,
                  dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        phone_number = tracker.sender_id
        
        sections = [
            {
                "title": "🏍️ Our Vehicle Collection",
                "rows": [
                    {
                        "id": "apache_rtr_160",
                        "title": "Apache RTR 160",
                        "description": "₹1,15,000 • 159.7cc • 17.55 PS"
                    },
                    {
                        "id": "apache_200_4v",
                        "title": "Apache 200 4V",
                        "description": "₹1,42,000 • 197.75cc • 20.82 PS"
                    },
                    {
                        "id": "tvs_jupiter",
                        "title": "TVS Jupiter",
                        "description": "₹73,000 • 109.7cc • 7.88 PS"
                    },
                    {
                        "id": "tvs_ronin",
                        "title": "TVS Ronin",
                        "description": "₹1,49,000 • 225.9cc • 20.4 PS"
                    }
                ]
            }
        ]
        
        payload = {
            "to": phone_number,
            "header": "Our Vehicles 🏍️",
            "body": "Select a vehicle to see detailed specifications:",
            "button_text": "Select Vehicle",
            "sections": sections
        }
        
        try:
            print("🚀 Sending vehicle list via backend...")
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(BACKEND_SEND_LIST_URL, json=payload)
                response.raise_for_status()
            
            print("✅ Vehicle list sent successfully")
        
        except Exception as e:
            print(f"❌ Error sending vehicle list: {e}")
            dispatcher.utter_message(text="Sorry, couldn't load vehicles.")
        
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
                "pdf_url": "https://www.tvsmotor.com/tvs-apache/-/media/Brand-Pages/Apache/Brochure/TVS-Apache-200-4V-Brochure_V4.pdf",
                "filename": "TVS_Apache_200_4V_Brochure.pdf",
                "caption": "📄 TVS Apache 200 4V - Complete Brochure"
            },
            "TVS Jupiter": {
                "pdf_url": "https://www.tvsmotor.com/tvs-jupiter/-/media/Brand-Pages/Jupiter/Brochure/TVS-Jupiter-Brochure_V4.pdf",
                "filename": "TVS_Jupiter_Brochure.pdf",
                "caption": "📄 TVS Jupiter - Complete Brochure"
            },
            "TVS Ronin": {
                "pdf_url": "https://www.tvsmotor.com/tvs-ronin/-/media/Brand-Pages/Ronin/Brochure/TVS-Ronin-Brochure_V4.pdf",
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
                    text=f"✅ {chosen_vehicle} brochure has been sent! Check your messages."
                )
            except Exception as e:
                print(f"❌ Error sending brochure: {e}")
                dispatcher.utter_message(
                    text="Sorry, I couldn't send the brochure at the moment. Please try again later."
                )
        
        else:
            # If no vehicle selected, show all brochures as options
            dispatcher.utter_message(
                text="📚 Please select a vehicle to receive its brochure:",
                buttons=[
                    {"title": "Apache RTR 160", "payload": "/vehicle_selected{\"vehicle\":\"apache_rtr_160\"}"},
                    {"title": "Apache 200 4V", "payload": "/vehicle_selected{\"vehicle\":\"apache_200_4v\"}"},
                    {"title": "TVS Jupiter", "payload": "/vehicle_selected{\"vehicle\":\"tvs_jupiter\"}"},
                    {"title": "TVS Ronin", "payload": "/vehicle_selected{\"vehicle\":\"tvs_ronin\"}"}
                ]
            )
        
        return []



class ActionStoreVehicleChoiceAndShowDetails(Action):
    def name(self) -> Text:
        return "action_store_vehicle_choice_and_show_details"

    async def run(self,
                  dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        phone_number = tracker.sender_id
        
        # Get the vehicle ID from user message
        user_message = tracker.latest_message.get('text', '').lower().strip()
        
        vehicle_id = None
        for vid in VEHICLE_DATA.keys():
            if vid in user_message:
                vehicle_id = vid
                break
        
        if not vehicle_id:
            dispatcher.utter_message(text="Sorry, I couldn't identify the vehicle.")
            return []
        
        vehicle = VEHICLE_DATA[vehicle_id]
        vehicle_name = vehicle["name"]
        specs = vehicle["specs"]
        
        # Send specs via FastAPI
        message_payload = {
            "to": phone_number,
            "message": specs
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                await client.post(BACKEND_SEND_MESSAGE_URL, json=message_payload)
            print(f"✅ Sent specs for {vehicle_name}")
        except Exception as e:
            print(f"❌ Error sending specs: {e}")
        
        # Return buttons via dispatcher (FastAPI webhook will handle them)
        dispatcher.utter_message(
            text=f"What would you like to do with {vehicle_name}?",
            buttons=[
                {
                    "title": "📄 Get Brochure",
                    "payload": "brochure_request"
                },
                {
                    "title": "🏍️ Book Test Ride",
                    "payload": "book_test_ride"
                }
            ]
        )
        
        return [SlotSet("chosen_vehicle", vehicle_name)] 

class ActionGreetWithMenu(Action):
    def name(self) -> Text:
        return "action_greet_with_menu"

    async def run(self,
                  dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        phone_number = tracker.sender_id
        
        # Prepare menu sections with 4 options
        sections = [
            {
                "title": "🏍️ How can we help?",
                "rows": [
                    {
                        "id": "view_vehicles",
                        "title": "View Vehicles",
                        "description": "See our bike collection"
                    },
                    {
                        "id": "book_test_ride",
                        "title": "Book Test Ride",
                        "description": "Schedule a test ride"
                    },
                    {
                        "id": "brochure_request",
                        "title": "Get Brochure",
                        "description": "Download bike brochures"
                    },
                    {
                        "id": "talk_to_agent",
                        "title": "Talk to Agent",
                        "description": "Connect with our team"
                    }
                ]
            }
        ]
        
        payload = {
            "to": phone_number,
            "header": "Welcome to TVS MOTORS! 🏍️",
            "body": "We're here to help you find your perfect ride. What would you like to do today?",
            "button_text": "View Options",
            "sections": sections
        }
        
        try:
            print("🚀 Sending greeting menu via backend...")
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(BACKEND_SEND_LIST_URL, json=payload)
                response.raise_for_status()
            
            print("✅ Greeting menu sent successfully")
        
        except Exception as e:
            print(f"❌ Error sending greeting menu: {e}")
            # Fallback to text message
            dispatcher.utter_message(
                text="Welcome to TVS MOTORS! 🏍️\nHow can we assist you today?"
            )
        
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
        agent_phone = "918292253230"
        
        # WhatsApp link
        whatsapp_link = f"https://wa.me/{agent_phone}?text=Hi,%20I%20need%20assistance%20with%20TVS%20bikes"
        
        # Message to send to customer
        customer_message = f"""
        *Connecting you to our sales team...*

        📞 *Contact Us:*
        • Phone: +91-9962949643
        • WhatsApp: Click here 👇
        {whatsapp_link}
        • Email: support@blrtvsmotors.com

        📍 *Visit Us:*
        BLR TVS MOTORS
        [Your Showroom Address]
        Bangalore, Karnataka

        ⏰ *Working Hours:*
        Mon-Sat: 9:00 AM - 7:00 PM
        Sunday: 10:00 AM - 6:00 PM

        Our team will respond shortly! 🚀
        """.strip()
        
        # Payload for customer message
        customer_payload = {
            "to": customer_phone,
            "message": customer_message
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
            dispatcher.utter_message(
                text="Sorry, couldn't connect to agent at the moment. Please try again."
            )
        
        return []
    

class ActionAskNameForTestRide(Action):
    def name(self) -> Text:
        return "action_ask_name_for_test_ride"

    async def run(self,
                  dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        phone_number = tracker.sender_id
        chosen_vehicle = tracker.get_slot("chosen_vehicle")
        
        if not chosen_vehicle:
            dispatcher.utter_message(text="Please select a vehicle first.")
            return []
        
        message = f"Great! You're booking a test ride for *{chosen_vehicle}* 🏍️\n\nMay I know your name?"
        
        payload = {
            "to": phone_number,
            "message": message
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                await client.post(BACKEND_SEND_MESSAGE_URL, json=payload)
        except Exception as e:
            print(f"❌ Error asking name: {e}")
            dispatcher.utter_message(text="May I know your name?")
        
        return []
    

class ActionBookTestRide(Action):
    def name(self) -> Text:
        return "action_book_test_ride"

    async def run(self,
                  dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        phone_number = tracker.sender_id
        user_name = tracker.get_slot("user_name")
        chosen_vehicle = tracker.get_slot("chosen_vehicle")
        
        if not user_name or not chosen_vehicle:
            dispatcher.utter_message(text="Missing information. Please start again.")
            return []
        
        payload = {
            "phone": phone_number,
            "name": user_name,
            "vehicle": chosen_vehicle
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(BACKEND_BOOK_TEST_RIDE_URL, json=payload)
                response.raise_for_status()
            
            confirmation_message = f"""
✅ *Test Ride Booked Successfully!*

👤 Name: {user_name}
🏍️ Vehicle: {chosen_vehicle}
📞 Phone: {phone_number}

📍 Location: BLR TVS MOTORS
⏰ Our team will contact you shortly to confirm the date and time.

Thank you for choosing TVS Motors! 🚀
            """.strip()
            
            message_payload = {
                "to": phone_number,
                "message": confirmation_message
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                await client.post(BACKEND_SEND_MESSAGE_URL, json=message_payload)
            
            print(f"✅ Test ride booked for {user_name} - {chosen_vehicle}")
        
        except Exception as e:
            print(f"❌ Error booking test ride: {e}")
            dispatcher.utter_message(text="Sorry, couldn't book the test ride. Please try again.")
        
        return []