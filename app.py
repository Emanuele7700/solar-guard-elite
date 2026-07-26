import streamlit as st

if "logged_in" not in st.session_state:
st.session_state.logged_in = False
import streamlit as st
import cv2
import numpy as np
import pandas as pd
from datetime import datetime
import io, os, json, smtplib, piexif
from concurrent.futures import ThreadPoolExecutor
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# --- NUOVI IMPORTS PER GPS, MAPPE E AI ---
import folium
from streamlit_folium import st_folium
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False

# --- REPORTLAB IMPORTS ---
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
# --- INIZIALIZZAZIONE LOGIN ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Solar Guard ELITE - Enterprise", page_icon="🛰️", layout="wide")

# --- 2. CUSTOM CSS DARK FORCE (CON CORREZIONE DEFINITIVA CARICAMENTO FILE) ---
st.markdown("""
    <style>
    :root { color-scheme: dark !important; }

    .stApp {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        color: #ffffff;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    
    h1, h2, h3 {
        color: #fbbf24 !important;
        font-weight: 800 !important;
    def login_screen():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; color: #fbbf24;'>☀️ Solar Guard Elite</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; color: #ffffff;'>Area riservata agli Installatori</h3>", unsafe_allow_html=True)
        
        # Creazione dei tab con visibilità forzata
        tab_accedi, tab_registrati = st.tabs(["🔑 Accedi", "📝 Registrati"])
        
        with tab_accedi:
            st.write("")
            with st.form("login_form"):
                username = st.text_input("Email o Username", key="login_user")
                password = st.text_input("Password", type="password", key="login_pass")
                submit_login = st.form_submit_button("Accedi al Software", use_company_width=True if 'use_company_width' in globals() else False, use_container_width=True)
                
                if submit_login:
                    if username == "admin" and password == "solarguard2026":
                        st.session_state.logged_in = True
                        st.success("Accesso effettuato!")
                        st.rerun()
                    else:
                        st.error("Credenziali errate.")
                        
        with tab_registrati:
            st.write("")
            with st.form("register_form"):
                new_user = st.text_input("Scegli un'Email", key="reg_user")
                new_pass = st.text_input("Scegli una Password", type="password", key="reg_pass")
                submit_reg = st.form_submit_button("Crea Account", use_container_width=True)
                
                if submit_reg:
                    if new_user and new_pass:
                        st.success("Account registrato con successo! Ora puoi passare al tab 'Accedi'.")
                    else:
                        st.error("Compila tutti i campi per registrarti.")
                        
        with tab_registrati:
            with st.form("register_form"):
                new_user = st.text_input("Scegli un'Email", key="reg_user")
                new_pass = st.text_input("Scegli una Password", type="password", key="reg_pass")
                submit_reg = st.form_submit_button("Crea Account", use_container_width=True)
                
                if submit_reg:
                    if new_user and new_pass:
                        st.success("Account registrato con successo! Ora puoi passare al tab 'Accedi'.")
                    else:
                        st.error("Compila tutti i campi per registrarti.")
    div[data-testid="stVerticalBlock"] > div > div {
        background-color: rgba(30, 41, 59, 0.85);
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.15);
        padding: 20px;
    }

    label, div[data-testid="stWidgetLabel"] p {
        color: #fbbf24 !important;
        font-weight: 700 !important;
        font-size: 15px !important;
    }

    /* --- CORREZIONE COMPLETA FILE UPLOADER (SFONDO SCURO BLINDATO) --- */
    div[data-testid="stFileUploader"],
    div[data-testid="stFileUploader"] section,
    section[data-testid="stFileUploadDropzone"],
    div[data-baseweb="file-uploader"],
    div[data-baseweb="file-uploader"] section,
    div[data-baseweb="file-uploader"] > div {
        background-color: #0f172a !important;
        background: #0f172a !important;
        border: 2px dashed #fbbf24 !important;
        border-radius: 12px !important;
    }

    div[data-testid="stFileUploader"] *,
    section[data-testid="stFileUploadDropzone"] * {
        color: #ffffff !important;
        fill: #ffffff !important;
    }

    div[data-testid="stFileUploader"] section p,
    section[data-testid="stFileUploadDropzone"] p {
        color: #fbbf24 !important;
        font-weight: 800 !important;
        font-size: 16px !important;
    }

    div[data-testid="stFileUploader"] button,
    section[data-testid="stFileUploadDropzone"] button,
    .stButton button {
        background-color: #2563eb !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: bold !important;
    }

    .stButton button:hover {
        background-color: #1d4ed8 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATABASE UTENTI & TENANT ---
DB_UTENTI = "utenti.json"
def carica_database_utenti():
    if not os.path.exists(DB_UTENTI):
        default_db = {
            "admin": {"password": "solarguard2026", "role": "admin", "client_id": "elite_internal"},
            "tecnico1": {"password": "drone", "role": "tecnico", "client_id": "elite_internal"},
            "cliente1": {"password": "solar", "role": "cliente", "client_id": "solar_campania_spa"}
        }
        with open(DB_UTENTI, "w") as f: json.dump(default_db, f)
        return default_db
    with open(DB_UTENTI, "r") as f: return json.load(f)

# --- GESTIONE SESSIONE ---
if "autenticato" not in st.session_state: st.session_state["autenticato"] = False
if "ai_model" not in st.session_state: st.session_state["ai_model"] = None

# --- 4. LOGIN CON RUOLI & MULTI-TENANCY ---
if not st.session_state["autenticato"]:
    c1, col_login, c3 = st.columns([1, 1.2, 1])
    with col_login:
        st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
        st.markdown("<h1>Solar Guard ELITE</h1><p style='color:#94a3b8;'>Piattaforma Enterprise Multi-Tenant</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        u_in = st.text_input("Nome Utente")
        p_in = st.text_input("Password", type="password")
        
        if st.button("ENTRA NEL SISTEMA"):
            db = carica_database_utenti()
            if u_in in db and db[u_in]["password"] == p_in:
                u_data = db[u_in]
                st.session_state["autenticato"] = True
                st.session_state["user"] = u_in
                st.session_state["role"] = u_data.get("role", "tecnico")
                st.session_state["tenant_id"] = u_data.get("client_id", "elite_internal")
                st.rerun()
            else:
                st.error("❌ Credenziali errate")
    st.stop()

# --- CARICAMENTO MODELLO AI (YOLO) ---
if YOLO_AVAILABLE and st.session_state["ai_model"] is None:
    try:
        st.session_state["ai_model"] = YOLO("yolov8n.pt")
    except Exception:
        YOLO_AVAILABLE = False

# --- SIDEBAR & NAVIGAZIONE ---
st.sidebar.title(f"👤 {st.session_state['user']} ({st.session_state['role'].upper()})")
if st.sidebar.button("🚪 Logout"):
    st.session_state["autenticato"] = False
    st.rerun()

st.sidebar.markdown("---")
sezione = st.sidebar.radio("📌 Navigazione", ["🛰️ Analisi Impianto", "📁 Archivio Storico", "🗺️ Mappa Droni GPS"])

st.sidebar.markdown("---")
nome_impianto = st.sidebar.text_input("🏷️ Impianto/Cliente", "Centrale Solare Elite")
sensibilita = st.sidebar.slider("🌡️ Sensibilità Sensore", 150, 255, 240)
palette_scelta = st.sidebar.selectbox("🎨 Palette Termica", ["Nativo", "JET", "INFERNO", "PLASMA", "HOT", "RAINBOW"])

tenant_id = st.session_state["tenant_id"]
st.sidebar.markdown(f"🔒 Client ID: **{tenant_id}**")
os.makedirs(f"storico_report/{tenant_id}", exist_ok=True)

# --- EXTRACTION GPS ---
def dms_to_dd(gps_coords, ref):
    if not gps_coords: return None
    d = float(gps_coords[0][0]) / float(gps_coords[0][1])
    m = float(gps_coords[1][0]) / float(gps_coords[1][1])
    s = float(gps_coords[2][0]) / float(gps_coords[2][1])
    dd = d + (m / 60.0) + (s / 3600.0)
    if ref in ['S', 'W']: dd *= -1
    return dd

def extract_gps(file_bytes):
    try:
        exif_dict = piexif.load(file_bytes)
        gps = exif_dict.get('GPS', {})
        if not gps: return None
        lat = dms_to_dd(gps.get(piexif.GPSIFD.GPSLatitude), gps.get(piexif.GPSIFD.GPSLatitudeRef, b'N').decode())
        lon = dms_to_dd(gps.get(piexif.GPSIFD.GPSLongitude), gps.get(piexif.GPSIFD.GPSLongitudeRef, b'E').decode())
        return lat, lon
    except:
        return None

# --- INVIO EMAIL ---
def send_email_report(receiver_email, impianto_nome, pdf_data):
    try:
        smtp_conf = st.secrets["email"]
        msg = MIMEMultipart()
        msg['Subject'] = f"🚨 ALERT CRITICO SolarGuard: {impianto_nome}"
        msg['From'] = smtp_conf["sender_email"]
        msg['To'] = receiver_email

        body = f"Solar Guard ELITE ha rilevato criticità nell'impianto: {impianto_nome}.\nOperatore: {st.session_state['user']}\nIn allegato il report PDF completo."
        msg.attach(MIMEText(body, 'plain'))
        
        att = MIMEApplication(pdf_data, _subtype="pdf")
        att.add_header('Content-Disposition', 'attachment', filename=f"Report_{impianto_nome}.pdf")
        msg.attach(att)

        with smtplib.SMTP(smtp_conf["smtp_server"], int(smtp_conf["smtp_port"])) as server:
            server.starttls()
            server.login(smtp_conf["sender_email"], smtp_conf["sender_password"])
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"⚠️ Errore invio Email (Verifica .streamlit/secrets.toml): {e}")
        return False

# --- ESECUZIONE ANALISI ---
def analizza_img_enterprise(file_bytes, filename, sens, palette, use_ai, ai_conf):
    arr = np.asarray(bytearray(file_bytes), dtype=np.uint8)
    img_orig = cv2.imdecode(arr, 1)
    gray = cv2.cvtColor(img_orig, cv2.COLOR_BGR2GRAY)
    gps_coords = extract_gps(file_bytes)

    count = 0
    img_base = img_orig.copy()

    if use_ai and YOLO_AVAILABLE and st.session_state["ai_model"]:
        results = st.session_state["ai_model"](img_orig, conf=ai_conf, verbose=False)[0]
        for box in results.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(img_base, (x1, y1), (x2, y2), (255, 0, 0), 3)
            count += 1
    else:
        if palette != "Nativo":
            cm_dict = {"JET": 2, "INFERNO": 8, "PLASMA": 9, "HOT": 11, "RAINBOW": 4}
            if palette in cm_dict: img_base = cv2.applyColorMap(gray, cm_dict[palette])

        _, mask = cv2.threshold(gray, sens, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for c in contours:
            if 30 <= cv2.contourArea(c) <= 2500:
                x,y,w,h = cv2.boundingRect(c)
                cv2.rectangle(img_base, (x,y), (x+w, y+h), (0,255,0), 2)
                count += 1
            
    img_rgb = cv2.cvtColor(img_base, cv2.COLOR_BGR2RGB)
    stato = "OK ✅" if count == 0 else ("ATTENZIONE ⚠️" if count < 3 else "CRITICO 🚨")
    return filename, img_rgb, count, stato, gps_coords

# --- GENERAZIONE PDF ---
def genera_pdf_report(nome_imp, operatore, df_rep, risultati_img):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    story = []
    
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor("#1e293b"), spaceAfter=10)
    story.append(Paragraph(f"<b>SOLAR GUARD ELITE Enterprise Report: {nome_imp}</b>", title_style))
    story.append(Spacer(1, 15))

    grid_sum = [[Paragraph(f"<b>Moduli:</b> {len(df_rep)}", styles['Normal']), Paragraph(f"<b>Hotspot:</b> {df_rep['Hotspot'].sum()}", styles['Normal']), Paragraph(f"<b>Critici:</b> {len(df_rep[df_rep['Stato'] == 'CRITICO 🚨'])}", styles['Normal'])]]
    t_sum = Table(grid_sum, colWidths=[2.3*inch, 2.3*inch, 2.3*inch])
    t_sum.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'), ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")), ('BOTTOMPADDING', (0,0), (-1,-1), 8)]))
    story.append(t_sum)
    story.append(Spacer(1, 20))

    story.append(Paragraph("<b>Dettaglio Scansioni Termiche:</b>", styles['Heading2']))
    story.append(Spacer(1, 10))
    grid_data = []
    row = []
    for name, img_rgb, count, stato, _ in risultati_img:
        _, enc = cv2.imencode('.jpg', cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR))
        rl_img = RLImage(io.BytesIO(enc.tobytes()), width=2.2*inch, height=1.65*inch)
        row.append([rl_img, Paragraph(f"<b>{name}</b><br/>Hotspot: {count} | {stato}", styles['Normal'])])
        if len(row) == 3:
            grid_data.append(row); row = []
    if row: grid_data.append(row)
    if grid_data:
        t_grid = Table(grid_data, colWidths=[2.3*inch, 2.3*inch, 2.3*inch])
        t_grid.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
        story.append(t_grid)
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# ==============================================================================
# SEZIONE 1: ANALISI IMPIANTO
# ==============================================================================
if sezione == "🛰️ Analisi Impianto":
    st.header(f"🛰️ Analisi Termica Enterprise: {nome_impianto}")
    
    if st.session_state["role"] not in ["tecnico", "admin"]:
        st.warning("🔒 Modalità Cliente (Sola Lettura). Solo i tecnici possono analizzare nuove immagini.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            use_ai = st.toggle("🤖 Attiva Rilevamento AI YOLOv8", value=YOLO_AVAILABLE)
            if not YOLO_AVAILABLE:
                st.info("ℹ️ AI YOLOv8 non attiva (esegui `python -m pip install ultralytics` per abilitarla).")
        with c2:
            ai_conf = st.slider("🎯 Confidenza AI", 0.10, 0.90, 0.50) if use_ai else 0.50
        
        st.markdown("---")
        files = st.file_uploader("📂 Trascina immagini drone qui sotto (supporta EXIF GPS):", accept_multiple_files=True)

        if files:
            with ThreadPoolExecutor() as exe:
                tasks = [(f.read(), f.name, sensibilita, palette_scelta, use_ai, ai_conf) for f in files]
                risultati = list(exe.map(lambda p: analizza_img_enterprise(*p), tasks))
            
            report_list = []
            grid = st.columns(3)
            for i, (name, img, count, stato, gps) in enumerate(risultati):
                report_list.append({
                    "Nome File": name, "Tenant": tenant_id, "Hotspot": count, "Stato": stato,
                    "GPS_Lat": gps[0] if gps else None, "GPS_Lon": gps[1] if gps else None
                })
                with grid[i % 3]:
                    st.image(img, caption=f"{name} | {stato}", use_container_width=True)

            df = pd.DataFrame(report_list)
            st.markdown("---")
            st.subheader("📊 Riepilogo Analisi")
            
            pdf_data = genera_pdf_report(nome_impianto, st.session_state['user'], df, risultati)
            
            col_d1, col_d2, col_d3 = st.columns(3)
            with col_d1:
                st.download_button("📄 Scarica Report PDF", pdf_data, f"Report_{nome_impianto}.pdf", "application/pdf")
            with col_d2:
                st.download_button("💾 Scarica CSV", df.to_csv(index=False).encode('utf-8'), "dati.csv", "text/csv")
            
            moduli_critici = len(df[df["Stato"] == "CRITICO 🚨"])
            if moduli_critici > 0:
                with col_d3:
                    email_dest = st.text_input("📧 Email alert", value="tecnico@azienda.com")
                    if st.button("📩 Invia Alert Email"):
                        if send_email_report(email_dest, nome_impianto, pdf_data):
                            st.success("📩 Alert inviato via Email!")

            if st.button("💾 Salva Ispezione in Archivio Storico"):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                folder_path = os.path.join("storico_report", tenant_id, f"{timestamp}_{nome_impianto}")
                os.makedirs(folder_path, exist_ok=True)
                df.to_csv(os.path.join(folder_path, "dati.csv"), index=False)
                with open(os.path.join(folder_path, "report.pdf"), "wb") as f:
                    f.write(pdf_data)
                st.success(f"✅ Salvato con successo nell'archivio storico!")

# ==============================================================================
# SEZIONE 2: MAPPA DRONI GPS
# ==============================================================================
elif sezione == "🗺️ Mappa Droni GPS":
    st.header("🗺️ Mappa Satellitare Interattiva Hotspot GPS")
    
    tenant_rep = f"storico_report/{tenant_id}"
    all_reports_list = []
    
    if os.path.exists(tenant_rep):
        for f in os.listdir(tenant_rep):
            f_path = os.path.join(tenant_rep, f)
            if os.path.isdir(f_path):
                csv_p = os.path.join(f_path, "dati.csv")
                if os.path.exists(csv_p):
                    try: all_reports_list.append(pd.read_csv(csv_p))
                    except: pass
                    
    if not all_reports_list:
        st.info("🗺️ Nessun dato storico ancora salvato. Salva un'ispezione con foto contenenti dati GPS.")
    else:
        df_all = pd.concat(all_reports_list, ignore_index=True)
        df_gps = df_all.dropna(subset=['GPS_Lat', 'GPS_Lon'])
        
        if df_gps.empty:
            st.warning("⚠️ Le immagini analizzate finora non contenevano coordinate GPS nei metadati EXIF.")
        else:
            st.markdown(f"Pannelli mappati sul territorio: **{len(df_gps)}**")
            centro = [df_gps['GPS_Lat'].mean(), df_gps['GPS_Lon'].mean()]
            m = folium.Map(location=centro, zoom_start=18)
            folium.TileLayer('https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google Satellite', name='Google Satellite', overlay=False).add_to(m)

            for _, r in df_gps.iterrows():
                color = "red" if "CRITICO" in str(r['Stato']) else "orange"
                popup_html = f"<b>{r['Stato']}</b><br/>File: {r['Nome File']}<br/>Hotspot: {r['Hotspot']}"
                folium.Marker(
                    location=[r['GPS_Lat'], r['GPS_Lon']],
                    popup=folium.Popup(popup_html, max_width=300),
                    icon=folium.Icon(color=color, icon="info-sign")
                ).add_to(m)
                
            st_folium(m, width=1200, height=600)

# ==============================================================================
# SEZIONE 3: ARCHIVIO STORICO
# ==============================================================================
else:
    st.header("📁 Archivio Storico Report")
    os.makedirs(f"storico_report/{tenant_id}", exist_ok=True)
    cartelle = sorted(os.listdir(f"storico_report/{tenant_id}"), reverse=True)
    
    if not cartelle:
        st.info("ℹ️ Nessun report ancora salvato in archivio per il tuo profilo.")
    else:
        scelta_r = st.selectbox("📂 Seleziona Ispezione Passata:", cartelle)
        if scelta_r:
            path_p = os.path.join("storico_report", tenant_id, scelta_r)
            st.markdown(f"### 📋 Dettagli Ispezione: `{scelta_r}`")
            c1, c2 = st.columns([2, 1])
            with c1:
                df_o = pd.read_csv(os.path.join(path_p, "dati.csv"))
                st.dataframe(df_o, use_container_width=True)
            with c2:
                with open(os.path.join(path_p, "report.pdf"), "rb") as f:
                    st.download_button("📄 Scarica Report PDF Storico", f.read(), f"{scelta_r}.pdf", "application/pdf")
if not st.session_state.logged_in:
    login_screen()
else:
    # 👉 (Qui sotto va tutto il resto del codice della tua app esistente)
def login_screen():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("☀️ Solar Guard Elite")
        st.subheader("Area riservata agli Installatori")
        
        # Creiamo due tab: uno per accedere, uno per registrarsi
        tab_accedi, tab_registrati = st.tabs(["Accedi", "Registrati"])
        
        with tab_accedi:
            with st.form("login_form"):
                username = st.text_input("Email o Username", key="login_user")
                password = st.text_input("Password", type="password", key="login_pass")
                submit_login = st.form_submit_button("Accedi al Software", use_container_width=True)
                
                if submit_login:
                    if username == "admin" and password == "solarguard2026":
                        st.session_state.logged_in = True
                        st.success("Accesso effettuato!")
                        st.rerun()
                    else:
                        st.error("Credenziali errate.")
                        
        with tab_registrati:
            with st.form("register_form"):
                new_user = st.text_input("Scegli un'Email", key="reg_user")
                new_pass = st.text_input("Scegli una Password", type="password", key="reg_pass")
                submit_reg = st.form_submit_button("Crea Account", use_container_width=True)
                
                if submit_reg:
                    if new_user and new_pass:
                        st.success("Account registrato con successo! Ora puoi passare al tab 'Accedi'.")
                    else:
                        st.error("Compila tutti i campi per registrarti.")
