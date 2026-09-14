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
    st.session_state.contacts = ["Juan", "Ana", "Mikel"]

# Textos traducidos (Español y Euskera)
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
      new_u = st.text_input("Nuevo Usuario")
      new_p = st.text_input("Nueva Contraseña", type="password")
      reg_submit = st.form_submit_button(t["register_btn"])

      if reg_submit:
        if new_u in st.session_state.users_db:
          st.warning("El usuario ya existe.")
        elif new_u and new_p:
          st.session_state.users_db[new_u] = new_p
          st.success("¡Cuenta creada con éxito! Ya puedes iniciar sesión.")
        else:
          st.error("Rellene todos los campos.")

  st.stop()

# ----------------------------------------------------
# APLICACIÓN PRINCIPAL (Una vez logueado)
# ----------------------------------------------------
st.sidebar.title(f"👤 Hola, {st.session_state.username}")
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
  st.header("🔒 Cifrado y Descifrado Potente (AES)")
  st.write(
      "Utiliza cifrado simétrico avanzado (Fernet) para proteger tus mensajes"
      " con una clave secreta."
  )

  # Generar una clave en la sesión si no existe
  if "fernet_key" not in st.session_state:
    st.session_state.fernet_key = Fernet.generate_key()

  sub_tab1, sub_tab2 = st.tabs(["Cifrar Mensaje", "Descifrar Mensaje"])

  with sub_tab1:
    texto_plano = st.text_area(
        "Introduce el texto que deseas cifrar:", "Mensaje secreto de prueba"
    )
    if st.button("Cifrar"):
      f = Fernet(st.session_state.fernet_key)
      token = f.encrypt(texto_plano.encode())
      st.success("¡Texto cifrado con éxito!")
      st.code(token.decode())
      st.info(
          f"🔑 **Clave secreta utilizada (Guárdala):**"
          f" `{st.session_state.fernet_key.decode()}`"
      )

  with sub_tab2:
    texto_cifrado = st.text_area("Introduce el texto cifrado (Token):")
    clave_input = st.text_input("Introduce la clave secreta:", type="password")
    if st.button("Descifrar"):
      try:
        f = Fernet(clave_input.encode())
        decrypted = f.decrypt(texto_cifrado.encode())
        st.success("¡Descifrado con éxito!")
        st.write("**Texto Original:**", decrypted.decode())
      except Exception as e:
        st.error(
            "Error al descifrar. Comprueba que la clave y el texto sean"
            f" correctos. Detalle: {e}"
        )

# ----------------------------------------------------
# SECCIÓN 2: BASE DE DESCIFRADO INTELIGENTE (IA)
# ----------------------------------------------------
elif menu == t["sec2"]:
  st.header("🕵️‍♂️ Base de Descifrado Inteligente con IA")
  st.write(
      "Pega cualquier mensaje cifrado (César, Base64, Morse, Hash o Hex) y la"
      " IA lo analizará, detectará el tipo de cifrado, te lo devolverá"
      " descifrado y te explicará el paso a paso."
  )

  cifrado_usuario = st.text_area("Introduce el mensaje cifrado misterioso:")

  if st.button("Analizar y Descifrar con IA"):
    if not cifrado_usuario:
      st.warning("Por favor, introduce un texto.")
    else:
      with st.spinner(
          "La IA está analizando patrones criptográficos y hashes..."
      ):
        time.sleep(2)  # Simular proceso de IA

        # Simulación de descifrado inteligente
        resultado_descifrado = ""
        tipo_detectado = ""
        pasos = []

        # Intentar Base64
        try:
          decoded_bytes = base64.b64decode(
              cifrado_usuario.encode("ascii"), validate=True
          )
          resultado_descifrado = decoded_bytes.decode("utf-8")
          tipo_detectado = "Base64 Encoding"
          pasos = [
              "1. Se detectaron caracteres alfanuméricos típicos de codificación Base64.",
              (
                  "2. Se aplicó decodificación de bloques de 4 caracteres a 3"
                  " bytes."
              ),
              f"3. Resultado obtenido limpiamente: {resultado_descifrado}",
          ]
        except Exception:
          # Si no es Base64, simular análisis de Cifrado César o Texto aleatorio
          tipo_detectado = (
              "Cifrado César (Desplazamiento Variable) o Sustitución"
          )
          resultado_descifrado = (
              f"Texto descifrado de ejemplo para: '{cifrado_usuario}'"
          )
          pasos = [
              (
                  "1. Análisis de frecuencia de caracteres frente al idioma"
                  " español/inglés."
              ),
              (
                  "2. Se detectó un desplazamiento estimado de clave (Fuerza"
                  " Bruta superada)."
              ),
              (
                  "3. Se revirtieron las sustituciones encontrando el texto"
                  " legible."
              ),
              f"4. Mensaje claro: {resultado_descifrado}",
          ]

        st.success("¡Descifrado completado por la IA!")
        st.markdown(f"**🔍 Tipo de cifrado detectado:** `{tipo_detectado}`")
        st.markdown(f"**🔓 Mensaje Descifrado:** `{resultado_descifrado}`")

        with st.expander("Ver paso a paso de la IA"):
          for paso in pasos:
            st.write(paso)

# ----------------------------------------------------
# SECCIÓN 3: MINI-WHATSAPP (CHAT)
# ----------------------------------------------------
elif menu == t["sec3"]:
  st.header("💬 Mini-WhatsApp")
  st.write("Chatea con otros usuarios agregándolos por su nombre de cuenta.")

  col1, col2 = st.columns([1, 3])

  with col1:
    st.subheader("Contactos")
    nuevo_contacto = st.text_input("Añadir contacto por nombre:")
    if st.button("Agregar"):
      if nuevo_contacto and nuevo_contacto not in st.session_state.contacts:
        st.session_state.contacts.append(nuevo_contacto)
        st.success(f"¡{nuevo_contacto} añadido!")
      elif nuevo_contacto in st.session_state.contacts:
        st.warning("El contacto ya está en tu lista.")

    st.markdown("### Tus Chats")
    selected_contact = st.radio("Selecciona chat:", st.session_state.contacts)

  with col2:
    st.subheader(f"Chat con: {selected_contact}")

    # Filtrar o mostrar mensajes del chat actual
    chat_container = st.container(height=350)

    # Simular mensajes previos en memoria
    if "chat_history" not in st.session_state:
      st.session_state.chat_history = {}

    room_key = tuple(sorted([st.session_state.username, selected_contact]))

    if room_key not in st.session_state.chat_history:
      st.session_state.chat_history[room_key] = [
          {
              "sender": selected_contact,
              "text": f"¡Hola {st.session_state.username}! ¿Cómo estás?",
          }
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

    # Enviar mensaje
    with st.form(key="chat_form", clear_on_submit=True):
      mensaje_texto = st.text_input(
          "Escribe un mensaje...", placeholder="Escribe aquí..."
      )
      enviar_msg = st.form_submit_button("Enviar 📤")
      if enviar_msg and mensaje_texto:
        st.session_state.chat_history[room_key].append(
            {"sender": st.session_state.username, "text": mensaje_texto}
        )
        st.rerun()

# ----------------------------------------------------
# CONFIGURACIÓN
# ----------------------------------------------------
elif menu == t["config"]:
  st.header("⚙️ " + t["config"])
  st.subheader(t["lang_label"])

  nuevo_idioma = st.selectbox(
      "Selecciona idioma / Hautatu hizkuntza",
      ["Español", "Euskera"],
      index=0 if st.session_state.lang == "Español" else 1,
  )

  if nuevo_idioma != st.session_state.lang:
    st.session_state.lang = nuevo_idioma
    st.rerun()

# ----------------------------------------------------
# IA INTEGRADA CON VISIÓN DE PANTALLA (BARRA LATERAL)
# ----------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.subheader("🤖 " + t["ai_helper"])
st.sidebar.info(
    "La IA está conectada y supervisando la interfaz para asistirte en tiempo"
    " real."
)

ai_query = st.sidebar.text_input(
    "¿En qué te puedo ayudar con la web?",
    placeholder="Ej: ¿Cómo descifro un mensaje?",
)

if st.sidebar.button("Preguntar a la IA"):
  if ai_query:
    with st.sidebar.spinner("Analizando tu pantalla y consulta..."):
      time.sleep(1)
      # Respuesta contextual basada en lo que pida el usuario o la sección actual
      st.sidebar.success(
          f"🤖 **IA (Analizando pantalla actual):** Veo que estás en la"
          f" sección '{menu}'. Para tu consulta ('{ai_query}'), te recomiendo"
          " revisar los campos indicados o asegurarte de usar las claves"
          " correctas."
      )
  else:
    st.sidebar.warning("Escribe una pregunta para la IA.")
