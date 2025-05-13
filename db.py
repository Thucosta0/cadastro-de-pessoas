# --------------------------------------------------
# Import bibliotecas
# --------------------------------------------------
import os
import mysql.connector
from datetime import datetime
import json
import tkinter as tk
from tkinter import simpledialog, messagebox

# --------------------------------------------------
# Configs global
# --------------------------------------------------
# Constantes em maiúsculas e definidas no topo do arquivo
CONFIG_FILE = "db_config.json"

# Configurações padrão definidas como dicionário para fácil acesso
CONFIG_MYSQL = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'Thu3048#',
    'database': 'cadastro_pessoas'
}

# --------------------------------------------------
# Config banco de dados 
# --------------------------------------------------
def carregar_configuracao():
    """
    Carrega as configurações do arquivo JSON para a variável global.
    Retorna True se bem-sucedido, False caso contrário.
    """
    # Uso explícito da variável global
    global CONFIG_MYSQL
    
    if os.path.exists(CONFIG_FILE):
        try:
            # Uso do with para gerenciamento automático de recursos
            with open(CONFIG_FILE, 'r') as file:
                CONFIG_MYSQL = json.load(file)
            return True
        except Exception as e:
            return False
    return False

def salvar_configuracao():
    """
    Salva as configurações atuais no arquivo JSON.
    Retorna True se bem-sucedido, False caso contrário.
    """
    try:
        # Uso do with para garantir fechamento do arquivo
        with open(CONFIG_FILE, 'w') as file:
            # Formatação JSON com indent para legibilidade
            json.dump(CONFIG_MYSQL, file, indent=4)
        return True
    except Exception as e:
        return False

def configurar_mysql_gui():
    """
    Exibe uma interface gráfica para configuração do MySQL.
    Retorna True se a configuração foi salva, False caso contrário.
    """
    # Uso de variáveis globais apenas quando necessário
    global CONFIG_MYSQL
    
    # Criação de janela modal para configuração
    dialog = tk.Toplevel()
    dialog.title("Configuração do MySQL")
    dialog.geometry("400x300")
    dialog.resizable(False, False)
    
    # Centralização da janela na tela para melhor UX
    dialog.update_idletasks()
    width = dialog.winfo_width()
    height = dialog.winfo_height()
    x = (dialog.winfo_screenwidth() // 2) - (width // 2)
    y = (dialog.winfo_screenheight() // 2) - (height // 2)
    dialog.geometry(f'+{x}+{y}')
    
    # Organização da interface em frames
    main_frame = tk.Frame(dialog, padx=20, pady=20)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    tk.Label(main_frame, text="Configuração do MySQL", font=("Helvetica", 12, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))
    
    # Layout de formulário organizado e alinhado
    tk.Label(main_frame, text="Host:").grid(row=1, column=0, sticky="w", pady=5)
    host_entry = tk.Entry(main_frame, width=30)
    host_entry.grid(row=1, column=1, sticky="w", pady=5)
    host_entry.insert(0, CONFIG_MYSQL['host'])
    
    tk.Label(main_frame, text="Porta:").grid(row=2, column=0, sticky="w", pady=5)
    port_entry = tk.Entry(main_frame, width=30)
    port_entry.grid(row=2, column=1, sticky="w", pady=5)
    port_entry.insert(0, str(CONFIG_MYSQL['port']))
    
    tk.Label(main_frame, text="Usuário:").grid(row=3, column=0, sticky="w", pady=5)
    user_entry = tk.Entry(main_frame, width=30)
    user_entry.grid(row=3, column=1, sticky="w", pady=5)
    user_entry.insert(0, CONFIG_MYSQL['user'])
    
    tk.Label(main_frame, text="Senha:").grid(row=4, column=0, sticky="w", pady=5)
    password_entry = tk.Entry(main_frame, width=30, show="*")
    password_entry.grid(row=4, column=1, sticky="w", pady=5)
    password_entry.insert(0, CONFIG_MYSQL['password'])
    
    tk.Label(main_frame, text="Banco de Dados:").grid(row=5, column=0, sticky="w", pady=5)
    database_entry = tk.Entry(main_frame, width=30)
    database_entry.grid(row=5, column=1, sticky="w", pady=5)
    database_entry.insert(0, CONFIG_MYSQL['database'])
    
    # Uso de dicionário para compartilhar estado entre funções
    result = {"success": False}
    
    def save_config():
        """Valida e salva as configurações do formulário."""
        # Validação de dados antes de salvar
        try:
            CONFIG_MYSQL['host'] = host_entry.get()
            CONFIG_MYSQL['port'] = int(port_entry.get())
            CONFIG_MYSQL['user'] = user_entry.get()
            CONFIG_MYSQL['password'] = password_entry.get()
            CONFIG_MYSQL['database'] = database_entry.get()
            
            if salvar_configuracao():
                messagebox.showinfo("Sucesso", "Configuração salva com sucesso!")
                result["success"] = True
                dialog.destroy()
            else:
                messagebox.showerror("Erro", "Não foi possível salvar a configuração!")
        except ValueError:
            # Mensagem de erro específica para o problema encontrado
            messagebox.showerror("Erro", "A porta deve ser um número inteiro!")
    
    def cancel():
        """Fecha o diálogo sem salvar."""
        dialog.destroy()
    
    # Organização de botões de forma padronizada
    button_frame = tk.Frame(main_frame)
    button_frame.grid(row=6, column=0, columnspan=2, pady=(20, 0))
    
    tk.Button(button_frame, text="Salvar", command=save_config, width=10).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Cancelar", command=cancel, width=10).pack(side=tk.LEFT, padx=5)
    
    # Configuração da janela como modal para evitar interações indesejadas
    dialog.transient()
    dialog.grab_set()
    dialog.wait_window()
    
    return result["success"]

# --------------------------------------------------
# Conexões banco 
# --------------------------------------------------
def conectar_banco():
    """
    Conecta ao banco de dados MySQL usando as configurações salvas.
    Retorna uma tupla (conexão, cursor) ou (None, None) se falhar.
    """
    # Carregamento de configurações antes de usar
    carregar_configuracao()
    
    try:
        # Parâmetros nomeados para maior clareza
        conexao = mysql.connector.connect(
            host=CONFIG_MYSQL['host'],
            port=CONFIG_MYSQL['port'],
            user=CONFIG_MYSQL['user'], 
            password=CONFIG_MYSQL['password'],
            database=CONFIG_MYSQL['database']
        )
        cursor = conexao.cursor()
        
        # Garantir que as tabelas existam antes de usar
        criar_tabelas(cursor)
        conexao.commit()
        
        return conexao, cursor
    except mysql.connector.Error as erro:
        # Tratamento específico para erros conhecidos
        if erro.errno == 1049:  # Erro: banco de dados não existe
            if criar_banco():
                # Recursão com propósito claro - tentar novamente após criar o banco
                return conectar_banco()
        
        return None, None  # Retorno consistente para facilitar verificações

def criar_banco():
    """
    Cria o banco de dados se não existir.
    Retorna True se bem-sucedido, False caso contrário.
    """
    try:
        # Conexão sem especificar banco para poder criá-lo
        conexao = mysql.connector.connect(
            host=CONFIG_MYSQL['host'],
            port=CONFIG_MYSQL['port'],
            user=CONFIG_MYSQL['user'],
            password=CONFIG_MYSQL['password']
        )
        cursor = conexao.cursor()
        
        # Uso de IF NOT EXISTS para evitar erros
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {CONFIG_MYSQL['database']}")
        
        # Fechamento explícito da conexão após uso
        conexao.close()
        return True
    except mysql.connector.Error as err:
        return False

def criar_tabelas(cursor):
    """
    Cria as tabelas necessárias se não existirem.
    """
    # Uso de SQL multilinhas com aspas triplas para legibilidade
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pessoas (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nome VARCHAR(100) NOT NULL,
        email VARCHAR(100),
        telefone VARCHAR(20),
        categoria VARCHAR(20) DEFAULT 'Cliente',
        data_criacao DATETIME
    )
    ''')

# --------------------------------------------------
# FUNÇÕES DE FORMATAÇÃO DE DADOS
# --------------------------------------------------
def formatar_data_para_exibicao(data_str):
    """
    Converte uma data do formato MySQL para o formato brasileiro.
    Retorna string vazia se a entrada for nula.
    """
    # Verificação de dados vazios antes de processar
    if not data_str:
        return ""
    
    try:
        # Conversão explícita entre formatos de data
        data = datetime.strptime(data_str, '%Y-%m-%d %H:%M:%S')
        return data.strftime('%d/%m/%Y %H:%M:%S')
    except ValueError:
        # Fallback seguro em caso de erro
        return data_str

# --------------------------------------------------
# FUNÇÕES BÁSICAS DO BANCO DE DADOS (CRUD)
# --------------------------------------------------

# ----- CREATE (CRIAR) -----
def adicionar_pessoa(nome, email, telefone, categoria):
    """
    Insere uma nova pessoa no banco de dados.
    Retorna True se bem-sucedido, False caso contrário.
    """
    try:
        conexao, cursor = conectar_banco()
        
        # Verificação de conexão bem-sucedida
        if not conexao:
            return False
        
        # Captura de timestamp no momento da criação
        data_atual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Uso de consulta parametrizada para evitar SQL Injection
        cursor.execute('''
        INSERT INTO pessoas (nome, email, telefone, categoria, data_criacao)
        VALUES (%s, %s, %s, %s, %s)
        ''', (nome, email, telefone, categoria, data_atual))
        
        # Commit explícito para persistir as mudanças
        conexao.commit()
        
        # Fechamento da conexão após uso
        conexao.close()
        
        return True
    except Exception as e:
        return False

# ----- READ (LER) -----
def obter_todas_pessoas():
    """
    Retorna todas as pessoas cadastradas no banco de dados.
    Retorna uma lista vazia em caso de erro.
    """
    try:
        conexao, cursor = conectar_banco()
        
        if not conexao:
            return []
        
        # Consulta SQL com ordenação para consistência
        cursor.execute('''
        SELECT id, nome, email, telefone, categoria, data_criacao
        FROM pessoas
        ORDER BY nome
        ''')
        
        # Processamento dos resultados para formato adequado
        resultados = []
        for pessoa in cursor.fetchall():
            # Formata a data de criação para exibição
            data_formatada = formatar_data_para_exibicao(str(pessoa[5]) if pessoa[5] else None)
            
            # Adiciona a pessoa com os dados formatados
            resultados.append((
                pessoa[0],  # ID
                pessoa[1],  # Nome
                pessoa[2] if pessoa[2] else "",  # Email
                pessoa[3] if pessoa[3] else "",  # Telefone
                pessoa[4] if pessoa[4] else "Cliente",  # Categoria
                data_formatada  # Data de criação
            ))
        
        conexao.close()
        
        return resultados
    except Exception as e:
        return []

def buscar_pessoas(termo_busca):
    """
    Busca pessoas pelo nome, email ou telefone.
    Retorna uma lista de resultados ou lista vazia em caso de erro.
    """
    try:
        conexao, cursor = conectar_banco()
        
        if not conexao:
            return []
        
        # Uso de LIKE com wildcards para busca parcial
        termo = f"%{termo_busca}%"
        
        # Consulta parametrizada com operador OR para múltiplos campos
        cursor.execute('''
        SELECT id, nome, email, telefone, categoria, data_criacao
        FROM pessoas
        WHERE 
            nome LIKE %s OR
            email LIKE %s OR
            telefone LIKE %s
        ORDER BY nome
        ''', (termo, termo, termo))
        
        resultados = []
        for pessoa in cursor.fetchall():
            data_formatada = formatar_data_para_exibicao(str(pessoa[5]) if pessoa[5] else None)
            
            resultados.append((
                pessoa[0],
                pessoa[1],
                pessoa[2] if pessoa[2] else "",
                pessoa[3] if pessoa[3] else "",
                pessoa[4] if pessoa[4] else "Cliente",
                data_formatada
            ))
        
        conexao.close()
        
        return resultados
    except Exception as e:
        return []

def filtrar_pessoas_por_categoria(categoria):
    """
    Filtra pessoas por categoria específica.
    Retorna uma lista de resultados ou lista vazia em caso de erro.
    """
    try:
        conexao, cursor = conectar_banco()
        
        if not conexao:
            return []
        
        # Busca exata para filtro por categoria
        cursor.execute('''
        SELECT id, nome, email, telefone, categoria, data_criacao
        FROM pessoas
        WHERE categoria = %s
        ORDER BY nome
        ''', (categoria,))  # Tupla de parâmetro único com vírgula no final
        
        resultados = []
        for pessoa in cursor.fetchall():
            data_formatada = formatar_data_para_exibicao(str(pessoa[5]) if pessoa[5] else None)
            
            resultados.append((
                pessoa[0],
                pessoa[1],
                pessoa[2] if pessoa[2] else "",
                pessoa[3] if pessoa[3] else "",
                pessoa[4] if pessoa[4] else "Cliente",
                data_formatada
            ))
        
        conexao.close()
        
        return resultados
    except Exception as e:
        return []

def obter_pessoa_por_id(id_pessoa):
    """
    Busca uma pessoa específica pelo ID.
    Retorna uma tupla com os dados da pessoa ou None em caso de erro.
    """
    try:
        conexao, cursor = conectar_banco()
        
        if not conexao:
            return None
        
        # Busca por ID com parâmetro para evitar SQL Injection
        cursor.execute('SELECT * FROM pessoas WHERE id = %s', (id_pessoa,))
        
        # fetchone() para obter um único registro
        pessoa = cursor.fetchone()
        
        conexao.close()
        
        return pessoa
    except Exception as e:
        return None

# ----- UPDATE (ATUALIZAR) -----
def atualizar_pessoa(id_pessoa, nome, email, telefone, categoria):
    """
    Atualiza os dados de uma pessoa existente pelo ID.
    Retorna True se bem-sucedido, False caso contrário.
    """
    try:
        conexao, cursor = conectar_banco()
        
        if not conexao:
            return False
        
        # Consulta UPDATE com WHERE para segurança
        cursor.execute('''
        UPDATE pessoas
        SET nome = %s, email = %s, telefone = %s, categoria = %s
        WHERE id = %s
        ''', (nome, email, telefone, categoria, id_pessoa))
        
        conexao.commit()
        conexao.close()
        
        return True
    except Exception as e:
        return False

# ----- DELETE (EXCLUIR) -----
def excluir_pessoa(id_pessoa):
    """
    Remove uma pessoa do banco de dados pelo ID.
    Retorna True se bem-sucedido, False caso contrário.
    """
    try:
        conexao, cursor = conectar_banco()
        
        if not conexao:
            return False
        
        # Consulta DELETE com WHERE para evitar exclusão acidental de todos os registros
        cursor.execute('DELETE FROM pessoas WHERE id = %s', (id_pessoa,))
        
        conexao.commit()
        conexao.close()
        
        return True
    except Exception as e:
        return False

# INÍCIO DO PROGRAMA
# Este código só é executado quando rodamos este arquivo diretamente,
# não quando ele é importado em outro arquivo
if __name__ == "__main__":
    print("TESTE DO MÓDULO DE BANCO DE DADOS")
    
    # Tenta carregar, se não encontrar, pede configuração
    if not carregar_configuracao():
        print("Configuração não encontrada. Vamos configurar o MySQL.")
        configurar_mysql_gui()
    
    # Testa a conexão
    conexao, cursor = conectar_banco()
    
    if conexao:
        print("Conexão estabelecida com sucesso.")
        conexao.close()
    else:
        print("Falha na conexão. Execute o arquivo app.py para configurar.") 