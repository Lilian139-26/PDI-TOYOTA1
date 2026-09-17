import streamlit as st
import database as db

if 'usuario' not in st.session_state or st.session_state['usuario'] is None:
    st.warning("Acesso restrito.")
    st.stop()

usuario = st.session_state['usuario']

# Botão de Sair na Barra Lateral
with st.sidebar:
    st.write(f"Logado como: **{usuario['nome']}**")
    if st.button("🚪 Sair da Conta (Logout)", use_container_width=True):
        st.session_state['usuario'] = None
        st.rerun()

# Centralizar Logo
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try:
        st.image("logo.png", width=250)
    except:
        try:
            st.image("logo.jpg", width=250)
        except:
            pass

st.title("Configurações de Segurança")
st.markdown("Altere sua senha de acesso ao portal.")
st.divider()

with st.form("form_alterar_senha_colab_pagina"):
    nova_senha = st.text_input("Nova Senha", type="password")
    confirma_senha = st.text_input("Confirmar Nova Senha", type="password")
    
    if st.form_submit_button("Atualizar Minha Senha", use_container_width=True):
        if nova_senha.strip() != "" and confirma_senha.strip() != "":
            if nova_senha == confirma_senha:
                conn_pass = db.get_connection()
                c_pass = conn_pass.cursor()
                c_pass.execute("UPDATE usuarios SET senha = ? WHERE id = ?", (nova_senha, usuario['id']))
                conn_pass.commit()
                conn_pass.close()
                st.success("Senha alterada com sucesso!")
            else:
                st.error("As senhas não coincidem. Verifique e tente novamente.")
        else:
            st.warning("Preencha os campos de senha.")