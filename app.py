import streamlit as st

# 1. Inizializza lo stato di login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# 2. Se NON è loggato, mostra i tab di Accesso/Registrazione e blocca l'app qui
if not st.session_state.logged_in:
    st.title("Solar Guard ELITE - Accesso")
    tab_accedi, tab_registrati = st.tabs(["Accedi", "Registrati"])
    
    with tab_accedi:
        with st.form("login_form"):
            user = st.text_input("Email", key="l_user")
            pwd = st.text_input("Password", type="password", key="l_pwd")
            submit_login = st.form_submit_button("Entra", use_container_width=True)
            if submit_login:
                if user and pwd:
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Inserisci email e password.")
                    
    with tab_registrati:
        with st.form("register_form"):
            new_user = st.text_input("Scegli un'Email", key="r_user")
            new_pass = st.text_input("Scegli una Password", type="password", key="r_pwd")
            submit_reg = st.form_submit_button("Crea Account", use_container_width=True)
            if submit_reg:
                if new_user and new_pass:
                    st.success("Registrato! Ora vai nel tab 'Accedi'.")
                else:
                    st.error("Compila tutti i campi.")
                    
    st.stop()

# 3. AREA PROTETTA (Il resto della tua app originale va qui sotto)
st.success("Benvenuto nell'area protetta di Solar Guard ELITE!")
