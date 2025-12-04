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
        vehicle = tracker.get_slot("chosen_vehicle")
        phone = tracker.sender_id

        payload = {
            "name": name,
            "vehicle": vehicle if vehicle else "Not specified",
            "phone": phone
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(BACKEND_BOOK_TEST_RIDE_URL, json=payload)
                response.raise_for_status()

            # Confirmation to user
            vehicle_text = f" for {vehicle}" if vehicle else ""
            dispatcher.utter_message(
                text=f"🎉 Thanks {name}! Your test ride{vehicle_text} booking request has been received.\n\n📍 Location: BLR TVS MOTORS\n📞 Our team will contact you shortly to confirm the time.\n\nWe look forward to seeing you!"
            )
        except Exception as e:
            print(f"❌ Error booking test ride: {e}")
            dispatcher.utter_message(
                text="Sorry, there was an issue booking your test ride. Please try again or contact us directly."
            )

        return []


class ActionShowVehicleAvailability(Action):
    def name(self) -> Text:
        return "action_show_vehicle_availability"

    async def run(self,
                  dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get user's phone number from sender_id
        phone_number = tracker.sender_id
        
        # Prepare vehicle list sections
        sections = [
            {
                "title": "🏍️ Available Bikes",
                "rows": [
                    {
                        "id": "apache_rtr_160",
                        "title": "Apache RTR 160",
                        
                    },
                    {
                        "id": "apache_200_4v",
                        "title": "Apache 200 4V",
                        
                    },
                    {
                        "id": "tvs_jupiter",
                        "title": "TVS Jupiter"
                    },
                    {
                        "id": "tvs_ronin",
                        "title": "TVS Ronin"
                    }
                ]
            }
        ]
        
        # Prepare payload for backend
        payload = {
            "to": phone_number,
            "header": "🏍️ Vehicle Availability",
            "body": "Choose a vehicle to check availability and book:",
            "button_text": "View Vehicles",
            "sections": sections
        }
        
        try:
            # Call Backend API to send list message
            print("🚀 Sending vehicle list via backend...")
            print(f"Payload: {payload}")
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(BACKEND_SEND_LIST_URL, json=payload)
                response.raise_for_status()
            
            print("✅ Vehicle list sent successfully via backend")
        
        except httpx.HTTPStatusError as e:
            print(f"❌ HTTP Error sending vehicle list: {e.response.status_code} - {e.response.text}")
            dispatcher.utter_message(text="Sorry, I couldn't fetch vehicle availability at the moment. Please try again.")
        except Exception as e:
            print(f"❌ Error sending vehicle list: {e}")
            dispatcher.utter_message(text="Sorry, I couldn't fetch vehicle availability at the moment. Please try again.")
        
        return []


class ActionShowVehicleListForTestRide(Action):
    def name(self) -> Text:
        return "action_show_vehicle_list_for_test_ride"

    async def run(self,
                  dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get user's phone number from sender_id
        phone_number = tracker.sender_id
        
        # Prepare vehicle list sections (same as vehicle availability)
        sections = [
            {
                "title": "🏍️ Available Vehicles",
                "rows": [
                    {
                        "id": "apache_rtr_160",
                        "title": "Apache RTR 160",
                        
                    },
                    {
                        "id": "apache_200_4v",
                        "title": "Apache 200 4V",
                        
                    },
                    {
                        "id": "tvs_jupiter",
                        "title": "TVS Jupiter"
                    },
                    {
                        "id": "tvs_ronin",
                        "title": "TVS Ronin"
                    }
                ]
            }
        ]
        
        # Prepare payload for backend
        payload = {
            "to": phone_number,
            "header": "🏍️ Select Vehicle for Test Ride",
            "body": "Which bike would you like to test ride?",
            "button_text": "Select Vehicle",
            "sections": sections
        }
        
        try:
            # Call Backend API to send list message
            print("🚀 Sending test ride vehicle list via backend...")
            print(f"Payload: {payload}")
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(BACKEND_SEND_LIST_URL, json=payload)
                response.raise_for_status()
            
            print("✅ Test ride vehicle list sent successfully via backend")
        
        except httpx.HTTPStatusError as e:
            print(f"❌ HTTP Error sending test ride vehicle list: {e.response.status_code} - {e.response.text}")
            dispatcher.utter_message(text="Sorry, I couldn't show vehicle list at the moment. Please try again.")
        except Exception as e:
            print(f"❌ Error sending test ride vehicle list: {e}")
            dispatcher.utter_message(text="Sorry, I couldn't show vehicle list at the moment. Please try again.")
        
        return []


class ActionStoreVehicleChoice(Action):
    def name(self) -> Text:
        return "action_store_vehicle_choice"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get the vehicle ID from the user's selection
        vehicle_id = tracker.latest_message.get("text")
        
        # Detailed vehicle information
        vehicle_details = {
            "apache_rtr_160": {
                "name": "Apache RTR 160",
                "price": "₹1,12,000",
                "engine": "160cc, Single Cylinder",
                "mileage": "45-50 km/l",
                "power": "17.55 PS @ 9250 rpm",
                "features": "Race-tuned Fuel Injection, ABS, SmartXonnect",
                "colors": "Racing Red, Matte Black, Pearl White"
            },
            "apache_200_4v": {
                "name": "Apache 200 4V",
                "price": "₹1,42,000",
                "engine": "200cc, 4-Valve",
                "mileage": "35-40 km/l",
                "power": "20.8 PS @ 9000 rpm",
                "features": "4-Valve Engine, Dual Channel ABS, Riding Modes",
                "colors": "Knight Black, Racing Red, White"
            },
            "tvs_jupiter": {
                "name": "TVS Jupiter",
                "price": "₹73,400",
                "engine": "110cc, CVTi Engine",
                "mileage": "62 km/l",
                "power": "7.88 PS @ 7500 rpm",
                "features": "Econometer, LED Headlamp, USB Charger, 33L Storage",
                "colors": "Titanium Grey, Starlight Blue, Volcano Red"
            },
            "tvs_ronin": {
                "name": "TVS Ronin",
                "price": "₹1,49,000",
                "engine": "225.9cc, Single Cylinder",
                "mileage": "35-38 km/l",
                "power": "20.4 PS @ 7750 rpm",
                "features": "3 Riding Modes, Dual Channel ABS, TFT Display, Cruise Control",
                "colors": "Stargaze Black, Canyon Copper, Tornado Grey"
            }
        }
        
        # Get vehicle details
        vehicle = vehicle_details.get(vehicle_id)
        
        if vehicle:
            # Create detailed message
            message = f"""
🏍️ *{vehicle['name']}*

💰 *Price:* {vehicle['price']}
⚙️ *Engine:* {vehicle['engine']}
⛽ *Mileage:* {vehicle['mileage']}
🔥 *Power:* {vehicle['power']}

✨ *Key Features:*
{vehicle['features']}

🎨 *Available Colors:*
{vehicle['colors']}

📍 *Available at BLR TVS MOTORS*

What would you like to do next?
            """
            
            # Send message with buttons for next actions
            buttons = [
                {"title": "Book Test Ride", "payload": "/book_test_ride"},
                {"title": "Get Brochure", "payload": "/brochure_request"},
                {"title": "View Other Vehicles", "payload": "/vehicle_availability"}
            ]
            
            dispatcher.utter_message(text=message.strip(), buttons=buttons)
        else:
            dispatcher.utter_message(text="Sorry, I couldn't find details for that vehicle.")
        
        # Store in slot
        return [SlotSet("chosen_vehicle", vehicle.get("name", vehicle_id) if vehicle else vehicle_id)]


class ActionStoreVehicleChoiceForTestRide(Action):
    def name(self) -> Text:
        return "action_store_vehicle_choice_for_test_ride"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get the vehicle ID from the user's selection
        vehicle_id = tracker.latest_message.get("text")
        
        # Map vehicle IDs to readable names
        vehicle_map = {
            "apache_rtr_160": "Apache RTR 160",
            "apache_200_4v": "Apache 200 4V",
            "tvs_jupiter": "TVS Jupiter",
            "tvs_ronin": "TVS Ronin"
        }
        
        vehicle_name = vehicle_map.get(vehicle_id, vehicle_id)
        
        # Store in slot and ask for name
        dispatcher.utter_message(text=f"Great! You selected {vehicle_name} for test ride. May I know your name?")
        
        return [SlotSet("chosen_vehicle", vehicle_name)]


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
                        "id": "vehicle_availability",
                        "title": "Vehicle Availability",
                        "description": "Check available bikes"
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