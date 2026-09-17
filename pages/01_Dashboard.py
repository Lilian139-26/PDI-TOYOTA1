import streamlit as st
import pandas as pd
import database as db
from datetime import datetime

if 'usuario' not in st.session_state or st.session_state['usuario'] is None:
    st.warning("Faça login.")
    st.stop()

usuario = st.session_state['usuario']

# Botão de Sair na Barra Lateral
with st.sidebar:
    st.write(f"Logado como: **{usuario['nome']}**")
    if st.button("🚪 Sair da Conta (Logout)", use_container_width=True):
        st.session_state['usuario'] = None
        st.rerun()

# Centralizar Logo perfeitamente em todas as telas
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try:
        st.image("logo.png", width=250)
    except:
        try:
            st.image("logo.jpg", width=250)
        except:
            pass

# Exibe o nome atualizado do gestor dinamicamente
st.title(f"Olá, {usuario['nome']} 😄")
st.divider()

conn = db.get_connection()
try:
    df_atividades = pd.read_sql("SELECT u.id as colab_id, u.nome as Colaborador, u.area as Departamento, a.id, a.titulo as Atividade, a.descricao as Descricao, a.prioridade as Prioridade, a.status as Status, a.data_vencimento as Vencimento FROM atividades a JOIN usuarios u ON a.colaborador_id = u.id", conn)
except:
    df_atividades = pd.DataFrame()

conn.close()

hoje = datetime.now().date()

def formatar_data_br(data_str):
    if not data_str:
        return ""
    venc_str = str(data_str).split('T')[0]
    try:
        return datetime.strptime(venc_str, '%Y-%m-%d').strftime('%d/%m/%Y')
    except:
        return venc_str

if not df_atividades.empty and 'Vencimento' in df_atividades.columns:
    def recalcular_status(row):
        status_atual = row['Status']
        venc_str = str(row['Vencimento']).split('T')[0]
        try:
            data_venc = datetime.strptime(venc_str, '%Y-%m-%d').date()
            if status_atual != 'Concluído' and data_venc < hoje:
                return 'Atrasado'
        except:
            pass
        return status_atual

    df_atividades['Status'] = df_atividades.apply(recalcular_status, axis=1)
    df_atividades['Vencimento_Formatado'] = df_atividades['Vencimento'].apply(formatar_data_br)

lista_colaboradores = ["Todos os Colaboradores"]
if not df_atividades.empty and 'Colaborador' in df_atividades.columns:
    lista_colaboradores += list(df_atividades['Colaborador'].dropna().unique())

colab_selecionado = st.selectbox("Filtrar painel por Nome do Colaborador:", lista_colaboradores)

df_filtrado = df_atividades.copy()

if colab_selecionado != "Todos os Colaboradores":
    if not df_atividades.empty:
        df_filtrado = df_atividades[df_atividades['Colaborador'] == colab_selecionado]

concluidas = len(df_filtrado[df_filtrado['Status'] == 'Concluído']) if not df_filtrado.empty else 0
em_andamento = len(df_filtrado[df_filtrado['Status'] == 'Em andamento']) if not df_filtrado.empty else 0
atrasados = len(df_filtrado[df_filtrado['Status'] == 'Atrasado']) if not df_filtrado.empty else 0
nao_iniciado = len(df_filtrado[df_filtrado['Status'] == 'Não iniciado']) if not df_filtrado.empty else 0

st.subheader("Visão Geral do PDI (Indicadores)")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
        <div style="padding: 15px; border-radius: 8px; background-color: #1e1e1e; border-left: 5px solid #2ecc71; text-align: center;">
            <p style="margin: 0; font-size: 14px; color: #aaa;">Concluídas</p>
            <h2 style="margin: 0; color: #2ecc71;">{concluidas}</h2>
        </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
        <div style="padding: 15px; border-radius: 8px; background-color: #1e1e1e; border-left: 5px solid #3498db; text-align: center;">
            <p style="margin: 0; font-size: 14px; color: #aaa;">Iniciadas/Andamento</p>
            <h2 style="margin: 0; color: #3498db;">{em_andamento}</h2>
        </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
        <div style="padding: 15px; border-radius: 8px; background-color: #1e1e1e; border-left: 5px solid #e74c3c; text-align: center;">
            <p style="margin: 0; font-size: 14px; color: #aaa;">Atrasados</p>
            <h2 style="margin: 0; color: #e74c3c;">{atrasados}</h2>
        </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
        <div style="padding: 15px; border-radius: 8px; background-color: #1e1e1e; border-left: 5px solid #CD853F; text-align: center;">
            <p style="margin: 0; font-size: 14px; color: #aaa;">Não Iniciadas</p>
            <h2 style="margin: 0; color: #CD853F;">{nao_iniciado}</h2>
        </div>
    """, unsafe_allow_html=True)

st.divider()

st.subheader("Metas, Descrições e Gestão de Prazos (PDIs)")

if not df_atividades.empty:
    colab_detalhe_meta = st.selectbox("Selecione um colaborador para inspecionar e gerenciar as metas:", df_atividades['Colaborador'].unique(), key="sel_meta")
    df_detalhe_colab = df_atividades[df_atividades['Colaborador'] == colab_detalhe_meta]
    
    if not df_detalhe_colab.empty:
        st.write("Abra a meta abaixo para visualizar a descrição e renegociar/alterar a data de vencimento:")
        
        for index, row in df_detalhe_colab.iterrows():
            meta_id = row['id']
            meta_titulo = row['Atividade']
            meta_status = row['Status']
            meta_prio = row['Prioridade']
            meta_desc = row['Descricao']
            meta_venc_original = str(row['Vencimento']).split('T')[0]
            
            try:
                data_obj = datetime.strptime(meta_venc_original, '%Y-%m-%d').date()
            except:
                data_obj = hoje

            icone_status = "🟢" if meta_status == 'Concluído' else ("🔵" if meta_status == 'Em andamento' else ("🔴" if meta_status == 'Atrasado' else "🤎"))

            with st.expander(f"{icone_status} Meta: {meta_titulo} (Prioridade: {meta_prio} | Status: {meta_status})"):
                st.markdown(f"**Descrição detalhada enviada pelo colaborador:**")
                st.info(meta_desc if str(meta_desc).strip() != "" else "Nenhuma descrição detalhada informada.")
                st.caption(f"📅 Vencimento Atual: {row['Vencimento_Formatado']}")
                
                with st.form(f"form_gestor_data_{meta_id}"):
                    nova_data_venc = st.date_input("Alterar Data de Vencimento (Prazo):", value=data_obj)
                    if st.form_submit_button("Salvar Nova Data de Vencimento", use_container_width=True):
                        conn_up = db.get_connection()
                        c_up = conn_up.cursor()
                        c_up.execute("UPDATE atividades SET data_vencimento = ? WHERE id = ?", (str(nova_data_venc), meta_id))
                        conn_up.commit()
                        conn_up.close()
                        st.success("Data de vencimento atualizada com sucesso!")
                        st.rerun()

    st.write("---")

if not df_filtrado.empty:
    df_exibicao = df_filtrado.drop(columns=['Vencimento', 'id', 'colab_id']).rename(columns={'Vencimento_Formatado': 'Vencimento'})
    
    def colorir_status(val):
        if val == 'Concluído':
            return 'color: #2ecc71; font-weight: bold;'
        elif val == 'Em andamento':
            return 'color: #3498db; font-weight: bold;'
        elif val == 'Atrasado':
            return 'color: #e74c3c; font-weight: bold;'
        elif val == 'Não iniciado':
            return 'color: #CD853F; font-weight: bold;'
        return ''

    st.dataframe(df_exibicao.style.map(colorir_status, subset=['Status']), hide_index=True, use_container_width=True)
else:
    st.info("Nenhuma atividade cadastrada para este filtro.")