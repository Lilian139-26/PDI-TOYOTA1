import sqlite3

def get_connection():
    conn = sqlite3.connect('pdi_database.db', check_same_thread=False)
    return conn

def inicializar_banco():
    conn = get_connection()
    c = conn.cursor()
    
    # Tabela de Usuários (Gestores e Colaboradores)
    c.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            perfil TEXT NOT NULL,
            area TEXT NOT NULL
        )
    ''')
    
    # Tabela de Metas/Atividades do PDI
    c.execute('''
        CREATE TABLE IF NOT EXISTS atividades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            colaborador_id INTEGER,
            titulo TEXT NOT NULL,
            descricao TEXT,
            prioridade TEXT,
            status TEXT,
            data_vencimento TEXT,
            FOREIGN KEY (colaborador_id) REFERENCES usuarios (id)
        )
    ''')
    
    # Criação de um usuário Gestor padrão caso não exista nenhum cadastrado
    c.execute("SELECT COUNT(*) FROM usuarios WHERE perfil = 'Gestor'")
    if c.fetchone()[0] == 0:
        c.execute("""
            INSERT INTO usuarios (nome, email, senha, perfil, area)
            VALUES (?, ?, ?, ?, ?)
        """, ("Gestor Toyota", "gestor@toyota.com", "123456", "Gestor", "Administrativo"))

    conn.commit()
    conn.close()

inicializar_banco()

def autenticar_usuario(email, senha):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, nome, email, perfil, area FROM usuarios WHERE email = ? AND senha = ?", (email, senha))
    row = c.fetchone()
    conn.close()
    
    if row:
        return {
            "id": row[0],
            "nome": row[1],
            "email": row[2],
            "perfil": row[3],
            "area": row[4]
        }
    return None