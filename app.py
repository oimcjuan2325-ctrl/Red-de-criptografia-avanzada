import base64
import datetime
import io
import json
import os
import time
import google.generativeai as genai
import streamlit as st
from cryptography.fernet import Fernet
from PIL import Image, UnidentifiedImageError

# ====================================================
# CONFIGURACIÓN SEGURA DE LA API KEY (DESDE SECRETS)
# ====================================================
try:
  genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
  gemini_model = genai.GenerativeModel("gemini-1.5-flash")
except Exception:
  gemini_model = None

# Configuración de la página
st.set_page_config(
    page_title="Plataforma Segura e Inteligente",
    page_icon="🔒",
    layout="wide",
)

# ----------------------------------------------------
# FUNCIONES PARA PERSISTENCIA DE DATOS (JSON)
# ----------------------------------------------------
USERS_FILE = "users.json"
CHATS_FILE = "chats.json"
CONTACTS_FILE = "contacts.json"
TRASH_FILE = "trash.json"
AUDIT_FILE = "audit.json"


def load_users():
  if os.path.exists(USERS_FILE):
    with open(USERS_FILE, "r", encoding="utf-8") as f:
      try:
        return json.load(f)
      except json.JSONDecodeError:
        return {"Juan": "2325"}
  return {"Juan": "2325"}


def save_users(users):
  with open(USERS_FILE, "w", encoding="utf-8") as f:
    json.dump(users, f, ensure_ascii=False, indent=4)


def load_chats():
  if os.path.exists(CHATS_FILE):
    with open(CHATS_FILE, "r", encoding="utf-8") as f:
      try:
        data = json.load(f)
        return {eval(k): v for k, v in data.items()}
      except Exception:
        return {}
  return {}


def save_chats(chats):
  with open(CHATS_FILE, "w", encoding="utf-8") as f:
    data = {str(k): v for k, v in chats.items()}
    json.dump(data, f, ensure_ascii=False, indent=4)


def load_contacts():
  if os.path.exists(CONTACTS_FILE):
    with open(CONTACTS_FILE, "r", encoding="utf-8") as f:
      try:
        return json.load(f)
      except json.JSONDecodeError:
        return {}
  return {}


def save_contacts(contacts):
  with open(CONTACTS_FILE, "w", encoding="utf-8") as f:
    json.dump(contacts, f, ensure_ascii=False, indent=4)


def load_trash():
  if os.path.exists(TRASH_FILE):
    with open(TRASH_FILE, "r", encoding="utf-8") as f:
      try:
        return json.load(f)
      except json.JSONDecodeError:
        return {}
  return {}


def save_trash(trash):
  with open(TRASH_FILE, "w", encoding="utf-8") as f:
    json.dump(trash, f, ensure_ascii=False, indent=4)


def load_audit():
  if os.path.exists(AUDIT_FILE):
    with open(AUDIT_FILE, "r", encoding="utf-8") as f:
      try:
        return json.load(f)
      except json.JSONDecodeError:
        return {}
  return {}


def log_audit_event(username, event_desc):
  audit_data = load_audit()
  if username not in audit_data:
    audit_data[username] = []
  timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  audit_data[username].append({"time": timestamp, "event": event_desc})
  with open(AUDIT_FILE, "w", encoding="utf-8") as f:
    json.dump(audit_data, f, ensure_ascii=False, indent=4)


# Inicializar estados de sesión
if "logged_in" not in st.session_state:
  st.session_state.logged_in = False
if "username" not in st.session_state:
  st.session_state.username = ""
if "lang" not in st.session_state:
  st.session_state.lang = "Español"
if "login_attempts" not in st.session_state:
  st.session_state.login_attempts = {}

if "users_db" not in st.session_state:
  st.session_state.users_db = load_users()

if "chat_history" not in st.session_state:
  st.session_state.chat_history = load_chats()

if "ai_chat_memory" not in st.session_state:
  st.session_state.ai_chat_memory = []

# ====================================================
# DICCIONARIO COMPLETO DE TRADUCCIONES (ES, EU, EN, FR)
# ====================================================
TRANSLATIONS = {
    "Español": {
        "login_title": "Iniciar Sesión",
        "user_label": "Nombre de usuario",
        "pass_label": "Contraseña",
        "login_btn": "Entrar",
        "login_error": "Usuario o contraseña incorrectos",
        "account_locked": (
            "Cuenta bloqueada temporalmente por múltiples intentos fallidos."
        ),
        "register_txt": "¿No tienes cuenta? Regístrate aquí",
        "register_btn": "Registrarse",
        "logout": "Cerrar Sesión",
        "nav_title": "Menú Principal",
        "sec1": "1. Cifrado y Descifrado Potente",
        "sec2": "2. Chatbot IA con Memoria (Gemini)",
        "sec3": "3. Mini-WhatsApp (Chat)",
        "sec4": "4. Cifrado de Imágenes (Bits)",
        "sec5": "5. Papelera de Reciclaje",
        "admin_sec": "6. Panel de Administración (Juan)",
        "config": "Configuración",
        "ai_helper": "Asistente IA Rápido",
        "lang_label": "Idioma / Hizkuntza / Language / Langue",
        "save_config": "Guardar cambios",
        "config_success": "¡Idioma actualizado y web reiniciada con éxito!",
        "chat_title": "Mini-WhatsApp",
        "chat_desc": (
            "Chatea con otros usuarios agregándolos por su nombre de cuenta"
            " existente."
        ),
        "add_contact_label": "Añadir contacto por nombre:",
        "add_btn": "Agregar",
        "contact_added": "¡Contacto añadido con éxito!",
        "contact_not_found": (
            "Error: El usuario no existe en la base de datos, ya está en tus"
            " contactos o es tu propio usuario."
        ),
        "no_contacts": (
            "No tienes contactos aún. Agrega uno existente a la izquierda para"
            " empezar a chatear."
        ),
        "select_chat": "Selecciona chat:",
        "your_chats": "Tus Chats",
        "type_msg": "Escribe un mensaje...",
        "send_btn": "Enviar 📤",
        "cifrado_title": "Cifrado y Descifrado Potente (AES)",
        "cifrado_desc": (
            "Utiliza cifrado simétrico avanzado (Fernet) para proteger tus"
            " mensajes integrando la clave en el propio token."
        ),
        "cifrar_tab": "Cifrar Mensaje",
        "descifrar_tab": "Descifrar Mensaje",
        "texto_plano_label": "Introduce el texto que deseas cifrar:",
        "cifrar_btn": "Cifrar Mensaje (Autocontenido)",
        "cifrado_exito": (
            "¡Texto cifrado con éxito! La clave ya va integrada en el token:"
        ),
        "texto_cifrado_label": (
            "Introduce el token cifrado completo (incluye clave y datos):"
        ),
        "descifrar_btn": "Descifrar Token",
        "descifrar_exito": "¡Descifrado con éxito!",
        "texto_original": "Texto Original:",
        "ia_title": "Chatbot IA Avanzado con Memoria (Gemini)",
        "ia_desc": (
            "Mantén una conversación fluida con memoria de contexto sobre"
            " ciberseguridad, cifrado y consultas generales."
        ),
        "ia_input": "Escribe tu mensaje para Gemini...",
        "ia_btn": "Enviar a Gemini",
        "ia_spinner": "Gemini está procesando tu respuesta...",
        "ai_clear_btn": "Limpiar Historial de Chat",
        "img_title": "Cifrado de Imágenes a Nivel de Bits",
        "img_desc": (
            "Sube una imagen, conviértela a binario y empaqueta la clave de"
            " seguridad en un único token cifrado."
        ),
        "img_cifrar_tab": "Cifrar Imagen",
        "img_descifrar_tab": "Descifrar Imagen",
        "subir_img_label": "Sube una imagen válida (PNG o JPG):",
        "cifrar_img_btn": "Cifrar Imagen (Autocontenida)",
        "img_cifrada_exito": (
            "¡Imagen cifrada con éxito! Este token incluye la imagen y su"
            " clave:"
        ),
        "token_img_label": "Token completo de la imagen cifrada:",
        "token_img_input": "Introduce el token completo de la imagen:",
        "descifrar_img_btn": "Desenkripatu y Restaurar Imagen",
        "img_original_caption": "Imagen Original",
        "img_decrypted_success": "¡Imagen descifrada y restaurada con éxito!",
        "img_decrypted_caption": "Imagen Descifrada",
        "img_error": "Error al descifrar la imagen o archivo inválido: ",
        "invalid_image_err": (
            "El archivo subido no es una imagen válida o está dañado."
        ),
        "ai_helper_desc": (
            "Gemini está conectado para ayudarte en esta sección."
        ),
        "ai_query_label": "¿En qué te puedo ayudar?",
        "ai_query_btn": "Preguntar a Gemini",
        "ai_thinking": "Gemini pensando...",
        "ai_missing_key": "Falta configurar la API Key en los Secrets.",
        "write_query": "Escribe una consulta.",
        "select_contact_prompt": (
            "Selecciona o agrega un contacto para ver la conversación."
        ),
        "contacts_header": "Contactos",
        "user_exists_warn": "El usuario ya existe.",
        "account_created": "¡Cuenta creada con éxito!",
        "fill_fields": "Rellene todos los campos.",
        "nav_sidebar": "Navegación",
        "same_lang_info": "El idioma seleccionado es el mismo.",
        "ai_helper_prompt": (
            "Estás en una web de ciberseguridad en la sección '{menu}'."
            " Responde a la siguiente consulta del usuario hablando"
            " estrictamente en ESPAÑOL: {ai_query}"
        ),
        "calc_link": "🔗 **[calculadora con IA](https://calculadora-con-ia.streamlit.app)**",
        "account_deleted_chat_msg": (
            "Esta cuenta ha sido borrada, ya no puedes chatear con esa cuenta."
        ),
        "delete_contact_btn": "Enviar a la papelera",
        "contact_deleted_success": (
            "Contacto y chats enviados a la papelera correctamente."
        ),
        "del_contact_section": "Eliminar Contacto",
        "select_to_delete": "Selecciona contacto a eliminar:",
        "trash_title": "Papelera de Reciclaje",
        "trash_desc": (
            "Aquí puedes restaurar tus contactos y chats eliminados o"
            " borrarlos permanentemente."
        ),
        "no_trash": "La papelera está vacía.",
        "restore_btn": "Restaurar",
        "permanent_delete_btn": "Borrar Definitivamente",
        "item_restored": "¡Elemento restaurado con éxito!",
        "item_purged": "¡Elemento purgado definitivamente!",
        "audit_title": "Auditoría y Seguridad de Cuenta",
        "audit_desc": (
            "Historial de eventos y accesos registrados de los usuarios."
        ),
        "no_audit": "No hay registros de auditoría aún.",
        "audit_time": "Fecha y Hora",
        "audit_event": "Evento Registrado",
        "admin_title": "Panel de Administración",
        "admin_desc": (
            "Control total de usuarios registrados, sesiones activas,"
            " supervisión de chats y auditoría."
        ),
        "admin_tab1": "Cuentas y Conexiones",
        "admin_tab2": "Supervisión de Chats",
        "admin_tab3": "Auditoría de Seguridad",
        "accounts_registered": "Cuentas Registradas y Estado Actual",
        "chats_registered_admin": "Conversaciones Privadas de los Usuarios",
        "no_chats_admin": "No hay chats registrados aún.",
        "chat_between": "Conversación entre",
        "expulsar_btn": "expulsar",
        "user_expulsado": "Usuario expulsado/eliminado.",
    },
    "Euskera": {
        "login_title": "Saioa Hasi",
        "user_label": "Erabiltzaile izena",
        "pass_label": "Pasahitza",
        "login_btn": "Sartu",
        "login_error": "Erabiltzaile edo pasahitz okerra",
        "account_locked": (
            "Kontua aldi baterako blokeatuta dago huts egindako saiakera"
            " anitzengatik."
        ),
        "register_txt": "Ez duzu konturik? Erregistratu hemen",
        "register_btn": "Erregistratu",
        "logout": "Saioa Itxi",
        "nav_title": "Menu Nagusia",
        "sec1": "1. Enkripzio eta Desenkripzio Indartsua",
        "sec2": "2. Memoriadun AI Chatbota (Gemini)",
        "sec3": "3. Mini-WhatsApp (Txata)",
        "sec4": "4. Irudiak Enkripatzea (Bitak)",
        "sec5": "5. Zakarrontzia",
        "admin_sec": "6. Administrazio Panela (Juan)",
        "config": "Konfigurazioa",
        "ai_helper": "AI Laguntzaile Azkarra",
        "lang_label": "Hizkuntza / Idioma / Language / Langue",
        "save_config": "Gorde aldaketak",
        "config_success": (
            "Hizkuntza eguneratuta eta webgunea berrabiarazi da arrakastaz!"
        ),
        "chat_title": "Mini-WhatsApp",
        "chat_desc": (
            "Txateatu beste erabiltzaile batzuekin existitzen den kontu-izenaren"
            " bidez gehituz."
        ),
        "add_contact_label": "Gehitu kontaktua izenez:",
        "add_btn": "Gehitu",
        "contact_added": "Kontaktua arrakastaz gehituta!",
        "contact_not_found": (
            "Errorea: Erabiltzailea ez da existitzen datu-basean, jada"
            " kontaktuetan dago edo zure erabiltzailea da."
        ),
        "no_contacts": (
            "Ez duzu kontakturik oraindik. Gehitu daitekeen bat ezkerrean"
            " txateatzen hasteko."
        ),
        "select_chat": "Hautatu txata:",
        "your_chats": "Zure Txatak",
        "type_msg": "Idatzi mezua...",
        "send_btn": "Bidali 📤",
        "cifrado_title": "Enkripzio eta Desenkripzio Indartsua (AES)",
        "cifrado_desc": (
            "Erabili enkripzio simetriko aurreratua (Fernet) zure mezuak"
            " gakoa mezuaren barruan txertatuz babesteko."
        ),
        "cifrar_tab": "Enkripatu Mezua",
        "descifrar_tab": "Desenkripatu Mezua",
        "texto_plano_label": "Sartu enkripatu nahi duzun testua:",
        "cifrar_btn": "Enkripatu Mezua (Autoeustsia)",
        "cifrado_exito": (
            "Testua arrakastaz enkripatu da! Gakoa token barruan doa:"
        ),
        "texto_cifrado_label": (
            "Sartu enkripatutako token osoa (gakoa eta datuak barne):"
        ),
        "descifrar_btn": "Desenkripatu Tokena",
        "descifrar_exito": "Arrakastaz desenkripatua!",
        "texto_original": "Jatorrizko Testua:",
        "ia_title": "Memoriadun AI Chatbot Aurreratua (Gemini)",
        "ia_desc": (
            "Mantendu elkarrizketa arina testuinguru-memoriarekin"
            " zibersegurtasunari, enkripzioari eta kontsulta orokorrei buruz."
        ),
        "ia_input": "Idatzi zure mezua Gemini-rentzat...",
        "ia_btn": "Bidali Gemini-ri",
        "ia_spinner": "Gemini zure erantzuna prozesatzen ari da...",
        "ai_clear_btn": "Garbitu Txataren Historia",
        "img_title": "Irudiak Bit Mailan Enkripatzea",
        "img_desc": (
            "Igo irudi bat, bihurtu bit-fluxu eta paketatu segurtasun gakoa"
            " token bakar batean."
        ),
        "img_cifrar_tab": "Enkripatu Irudia",
        "img_descifrar_tab": "Desenkripatu Irudia",
        "subir_img_label": "Igo irudi baliogabea ez den beste irudi bat (PNG/JPG):",
        "cifrar_img_btn": "Enkripatu Irudia (Autoeustsia)",
        "img_cifrada_exito": (
            "Irudia arrakastaz enkripatu da! Token honek irudia eta gakoa"
            " barne hartzen ditu:"
        ),
        "token_img_label": "Enkripatutako irudiaren token osoa:",
        "token_img_input": "Sartu irudiaren token osoa:",
        "descifrar_img_btn": "Desenkripatu eta Berreskuratu Irudia",
        "img_original_caption": "Jatorrizko Irudia",
        "img_decrypted_success": "Irudia arrakastaz desenkripatu eta berreskuratu da!",
        "img_decrypted_caption": "Irudi Desenkripatua",
        "img_error": "Errorea irudia desenkripatzean edo fitxategia okerra da: ",
        "invalid_image_err": (
            "Igotako fitxategia ez da baliozko irudia edo hondatuta dago."
        ),
        "ai_helper_desc": (
            "Gemini konektatuta dago atal honetan laguntzeko."
        ),
        "ai_query_label": "Zertan lagundu dezaket?",
        "ai_query_btn": "Galdetu Gemini-ri",
        "ai_thinking": "Gemini pentsatzen...",
        "ai_missing_key": "API Gakoa konfiguratu gabe dago Secret-etan.",
        "write_query": "Idatzi kontsulta bat.",
        "select_contact_prompt": (
            "Hautatu edo gehitu kontaktu bat elkarrizketa ikusteko."
        ),
        "contacts_header": "Kontaktuak",
        "user_exists_warn": "Erabiltzailea badago jada.",
        "account_created": "Kontua arrakastaz sortu da!",
        "fill_fields": "Bete eremu guztiak.",
        "nav_sidebar": "Nabigazioa",
        "same_lang_info": "Hautatutako hizkuntza bera da.",
        "ai_helper_prompt": (
            "Zibersegurtasun webgune bateko '{menu}' atalean zaude. Erantzun"
            " erabiltzailearen honako galderari euskaraz soilik: {ai_query}"
        ),
        "calc_link": "🔗 **[kalkulagailua AI-rekin](https://calculadora-con-ia.streamlit.app)**",
        "account_deleted_chat_msg": (
            "Kontu hau ezabatua izan da, ezin duzu jada kontu horrekin"
            " txateatu."
        ),
        "delete_contact_btn": "Bidali zakarrontzira",
        "contact_deleted_success": (
            "Kontaktua eta txatak zakarrontzira bidali dira arrakastaz."
        ),
        "del_contact_section": "Ezabatu Kontaktua",
        "select_to_delete": "Hautatu ezabatzeko kontaktua:",
        "trash_title": "Zakarrontzia",
        "trash_desc": (
            "Hemen ezabatutako kontaktuak eta txatak berreskuratu edo betiko"
            " ezabatu ditzakezu."
        ),
        "no_trash": "Zakarrontzia hutsik dago.",
        "restore_btn": "Berreskuratu",
        "permanent_delete_btn": "Ezabatu Betiko",
        "item_restored": "Elementua arrakastaz berreskuratu da!",
        "item_purged": "Elementua behin betiko ezabatu da!",
        "audit_title": "Kontuaren Auditoria eta Segurtasuna",
        "audit_desc": "Erabiltzaileen gertaera eta sarreren historia erregistratua.",
        "no_audit": "Ez dago auditoria erregistrorik oraindik.",
        "audit_time": "Data eta Ordua",
        "audit_event": "Erregistratutako Gertaera",
        "admin_title": "Administrazio Panela",
        "admin_desc": (
            "Erregistratutako erabiltzaileen, saio aktiboen, txaten"
            " ikuskapenaren eta auditoriaren kontrol osoa."
        ),
        "admin_tab1": "Kontuak eta Konexioak",
        "admin_tab2": "Txaten Ikuskapena",
        "admin_tab3": "Segurtasun Auditoria",
        "accounts_registered": "Erregistratutako Kontuak eta Egoera",
        "chats_registered_admin": "Erabiltzaileen Elkarrizketa Pribatuak",
        "no_chats_admin": "Ez dago txat erregistrorik oraindik.",
        "chat_between": "Elkarrizketa honen artean",
        "expulsar_btn": "kanporatu",
        "user_expulsado": "erabiltzailea kanporatu da.",
    },
    "English": {
        "login_title": "Sign In",
        "user_label": "Username",
        "pass_label": "Password",
        "login_btn": "Login",
        "login_error": "Incorrect username or password",
        "account_locked": (
            "Account temporarily locked due to multiple failed attempts."
        ),
        "register_txt": "Don't have an account? Register here",
        "register_btn": "Register",
        "logout": "Log Out",
        "nav_title": "Main Menu",
        "sec1": "1. Powerful Encryption & Decryption",
        "sec2": "2. AI Chatbot with Memory (Gemini)",
        "sec3": "3. Mini-WhatsApp (Chat)",
        "sec4": "4. Image Encryption (Bits)",
        "sec5": "5. Recycle Bin",
        "admin_sec": "6. Admin Panel (Juan)",
        "config": "Settings",
        "ai_helper": "Quick AI Assistant",
        "lang_label": "Language / Hizkuntza / Idioma / Langue",
        "save_config": "Save changes",
        "config_success": "Language updated and web successfully restarted!",
        "chat_title": "Mini-WhatsApp",
        "chat_desc": (
            "Chat with other users by adding them via their existing account"
            " name."
        ),
        "add_contact_label": "Add contact by name:",
        "add_btn": "Add",
        "contact_added": "Contact successfully added!",
        "contact_not_found": (
            "Error: User does not exist in the database, is already in your"
            " contacts, or is your own user."
        ),
        "no_contacts": (
            "You have no contacts yet. Add an existing one on the left to"
            " start chatting."
        ),
        "select_chat": "Select chat:",
        "your_chats": "Your Chats",
        "type_msg": "Type a message...",
        "send_btn": "Send 📤",
        "cifrado_title": "Powerful Encryption & Decryption (AES)",
        "cifrado_desc": (
            "Use advanced symmetric encryption (Fernet) to protect your"
            " messages by embedding the key inside the token."
        ),
        "cifrar_tab": "Encrypt Message",
        "descifrar_tab": "Decrypt Message",
        "texto_plano_label": "Enter the text you want to encrypt:",
        "cifrar_btn": "Encrypt Message (Self-contained)",
        "cifrado_exito": (
            "Text successfully encrypted! The key is already embedded in the"
            " token:"
        ),
        "texto_cifrado_label": (
            "Enter the complete encrypted token (includes key and data):"
        ),
        "descifrar_btn": "Decrypt Token",
        "descifrar_exito": "Successfully decrypted!",
        "texto_original": "Original Text:",
        "ia_title": "Advanced AI Chatbot with Memory (Gemini)",
        "ia_desc": (
            "Maintain a smooth conversation with context memory about"
            " cybersecurity, encryption, and general inquiries."
        ),
        "ia_input": "Type your message for Gemini...",
        "ia_btn": "Send to Gemini",
        "ia_spinner": "Gemini is processing your response...",
        "ai_clear_btn": "Clear Chat History",
        "img_title": "Bit-Level Image Encryption",
        "img_desc": (
            "Upload an image, convert it to binary, and bundle the security"
            " key into a single encrypted token."
        ),
        "img_cifrar_tab": "Encrypt Image",
        "img_descifrar_tab": "Decrypt Image",
        "subir_img_label": "Upload a valid image (PNG or JPG):",
        "cifrar_img_btn": "Encrypt Image (Self-contained)",
        "img_cifrada_exito": (
            "Image successfully encrypted! This token includes the image and"
            " its key:"
        ),
        "token_img_label": "Full encrypted image token:",
        "token_img_input": "Enter the full image token:",
        "descifrar_img_btn": "Decrypt and Restore Image",
        "img_original_caption": "Original Image",
        "img_decrypted_success": "Image successfully decrypted and restored!",
        "img_decrypted_caption": "Decrypted Image",
        "img_error": "Error decrypting image or invalid file: ",
        "invalid_image_err": (
            "The uploaded file is not a valid image or is corrupted."
        ),
        "ai_helper_desc": "Gemini is connected to help you in this section.",
        "ai_query_label": "How can I help you?",
        "ai_query_btn": "Ask Gemini",
        "ai_thinking": "Gemini thinking...",
        "ai_missing_key": "API Key is missing in Secrets.",
        "write_query": "Write a query.",
        "select_contact_prompt": "Select or add a contact to view the chat.",
        "contacts_header": "Contacts",
        "user_exists_warn": "User already exists.",
        "account_created": "Account successfully created!",
        "fill_fields": "Please fill in all fields.",
        "nav_sidebar": "Navigation",
        "same_lang_info": "Selected language is the same.",
        "ai_helper_prompt": (
            "You are on a cybersecurity website in the '{menu}' section."
            " Answer the following user query speaking strictly in ENGLISH:"
            " {ai_query}"
        ),
        "calc_link": "🔗 **[calculator with AI](https://calculadora-con-ia.streamlit.app)**",
        "account_deleted_chat_msg": (
            "This account has been deleted, you can no longer chat with it."
        ),
        "delete_contact_btn": "Send to recycle bin",
        "contact_deleted_success": (
            "Contact and chats successfully sent to recycle bin."
        ),
        "del_contact_section": "Delete Contact",
        "select_to_delete": "Select contact to delete:",
        "trash_title": "Recycle Bin",
        "trash_desc": (
            "Here you can restore your deleted contacts and chats or delete"
            " them permanently."
        ),
        "no_trash": "Recycle bin is empty.",
        "restore_btn": "Restore",
        "permanent_delete_btn": "Delete Permanently",
        "item_restored": "Item successfully restored!",
        "item_purged": "Item permanently deleted!",
        "audit_title": "Security Audit Log",
        "audit_desc": "History of events and accesses recorded for users.",
        "no_audit": "No audit records yet.",
        "audit_time": "Date and Time",
        "audit_event": "Recorded Event",
        "admin_title": "Administration Panel",
        "admin_desc": (
            "Total control of registered users, active sessions, chat"
            " supervision, and security audit."
        ),
        "admin_tab1": "Accounts & Connections",
        "admin_tab2": "Chat Supervision",
        "admin_tab3": "Security Audit",
        "accounts_registered": "Registered Accounts and Current Status",
        "chats_registered_admin": "Private User Conversations",
        "no_chats_admin": "No chats recorded yet.",
        "chat_between": "Conversation between",
        "expulsar_btn": "kick",
        "user_expulsado": "user kicked/deleted.",
    },
    "Français": {
        "login_title": "Connexion",
        "user_label": "Nom d'utilisateur",
        "pass_label": "Mot de passe",
        "login_btn": "Entrer",
        "login_error": "Nom d'utilisateur ou mot de passe incorrect",
        "account_locked": (
            "Compte temporairement bloqué en raison de multiples tentatives"
            " échouées."
        ),
        "register_txt": "Vous n'avez pas de compte ? Inscrivez-vous ici",
        "register_btn": "S'inscrire",
        "logout": "Se déconnecter",
        "nav_title": "Menu Principal",
        "sec1": "1. Chiffrement et Déchiffrement Puissant",
        "sec2": "2. Chatbot IA avec Mémoire (Gemini)",
        "sec3": "3. Mini-WhatsApp (Chat)",
        "sec4": "4. Chiffrement d'Images (Bits)",
        "sec5": "5. Corbeille",
        "admin_sec": "6. Panneau d'Administration (Juan)",
        "config": "Paramètres",
        "ai_helper": "Assistant IA Rapide",
        "lang_label": "Langue / Hizkuntza / Idioma / Language",
        "save_config": "Enregistrer les modifications",
        "config_success": (
            "Langue mise à jour et site Web redémarré avec succès !"
        ),
        "chat_title": "Mini-WhatsApp",
        "chat_desc": (
            "Discutez avec d'autres utilisateurs en les ajoutant via leur nom"
            " de compte existant."
        ),
        "add_contact_label": "Ajouter un contact par nom :",
        "add_btn": "Ajouter",
        "contact_added": "Contact ajouté avec succès !",
        "contact_not_found": (
            "Erreur : L'utilisateur n'existe pas dans la base de données, est"
            " déjà dans vos contacts ou est votre propre utilisateur."
        ),
        "no_contacts": (
            "Vous n'avez pas encore de contacts. Ajoutez-en un existant à"
            " gauche pour commencer à discuter."
        ),
        "select_chat": "Sélectionner le chat :",
        "your_chats": "Vos Chats",
        "type_msg": "Écrivez un message...",
        "send_btn": "Envoyer 📤",
        "cifrado_title": "Chiffrement et Déchiffrement Puissant (AES)",
        "cifrado_desc": (
            "Utilisez un chiffrement symétrique avancé (Fernet) pour protéger"
            " vos messages en intégrant la clé dans le jeton."
        ),
        "cifrar_tab": "Chiffrer le Message",
        "descifrar_tab": "Déchiffrer le Message",
        "texto_plano_label": "Entrez le texte que vous souhaitez chiffrer :",
        "cifrar_btn": "Chiffrer le Message (Autonome)",
        "cifrado_exito": (
            "Texte chiffré avec succès ! La clé est déjà intégrée dans le"
            " jeton :"
        ),
        "texto_cifrado_label": (
            "Entrez le jeton chiffré complet (inclut la clé et les données) :"
        ),
        "descifrar_btn": "Déchiffrer le Jeton",
        "descifrar_exito": "Déchiffré avec succès !",
        "texto_original": "Texte Original :",
        "ia_title": "Chatbot IA Avancé avec Mémoire (Gemini)",
        "ia_desc": (
            "Maintenez une conversation fluide avec mémoire contextuelle sur"
            " la cybersécurité, le chiffrement et les questions générales."
        ),
        "ia_input": "Écrivez votre message pour Gemini...",
        "ia_btn": "Envoyer à Gemini",
        "ia_spinner": "Gemini traite votre réponse...",
        "ai_clear_btn": "Effacer l'historique du chat",
        "img_title": "Chiffrement d'Images au Niveau des Bits",
        "img_desc": (
            "Téléchargez une image, convertissez-la en binaire et regroupez"
            " la clé de sécurité dans un jeton chiffré unique."
        ),
        "img_cifrar_tab": "Chiffrer l'Image",
        "img_descifrar_tab": "Déchiffrer l'Image",
        "subir_img_label": "Téléchargez une image valide (PNG ou JPG) :",
        "cifrar_img_btn": "Chiffrer l'Image (Autonome)",
        "img_cifrada_exito": (
            "Image chiffrée avec succès ! Ce jeton comprend l'image et sa"
            " clé :"
        ),
        "token_img_label": "Jeton complet de l'image chiffrée :",
        "token_img_input": "Entrez le jeton complet de l'image :",
        "descifrar_img_btn": "Déchiffrer et Restaurer l'Image",
        "img_original_caption": "Image Originale",
        "img_decrypted_success": "Image déchiffrée et restaurée avec succès !",
        "img_decrypted_caption": "Image Déchiffrée",
        "img_error": (
            "Erreur lors du déchiffrement de l'image ou fichier invalide : "
        ),
        "invalid_image_err": (
            "Le fichier téléchargé n'est pas une image valide ou est endommagé."
        ),
        "ai_helper_desc": "Gemini est connecté pour vous aider dans cette section.",
        "ai_query_label": "Comment puis-je vous aider ?",
        "ai_query_btn": "Demander à Gemini",
        "ai_thinking": "Gemini réfléchit...",
        "ai_missing_key": "La clé API est manquante dans les Secrets.",
        "write_query": "Écrivez une requête.",
        "select_contact_prompt": (
            "Sélectionnez ou ajoutez un contact pour voir la conversation."
        ),
        "contacts_header": "Contacts",
        "user_exists_warn": "L'utilisateur existe déjà.",
        "account_created": "Compte créé avec succès !",
        "fill_fields": "Veuillez remplir tous les champs.",
        "nav_sidebar": "Navigation",
        "same_lang_info": "La langue sélectionnée est la même.",
        "ai_helper_prompt": (
            "Vous êtes sur un site de cybersécurité dans la section '{menu}'."
            " Répondez à la requête suivante de l'utilisateur en parlant"
            " strictement en FRANÇAIS : {ai_query}"
        ),
        "calc_link": "🔗 **[calculatrice avec IA](https://calculadora-con-ia.streamlit.app)**",
        "account_deleted_chat_msg": (
            "Ce compte a été supprimé, vous ne pouvez plus discuter avec lui."
        ),
        "delete_contact_btn": "Envoyer à la corbeille",
        "contact_deleted_success": (
            "Contact et chats envoyés à la corbeille avec succès."
        ),
        "del_contact_section": "Supprimer le Contact",
        "select_to_delete": "Sélectionnez le contact à supprimer :",
        "trash_title": "Corbeille",
        "trash_desc": (
            "Ici, vous pouvez restaurer vos contacts et chats supprimés ou les"
            " supprimer définitivement."
        ),
        "no_trash": "La corbeille est vide.",
        "restore_btn": "Restaurer",
        "permanent_delete_btn": "Supprimer Définitivement",
        "item_restored": "Élément restauré avec succès !",
        "item_purged": "Élément purgé définitivement !",
        "audit_title": "Journal d'Audit de Sécurité",
        "audit_desc": (
            "Historique des événements et des accès enregistrés pour les"
            " utilisateurs."
        ),
        "no_audit": "Aucun enregistrement d'audit pour l'instant.",
        "audit_time": "Date et Heure",
        "audit_event": "Événement Enregistré",
        "admin_title": "Panneau d'Administration",
        "admin_desc": (
            "Contrôle total des utilisateurs enregistrés, des sessions actives,"
            " de la supervision des chats et de l'audit de sécurité."
        ),
        "admin_tab1": "Comptes et Connexions",
        "admin_tab2": "Supervision des Chats",
        "admin_tab3": "Audit de Sécurité",
        "accounts_registered": "Comptes Enregistrés et État Actuel",
        "chats_registered_admin": "Conversations Privées des Utilisateurs",
        "no_chats_admin": "Aucun chat enregistré pour l'instant.",
        "chat_between": "Conversation entre",
        "expulsar_btn": "expulser",
        "user_expulsado": "utilisateur expulsé/supprimé.",
    },
}

t = TRANSLATIONS[st.session_state.lang]

# ----------------------------------------------------
# REGISTRO GLOBAL DE USUARIOS CONECTADOS
# ----------------------------------------------------
if "active_sessions" not in st.session_state:
  st.session_state.active_sessions = set()

# ----------------------------------------------------
# PANTALLA DE INICIO DE SESIÓN
# ----------------------------------------------------
if not st.session_state.logged_in:
  st.title("🔐 " + t["login_title"])

  tab1, tab2 = st.tabs([t["login_btn"], t["register_btn"]])

  with tab1:
    with st.form("login_form"):
      u_input = st.text_input(t["user_label"])
      p_input = st.text_input(t["pass_label"], type="password")
      submit = st.form_submit_button(t["login_btn"])

      if submit:
        fails = st.session_state.login_attempts.get(u_input, 0)
        if fails >= 3:
          st.error(t["account_locked"])
        else:
          users_db = load_users()
          if u_input in users_db and users_db[u_input] == p_input:
            st.session_state.login_attempts[u_input] = 0
            st.session_state.logged_in = True
            st.session_state.username = u_input
            st.session_state.active_sessions.add(u_input)
            log_audit_event(u_input, "Sesión iniciada / Saioa hasi da")
            st.rerun()
          else:
            st.session_state.login_attempts[u_input] = fails + 1
            log_audit_event(u_input, "Intento fallido / Saiakera okerra")
            st.error(t["login_error"])

  with tab2:
    with st.form("reg_form"):
      new_u = st.text_input(t["user_label"])
      new_p = st.text_input(t["pass_label"], type="password")
      reg_submit = st.form_submit_button(t["register_btn"])

      if reg_submit:
        users_db = load_users()
        if new_u in users_db:
          st.warning(t["user_exists_warn"])
        elif new_u and new_p:
          users_db[new_u] = new_p
          save_users(users_db)
          log_audit_event(new_u, "Cuenta creada / Kontua sortu da")
          st.success(t["account_created"])
        else:
          st.error(t["fill_fields"])

  st.stop()

# ----------------------------------------------------
# APLICACIÓN PRINCIPAL
# ----------------------------------------------------
st.sidebar.title(f"👤 {st.session_state.username}")
if st.sidebar.button(t["logout"]):
  log_audit_event(st.session_state.username, "Cierre de sesión / Saioa itxi")
  if st.session_state.username in st.session_state.active_sessions:
    st.session_state.active_sessions.remove(st.session_state.username)
  st.session_state.logged_in = False
  st.session_state.username = ""
  st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader(t["nav_title"])

nav_options = [t["sec1"], t["sec2"], t["sec3"], t["sec4"], t["sec5"]]
if st.session_state.username == "Juan":
  nav_options.append(t["admin_sec"])
nav_options.append(t["config"])

menu = st.sidebar.radio(t["nav_sidebar"], nav_options)

# ----------------------------------------------------
# SECCIÓN 1: CIFRADO Y DESCIFRADO POTENTE (CON CLAVE INTERNA)
# ----------------------------------------------------
if menu == t["sec1"]:
  st.header("🔒 " + t["cifrado_title"])
  st.write(t["cifrado_desc"])

  sub_tab1, sub_tab2 = st.tabs([t["cifrar_tab"], t["descifrar_tab"]])

  with sub_tab1:
    texto_plano = st.text_area(t["texto_plano_label"], "Mensaje secreto")
    if st.button(t["cifrar_btn"]):
      clave_dinamica = Fernet.generate_key()
      f = Fernet(clave_dinamica)
      token_datos = f.encrypt(texto_plano.encode())

      paquete = {
          "key": clave_dinamica.decode(),
          "data": token_datos.decode(),
      }
      paquete_json = json.dumps(paquete)
      token_completo = base64.b64encode(paquete_json.encode()).decode()

      log_audit_event(st.session_state.username, "Mensaje cifrado")
      st.success(t["cifrado_exito"])
      st.code(token_completo)

  with sub_tab2:
    token_entrada = st.text_area(t["texto_cifrado_label"])
    if st.button(t["descifrar_btn"]):
      try:
        json_decodificado = base64.b64decode(token_entrada.encode()).decode()
        paquete = json.loads(json_decodificado)

        clave_extraida = paquete["key"].encode()
        datos_cifrados = paquete["data"].encode()

        f = Fernet(clave_extraida)
        decrypted = f.decrypt(datos_cifrados)

        log_audit_event(st.session_state.username, "Mensaje descifrado")
        st.success(t["descifrar_exito"])
        st.write(f"**{t['texto_original']}**", decrypted.decode())
      except Exception as e:
        st.error(f"Error: {e}")

# ----------------------------------------------------
# SECCIÓN 2: CHATBOT IA CON MEMORIA (ESTILO CHATGPT)
# ----------------------------------------------------
elif menu == t["sec2"]:
  st.header("🤖 " + t["ia_title"])
  st.write(t["ia_desc"])

  if st.button(t["ai_clear_btn"]):
    st.session_state.ai_chat_memory = []
    st.rerun()

  for message in st.session_state.ai_chat_memory:
    with st.chat_message(message["role"]):
      st.markdown(message["content"])

  if prompt_ia := st.chat_input(t["ia_input"]):
    if not gemini_model:
      st.error(t["ai_missing_key"])
    else:
      st.session_state.ai_chat_memory.append(
          {"role": "user", "content": prompt_ia}
      )
      with st.chat_message("user"):
        st.markdown(prompt_ia)

      with st.chat_message("assistant"):
        with st.spinner(t["ia_spinner"]):
          try:
            chat_session = gemini_model.start_chat(history=[])
            history_formatted = []
            for m in st.session_state.ai_chat_memory[:-1]:
              history_formatted.append(
                  {
                      "role": "user" if m["role"] == "user" else "model",
                      "parts": [m["content"]],
                  }
              )

            chat_session.history = history_formatted
            full_prompt = (
                f"Responde estrictamente en {st.session_state.lang} como"
                f" experto en ciberseguridad y tecnología. Pregunta:"
                f" {prompt_ia}"
            )

            response = chat_session.send_message(full_prompt)
            bot_reply = response.text
            st.markdown(bot_reply)
            st.session_state.ai_chat_memory.append(
                {"role": "assistant", "content": bot_reply}
            )
          except Exception as e:
            st.error(f"Error: {e}")

# ----------------------------------------------------
# SECCIÓN 3: MINI-WHATSAPP (CHAT)
# ----------------------------------------------------
elif menu == t["sec3"]:
  st.header("💬 " + t["chat_title"])
  st.write(t["chat_desc"])

  col1, col2 = st.columns([1, 3])

  all_contacts_db = load_contacts()
  user_contacts = all_contacts_db.get(st.session_state.username, [])
  users_db = load_users()

  with col1:
    st.subheader(t["contacts_header"])
    nuevo_contacto = st.text_input(t["add_contact_label"])
    if st.button(t["add_btn"]):
      if (
          nuevo_contacto in users_db
          and nuevo_contacto not in user_contacts
          and nuevo_contacto != st.session_state.username
      ):
        user_contacts.append(nuevo_contacto)
        all_contacts_db[st.session_state.username] = user_contacts
        save_contacts(all_contacts_db)

        other_contacts = all_contacts_db.get(nuevo_contacto, [])
        if st.session_state.username not in other_contacts:
          other_contacts.append(st.session_state.username)
          all_contacts_db[nuevo_contacto] = other_contacts
          save_contacts(all_contacts_db)

        log_audit_event(
            st.session_state.username, f"Contacto añadido: {nuevo_contacto}"
        )
        st.success(t["contact_added"])
        st.rerun()
      else:
        st.error(t["contact_not_found"])

    st.markdown("### " + t["your_chats"])
    if not user_contacts:
      st.info(t["no_contacts"])
      selected_contact = None
    else:
      selected_contact = st.radio(t["select_chat"], user_contacts)

    st.markdown("---")
    st.subheader(t["del_contact_section"])
    if user_contacts:
      contact_to_delete = st.selectbox(t["select_to_delete"], user_contacts)
      if st.button(t["delete_contact_btn"]):
        trash_db = load_trash()
        if st.session_state.username not in trash_db:
          trash_db[st.session_state.username] = []

        all_chats = load_chats()
        rooms_to_remove = [
            room
            for room in all_chats.keys()
            if st.session_state.username in room
            and contact_to_delete in room
        ]

        chat_backups = {}
        for r in rooms_to_remove:
          chat_backups[str(r)] = all_chats[r]
          del all_chats[r]
        save_chats(all_chats)

        if contact_to_delete in user_contacts:
          user_contacts.remove(contact_to_delete)
          all_contacts_db[st.session_state.username] = user_contacts
          save_contacts(all_contacts_db)

        trash_db[st.session_state.username].append({
            "type": "contact_chat",
            "contact": contact_to_delete,
            "chats": chat_backups,
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })
        save_trash(trash_db)

        log_audit_event(
            st.session_state.username, f"Contacto a papelera: {contact_to_delete}"
        )
        st.success(t["contact_deleted_success"])
        st.rerun()

  with col2:
    if selected_contact:
      if selected_contact not in users_db:
        st.error(t["account_deleted_chat_msg"])
        if st.button(t["delete_contact_btn"]):
          if selected_contact in user_contacts:
            user_contacts.remove(selected_contact)
            all_contacts_db[st.session_state.username] = user_contacts
            save_contacts(all_contacts_db)

          all_chats = load_chats()
          rooms_to_remove = [
              room
              for room in all_chats.keys()
              if st.session_state.username in room
              and selected_contact in room
          ]
          for r in rooms_to_remove:
            del all_chats[r]
          save_chats(all_chats)

          st.success(t["contact_deleted_success"])
          st.rerun()
      else:
        st.subheader(f"Chat: {selected_contact}")
        chat_container = st.container(height=350)

        st.session_state.chat_history = load_chats()
        room_key = tuple(sorted([st.session_state.username, selected_contact]))

        if room_key not in st.session_state.chat_history:
          st.session_state.chat_history[room_key] = [
              {"sender": selected_contact, "text": "¡Hola / Kaixo!"}
          ]
          save_chats(st.session_state.chat_history)

        with chat_container:
          for msg in st.session_state.chat_history[room_key]:
            if msg["sender"] == st.session_state.username:
              st.markdown(
                  f"<div style='text-align: right; background-color:"
                  f" #DCF8C6; color: black; padding: 8px; border-radius: 10px;"
                  f" margin: 5px;'><b>Tú / Zu:</b> {msg['text']}</div>",
                  unsafe_allow_html=True,
              )
            else:
              st.markdown(
                  f"<div style='text-align: left; background-color: #E2E2E2;"
                  f" color: black; padding: 8px; border-radius: 10px; margin:"
                  f" 5px;'><b>{msg['sender']}:</b> {msg['text']}</div>",
                  unsafe_allow_html=True,
              )

        with st.form(key="chat_form", clear_on_submit=True):
          mensaje_texto = st.text_input(t["type_msg"])
          enviar_msg = st.form_submit_button(t["send_btn"])
          if enviar_msg and mensaje_texto:
            st.session_state.chat_history[room_key].append(
                {"sender": st.session_state.username, "text": mensaje_texto}
            )
            save_chats(st.session_state.chat_history)
            st.rerun()
    else:
      st.info(t["select_contact_prompt"])

# ----------------------------------------------------
# SECCIÓN 4: CIFRADO DE IMÁGENES (CON CONTROL DE EXCEPCIÓN PIL)
# ----------------------------------------------------
elif menu == t["sec4"]:
  st.header("🖼️ " + t["img_title"])
  st.write(t["img_desc"])

  img_tab1, img_tab2 = st.tabs([t["img_cifrar_tab"], t["img_descifrar_tab"]])

  with img_tab1:
    uploaded_file = st.file_uploader(
        t["subir_img_label"], type=["png", "jpg", "jpeg"]
    )
    if uploaded_file is not None:
      try:
        uploaded_file.seek(0)
        image = Image.open(uploaded_file)
        st.image(image, caption=t["img_original_caption"], width=300)

        if st.button(t["cifrar_img_btn"]):
          uploaded_file.seek(0)
          img_bytes = uploaded_file.getvalue()
          clave_img = Fernet.generate_key()
          f_img = Fernet(clave_img)
          token_img_bytes = f_img.encrypt(img_bytes)

          paquete_img = {
              "key": clave_img.decode(),
              "data": token_img_bytes.decode(),
          }
          token_img_completo = base64.b64encode(
              json.dumps(paquete_img).encode()
          ).decode()

          log_audit_event(st.session_state.username, "Imagen cifrada")
          st.success(t["img_cifrada_exito"])
          st.text_area(t["token_img_label"], token_img_completo)

      except UnidentifiedImageError:
        st.error(t["invalid_image_err"])
      except Exception as e:
        st.error(f"Error: {e}")

  with img_tab2:
    token_input = st.text_area(t["token_img_input"])

    if st.button(t["descifrar_img_btn"]):
      try:
        json_decodificado = base64.b64decode(token_input.encode()).decode()
        paquete_img = json.loads(json_decodificado)

        clave_extraida = paquete_img["key"].encode()
        datos_cifrados = paquete_img["data"].encode()

        f_img = Fernet(clave_extraida)
        decrypted_bytes = f_img.decrypt(datos_cifrados)

        image_stream = io.BytesIO(decrypted_bytes)
        restored_image = Image.open(image_stream)

        log_audit_event(st.session_state.username, "Imagen descifrada")
        st.success(t["img_decrypted_success"])
        st.image(restored_image, caption=t["img_decrypted_caption"], width=300)
      except Exception as e:
        st.error(f"{t['img_error']}{e}")

# ----------------------------------------------------
# SECCIÓN 5: PAPELERA DE RECICLAJE
# ----------------------------------------------------
elif menu == t["sec5"]:
  st.header("🗑️ " + t["trash_title"])
  st.write(t["trash_desc"])

  trash_db = load_trash()
  user_trash = trash_db.get(st.session_state.username, [])

  if not user_trash:
    st.info(t["no_trash"])
  else:
    for idx, item in enumerate(user_trash):
      col_t1, col_t2, col_t3 = st.columns([3, 1, 1])
      with col_t1:
        st.markdown(
            f"**Contact / Kontaktua:** `{item['contact']}` — _({item['time']})_"
        )
      with col_t2:
        if st.button(t["restore_btn"], key=f"res_{idx}"):
          contacts_db = load_contacts()
          u_contacts = contacts_db.get(st.session_state.username, [])
          if item["contact"] not in u_contacts:
            u_contacts.append(item["contact"])
            contacts_db[st.session_state.username] = u_contacts
            save_contacts(contacts_db)

          all_chats = load_chats()
          for r_str, c_data in item["chats"].items():
            all_chats[eval(r_str)] = c_data
          save_chats(all_chats)

          user_trash.pop(idx)
          trash_db[st.session_state.username] = user_trash
          save_trash(trash_db)

          log_audit_event(
              st.session_state.username, f"Restaurado: {item['contact']}"
          )
          st.success(t["item_restored"])
          st.rerun()

      with col_t3:
        if st.button(t["permanent_delete_btn"], key=f"del_{idx}"):
          user_trash.pop(idx)
          trash_db[st.session_state.username] = user_trash
          save_trash(trash_db)

          log_audit_event(
              st.session_state.username, f"Purgado: {item['contact']}"
          )
          st.success(t["item_purged"])
          st.rerun()

# ----------------------------------------------------
# SECCIÓN 6: PANEL DE ADMINISTRACIÓN (EXCLUSIVO PARA JUAN)
# ----------------------------------------------------
elif menu == t["admin_sec"] and st.session_state.username == "Juan":
  st.header("🛡️ " + t["admin_title"])
  st.write(t["admin_desc"])

  users_db = load_users()
  all_chats = load_chats()
  audit_data = load_audit()

  admin_tab1, admin_tab2, admin_tab3 = st.tabs(
      [t["admin_tab1"], t["admin_tab2"], t["admin_tab3"]]
  )

  with admin_tab1:
    st.subheader(t["accounts_registered"])
    for usr in list(users_db.keys()):
      col_u1, col_u2, col_u3 = st.columns([2, 2, 2])
      with col_u1:
        is_online = usr in st.session_state.active_sessions
        status_txt = "🟢 Online" if is_online else "🔴 Offline"
        st.markdown(f"**{usr}** — {status_txt}")
      with col_u2:
        st.text(f"Password: {users_db[usr]}")
      with col_u3:
        if usr != "Juan":
          if st.button(f"{t['expulsar_btn']} {usr}", key=f"exp_{usr}"):
            if usr in users_db:
              del users_db[usr]
              save_users(users_db)
            if usr in st.session_state.active_sessions:
              st.session_state.active_sessions.remove(usr)
            st.success(f"{usr} {t['user_expulsado']}")
            st.rerun()

  with admin_tab2:
    st.subheader(t["chats_registered_admin"])
    if not all_chats:
      st.info(t["no_chats_admin"])
    else:
      for room, msgs in all_chats.items():
        user_a, user_b = room
        st.markdown(f"### 📁 {t['chat_between']}: **{user_a}** & **{user_b}**")
        for m in msgs:
          st.text(f"[{m['sender']}]: {m['text']}")
        st.markdown("---")

  with admin_tab3:
    st.subheader(t["audit_title"])
    st.write(t["audit_desc"])
    if not audit_data:
      st.info(t["no_audit"])
    else:
      for usr_acc, events in audit_data.items():
        st.markdown(f"### 👤 Usuario: **{usr_acc}**")
        event_rows = []
        for ev in events:
          event_rows.append(
              {t["audit_time"]: ev["time"], t["audit_event"]: ev["event"]}
          )
        st.table(event_rows)
        st.markdown("---")

# ----------------------------------------------------
# CONFIGURACIÓN
# ----------------------------------------------------
elif menu == t["config"]:
  st.header("⚙️ " + t["config"])

  with st.form("config_form"):
    st.subheader(t["lang_label"])
    nuevo_idioma = st.selectbox(
        "Select language / Hautatu hizkuntza / Seleccionar idioma / Choisir la langue",
        ["Español", "Euskera", "English", "Français"],
        index=["Español", "Euskera", "English", "Français"].index(
            st.session_state.lang
        ),
    )

    guardar_cambios = st.form_submit_button(t["save_config"])

    if guardar_cambios:
      if nuevo_idioma != st.session_state.lang:
        st.session_state.lang = nuevo_idioma
        st.success(t["config_success"])
        time.sleep(0.5)
        st.rerun()
      else:
        st.info(t["same_lang_info"])

# ----------------------------------------------------
# ASISTENTE IA DE GEMINI (BARRA LATERAL)
# ----------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.subheader("🤖 " + t["ai_helper"])
ai_query = st.sidebar.text_input(t["ai_query_label"])

if st.sidebar.button(t["ai_query_btn"]):
  if ai_query:
    if not gemini_model:
      st.sidebar.error(t["ai_missing_key"])
    else:
      with st.sidebar.spinner(t["ai_thinking"]):
        try:
          prompt_helper = t["ai_helper_prompt"].format(
              menu=menu, ai_query=ai_query
          )
          response = gemini_model.generate_content(prompt_helper)
          st.sidebar.success(response.text)
        except Exception as e:
          st.sidebar.error(f"Error: {e}")
  else:
    st.sidebar.warning(t["write_query"])

# ----------------------------------------------------
# ENLACE CALCULADORA CON IA
# ----------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.markdown(t["calc_link"])
