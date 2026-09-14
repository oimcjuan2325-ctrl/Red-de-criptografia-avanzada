import base64
import json
import os
import time
import google.generativeai as genai
import streamlit as st
from cryptography.fernet import Fernet

# ====================================================
# CONFIGURACIÓN SEGURA DE LA API KEY (DESDE SECRETS DE STREAMLIT)
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


# Inicializar estados de sesión
if "logged_in" not in st.session_state:
  st.session_state.logged_in = False
if "username" not in st.session_state:
  st.session_state.username = ""
if "lang" not in st.session_state:
  st.session_state.lang = "Español"

if "users_db" not in st.session_state:
  st.session_state.users_db = load_users()

if "chat_history" not in st.session_state:
  st.session_state.chat_history = load_chats()

# Textos traducidos completos (Español y Euskera)
TRANSLATIONS = {
    "Español": {
        "login_title": "Iniciar Sesión",
        "user_label": "Nombre de usuario",
        "pass_label": "Contraseña",
        "login_btn": "Entrar",
        "login_error": "Usuario o contraseña incorrectos",
        "register_txt": "¿No tienes cuenta? Regístrate aquí",
        "register_btn": "Registrarse",
        "logout": "Cerrar Sesión",
        "nav_title": "Menú Principal",
        "sec1": "1. Cifrado y Descifrado Potente",
        "sec2": "2. Base de Descifrado Inteligente (IA)",
        "sec3": "3. Mini-WhatsApp (Chat)",
        "config": "Configuración",
        "ai_helper": "Asistente IA",
        "lang_label": "Idioma / Hizkuntza",
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
            " mensajes con una clave secreta."
        ),
        "cifrar_tab": "Cifrar Mensaje",
        "descifrar_tab": "Descifrar Mensaje",
        "texto_plano_label": "Introduce el texto que deseas cifrar:",
        "cifrar_btn": "Cifrar",
        "cifrado_exito": "¡Texto cifrado con éxito!",
        "clave_usada": "🔑 **Clave secreta utilizada (Guárdala):**",
        "texto_cifrado_label": "Introduce el texto cifrado (Token):",
        "clave_input_label": "Introduce la clave secreta:",
        "descifrar_btn": "Descifrar",
        "descifrar_exito": "¡Descifrado con éxito!",
        "texto_original": "Texto Original:",
        "ia_title": "Base de Descifrado Inteligente con IA (Gemini)",
        "ia_desc": (
            "Pega cualquier mensaje cifrado y Gemini lo analizará,"
            " descifrará y explicará el paso a paso."
        ),
        "ia_input": "Introduce el mensaje cifrado misterioso:",
        "ia_btn": "Analizar y Descifrar con Gemini",
        "ia_spinner": "Gemini está analizando el cifrado...",
        "ia_result": "¡Análisis completado por Gemini!",
        "ai_helper_desc": (
            "Gemini está conectado para ayudarte en esta sección."
        ),
        "ai_query_label": "¿En qué te puedo ayudar?",
        "ai_query_btn": "Preguntar a Gemini",
    },
    "Euskera": {
        "login_title": "Saioa Hasi",
        "user_label": "Erabiltzaile izena",
        "pass_label": "Pasahitza",
        "login_btn": "Sartu",
        "login_error": "Erabiltzaile edo pasahitz okerra",
        "register_txt": "Ez duzu konturik? Erregistratu hemen",
        "register_btn": "Erregistratu",
        "logout": "Saioa Itxi",
        "nav_title": "Menu Nagusia",
        "sec1": "1. Enkripzio eta Desenkripzio Indartsua",
        "sec2": "2. Desenkripzio Adimendunaren Basea (AI)",
        "sec3": "3. Mini-WhatsApp (Txata)",
        "config": "Konfigurazioa",
        "ai_helper": "AI Laguntzailea",
        "lang_label": "Hizkuntza / Idioma",
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
            " gako sekretu batekin babesteko."
        ),
        "cifrar_tab": "Enkripatu Mezua",
        "descifrar_tab": "Desenkripatu Mezua",
        "texto_plano_label": "Sartu enkripatu nahi duzun testua:",
        "cifrar_btn": "Enkripatu",
        "cifrado_exito": "Testua arrakastaz enkripatu da!",
        "clave_usada": "🔑 **Erabilitako gako sekretua (Gorde ezazu):**",
        "texto_cifrado_label": "Sartu testu enkripatua (Tokena):",
        "clave_input_label": "Sartu gako sekretua:",
        "descifrar_btn": "Desenkripatu",
        "descifrar_exito": "Arrakastaz desenkripatua!",
        "texto_original": "Jatorrizko Testua:",
        "ia_title": "Desenkripzio Adimendunaren Basea AI-rekin (Gemini)",
        "ia_desc": (
            "Itsatsi edzein mezu eta Gemini-k aztertuko du, desenkripatu eta"
            " urratsez urrats azalduko du."
        ),
        "ia_input": "Sartu mezu enkripatu misteriotsua:",
        "ia_btn": "Aztertu eta Desenkripatu Gemini-rekin",
        "ia_spinner": "Gemini enkripzioa aztertzen ari da...",
        "ia_result": "Gemini-k analisia osatu du!",
        "ai_helper_desc": (
            "Gemini konektatuta dago atal honetan laguntzeko."
        ),
        "ai_query_label": "Zertan lagundu dezaket?",
        "ai_query_btn": "Galdetu Gemini-ri",
    },
}

t = TRANSLATIONS[st.session_state.lang]

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
        st.session_state.users_db = load_users()
        if (
            u_input in st.session_state.users_db
            and st.session_state.users_db[u_input] == p_input
        ):
          st.session_state.logged_in = True
          st.session_state.username = u_input
          st.rerun()
        else:
          st.error(t["login_error"])

  with tab2:
    with st.form("reg_form"):
      new_u = st.text_input(t["user_label"])
      new_p = st.text_input(t["pass_label"], type="password")
      reg_submit = st.form_submit_button(t["register_btn"])

      if reg_submit:
        st.session_state.users_db = load_users()
        if new_u in st.session_state.users_db:
          st.warning("El usuario ya existe. / Erabiltzailea badago jada.")
        elif new_u and new_p:
          st.session_state.users_db[new_u] = new_p
          save_users(st.session_state.users_db)
          st.success("¡Cuenta creada con éxito! / Kontua arrakastaz sortu da!")
        else:
          st.error("Rellene todos los campos. / Bete eremu guztiak.")

  st.stop()

# ----------------------------------------------------
# APLICACIÓN PRINCIPAL
# ----------------------------------------------------
st.sidebar.title(f"👤 {st.session_state.username}")
if st.sidebar.button(t["logout"]):
  st.session_state.logged_in = False
  st.session_state.username = ""
  st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader(t["nav_title"])
menu = st.sidebar.radio(
    "Navegación", [t["sec1"], t["sec2"], t["sec3"], t["config"]]
)

# ----------------------------------------------------
# SECCIÓN 1: CIFRADO Y DESCIFRADO POTENTE (AES)
# ----------------------------------------------------
if menu == t["sec1"]:
  st.header("🔒 " + t["cifrado_title"])
  st.write(t["cifrado_desc"])

  if "fernet_key" not in st.session_state:
    st.session_state.fernet_key = Fernet.generate_key()

  sub_tab1, sub_tab2 = st.tabs([t["cifrar_tab"], t["descifrar_tab"]])

  with sub_tab1:
    texto_plano = st.text_area(t["texto_plano_label"], "Mensaje secreto")
    if st.button(t["cifrar_btn"]):
      f = Fernet(st.session_state.fernet_key)
      token = f.encrypt(texto_plano.encode())
      st.success(t["cifrado_exito"])
      st.code(token.decode())
      st.info(f"{t['clave_usada']} `{st.session_state.fernet_key.decode()}`")

  with sub_tab2:
    texto_cifrado = st.text_area(t["texto_cifrado_label"])
    clave_input = st.text_input(t["clave_input_label"], type="password")
    if st.button(t["descifrar_btn"]):
      try:
        f = Fernet(clave_input.encode())
        decrypted = f.decrypt(texto_cifrado.encode())
        st.success(t["descifrar_exito"])
        st.write(f"**{t['texto_original']}**", decrypted.decode())
      except Exception as e:
        st.error(f"Error: {e}")

# ----------------------------------------------------
# SECCIÓN 2: BASE DE DESCIFRADO INTELIGENTE CON GEMINI
# ----------------------------------------------------
elif menu == t["sec2"]:
  st.header("🕵️‍♂️ " + t["ia_title"])
  st.write(t["ia_desc"])

  cifrado_usuario = st.text_area(t["ia_input"])

  if st.button(t["ia_btn"]):
    if not cifrado_usuario:
      st.warning("Por favor, introduce un texto.")
    elif not gemini_model:
      st.error(
          "La API Key no está configurada en los Secrets de Streamlit Cloud."
      )
    else:
      with st.spinner(t["ia_spinner"]):
        try:
          prompt = (
              "Analiza el siguiente texto cifrado o codificado. Detecta el tipo"
              " de cifrado, devuélvelo descifrado y explica el paso a paso."
              f" Texto: {cifrado_usuario}"
          )
          response = gemini_model.generate_content(prompt)
          st.success(t["ia_result"])
          st.markdown(response.text)
        except Exception as e:
          st.error(f"Error al conectar con Gemini: {e}")

# ----------------------------------------------------
# SECCIÓN 3: MINI-WHATSAPP (CHAT)
# ----------------------------------------------------
elif menu == t["sec3"]:
  st.header("💬 " + t["chat_title"])
  st.write(t["chat_desc"])

  col1, col2 = st.columns([1, 3])

  all_contacts_db = load_contacts()
  user_contacts = all_contacts_db.get(st.session_state.username, [])

  with col1:
    st.subheader("Contactos")
    nuevo_contacto = st.text_input(t["add_contact_label"])
    if st.button(t["add_btn"]):
      st.session_state.users_db = load_users()

      if (
          nuevo_contacto in st.session_state.users_db
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

  with col2:
    if selected_contact:
      st.subheader(f"Chat con: {selected_contact}")
      chat_container = st.container(height=350)

      st.session_state.chat_history = load_chats()
      room_key = tuple(sorted([st.session_state.username, selected_contact]))

      if room_key not in st.session_state.chat_history:
        st.session_state.chat_history[room_key] = [
            {"sender": selected_contact, "text": "¡Hola!"}
        ]
        save_chats(st.session_state.chat_history)

      with chat_container:
        for msg in st.session_state.chat_history[room_key]:
          if msg["sender"] == st.session_state.username:
            st.markdown(
                f"<div style='text-align: right; background-color:"
                f" #DCF8C6; color: black; padding: 8px; border-radius: 10px;"
                f" margin: 5px;'><b>Tú:</b> {msg['text']}</div>",
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
      st.info("Selecciona o agrega un contacto para ver la conversación.")

# ----------------------------------------------------
# CONFIGURACIÓN
# ----------------------------------------------------
elif menu == t["config"]:
  st.header("⚙️ " + t["config"])

  with st.form("config_form"):
    st.subheader(t["lang_label"])
    nuevo_idioma = st.selectbox(
        "Selecciona idioma / Hautatu hizkuntza",
        ["Español", "Euskera"],
        index=0 if st.session_state.lang == "Español" else 1,
    )

    guardar_cambios = st.form_submit_button(t["save_config"])

    if guardar_cambios:
      if nuevo_idioma != st.session_state.lang:
        st.session_state.lang = nuevo_idioma
        st.success(t["config_success"])
        time.sleep(0.5)
        st.rerun()
      else:
        st.info("El idioma seleccionado es el mismo.")

# ----------------------------------------------------
# ASISTENTE IA DE GEMINI (BARRA LATERAL)
# ----------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.subheader("🤖 " + t["ai_helper"])
ai_query = st.sidebar.text_input(t["ai_query_label"])

if st.sidebar.button(t["ai_query_btn"]):
  if ai_query:
    if not gemini_model:
      st.sidebar.error("Falta configurar la API Key en los Secrets.")
    else:
      with st.sidebar.spinner("Gemini pensando..."):
        try:
          prompt_helper = (
              f"Estás en una web de ciberseguridad en la sección '{menu}'."
              f" El usuario pregunta: {ai_query}. Responde de forma útil y"
              " breve."
          )
          response = gemini_model.generate_content(prompt_helper)
          st.sidebar.success(response.text)
        except Exception as e:
          st.sidebar.error(f"Error: {e}")
  else:
    st.sidebar.warning("Escribe una consulta.")

# ----------------------------------------------------
# ENLACE CALCULADORA CON IA
# ----------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.markdown(
    "🔗 **[calculadora con IA](https://calculadora-con-ia.streamlit.app)**"
)
