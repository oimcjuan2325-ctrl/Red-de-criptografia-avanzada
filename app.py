import mpmath
import numpy as np
import streamlit as st
import sympy as sp
import plotly.graph_objects as go
from google import genai

mpmath.mp.dps = 30

st.set_page_config(
    page_title="HyperCalc | Consola Científica Avanzada",
    page_icon="🧮",
    layout="wide",
)

st.markdown(
    """
    <style>
    .main { background-color: #0e1117; }
    h1 { color: #00ffcc; }
    .stTextInput input, .stTextArea textarea { 
        background-color: #161b22; 
        color: #00ffcc; 
        border: 1px solid #30363d; 
        font-family: monospace;
        font-size: 1.1rem;
    }
    div.stButton > button {
        background-color: #21262d;
        color: #c9d1d9;
        border: 1px solid #30363d;
        border-radius: 6px;
        font-weight: bold;
    }
    div.stButton > button:hover {
        background-color: #30363d;
        color: #00ffcc;
        border-color: #00ffcc;
    }
    </style>
""",
    unsafe_allow_html=True,
)

if "lang" not in st.session_state:
    st.session_state.lang = "Español"
if "sci_val" not in st.session_state:
    st.session_state.sci_val = ""
if "last_result" not in st.session_state:
    st.session_state.last_result = "Ningún cálculo realizado todavía."
if "last_numeric_res" not in st.session_state:
    st.session_state.last_numeric_res = None
if "ai_messages" not in st.session_state:
    st.session_state.ai_messages = []
if "history" not in st.session_state:
    st.session_state.history = []

t = {
    "Español": {
        "title": "🧮 Consola Científica de Precisión & Motor Simbólico",
        "subtitle": "Sistema avanzado con gráficos 2D, conversor de unidades, historial, LaTeX, GeoGebra 2D/3D e IA.",
        "settings_header": "⚙️ Ajustes de la App",
        "lang_label": "Idioma / Hizkuntza",
        "save_btn": "Guardar ajustes",
        "secure_platform_header": "🔒 Plataforma Segura e Inteligente",
        "secure_platform_desc": "Accede al sistema cifrado avanzado:",
        "secure_platform_btn": "🔗 Entrar en Plataforma Segura",
        "mode_label": "Modo de Operación:",
        "modes": [
            "Calculadora Científica Interactiva",
            "Graficador 2D de Funciones",
            "Conversor de Unidades Científicas",
            "Geometria Avanzada 2D",
            "Geometria Avanzada 3D",
            "Cursos de Matemáticas",
        ],
        "ai_header": "🤖 Asistente Matemático IA",
        "ai_desc": "Pregúntale sobre lo que hay en pantalla (se borra al salir):",
        "ai_placeholder": "Ej: ¿Por qué da error esto?",
        "ai_btn": "Preguntar a la IA",
        "calc_sub": "🔢 Calculadora Científica Interactiva & Símbolos Matemáticos",
        "calc_desc": "Usa el teclado virtual. Las expresiones se renderizan automáticamente con notación matemática formal.",
        "keyboard": "⌨️ Teclado Científico Unificado:",
        "clear": "🗑️ Borrar",
        "trig": "Funciones Trigonométricas:",
        "powers": "Potencias, Raíces, Logaritmos y Constantes:",
        "input_label": "Expresión Científica:",
        "calc_btn": "🚀 Calcular Expresión y Mostrar Símbolos",
        "simplify_btn": "🧹 Simplificar Número (Redondear)",
        "decimals_label": "Número de decimales:",
        "warning_empty": "Por favor, introduce alguna expresión para calcular.",
        "success_calc": "¡Expresión evaluada con éxito!",
        "symbolic_label": "✨ Representación Matemática Formal (LaTeX):",
        "history_sub": "📜 Historial de Cálculos Recientes",
        "plot_sub": "📈 Graficador 2D de Funciones",
        "plot_desc": "Introduce una función en términos de x (ej: x**2 - 4, sin(x), log(x)):",
        "plot_btn": "Generar Gráfica",
        "conv_sub": "🔄 Conversor de Unidades Científicas",
        "conv_type": "Tipo de Magnitud:",
        "conv_val": "Valor a convertir:",
        "conv_from": "De:",
        "conv_to": "A:",
        "conv_btn": "Convertir Unidades",
        "geo2d_sub": "📐 Geometría Avanzada 2D (GeoGebra)",
        "geo3d_sub": "📐 Geometría Avanzada 3D (GeoGebra)",
        "math_courses_sub": "📚 Cursos y Recursos de Matemáticas",
        "math_courses_desc": "Selecciona un recurso o curso recomendado para aprender y perfeccionar tus habilidades:",
        "calc_guide_title": "📖 Guía de la Calculadora",
        "calc_guide_desc": "Aprende a utilizar todas las funciones, el teclado virtual y las herramientas avanzadas de esta consola científica.",
        "calc_guide_link": "🔗 Métete aquí para aprender sobre cómo utilizar la calculadora científica",
        "trig_title": "📐 Trigonometría Básica",
        "trig_desc": "Domina las razones trigonométricas, el círculo unitario, senos, cosenos, tangentes y conversiones de ángulos.",
        "trig_link": "🔗 Métete aquí para aprender sobre trigonometría básica",
        "arith_title": "➕ Aritmetika eta Oinarriak",
        "arith_desc": "Refuerza las bases matemáticas esenciales: operaciones con fracciones, potencias, raíces y leyes de los signos.",
        "arith_link": "🔗 Métete aquí para aprender matemáticas (aritmética)",
        "algebra_title": "📈 Álgebra y Funciones",
        "algebra_desc": "Comprende el manejo de expresiones simbólicas, resolución de ecuaciones y representación gráfica de funciones.",
        "algebra_link": "🔗 Métete aquí para aprender sobre álgebra y funciones",
        "footer": "Consola científica avanzada impulsada por Python, Streamlit, Plotly, SymPy y Google Gemini.",
    },
    "Euskera": {
        "title": "🧮 Doitasun Handiko Kontsola Zientifikoa & Motor Sinbolikoa",
        "subtitle": "Sistema aurreratua 2D grafikoekin, unitate bihurtzailearekin, historikoarekin eta abarrekin.",
        "settings_header": "⚙️ Aplikazioaren Ezarpenak",
        "lang_label": "Idioma / Hizkuntza",
        "save_btn": "Gorde ezarpenak",
        "secure_platform_header": "🔒 Plataforma Seguru eta Adimenduna",
        "secure_platform_desc": "Sartu zifratze aurreratuko sistemara:",
        "secure_platform_btn": "🔗 Sartu Plataforma Segurura",
        "mode_label": "Eragiketa Modua:",
        "modes": [
            "Kalkulagailu Zientifiko Interaktiboa",
            "2D Funtzioen Grafikatzailea",
            "Unitate Zientifikoen Bihurtzailea",
            "Geometria Aurreratua 2D",
            "Geometria Aurreratua 3D",
            "Matematika Ikastaroak",
        ],
        "ai_header": "🤖 IA Laguntzaile Matematikoa",
        "ai_desc": "Galdetu pantailan daukazunari buruz (atera ez gero ezabatzen da):",
        "ai_placeholder": "Adib: Zergatik ematen du akats hau?",
        "ai_btn": "IArif galdetu",
        "calc_sub": "🔢 Kalkulagailu Zientifiko Interaktiboa & Ikur Matematikoak",
        "calc_desc": "Erabili teklatu birtuala. Adierazpenak modu formalean marrazten dira pantailan.",
        "keyboard": "⌨️ Teklatu Zientifiko Bateratua:",
        "clear": "🗑️ Garbitu",
        "trig": "Funtzio Trigonometrikoak:",
        "powers": "Berreketak, Erraiak, Logaritmoak eta Konstanteak:",
        "input_label": "Adierazpen Zientifikoa:",
        "calc_btn": "🚀 Kalkulatu Adierazpena eta Erakutsi Ikurrak",
        "simplify_btn": "🧹 Sinplifikatu Zenbakia (Borobildu)",
        "decimals_label": "Hamartar kopurua:",
        "warning_empty": "Mesedez, sartu adierazpen bat kalkulatzeko.",
        "success_calc": "Adierazpena arrakastaz ebaluatuta!",
        "symbolic_label": "✨ Matematika Erakustaldia (LaTeX formatuan):",
        "history_sub": "📜 Azken Kalkuluen Historikoa",
        "plot_sub": "📈 2D Funtzioen Grafikatzailea",
        "plot_desc": "Sartu funtzio bat x-ren arabera (adib: x**2 - 4, sin(x)):",
        "plot_btn": "Sortu Grafikoa",
        "conv_sub": "🔄 Unitate Zientifikoen Bihurtzailea",
        "conv_type": "Magnitudo Mota:",
        "conv_val": "Bihurtu beharreko balioa:",
        "conv_from": "Hemendik:",
        "conv_to": " Hona:",
        "conv_btn": "Bihurtu Unitateak",
        "geo2d_sub": "📐 Geometria Aurreratua 2D (GeoGebra)",
        "geo3d_sub": "📐 Geometria Aurreratua 3D (GeoGebra)",
        "math_courses_sub": "📚 Matematika Ikastaroak eta Baliabideak",
        "math_courses_desc": "Hautatu gomendatutako baliabide edo ikastaro bat ikasteko eta trebetasunak hobetzeko:",
        "calc_guide_title": "📖 Kalkulagailuaren Gida",
        "calc_guide_desc": "Ikasi kontsola zientifiko honen funtzio guztiak, teklatu birtuala eta tresna aurreratuak erabiltzen.",
        "calc_guide_link": "🔗 Sartu hemen kalkulagailu zientifikoa nola erabili ikasteko",
        "trig_title": "📐 Oinarrizko Trigonometria",
        "trig_desc": "Menperatu arrazoi trigonometrikoak, zirkulu unitarioa, sinuak, kosinuak, tangenteak eta angeluen bihurketak.",
        "trig_link": "🔗 Sartu hemen oinarrizko trigonometriari buruz ikasteko",
        "arith_title": "➕ Aritmetika eta Oinarriak",
        "arith_desc": "Indartu funtsezko oinarri matematikoak: zatikien eragiketak, berreketak, erroak eta zeinuen legeak.",
        "arith_link": "🔗 Sartu hemen matematika (aritmetika) ikasteko",
        "algebra_title": "📈 Aljebra eta Funtzioak",
        "algebra_desc": "Ulertu adierazpen sinbolikoen erabilera, ekuazioen ebazpena eta funtzioen irudikapen grafikoa.",
        "algebra_link": "🔗 Sartu hemen aljebrari eta funtzioei buruz ikasteko",
        "footer": "Kontsola zientifiko aurreratua Python, Streamlit, Plotly, SymPy eta Google Geminik bultzatuta.",
    },
}

lang_texts = t[st.session_state.lang]

with st.sidebar:
    with st.expander(lang_texts["settings_header"], expanded=False):
        selected_lang = st.selectbox(
            lang_texts["lang_label"],
            ["Español", "Euskera"],
            index=0 if st.session_state.lang == "Español" else 1,
        )
        if st.button(lang_texts["save_btn"]):
            st.session_state.lang = selected_lang
            st.rerun()

        st.markdown("---")
        st.markdown(f"**{lang_texts['secure_platform_header']}**")
        st.markdown(lang_texts["secure_platform_desc"])
        st.markdown(f"[{lang_texts['secure_platform_btn']}](https://oimcjuan2325-ctrl-red-de-criptografia-avanzada-app-cno4oj.streamlit.app)")

    st.markdown("---")
    modo = st.selectbox(lang_texts["mode_label"], lang_texts["modes"])
    st.markdown("---")

    st.subheader(lang_texts["ai_header"])
    st.markdown(lang_texts["ai_desc"])

    for msg in st.session_state.ai_messages[-2:]:
        if msg["role"] == "user":
            st.markdown(f"**Tú / Zu:** {msg['content']}")
        else:
            st.markdown(f"**IA:** {msg['content']}")

    user_query = st.text_input(
        "Duda / Zalantza:",
        key="ai_quick_query",
        placeholder=lang_texts["ai_placeholder"],
    )

    if st.button(lang_texts["ai_btn"]):
        if user_query.strip():
            try:
                api_key = st.secrets.get("GEMINI_API_KEY", "")
                if not api_key:
                    st.error("Falta configurar GEMINI_API_KEY en st.secrets.")
                else:
                    client = genai.Client(api_key=api_key)
                    contexto_pantalla = st.session_state.get("last_result", "Sin datos")
                    system_prompt = (
                        f"Eres un profesor experto en matemáticas. Responde SIEMPRE en el idioma: {st.session_state.lang}. "
                        "Analiza el contexto actual y responde de forma concisa y directa a su duda.\n\n"
                        f"Contexto actual: {contexto_pantalla}\nPregunta: {user_query}"
                    )
                    response = client.models.generate_content(
                        model="gemini-3.6-flash", contents=system_prompt
                    )
                    st.session_state.ai_messages.append({"role": "user", "content": user_query})
                    st.session_state.ai_messages.append({"role": "assistant", "content": response.text})
                    st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

st.title(lang_texts["title"])
st.markdown(lang_texts["subtitle"])
st.markdown("---")

modo_actual = modo

if modo_actual in ["Calculadora Científica Interactiva", "Kalkulagailu Zientifiko Interaktiboa"]:
    st.subheader(lang_texts["calc_sub"])
    st.markdown(lang_texts["calc_desc"])

    def add_sci(val):
        st.session_state.sci_val += val

    st.markdown(lang_texts["keyboard"])

    b1, b2, b3, b4, b5, b6, b7 = st.columns(7)
    if b1.button("➕ (+)"): add_sci("+")
    if b2.button("➖ (-)"): add_sci("-")
    if b3.button("✖️ (*)"): add_sci("*")
    if b4.button("➗ (/)"): add_sci("/")
    if b5.button("("): add_sci("(")
    if b6.button(")"): add_sci(")")
    if b7.button(lang_texts["clear"]):
        st.session_state.sci_val = ""
        st.session_state.last_result = "Limpiado." if st.session_state.lang == "Español" else "Garbituta."

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    if c1.button("7"): add_sci("7")
    if c2.button("8"): add_sci("8")
    if c3.button("9"): add_sci("9")
    if c4.button("4"): add_sci("4")
    if c5.button("5"): add_sci("5")
    if c6.button("6"): add_sci("6")

    c7, c8, c9, c10, c11 = st.columns(5)
    if c7.button("1"): add_sci("1")
    if c8.button("2"): add_sci("2")
    if c9.button("3"): add_sci("3")
    if c10.button("0"): add_sci("0")
    if c11.button("."): add_sci(".")

    st.markdown(lang_texts["trig"])
    t1, t2, t3, t4, t5, t6 = st.columns(6)
    if t1.button("sin(x)"): add_sci("sin(")
    if t2.button("cos(x)"): add_sci("cos(")
    if t3.button("tan(x)"): add_sci("tan(")
    if t4.button("csc(x)"): add_sci("csc(")
    if t5.button("sec(x)"): add_sci("sec(")
    if t6.button("cot(x)"): add_sci("cot(")

    st.markdown(lang_texts["powers"])
    p1, p2, p3, p4, p5, p6, p7, p8, p9 = st.columns(9)
    if p1.button("√x"): add_sci("sqrt(")
    if p2.button("∛x"): add_sci("cbrt(")
    if p3.button("**"): add_sci("**")
    if p4.button("!"): add_sci("factorial(")
    if p5.button("%"): add_sci("%")
    if p6.button("lg("): add_sci("log10(")
    if p7.button("ln("): add_sci("ln(")
    if p8.button("π"): add_sci("pi")
    if p9.button("ℯ"): add_sci("e")

    sci_input = st.text_input(lang_texts["input_label"], key="sci_val")

    col_btn1, col_btn2 = st.columns([2, 2])
    with col_btn1:
        calc_pressed = st.button(lang_texts["calc_btn"], type="primary")
    with col_btn2:
        simplify_pressed = st.button(lang_texts["simplify_btn"])

    num_decimals = st.slider(lang_texts["decimals_label"], min_value=0, max_value=15, value=4)

    if calc_pressed:
        if not sci_input.strip():
            st.warning(lang_texts["warning_empty"])
        else:
            try:
                safe_dict = {
                    "sin": mpmath.sin, "cos": mpmath.cos, "tan": mpmath.tan,
                    "csc": lambda val: 1 / mpmath.sin(val),
                    "sec": lambda val: 1 / mpmath.cos(val),
                    "cot": lambda val: 1 / mpmath.tan(val),
                    "sqrt": mpmath.sqrt,
                    "cbrt": lambda val: mpmath.power(val, 1 / 3),
                    "factorial": mpmath.factorial, "log10": mpmath.log10,
                    "ln": mpmath.ln, "log": mpmath.log, "pi": mpmath.pi,
                    "e": mpmath.e, "__builtins__": None,
                }
                resultado_eval = eval(sci_input, safe_dict, {})
                res_sci = mpmath.nstr(resultado_eval, 30)

                st.session_state.last_numeric_res = float(mpmath.mpf(resultado_eval))
                st.session_state.last_result = f"Expresión: {sci_input} | Resultado: {res_sci}"
                st.success(lang_texts["success_calc"])
                st.code(res_sci, language="text")

                st.session_state.history.insert(0, {"expr": sci_input, "res": res_sci})
                if len(st.session_state.history) > 5:
                    st.session_state.history.pop()

                st.markdown(lang_texts["symbolic_label"])
                expr_sympy_str = (
                    sci_input.replace("ln(", "log(")
                    .replace("log10(", "log(..., 10)")
                    .replace("cbrt(", "(...)**(1/3)")
                )
                expr_simbolica = sp.sympify(expr_sympy_str, evaluate=False)
                st.latex(sp.latex(expr_simbolica))

            except Exception as e:
                st.session_state.last_result = f"Expresión: {sci_input} | Error: {e}"
                st.error(f"Error: {e}")

    elif simplify_pressed:
        if st.session_state.last_numeric_res is not None:
            val_simplificado = round(st.session_state.last_numeric_res, num_decimals)
            st.success(f"Resultado simplificado ({num_decimals} decimales):")
            st.code(str(val_simplificado), language="text")
        else:
            st.warning("Primero debes realizar un cálculo válido para poder simplificarlo.")

    if st.session_state.history:
        st.markdown("---")
        st.subheader(lang_texts["history_sub"])
        for idx, item in enumerate(st.session_state.history):
            st.text(f"#{idx+1} -> {item['expr']} = {item['res'][:15]}...")

elif modo_actual in ["Graficador 2D de Funciones", "2D Funtzioen Grafikatzailea"]:
    st.subheader(lang_texts["plot_sub"])
    st.markdown(lang_texts["plot_desc"])

    func_input = st.text_input("f(x) =", value="x**2 - 2*x - 3")
    col1, col2 = st.columns(2)
    xmin = col1.number_input("X mínimo", value=-10.0)
    xmax = col2.number_input("X máximo", value=10.0)

    if st.button(lang_texts["plot_btn"], type="primary"):
        try:
            x_vals = np.linspace(xmin, xmax, 400)
            safe_np_dict = {
                "sin": np.sin, "cos": np.cos, "tan": np.tan,
                "csc": lambda val: 1 / np.sin(val),
                "sec": lambda val: 1 / np.cos(val),
                "cot": lambda val: 1 / np.tan(val),
                "sqrt": np.sqrt, "exp": np.exp, "log": np.log, "log10": np.log10,
                "pi": np.pi, "e": np.e, "x": x_vals, "__builtins__": None
            }
            y_vals = eval(func_input, safe_np_dict, {})

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines', name=f"f(x) = {func_input}", line=dict(color='#00ffcc', width=2)))
            fig.update_layout(
                paper_bgcolor='#0e1117', plot_bgcolor='#161b22',
                font=dict(color='#c9d1d9'),
                xaxis=dict(gridcolor='#30363d'), yaxis=dict(gridcolor='#30363d'),
                margin=dict(l=20, r=20, t=20, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)
            st.session_state.last_result = f"Gráfica generada para f(x) = {func_input}"
        except Exception as e:
            st.error(f"Error al graficar: {e}")

elif modo_actual in ["Conversor de Unidades Científicas", "Unitate Zientifikoen Bihurtzailea"]:
    st.subheader(lang_texts["conv_sub"])
    tipo_magnitud = st.selectbox(lang_texts["conv_type"], ["Ángulo", "Longitud", "Temperatura"])
    
    if tipo_magnitud == "Ángulo":
        unidades = {"Radianes": 1.0, "Grados": np.pi / 180, "Gradiantes": np.pi / 200}
    elif tipo_magnitud == "Longitud":
        unidades = {"Metros": 1.0, "Kilómetros": 1000.0, "Millas": 1609.34, "Pies": 0.3048}
    else:
        unidades = {"Celsius": "C", "Fahrenheit": "F", "Kelvin": "K"}

    val_ingresado = st.number_input(lang_texts["conv_val"], value=1.0)
    
    if tipo_magnitud != "Temperatura":
        from_u = st.selectbox(lang_texts["conv_from"], list(unidades.keys()))
        to_u = st.selectbox(lang_texts["conv_to"], list(unidades.keys()), index=1)
        if st.button(lang_texts["conv_btn"], type="primary"):
            en_base = val_ingresado * unidades[from_u]
            resultado_conv = en_base / unidades[to_u]
            st.success(f"Resultado: {val_ingresado} {from_u} = {resultado_conv} {to_u}")
            st.session_state.last_result = f"Conversión: {val_ingresado} {from_u} = {resultado_conv} {to_u}"
    else:
        from_u = st.selectbox(lang_texts["conv_from"], list(unidades.keys()))
        to_u = st.selectbox(lang_texts["conv_to"], list(unidades.keys()), index=2)
        if st.button(lang_texts["conv_btn"], type="primary"):
            if from_u == "Celsius": c = val_ingresado
            elif from_u == "Fahrenheit": c = (val_ingresado - 32) * 5/9
            else: c = val_ingresado - 273.15
            
            if to_u == "Celsius": res_t = c
            elif to_u == "Fahrenheit": res_t = c * 9/5 + 32
            else: res_t = c + 273.15
            
            st.success(f"Resultado: {val_ingresado} {from_u} = {res_t} {to_u}")
            st.session_state.last_result = f"Conversión: {val_ingresado} {from_u} = {res_t} {to_u}"

elif modo_actual in ["Geometria Avanzada 2D", "Geometria Aurreratua 2D"]:
    st.subheader(lang_texts["geo2d_sub"])
    st.session_state.last_result = "GeoGebra 2D activo."
    geogebra_html = """
    <div style="width: 100%; height: 85vh; background-color: #161b22; border-radius: 10px; overflow: hidden; border: 1px solid #30363d;">
        <iframe src="https://www.geogebra.org/geometry?embed" width="100%" height="100%" style="border:none;" allowfullscreen></iframe>
    </div>
    """
    st.components.v1.html(geogebra_html, height=750, scrolling=False)

elif modo_actual in ["Geometria Avanzada 3D", "Geometria Aurreratua 3D"]:
    st.subheader(lang_texts["geo3d_sub"])
    st.session_state.last_result = "GeoGebra 3D activo."
    geogebra_html = """
    <div style="width: 100%; height: 85vh; background-color: #161b22; border-radius: 10px; overflow: hidden; border: 1px solid #30363d;">
        <iframe src="https://www.geogebra.org/3d?embed" width="100%" height="100%" style="border:none;" allowfullscreen></iframe>
    </div>
    """
    st.components.v1.html(geogebra_html, height=750, scrolling=False)

else:
    st.subheader(lang_texts["math_courses_sub"])
    st.markdown(lang_texts["math_courses_desc"])
    st.session_state.last_result = "Sección de Cursos de Matemáticas abierta." if st.session_state.lang == "Español" else "Matematika Ikastaroen atala irekita."

    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"### {lang_texts['calc_guide_title']}")
        st.markdown(lang_texts['calc_guide_desc'])
        st.markdown(f"[{lang_texts['calc_guide_link']}](https://example.com/curso-calculadora)")

        st.markdown(f"### {lang_texts['trig_title']}")
        st.markdown(lang_texts['trig_desc'])
        st.markdown(f"[{lang_texts['trig_link']}](https://example.com/curso-trigonometria)")

    with col2:
        st.markdown(f"### {lang_texts['arith_title']}")
        st.markdown(lang_texts['arith_desc'])
        st.markdown(f"[{lang_texts['arith_link']}](https://example.com/curso-aritmetica)")

        st.markdown(f"### {lang_texts['algebra_title']}")
        st.markdown(lang_texts['algebra_desc'])
        st.markdown(f"[{lang_texts['algebra_link']}](https://example.com/curso-algebra)")

st.markdown("---")
st.caption(lang_texts["footer"])
