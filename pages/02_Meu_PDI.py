import streamlit as st
import pandas as pd
import database as db
from datetime import datetime

if 'usuario' not in st.session_state or st.session_state['usuario'] is None:
    st.warning("Faça login.")
    st.stop()

if st.session_state['usuario']['perfil'] == 'Gestor':
    st.warning("Esta página é exclusiva para colaboradores.")
    st.stop()

usuario = st.session_state['usuario']

# Botão de Sair na Barra Lateral
with st.sidebar:
    st.write(f"Logado como: **{usuario['nome']}**")
    if st.button("🚪 Sair da Conta (Logout)", use_container_width=True):
        st.session_state['usuario'] = None
        st.rerun()

# Centralizar Logo perfeitamente
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try:
        st.image("logo.png", width=250)
    except:
        try:
            st.image("logo.jpg", width=250)
        except:
            pass

st.title(f"Olá, {usuario['nome']}! 😊")
st.divider()

conn = db.get_connection()
df_atividades = pd.read_sql(f"SELECT * FROM atividades WHERE colaborador_id = {usuario['id']}", conn)

hoje = datetime.now().date()

def formatar_data_br(data_str):
    if not data_str:
        return ""
    venc_str = str(data_str).split('T')[0]
    try:
        return datetime.strptime(venc_str, '%Y-%m-%d').strftime('%d/%m/%Y')
    except:
        return venc_str

if not df_atividades.empty and 'data_vencimento' in df_atividades.columns:
    def recalcular_status_colab(row):
        status_atual = row['status']
        venc_str = str(row['data_vencimento']).split('T')[0]
        try:
            data_venc = datetime.strptime(venc_str, '%Y-%m-%d').date()
            if status_atual != 'Concluído' and data_venc < hoje:
                return 'Atrasado'
        except:
            pass
        return status_atual

    df_atividades['status'] = df_atividades.apply(recalcular_status_colab, axis=1)

concluidas = len(df_atividades[df_atividades['status'] == 'Concluído']) if not df_atividades.empty else 0
em_andamento = len(df_atividades[df_atividades['status'] == 'Em andamento']) if not df_atividades.empty else 0
atrasados = len(df_atividades[df_atividades['status'] == 'Atrasado']) if not df_atividades.empty else 0
nao_iniciado = len(df_atividades[df_atividades['status'] == 'Não iniciado']) if not df_atividades.empty else 0

st.subheader("Resumo das Minhas Metas")
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
        <div style="padding: 12px; border-radius: 8px; background-color: #1e1e1e; border-left: 5px solid #2ecc71; text-align: center;">
            <p style="margin: 0; font-size: 13px; color: #aaa;">Concluídas</p>
            <h3 style="margin: 0; color: #2ecc71;">{concluidas}</h3>
        </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
        <div style="padding: 12px; border-radius: 8px; background-color: #1e1e1e; border-left: 5px solid #3498db; text-align: center;">
            <p style="margin: 0; font-size: 13px; color: #aaa;">Em Andamento</p>
            <h3 style="margin: 0; color: #3498db;">{em_andamento}</h3>
        </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
        <div style="padding: 12px; border-radius: 8px; background-color: #1e1e1e; border-left: 5px solid #e74c3c; text-align: center;">
            <p style="margin: 0; font-size: 13px; color: #aaa;">Atrasados</p>
            <h3 style="margin: 0; color: #e74c3c;">{atrasados}</h3>
        </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
        <div style="padding: 12px; border-radius: 8px; background-color: #1e1e1e; border-left: 5px solid #CD853F; text-align: center;">
            <p style="margin: 0; font-size: 13px; color: #aaa;">Não Iniciadas</p>
            <h3 style="margin: 0; color: #CD853F;">{nao_iniciado}</h3>
        </div>
    """, unsafe_allow_html=True)

st.write("")

with st.expander("➕ Cadastrar Nova Meta ou Atividade"):
    with st.form("form_nova_atividade_colab"):
        titulo = st.text_input("Título da Meta/Atividade")
        descricao = st.text_area("Descrição detalhada")
        prioridade = st.selectbox("Prioridade", ["Baixa", "Média", "Alta"])
        status = st.selectbox("Status Inicial", ["Não iniciado", "Em andamento", "Concluído"])
        vencimento = st.date_input("Data de Vencimento")
        
        if st.form_submit_button("Cadastrar Atividade", use_container_width=True):
            if titulo.strip() != "":
                c = conn.cursor()
                c.execute("""
                    INSERT INTO atividades (colaborador_id, titulo, descricao, prioridade, status, data_vencimento)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (usuario['id'], titulo, descricao, prioridade, status, str(vencimento)))
                conn.commit()
                conn.close()
                st.success("Nova meta cadastrada com sucesso!")
                st.rerun()
            else:
                st.error("O título da meta não pode estar vazio.")

st.write("---")
st.subheader("Minhas Metas Cadastradas (Gerenciamento)")

if not df_atividades.empty:
    st.write("Abra a meta abaixo para atualizar o status, editar a descrição ou excluí-la.")
    
    for index, row in df_atividades.iterrows():
        meta_id = row['id']
        meta_titulo = row['titulo']
        meta_status_atual = row['status']
        meta_desc = row['descricao']
        meta_prio = row['prioridade']
        meta_venc = str(row['data_vencimento']).split('T')[0]
        meta_venc_br = formatar_data_br(meta_venc)

        icone_status = "🟢" if meta_status_atual == 'Concluído' else ("🔵" if meta_status_atual == 'Em andamento' else ("🔴" if meta_status_atual == 'Atrasado' else "🤎"))

        with st.expander(f"{icone_status} {meta_titulo} (Prioridade: {meta_prio} | Status: {meta_status_atual})"):
            
            with st.form(f"form_editar_meta_{meta_id}"):
                st.markdown(f"**Editar Informações da Meta:**")
                novo_titulo = st.text_input("Título", value=meta_titulo, key=f"edit_tit_{meta_id}")
                nova_descricao = st.text_area("Descrição Detalhada", value=meta_desc, key=f"edit_desc_{meta_id}")
                
                if st.form_submit_button("Salvar Alterações de Texto", use_container_width=True):
                    if novo_titulo.strip() != "":
                        c = conn.cursor()
                        c.execute("UPDATE atividades SET titulo = ?, descricao = ? WHERE id = ?", (novo_titulo, nova_descricao, meta_id))
                        conn.commit()
                        conn.close()
                        st.success("Título e descrição atualizados com sucesso!")
                        st.rerun()
                    else:
                        st.error("O título da meta não pode ficar vazio.")

            if meta_status_atual == 'Atrasado':
                st.error(f"📅 Data de Vencimento: {meta_venc_br} (⚠️ Prazo vencido. Apenas o(a) gestor(a) pode alterar esta data.)")
            else:
                st.caption(f"📅 Data de Vencimento: {meta_venc_br}")
            
            opcoes_status = ["Não iniciado", "Em andamento", "Concluído"]
            idx_atual = opcoes_status.index(meta_status_atual) if meta_status_atual in opcoes_status else 0

            col_status, col_excluir = st.columns([3, 1])
            
            with col_status:
                with st.form(f"form_status_{meta_id}"):
                    novo_status_meta = st.selectbox("Atualizar Status:", opcoes_status, index=idx_atual, key=f"sel_st_{meta_id}")
                    if st.form_submit_button("Salvar Status", use_container_width=True):
                        c = conn.cursor()
                        c.execute("UPDATE atividades SET status = ? WHERE id = ?", (novo_status_meta, meta_id))
                        conn.commit()
                        conn.close()
                        st.success("Status atualizado com sucesso!")
                        st.rerun()
                        
            with col_excluir:
                st.write("")
                st.write("")
                if st.button("🗑️ Excluir", key=f"btn_excluir_{meta_id}", use_container_width=True):
                    c = conn.cursor()
                    c.execute("DELETE FROM atividades WHERE id = ?", (meta_id,))
                    conn.commit()
                    conn.close()
                    st.success("Meta excluída com sucesso!")
                    st.rerun()

    conn.close()

    st.write("---")
    st.subheader("Tabela Resumo Geral")
    
    df_atividades['vencimento_br'] = df_atividades['data_vencimento'].apply(formatar_data_br)

    df_exibicao = df_atividades[['titulo', 'descricao', 'prioridade', 'status', 'vencimento_br']].rename(
        columns={
            'titulo': 'Atividade', 
            'descricao': 'Descrição', 
            'prioridade': 'Prioridade', 
            'status': 'Status', 
            'vencimento_br': 'Vencimento'
        }
    )
    
    def colorir_status_colab(val):
        if val == 'Concluído':
            return 'color: #2ecc71; font-weight: bold;'
        elif val == 'Em andamento':
            return 'color: #3498db; font-weight: bold;'
        elif val == 'Atrasado':
            return 'color: #e74c3c; font-weight: bold;'
        elif val == 'Não iniciado':
            return 'color: #CD853F; font-weight: bold;'
        return ''

    st.dataframe(df_exibicao.style.map(colorir_status_colab, subset=['Status']), hide_index=True, use_container_width=True)
else:
    conn.close()
    st.info("Você ainda não possui metas cadastradas. Utilize o campo acima para cadastrar sua primeira atividade!")