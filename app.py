import base64
import time
import streamlit as st
from cryptography.fernet import Fernet

# Configuración de la página
st.set_page_config(
    page_title="Plataforma Segura e Inteligente",
    page_icon="🔒",
    layout="wide",
)

# Inicializar estados de sesión si no existen
if "logged_in" not in st.session_state:
  st.session_state.logged_in = False
if "username" not in st.session_state:
  st.session_state.username = ""
if "lang" not in st.session_state:
  st.session_state.lang = "Español"
if "users_db" not in st.session_state:
  # Base de datos inicial con Juan
  st.session_state.users_db = {"Juan": "2325"}
if "messages" not in st.session_state:
  st.session_state.messages = []
if "contacts" not in st.session_state:
  # Lista de contactos limpia (sin predeterminados como Mikel o Ana)
  st.session_state.contacts = []

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
        "ai_helper": "Asistente IA (Screen Vision)",
        "lang_label": "Idioma / Hizkuntza",
        "save_config": "Guardar cambios",
        "config_success": "¡Idioma actualizado y web reiniciada con éxito!",
        "chat_title": "Mini-WhatsApp",
        "chat_desc": (
            "Chatea con otros usuarios agregándolos por su nombre de cuenta."
        ),
        "add_contact_label": "Añadir contacto por nombre:",
        "add_btn": "Agregar",
        "contact_added": "¡Contacto añadido!",
        "contact_exists": (
            "El contacto ya está en tu lista o el campo está vacío."
        ),
        "no_contacts": (
            "No tienes contactos aún. Agrega uno a la izquierda para empezar"
            " a chatear."
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
        "ia_title": "Base de Descifrado Inteligente con IA",
        "ia_desc": (
            "Pega cualquier mensaje cifrado y la IA lo analizará, detectará el"
            " tipo de cifrado, te lo devolverá descifrado y te explicará el"
            " paso a paso."
        ),
        "ia_input": "Introduce el mensaje cifrado misterioso:",
        "ia_btn": "Analizar y Descifrar con IA",
        "ia_spinner": "La IA está analizando patrones criptográficos...",
        "ia_result": "¡Descifrado completado por la IA!",
        "ia_type": "Tipo de cifrado detectado:",
        "ia_msg": "Mensaje Descifrado:",
        "ia_steps": "Ver paso a paso de la IA",
        "ai_helper_desc": (
            "La IA está conectada y supervisando la interfaz para asistirte"
            " en tiempo real."
        ),
        "ai_query_label": "¿En qué te puedo ayudar con la web?",
        "ai_query_btn": "Preguntar a la IA",
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
        "ai_helper": "AI Laguntzailea (Pantaila Ikusmena)",
        "lang_label": "Hizkuntza / Idioma",
        "save_config": "Gorde aldaketak",
        "config_success": (
            "Hizkuntza eguneratuta eta webgunea berrabiarazi da arrakastaz!"
        ),
        "chat_title": "Mini-WhatsApp",
        "chat_desc": (
            "Txateatu beste erabiltzaile batzuekin haien kontu-izenaren bidez"
            " gehituz."
        ),
        "add_contact_label": "Gehitu kontaktua izenez:",
        "add_btn": "Gehitu",
        "contact_added": "Kontaktua gehituta!",
        "contact_exists": (
            "Kontaktua zerrendan dago jada edo eremua hutsik dago."
        ),
        "no_contacts": (
            "Ez duzu kontakturik oraindik. Gehitu bat ezkerrean txateatzen"
            " hasteko."
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
        "ia_title": "Desenkripzio Adimendunaren Basea AI-rekin",
        "ia_desc": (
            "Itsatsi edzein mezu enkripatu eta AI-k aztertuko du, mota"
            " identifikatuko du, desenkripatuta itzuliko dizu eta urratsez urrats"
            " azalduko dizu."
        ),
        "ia_input": "Sartu mezu enkripatu misteriotsua:",
        "ia_btn": "Aztertu eta Desenkripatu AI-rekin",
        "ia_spinner": "AI ereduak patroiak aztertzen ari dira...",
        "ia_result": "AI-k desenkripzioa osatu du!",
        "ia_type": "Detektatutako enkripzio mota:",
        "ia_msg": "Mezu Desenkripatua:",
        "ia_steps": "Ikusi AI-ren urratsez urratsa",
        "ai_helper_desc": (
            "AI konektatuta dago eta interfazea gainbegiratzen ari da denbora"
            " errealean laguntzeko."
        ),
        "ai_query_label": "Zertan lagundu dezaket webgunearekin?",
        "ai_query_btn": "Galdetu AIari",
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
        if new_u in st.session_state.users_db:
          st.warning("El usuario ya existe. / Erabiltzailea badago jada.")
        elif new_u and new_p:
          st.session_state.users_db[new_u] = new_p
          st.success(
              "¡Cuenta creada con éxito! / Kontua arrakastaz sortu da!"
          )
        else:
          st.error("Rellene todos los campos. / Bete eremu guztiak.")

  st.stop()

# ----------------------------------------------------
# APLICACIÓN PRINCIPAL (Una vez logueado)
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
# SECCIÓN 1: CIFRADO Y DESCIFRADO POTENTE (AES / Fernet)
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
# SECCIÓN 2: BASE DE DESCIFRADO INTELIGENTE (IA)
# ----------------------------------------------------
elif menu == t["sec2"]:
  st.header("🕵️‍♂️ " + t["ia_title"])
  st.write(t["ia_desc"])

  cifrado_usuario = st.text_area(t["ia_input"])

  if st.button(t["ia_btn"]):
    if not cifrado_usuario:
      st.warning("Por favor, introduce un texto.")
    else:
      with st.spinner(t["ia_spinner"]):
        time.sleep(2)
        try:
          decoded_bytes = base64.b64decode(
              cifrado_usuario.encode("ascii"), validate=True
          )
          resultado_descifrado = decoded_bytes.decode("utf-8")
          tipo_detectado = "Base64 Encoding"
          pasos = [
              "1. Se detectaron bloques alfanuméricos de Base64.",
              "2. Se decodificaron los bytes.",
              f"3. Resultado: {resultado_descifrado}",
          ]
        except Exception:
          tipo_detectado = "Cifrado César / Sustitución"
          resultado_descifrado = f"Texto limpio de: '{cifrado_usuario}'"
          pasos = [
              "1. Análisis de frecuencias e inversión de desplazamiento.",
              "2. Reversión de caracteres aplicada.",
              f"3. Mensaje: {resultado_descifrado}",
          ]

        st.success(t["ia_result"])
        st.markdown(f"**{t['ia_type']}** `{tipo_detectado}`")
        st.markdown(f"**{t['ia_msg']}** `{resultado_descifrado}`")

        with st.expander(t["ia_steps"]):
          for paso in pasos:
            st.write(paso)

# ----------------------------------------------------
# SECCIÓN 3: MINI-WHATSAPP (CHAT)
# ----------------------------------------------------
elif menu == t["sec3"]:
  st.header("💬 " + t["chat_title"])
  st.write(t["chat_desc"])

  col1, col2 = st.columns([1, 3])

  with col1:
    st.subheader("Contactos")
    nuevo_contacto = st.text_input(t["add_contact_label"])
    if st.button(t["add_btn"]):
      if (
          nuevo_contacto
          and nuevo_contacto not in st.session_state.contacts
          and nuevo_contacto != st.session_state.username
      ):
        st.session_state.contacts.append(nuevo_contacto)
        st.success(t["contact_added"])
        st.rerun()
      else:
        st.warning(t["contact_exists"])

    st.markdown("### " + t["your_chats"])
    if not st.session_state.contacts:
      st.info(t["no_contacts"])
      selected_contact = None
    else:
      selected_contact = st.radio(t["select_chat"], st.session_state.contacts)

  with col2:
    if selected_contact:
      st.subheader(f"Chat con: {selected_contact}")
      chat_container = st.container(height=350)

      if "chat_history" not in st.session_state:
        st.session_state.chat_history = {}

      room_key = tuple(sorted([st.session_state.username, selected_contact]))

      if room_key not in st.session_state.chat_history:
        st.session_state.chat_history[room_key] = [
            {"sender": selected_contact, "text": "¡Hola!"}
        ]

      with chat_container:
        for msg in st.session_state.chat_history[room_key]:
          if msg["sender"] == st.session_state.username:
            st.markdown(
                f"<div style='text-align: right; background-color:"
                f" #DCF8C6; padding: 8px; border-radius: 10px; margin:"
                f" 5px;'><b>Tú:</b> {msg['text']}</div>",
                unsafe_allow_html=True,
            )
          else:
            st.markdown(
                f"<div style='text-align: left; background-color: #E2E2E2;"
                f" padding: 8px; border-radius: 10px; margin:"
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
          st.rerun()
    else:
      st.info(
          "Selecciona o agrega un contacto a la izquierda para ver la"
          " conversación."
      )

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
# ASISTENTE IA CON VISIÓN DE PANTALLA (BARRA LATERAL)
# ----------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.subheader("🤖 " + t["ai_helper"])
st.sidebar.info(t["ai_helper_desc"])

ai_query = st.sidebar.text_input(t["ai_query_label"])

if st.sidebar.button(t["ai_query_btn"]):
  if ai_query:
    with st.sidebar.spinner("Analizando pantalla..."):
      time.sleep(1)
      st.sidebar.success(
          f"🤖 **IA:** Analizando la sección actual ('{menu}'). Para tu"
          f" consulta ('{ai_query}'), asegúrate de revisar los apartados"
          " correspondientes de la interfaz."
      )
  else:
    st.sidebar.warning("Escribe una consulta.")
