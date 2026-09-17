import streamlit as st
import database as db

if 'usuario' not in st.session_state or st.session_state['usuario'] is None or st.session_state['usuario']['perfil'] != 'Gestor':
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

st.title("Meu Perfil (Gestor)")
st.markdown("Gerencie seus dados cadastrais e senha de acesso.")
st.divider()

with st.form("form_perfil_gestor_pagina"):
    novo_nome = st.text_input("Meu Nome", value=usuario['nome'])
    novo_email = st.text_input("Meu E-mail", value=usuario['email'])
    nova_area = st.text_input("Meu Departamento", value=usuario['area'])
    
    st.write("---")
    st.markdown("**Alterar Senha (Opcional):**")
    nova_senha_gestor = st.text_input("Nova Senha", type="password")
    confirma_senha_gestor = st.text_input("Confirmar Nova Senha", type="password")
    
    if st.form_submit_button("Salvar Alterações do Perfil", use_container_width=True):
        if novo_nome.strip() != "" and novo_email.strip() != "" and nova_area.strip() != "":
            conn_g = db.get_connection()
            c_g = conn_g.cursor()
            
            if nova_senha_gestor.strip() != "":
                if nova_senha_gestor == confirma_senha_gestor:
                    c_g.execute("""
                        UPDATE usuarios SET nome = ?, email = ?, area = ?, senha = ? WHERE id = ?
                    """, (novo_nome, novo_email, nova_area, nova_senha_gestor, usuario['id']))
                else:
                    conn_g.close()
                    st.error("As senhas não coincidem.")
                    st.stop()
            else:
                c_g.execute("""
                    UPDATE usuarios SET nome = ?, email = ?, area = ?, senha = ? WHERE id = ?
                """, (novo_nome, novo_email, nova_area, usuario['senha'], usuario['id']))
                
            conn_g.commit()
            conn_g.close()
            
            # Atualiza imediatamente a sessão local para refletir o nome no topo
            st.session_state['usuario']['nome'] = novo_nome
            st.session_state['usuario']['email'] = novo_email
            st.session_state['usuario']['area'] = nova_area
            
            st.success("Perfil atualizado com sucesso! O nome foi atualizado no sistema.")
            st.rerun()
        else:
            st.error("Preencha os campos obrigatórios (Nome, E-mail e Departamento).")