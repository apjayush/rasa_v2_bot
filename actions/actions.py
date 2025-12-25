from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker, ValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import httpx
import asyncio
import os
from rasa_sdk.types import DomainDict
import re
import logging
import logging.config
from pathlib import Path
import yaml 


os.makedirs('logs', exist_ok=True)

# Set up logging
log_config_path = Path("logging.yml")
if log_config_path.exists():
    with open(log_config_path, 'r') as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)

logger = logging.getLogger('actions')

# Helper function for sending messages
async def send_message(phone: str, message: str, dispatcher: CollectingDispatcher):
    """Send message via backend in production, dispatcher in test"""
    if IS_TEST_ENV:
        dispatcher.utter_message(text=message)
    else:
        payload = {"to": phone, "message": message}
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                await client.post(BACKEND_SEND_MESSAGE_URL, json=payload)
        except Exception as e:
            logger.exception(f"Error sending message: {e}")

# from vehicle_data.vehicle_info import VEHICLE_DATA
# from ./ import VEHICLE_DATA

# Environment detection
# IS_TEST_ENV = False

BACKEND_BASE_URL = os.getenv(
    "BACKEND_BASE_URL",
    "http://incoweb-api:8000"
)


logger.info(f"BACKEND_BASE_URL = {BACKEND_BASE_URL}")

# logger.info(f"IS_TEST_ENV = {IS_TEST_ENV}")

BACKEND_SEND_LIST_URL = f"{BACKEND_BASE_URL}/send-list"
BACKEND_SEND_BROCHURE_URL = f"{BACKEND_BASE_URL}/send-brochure"
# BACKEND_BOOK_TEST_RIDE_URL = f"{BACKEND_BASE_URL}/book-test-ride"
BACKEND_SEND_MESSAGE_URL = f"{BACKEND_BASE_URL}/send-message"
BACKEND_NOTIFY_AGENT_URL = f"{BACKEND_BASE_URL}/notify-agent"
BACKEND_SEND_IMAGE_URL = f"{BACKEND_BASE_URL}/send-image"
BACKEND_LEAD_UPDATE_URL = f"{BACKEND_BASE_URL}/update_lead"
BACKEND_SEND_BUTTON_URL = f"{BACKEND_BASE_URL}/send-buttons"


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



class ValidatePredefinedSlots(ValidationAction):
    """Validates slots with predefined mappings."""
    
    def validate_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate name value."""
        
        logger.debug(f"🔍 Validating name: {slot_value}")
        
        # Check if name exists and has minimum length
        if not slot_value or not isinstance(slot_value, str):
            logger.warning("❌ Name validation failed: empty or not string")
            dispatcher.utter_message(response="utter_invalid_name")
            return {"name": None}
        
        # Remove extra whitespace
        name = slot_value.strip()
        
        # Check minimum length
        if len(name) < 2:
            logger.warning("❌ Name validation failed: too short")
            dispatcher.utter_message(response="utter_invalid_name")
            return {"name": None}
        
        # Check if contains at least some letters
        if not re.search(r'[a-zA-Z]', name):
            logger.warning("❌ Name validation failed: no letters")
            dispatcher.utter_message(response="utter_invalid_name")
            return {"name": None}
        
        # Capitalize properly
        logger.info(f"✅ Name validation passed: {name.title()}")
        return {"name": name.title()}
    
    def validate_pincode(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate pincode value."""
        
        logger.debug(f"🔍 Validating pincode: {slot_value}")
        
        if not slot_value:
            logger.warning("❌ Pincode validation failed: empty")
            dispatcher.utter_message(response="utter_invalid_pincode")
            return {"pincode": None}
        
        # Convert to string and remove whitespace
        pincode = str(slot_value).strip()
        
        # Check if it's exactly 6 digits
        if not re.match(r'^\d{6}$', pincode):
            logger.warning("❌ Pincode validation failed: not 6 digits")
            dispatcher.utter_message(response="utter_invalid_pincode")
            return {"pincode": None}
        
        # ✅ ADD SERVICEABILITY CHECK
        serviceable_pincodes = [
            # --- PREVIOUS ENTRIES ---

            # --- BANGALORE URBAN (560xxx series) ---
            "560001", "560002", "560003", "560004", "560005", "560006", "560007", "560008", 
            "560009", "560010", "560011", "560012", "560013", "560014", "560015", "560016", 
            "560017", "560018", "560019", "560020", "560021", "560022", "560023", "560024", 
            "560025", "560026", "560027", "560029", "560030", "560032", "560033", "560034", 
            "560035", "560036", "560037", "560038", "560039", "560040", "560041", "560042", 
            "560043", "560044", "560045", "560046", "560047", "560048", "560049", "560050", 
            "560051", "560052", "560053", "560054", "560055", "560056", "560057", "560058", 
            "560059", "560060", "560061", "560062", "560063", "560064", "560065", "560066", 
            "560067", "560068", "560069", "560070", "560071", "560072", "560073", "560074", 
            "560075", "560076", "560077", "560078", "560079", "560080", "560081", "560082", 
            "560083", "560084", "560085", "560086", "560087", "560088", "560089", "560090", 
            "560091", "560092", "560093", "560094", "560095", "560096", "560097", "560098", 
            "560099", "560100", "560102", "560103", "560104", "560105", "560106", "560107",
            "560108", "560109", "560113", "560114", "560115", "560300",

            # --- BANGALORE RURAL / SUBURBAN (562xxx series) ---
            "562106", "562107", "562108", "562109", "562110", "562114", "562123", "562125", 
            "562129", "562130", "562149", "562157", "562162", "562164"
        ]
        
        if pincode not in serviceable_pincodes:
            logger.warning(f"❌ Pincode {pincode} not serviceable")
            dispatcher.utter_message(
                text=f"Sorry, we don't service pincode {pincode} yet. We'll notify you when we expand to your area!"
            )
            return {"pincode": None}
        
        # Validation succeeded
        logger.info(f"✅ Pincode validation passed: {pincode}")
        return {"pincode": pincode}

class ActionStoreName(Action):
    def name(self) -> str:
        return "action_store_name"

    async def run(self, dispatcher, tracker: Tracker, domain):

        # ✅ Get the validated name from the slot (validated by ValidationAction)
        name = tracker.get_slot("name")
        logger.debug(f"\033[91m📝 Name from slot: {name}\033[0m")

        # ✅ If validation failed, name will be None
        if not name:
            logger.warning("❌ Name slot is empty after validation")
            name = "Unknow Customer"
            # ValidationAction already sent error message
            return []

        # ✅ Resolve phone safely
        phone = (
            tracker.latest_message.get("metadata", {}).get("phone")
            or tracker.get_slot("phone")
            or tracker.sender_id
        )

        logger.debug(f"📞 Phone resolved as: {phone}")

        if not phone:
            logger.error("❌ Phone missing, aborting")
            return []

        # ✅ Update lead via backend
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
                    logger.error(f"Lead update failed: {resp.text}")
                else:
                    logger.info(f"✅ Name '{name}' stored in lead for {phone}")
        except Exception as e:
            logger.exception(f"Error updating lead: {e}")

        # ✅ Send acknowledgment
        if IS_TEST_ENV:
            dispatcher.utter_message(text=f"Nice to meet you, {name}! 😊")
        else:
            message_payload = {
                "to": phone,
                "message": f"Nice to meet you, {name}! 😊"
            }
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    await client.post(BACKEND_SEND_MESSAGE_URL, json=message_payload)
            except Exception as e:
                logger.exception(f"Error sending acknowledgment: {e}")

        # ✅ Set slot so next actions know name exists
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

        logger.debug(f"📞 Phone resolved as: {phone_number}")

        if not phone_number:
            logger.error("❌ Phone not found")
            return []
        

        update_payload = {
            "phone": phone_number
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    BACKEND_LEAD_UPDATE_URL,
                    json=update_payload
                )
                if resp.status_code != 200:
                    logger.error(f"Lead greet update failed")
                else:
                    logger.info(f"✅ Lead created/retrieved for {phone_number}")
        except Exception as e:
            logger.exception(f"Error updating lead: {e}")

        # 2️⃣ Send greeting message
        if IS_TEST_ENV:
            dispatcher.utter_message(text="Hi 👋 Welcome to TVS Motors — Built to Perform 🏍️")
        else:
            payload = {
                "to": phone_number,
                "message": "Hi 👋 Welcome to TVS Motors — Built to Perform 🏍️"
            }
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    await client.post(BACKEND_SEND_MESSAGE_URL, json=payload)
                logger.info("✅ Greeting sent via backend")
            except Exception as e:
                logger.error(f"❌ Error sending greeting: {e}")

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
            logger.error("❌ Phone not found")
            return []

        # 2️⃣ Ask for user's name
        if IS_TEST_ENV:
            dispatcher.utter_message(text="Before we continue, may I know your name?")
        else:
            payload = {
                "to": phone_number,
                "message": "Before we continue, may I know your name?"
            }
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    await client.post(BACKEND_SEND_MESSAGE_URL, json=payload)
                logger.info("✅ Name request sent successfully")
            except Exception as e:
                logger.error(f"❌ Error asking for name: {e}")

        # 3️⃣ No slot update yet (name not known)
        return []



class ActionSendBrochure(Action):
    def name(self) -> Text:
        return "action_send_brochure"

    async def run(self,
                  dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        name = tracker.get_slot("name")
        
        # Get user's phone number
        phone_number = (
            tracker.latest_message.get("metadata", {}).get("phone")
            or tracker.get_slot("phone")
            or tracker.sender_id
        )

        update_payload = {
            "phone": phone_number,
            "updates": {
                "lead_status": "warm"
            }
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    BACKEND_LEAD_UPDATE_URL,
                    json=update_payload
                )
                if resp.status_code != 200:
                    logger.error(f"Lead update failed: {resp.text}")
                else:
                    logger.info(f"Lead status warm stored in lead for {phone_number}")
        except Exception as e:
            logger.exception(f"Error updating lead: {e}")

        # Check if user has selected a vehicle
        chosen_vehicle = tracker.get_slot("chosen_vehicle")

        logger.info(f"chosen vehicle: {chosen_vehicle}")

        # Brochure URLs (You need to host these PDFs on a public server or cloud storage)
        brochure_data = {
            "Apache RTR 160 2V": {
                "pdf_url": "https://www.tvsmotor.com/tvs-apache/-/media/Brand-Pages/Apache/Brochure/TVS-Apache-RTR-160-Brochure_V4.pdf",
                "filename": "TVS_Apache_RTR_160_Brochure.pdf",
                "caption": "📄 TVS Apache RTR 160 - Complete Brochure"
            },

            "Apache RTR 160 4V": {
                "pdf_url": "https://www.tvsmotor.com/tvs-apache/-/media/Brand-Pages/Apache/Brochure/TVS-Apache-RTR-160-4V-Brochure.pdf",
                "filename": "TVS_Apache_RTR_160_4V_Brochure.pdf",
                "caption": "📄 TVS Apache RTR 160 4V - Complete Brochure"
            },

            "Apache RTR 200 4V": {
                "pdf_url": "https://www.tvsmotor.com/tvs-apache/-/media/Brand-Pages/Apache/Brochure/Apache-200-4V-BLUE-Leaflet.pdf",
                "filename": "TVS_Apache_RTR_200_4V_Brochure.pdf",
                "caption": "📄 TVS Apache RTR 200 4V - Complete Brochure"
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
            
            if IS_TEST_ENV:
                dispatcher.utter_message(text=f"✅ {chosen_vehicle} brochure has been sent!")
            else:
                payload = {
                    "to": phone_number,
                    "pdf_url": brochure["pdf_url"],
                    "filename": brochure["filename"],
                    "caption": brochure["caption"]
                }
                
                try:
                    logger.debug("Reached brochure sending part")
                    async with httpx.AsyncClient() as client:
                        response = await client.post(BACKEND_SEND_BROCHURE_URL, json=payload)
                        response.raise_for_status()
                    
                    dispatcher.utter_message(
                        text=f"✅ {chosen_vehicle} brochure has been sent!"
                    )
                except Exception as e:
                    logger.error(f"❌ Error sending brochure: {e}")
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
            
            if IS_TEST_ENV:
                list_items = [f"• {row['title']}" for row in sections[0]['rows']]
                list_text = "\n".join(list_items)
                dispatcher.utter_message(text=f"Select a Vehicle\n📚 Please select a vehicle to receive its brochure:\n\n{list_text}")
            else:
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
                    logger.error(f"❌ Error sending brochure options: {e}")
                    dispatcher.utter_message(text="Sorry, couldn't load brochure options.")
        
        return []


class ActionGreetWithMenu(Action):
    def name(self) -> Text:
        return "action_greet_with_menu"

    async def run(self,
                  dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        logger.info("🎯 ActionGreetWithMenu TRIGGERED!")
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
        
        if IS_TEST_ENV:
            list_items = [f"• {row['title']}" for row in sections[0]['rows']]
            list_text = "\n".join(list_items)
            dispatcher.utter_message(text=f"{greeting}\n\nSelect the model you're interested in:\n\n{list_text}")
        else:
            try:
                logger.debug("🚀 Sending vehicle menu via backend...")
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(BACKEND_SEND_LIST_URL, json=payload)
                    response.raise_for_status()
                
                logger.info("✅ Vehicle menu sent successfully")
            
            except Exception as e:
                logger.error(f"❌ Error sending vehicle menu: {e}")
                # Send error message via API instead of dispatcher
                error_payload = {
                    "to": phone_number,
                    "message": "Sorry, couldn't load vehicle menu. How can I assist you?"
                }
                try:
                    async with httpx.AsyncClient(timeout=10.0) as client:
                        await client.post(BACKEND_SEND_MESSAGE_URL, json=error_payload)
                except Exception as inner_e:
                    logger.error(f"❌ Fallback error message also failed: {inner_e}")
        
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
            # Send message to customer
            if IS_TEST_ENV:
                dispatcher.utter_message(text="Connecting you to our agent. Please hold on...")
            else:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(BACKEND_SEND_MESSAGE_URL, json=customer_payload)
                    response.raise_for_status()
                logger.info("✅ Contact info sent to customer")
            
            # Notify agent via FastAPI (keep as is for prod)
            if not IS_TEST_ENV:
                logger.info("📢 Notifying agent via FastAPI...")
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(BACKEND_NOTIFY_AGENT_URL, json=agent_payload)
                    response.raise_for_status()
                logger.info("✅ Agent notified successfully")
            else:
                logger.info("✅ [TEST] Agent notification simulated")
        
        except Exception as e:
            logger.error(f"❌ Error in talk to agent action: {e}")
            # Send error message
            if IS_TEST_ENV:
                dispatcher.utter_message(text="Sorry, couldn't connect to agent at the moment. Please try again.")
            else:
                error_payload = {
                    "to": customer_phone,
                    "text": "Sorry, couldn't connect to agent at the moment. Please try again."
                }
                try:
                    async with httpx.AsyncClient(timeout=10.0) as client:
                        await client.post(BACKEND_SEND_MESSAGE_URL, json=error_payload)
                except Exception as inner_e:
                    logger.error(f"❌ Fallback error message also failed: {inner_e}")
        
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

        logger.debug(f"Vehicle ID: {vehicle_id}")
        
        if not vehicle_id:
            if IS_TEST_ENV:
                dispatcher.utter_message(text="Sorry, I couldn't identify the vehicle.")
            else:
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

        phone = (
            tracker.latest_message.get("metadata", {}).get("phone")
            or tracker.get_slot("phone")
            or tracker.sender_id
        )

        update_payload = {
            "phone": phone,
            "updates": {
                "interested_in": vehicle_name
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
                    print(f"✅ Vehicle of interest {vehicle_name} stored in lead for {phone}")

        except Exception as e:
            print(f"❌ Error updating lead with pincode: {e}")

        # Send only the image first
        if IS_TEST_ENV:
            dispatcher.utter_message(text=f"[Image: {vehicle_image}] 🏍️ {vehicle_name}")
        else:
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
        if IS_TEST_ENV:
            dispatcher.utter_message(text=vehicle_spec)
        else:
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
        
        # Send action buttons
        buttons = [
            {
                "id": "brochure_request",
                "title": "📄 Get Brochure"
            },
            {
                "id": "book_test_ride",
                "title": "🏍️ Book Test Ride"
            },
            {
                "id": "get_price_or_EMI",
                "title": "💰 Get Price/EMI"
            }
        ]
        
        if IS_TEST_ENV:
            button_text = "\n".join([f"• {btn['title']}" for btn in buttons])
            dispatcher.utter_message(text=f"What would you like to do with {chosen_vehicle}?\n\n{button_text}")
        else:
            button_payload = {
                "to": phone_number,
                "body": f"What would you like to do with {chosen_vehicle}?",
                "buttons": buttons
            }
            
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(BACKEND_SEND_BUTTON_URL, json=button_payload)
                    response.raise_for_status()
                print(f"✅ Sent action buttons for {chosen_vehicle}")
            except Exception as e:
                print(f"❌ Error sending buttons: {e}")
        
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
        
        if IS_TEST_ENV:
            dispatcher.utter_message(text=message)
        else:
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
        
        # ✅ Get the validated pincode from the slot (validated by ValidationAction)
        pincode = tracker.get_slot("pincode")
        
        print(f"📍 Pincode from slot: {pincode}")
        
        # ✅ If validation failed, pincode will be None
        if not pincode:
            print("❌ Pincode slot is empty after validation")
            # ValidationAction already sent error message
            return []
        
        # ✅ Resolve phone number
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
        
        # ✅ Update lead via backend
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
        
        # ✅ Get ex-showroom price from VEHICLE_DATA
        ex_showroom_price = None
        for vid, vdata in VEHICLE_DATA.items():
            if vdata["name"] == chosen_vehicle:
                ex_showroom_price = vdata.get("ex_showroom_price")
                break

        if not ex_showroom_price:
            print(f"❌ Ex-showroom price not found for {chosen_vehicle}")
            ex_showroom_price = 115000  # Fallback

        # Format price
        if ex_showroom_price >= 100000:
            formatted_price = f"₹{ex_showroom_price // 100000}.{ex_showroom_price % 100000 // 10000}L"
        else:
            formatted_price = f"₹{ex_showroom_price:,}"

        # ✅ Send pricing message
        pricing_message = f"""
        📍 Thanks for sharing your pincode!

        💰 The ex-showroom price of **{chosen_vehicle}** starts from **{formatted_price}**.

        Our TVS sales executive will contact you shortly with the **best on-road price & EMI options** available for your area.
                """.strip()

        if IS_TEST_ENV:
            dispatcher.utter_message(text=pricing_message)
        else:
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

        return []


class ActionHandlePincodeBasedOnPurpose(Action):
    def name(self) -> Text:
        return "action_handle_pincode_based_on_purpose"

    async def run(self,
                  dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Check the purpose slot
        pincode_purpose = tracker.get_slot("pincode_purpose")

        print(f"🎯 Handling pincode based on purpose: {pincode_purpose}")

        if pincode_purpose == "pricing":
            # Call pricing logic
            return await self._handle_pricing(dispatcher, tracker, domain)
        elif pincode_purpose == "test_ride":
            # Call test ride logic
            return await self._handle_test_ride(dispatcher, tracker, domain)
        else:
            # Default to pricing if no purpose set
            print("⚠️ No pincode purpose set, defaulting to pricing")
            return await self._handle_pricing(dispatcher, tracker, domain)

    async def _handle_pricing(self, dispatcher, tracker, domain):
        """Handle pricing flow - copied from ActionStorePincodeAndShowPricing"""

        # 1️⃣ Extract pincode entity
        pincode = next(tracker.get_latest_entity_values("pincode"), None)

        print(100*"-")
        print(100*"-")
        print(f"Extracted pincode entity: {pincode}")
        print(100*"-")

        # Fallback: if no entity, try to extract from text (6 digits)
        if not pincode:
            user_message = tracker.latest_message.get('text', '').strip()
            if user_message.isdigit() and len(user_message) == 6:
                pincode = user_message

        print(f"📍 Extracted pincode: {pincode}")

        if not pincode:
            phone = (
                tracker.latest_message.get("metadata", {}).get("phone")
                or tracker.get_slot("phone")
                or tracker.sender_id
            )

            await send_message(phone, "Please enter a valid 6-digit pincode. 📍", dispatcher)
            return []

        # Validate pincode format
        if not pincode.isdigit() or len(pincode) != 6:
            phone = (
                tracker.latest_message.get("metadata", {}).get("phone")
                or tracker.get_slot("phone")
                or tracker.sender_id
            )

            await send_message(phone, "Please enter a valid 6-digit pincode. 📍", dispatcher)
            return []

        # 3️⃣ Resolve phone number
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

        # 4️⃣ Update lead via backend
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

        # 5️⃣ Get ex-showroom price
        ex_showroom_price = None
        for vid, vdata in VEHICLE_DATA.items():
            if vdata["name"] == chosen_vehicle:
                ex_showroom_price = vdata.get("ex_showroom_price")
                break

        if not ex_showroom_price:
            print(f"❌ Ex-showroom price not found for {chosen_vehicle}")
            ex_showroom_price = 115000

        # Format price
        if ex_showroom_price >= 100000:
            formatted_price = f"₹{ex_showroom_price // 100000}.{ex_showroom_price % 100000 // 10000}L"
        else:
            formatted_price = f"₹{ex_showroom_price:,}"

        # 6️⃣ Send pricing message
        pricing_message = f"""
        📍 Thanks for sharing your pincode!

        💰 The ex-showroom price of **{chosen_vehicle}** starts from **{formatted_price}**.

        Our TVS sales executive will contact you shortly with the **best on-road price & EMI options** available for your area.
        """.strip()

        await send_message(phone, pricing_message, dispatcher)

        # 7️⃣ Set slot
        return [SlotSet("pincode", pincode)]

    async def _handle_test_ride(self, dispatcher, tracker, domain):
        """Handle test ride flow"""

        # 1️⃣ Extract pincode entity
        pincode = next(tracker.get_latest_entity_values("pincode"), None)

        print(100*"-")
        print(100*"-")
        print(f"Extracted pincode entity: {pincode}")
        print(100*"-")

        # Fallback: if no entity, try to extract from text (6 digits)
        if not pincode:
            user_message = tracker.latest_message.get('text', '').strip()
            if user_message.isdigit() and len(user_message) == 6:
                pincode = user_message

        print(f"📍 Extracted pincode: {pincode}")

        if not pincode:
            phone = (
                tracker.latest_message.get("metadata", {}).get("phone")
                or tracker.get_slot("phone")
                or tracker.sender_id
            )

            await send_message(phone, "Please enter a valid 6-digit pincode for test ride booking. 📍", dispatcher)
            return []

        # Validate pincode format
        if not pincode.isdigit() or len(pincode) != 6:
            phone = (
                tracker.latest_message.get("metadata", {}).get("phone")
                or tracker.get_slot("phone")
                or tracker.sender_id
            )

            await send_message(phone, "Please enter a valid 6-digit pincode for test ride booking. 📍", dispatcher)
            return []

        # 3️⃣ Resolve phone number
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
        user_name = tracker.get_slot("user_name") or "Valued Customer"

        # 4️⃣ Update lead via backend
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

        # 5️⃣ Book test ride via backend
        test_ride_payload = {
            "phone": phone,
            "vehicle": chosen_vehicle,
            "pincode": pincode,
            "name": user_name
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    BACKEND_BOOK_TEST_RIDE_URL,
                    json=test_ride_payload
                )
                if resp.status_code == 200:
                    print(f"✅ Test ride booked for {chosen_vehicle} at pincode {pincode}")
                else:
                    print(f"❌ Test ride booking failed: {resp.text}")
        except Exception as e:
            print(f"❌ Error booking test ride: {e}")

        # 6️⃣ Send confirmation message
        confirmation_message = f"""
        🏍️ **Test Ride Booked Successfully!**

        Hi {user_name},

        Your test ride for **{chosen_vehicle}** has been booked!

        📍 **Location:** Based on pincode {pincode}
        📞 Our executive will contact you within 24 hours to confirm the test ride slot.

        🎯 **What happens next:**
        • Our sales executive will call you
        • Confirm the best test ride location near you
        • Schedule a convenient time slot

        Thank you for choosing TVS Motors! 🚀
        """.strip()

        await send_message(phone, confirmation_message, dispatcher)

        # 7️⃣ Set slot
        return [SlotSet("pincode", pincode)]


class ActionSetPincodePurposePricing(Action):
    def name(self) -> Text:
        return "action_set_pincode_purpose_pricing"

    async def run(self,
                  dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        print("🎯 Setting pincode purpose to: pricing")
        return [SlotSet("pincode_purpose", "pricing")]


class ActionSetPincodePurposeTestRide(Action):
    def name(self) -> Text:
        return "action_set_pincode_purpose_test_ride"

    async def run(self,
                  dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        print("🎯 Setting pincode purpose to: test_ride")
        return [SlotSet("pincode_purpose", "test_ride")]

    
class ActionBookTestRide(Action):
    def name(self) -> Text:
        return "action_book_test_ride"

    async def run(self,
                  dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        phone_number = tracker.sender_id
        chosen_vehicle = tracker.get_slot("chosen_vehicle")
        
        confirmation_message = f"""Thanks for booking a test ride for *{chosen_vehicle}*! Our TVS sales executive will contact you shortly to schedule your test ride. 🏍️
        """.strip()

        update_payload = {
            "phone": phone_number,
            "updates": {
                "lead_status": "hot"
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
                    print(f"✅ Lead status updated to hot for {phone_number}")
        except Exception as e:
            print(f"❌ Error updating lead status: {e}")

        if IS_TEST_ENV:
            await send_message(phone_number, confirmation_message, dispatcher)
        else:
            payload = {
                "to": phone_number,
                "message": confirmation_message
            }
            
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    await client.post(BACKEND_SEND_MESSAGE_URL, json=payload)
                print(f"✅ Sent test ride confirmation for {chosen_vehicle}")
            except Exception as e:
                print(f"❌ Error sending test ride confirmation: {e}")
            

        return []