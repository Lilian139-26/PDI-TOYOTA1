import streamlit as st
import database as db
import pandas as pd

if 'usuario' not in st.session_state or st.session_state['usuario'] is None or st.session_state['usuario']['perfil'] != 'Gestor':
    st.warning("Acesso restrito a gestores.")
    st.stop()

try:
    st.image("logo.png", width=250)
except:
    try:
        st.image("logo.jpg", width=250)
    except:
        pass

st.title("Gestão de Equipe e Convites")
st.divider()

st.subheader("Cadastrar Novo Colaborador")
st.write("Preencha os dados abaixo para criar o acesso do colaborador e definir sua senha provisória.")

with st.form("form_novo_colaborador"):
    nome_novo = st.text_input("Nome do Colaborador")
    email_novo = st.text_input("E-mail corporativo")
    area_novo = st.text_input("Área / Departamento")
    senha_provisoria = st.text_input("Senha Provisória Inicial", value="123456", type="password")
    
    if st.form_submit_button("Cadastrar e Gerar Acesso", use_container_width=True):
        if nome_novo.strip() != "" and email_novo.strip() != "" and area_novo.strip() != "" and senha_provisoria.strip() != "":
            conn = db.get_connection()
            c = conn.cursor()
            try:
                c.execute("""
                    INSERT INTO usuarios (nome, email, senha, perfil, area)
                    VALUES (?, ?, ?, ?, ?)
                """, (nome_novo, email_novo, senha_provisoria, "Colaborador", area_novo))
                conn.commit()
                conn.close()
                
                link_gerado = f"http://localhost:8501/?convite={email_novo.replace('@', '_at_')}"
                st.success("Colaborador cadastrado com sucesso!")
                st.markdown(f"**Envie os dados de acesso abaixo para o colaborador:**")
                st.markdown(f"- **E-mail:** `{email_novo}`")
                st.markdown(f"- **Senha Provisória:** `{senha_provisoria}`")
                st.code(link_gerado, language="text")
            except Exception as e:
                conn.close()
                st.error(f"Erro ao cadastrar (talvez o e-mail já esteja em uso): {e}")
        else:
            st.error("Preencha todos os campos para prosseguir.")

st.divider()
st.subheader("Colaboradores Cadastrados na Equipe")

conn = db.get_connection()
try:
    df_equipe = pd.read_sql("SELECT nome as Nome, email as E_mail, area as Área, perfil as Perfil FROM usuarios WHERE perfil != 'Gestor'", conn)
    if not df_equipe.empty:
        st.dataframe(df_equipe, hide_index=True, use_container_width=True)
    else:
        st.info("Nenhum colaborador cadastrado além de você.")
except:
    st.info("Não foi possível carregar a lista de colaboradores.")
conn.close()