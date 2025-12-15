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
        "specs": "🏍️ *Apache RTR 160*\n\n⚙️ *Engine:* 159.7cc, Oil-cooled\n💨 *Power:* 17.55 PS @ 8500 rpm\n🔧 *Torque:* 14.73 Nm @ 7000 rpm\n⚖️ *Weight:* 138 kg\n⛽ *Fuel Tank:* 12 Litres\n💰 *Price:* ₹1,15,000 (Ex-showroom)\n\nFor more details, visit: https://www.tvsmotor.com/tvs-apache/rtr-160"
    },
    "apache_200_4v": {
        "name": "Apache 200 4V",
        "specs": "🏍️ *Apache 200 4V*\n\n⚙️ *Engine:* 197.75cc, Oil-cooled\n💨 *Power:* 20.82 PS @ 8500 rpm\n🔧 *Torque:* 16.8 Nm @ 7250 rpm\n⚖️ *Weight:* 153 kg\n⛽ *Fuel Tank:* 12 Litres\n💰 *Price:* ₹1,42,000 (Ex-showroom)\n\nFor more details, visit: https://www.tvsmotor.com/tvs-apache/apache-200-4v"
    },
    "tvs_jupiter": {
        "name": "TVS Jupiter",
        "specs": "🏍️ *TVS Jupiter*\n\n⚙️ *Engine:* 109.7cc, Air-cooled\n💨 *Power:* 7.88 PS @ 7500 rpm\n🔧 *Torque:* 8.4 Nm @ 5500 rpm\n⚖️ *Weight:* 108 kg\n⛽ *Fuel Tank:* 6.5 Litres\n💰 *Price:* ₹73,000 (Ex-showroom)\n\nFor more details, visit: https://www.tvsmotor.com/tvs-jupiter-125"
    },  
    "tvs_ronin": {
        "name": "TVS Ronin",
        "specs": "🏍️ *TVS Ronin*\n\n⚙️ *Engine:* 225.9cc, Oil-cooled\n💨 *Power:* 20.4 PS @ 7500 rpm\n🔧 *Torque:* 19.93 Nm @ 6000 rpm\n⚖️ *Weight:* 162 kg\n⛽ *Fuel Tank:* 12 Litres\n💰 *Price:* ₹1,49,000 (Ex-showroom)\n\nFor more details, visit: https://www.tvsmotor.com/tvs-ronin"
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

        print("Storing user name:", name)

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
            # Send error via API
            error_payload = {
                "to": phone_number,
                "text": "Sorry, couldn't load vehicles."
            }
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    await client.post(BACKEND_SEND_MESSAGE_URL, json=error_payload)
            except Exception as inner_e:
                print(f"❌ Fallback error message also failed: {inner_e}")
        
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
                
                # Send success message via API
                success_payload = {
                    "to": phone_number,
                    "text": f"✅ {chosen_vehicle} brochure has been sent!"
                }
                async with httpx.AsyncClient() as client:
                    await client.post(BACKEND_SEND_MESSAGE_URL, json=success_payload)
            except Exception as e:
                print(f"❌ Error sending brochure: {e}")
                # Send error via API
                error_payload = {
                    "to": phone_number,
                    "text": "Sorry, I couldn't send the brochure at the moment. Please try again later."
                }
                try:
                    async with httpx.AsyncClient() as client:
                        await client.post(BACKEND_SEND_MESSAGE_URL, json=error_payload)
                except Exception as inner_e:
                    print(f"❌ Fallback error message also failed: {inner_e}")
        
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
                            "id": "tvs_ronin",
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
                # Send error via API
                error_payload = {
                    "to": phone_number,
                    "text": "Sorry, couldn't load brochure options."
                }
                try:
                    async with httpx.AsyncClient(timeout=10.0) as client:
                        await client.post(BACKEND_SEND_MESSAGE_URL, json=error_payload)
                except Exception as inner_e:
                    print(f"❌ Fallback error message also failed: {inner_e}")
        
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
        
        vehicle_id = user_message if user_message in VEHICLE_DATA else None
        
        if not vehicle_id:
            # Send error via API
            error_payload = {
                "to": phone_number,
                "text": "Sorry, I couldn't identify the vehicle."
            }
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    await client.post(BACKEND_SEND_MESSAGE_URL, json=error_payload)
            except Exception as inner_e:
                print(f"❌ Fallback error message also failed: {inner_e}")
            return []

        vehicle_name, vehicle_spec = VEHICLE_DATA[vehicle_id]['name'], VEHICLE_DATA[vehicle_id]['specs']

        print("Vehicle selected:", vehicle_name)
        print("Vehicle specs:", vehicle_spec)

        # Send specs via FastAPI
        message_payload = {
            "to": phone_number,
            "message": vehicle_spec
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                await client.post(BACKEND_SEND_MESSAGE_URL, json=message_payload)
            print(f"✅ Sent specs for {vehicle_name}")
        except Exception as e:
            print(f"❌ Error sending specs: {e}")
        
        sections = [
            {
                "title": f"{vehicle_name}?",
                "rows": [
                    {
                        "id": "get_brochure",
                        "title": "📄 Get Brochure",
                        "description": "Receive the full brochure"
                    },
                    {
                        "id": "book_test_ride",
                        "title": "🏍️ Book Test Ride",
                        "description": "Schedule a test ride"
                    }
                ]
            }
        ]
        
        button_payload = {
            "to": phone_number,
            "header": f"Options for {vehicle_name}",
            "body": f"What would you like to do with {vehicle_name}?",
            "button_text": "Choose Action",
            "sections": sections
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(BACKEND_SEND_LIST_URL, json=button_payload)
                response.raise_for_status()
        except Exception as e:
            print(f"❌ Error sending options: {e}")
            # Send error via API
            error_payload = {
                "to": phone_number,
                "text": f"Sorry, couldn't load options for {vehicle_name}."
            }
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    await client.post(BACKEND_SEND_MESSAGE_URL, json=error_payload)
            except Exception as inner_e:
                print(f"❌ Fallback error message also failed: {inner_e}")
        
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
            "body": "How can I help you today?\nYou can ask about prices, test rides, vehicles, or offers.",
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
            # Send error message via API instead of dispatcher
            error_payload = {
                "to": phone_number,
                "text": "Welcome to TVS MOTORS! 🏍️\nSorry, menu loading failed. How can I assist you?"
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
            # Send error via API
            error_payload = {
                "to": phone_number,
                "text": "Please select a vehicle first."
            }
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    await client.post(BACKEND_SEND_MESSAGE_URL, json=error_payload)
            except Exception as inner_e:
                print(f"❌ Fallback error message also failed: {inner_e}")
            return []
        
        message = f"Great! You're booking a test ride for *{chosen_vehicle}* 🏍️\n\nMay I know your name?"
        
        payload = {
            "to": phone_number,
            "text": message
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                await client.post(BACKEND_SEND_MESSAGE_URL, json=payload)
        except Exception as e:
            print(f"❌ Error asking name: {e}")
            # Send error via API
            error_payload = {
                "to": phone_number,
                "text": "May I know your name?"
            }
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    await client.post(BACKEND_SEND_MESSAGE_URL, json=error_payload)
            except Exception as inner_e:
                print(f"❌ Fallback error message also failed: {inner_e}")
        
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

        print("Booking test ride for:", user_name, chosen_vehicle)
        
        if not user_name or not chosen_vehicle:
            # Send error via API
            error_payload = {
                "to": phone_number,
                "text": "Missing information. Please start again."
            }
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    await client.post(BACKEND_SEND_MESSAGE_URL, json=error_payload)
            except Exception as inner_e:
                print(f"❌ Fallback error message also failed: {inner_e}")
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
            
            message_payload = {
                "to": phone_number,
                "text": f"✅ Test ride booked for {user_name} on {chosen_vehicle}! We'll contact you soon."
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                await client.post(BACKEND_SEND_MESSAGE_URL, json=message_payload)
            
            print(f"✅ Test ride booked for {user_name} - {chosen_vehicle}")
        
        except Exception as e:
            print(f"❌ Error booking test ride: {e}")
            # Send error via API
            error_payload = {
                "to": phone_number,
                "text": "Sorry, couldn't book the test ride. Please try again."
            }
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    await client.post(BACKEND_SEND_MESSAGE_URL, json=error_payload)
            except Exception as inner_e:
                print(f"❌ Fallback error message also failed: {inner_e}")
        
        return []