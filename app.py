import streamlit as st
import database as db

st.set_page_config(
    page_title="Portal PDI - Toyota",
    page_icon="📊",
    layout="centered"
)

db.inicializar_banco()

if 'usuario' not in st.session_state:
    st.session_state['usuario'] = None

usuario = st.session_state['usuario']

if usuario is not None:
    if usuario['perfil'] == 'Gestor':
        paginas = [
            st.Page("pages/01_Dashboard.py", title="Painel do Gestor", icon="📊"),
            st.Page("pages/03_Equipe.py", title="Gestão de Equipe", icon="👥"),
            st.Page("pages/05_Meu_Perfil.py", title="Meu Perfil", icon="⚙️")
        ]
    else:
        paginas = [
            st.Page("pages/02_Meu_PDI.py", title="Meu PDI", icon="🎯"),
            st.Page("pages/06_Seguranca.py", title="Segurança / Senha", icon="🔒")
        ]
    
    pg = st.navigation(paginas)
    pg.run()

else:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            st.image("logo.png", width=300)
        except:
            try:
                st.image("logo.jpg", width=300)
            except:
                pass

    st.title("Portal PDI")
    st.markdown("Acompanhe seu desenvolvimento profissional.")
    st.write("")

    with st.form("form_login"):
        email = st.text_input("E-mail")
        senha = st.text_input("Senha", type="password")
        
        btn_login = st.form_submit_button("Entrar no Sistema", use_container_width=True)
        
        if btn_login:
            if email.strip() != "" and senha.strip() != "":
                usuario_autenticado = db.autenticar_usuario(email, senha)
                if usuario_autenticado:
                    st.session_state['usuario'] = usuario_autenticado
                    st.success(f"Bem-vindo, {usuario_autenticado['nome']}!")
                    st.rerun()
                else:
                    st.error("E-mail ou senha incorretos.")
            else:
                st.warning("Preencha todos os campos.")