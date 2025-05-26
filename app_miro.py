import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import os
import json
import mysql.connector
from mysql.connector import Error
import hashlib
from datetime import datetime
import re
from CTkMessagebox import CTkMessagebox

# Configurações do tema
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Variáveis globais
janela = None
frame_atual = None
usuario_logado = {"id": None, "nome": None, "nivel_acesso": None}
janelas_abertas = {}

# Configurações do banco de dados (serão carregadas do arquivo config_db.json)
config_db = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "Thu3048#",
    "database": "sistema_miro"
}



# Funções de utilidade
def exibir_mensagem(titulo, mensagem):
    messagebox.showinfo(titulo, mensagem)

def exibir_erro(titulo, mensagem):
    messagebox.showerror(titulo, mensagem)

def centralizar_janela(janela, largura, altura):
    largura_tela = janela.winfo_screenwidth()
    altura_tela = janela.winfo_screenheight()
    x = (largura_tela - largura) // 2
    y = (altura_tela - altura) // 2
    janela.geometry(f'{largura}x{altura}+{x}+{y}')

def criar_hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def converter_data_para_banco(data_br):
    """Converte data do formato brasileiro (DD/MM/AAAA) para o formato do banco (AAAA-MM-DD)"""
    try:
        if not data_br:
            return None
        if not re.match(r'^\d{2}/\d{2}/\d{4}$', data_br):
            return None
        
        dia, mes, ano = data_br.split('/')
        data_banco = f"{ano}-{mes}-{dia}"
        
        # Validar se é uma data válida
        datetime.strptime(data_banco, '%Y-%m-%d')
        return data_banco
    except ValueError:
        return None

def converter_data_para_exibicao(data_banco):
    """Converte data do formato do banco (AAAA-MM-DD) para o formato brasileiro (DD/MM/AAAA)"""
    try:
        if not data_banco:
            return ""
        
        data = datetime.strptime(str(data_banco), '%Y-%m-%d')
        return data.strftime('%d/%m/%Y')
    except ValueError:
        return str(data_banco) if data_banco else ""

# Funções de banco de dados
def criar_conexao_mysql():
    try:
        conexao = mysql.connector.connect(
            host=config_db["host"],
            user=config_db["user"],
            password=config_db["password"],
            database=config_db["database"]
        )
        return conexao
    except Error as e:
        exibir_erro("Erro de Conexão", f"Erro ao conectar ao MySQL: {e}")
        return None

def checar_conexao_mysql():
    """Verifica se é possível conectar ao banco de dados com as configurações atuais"""
    try:
        conexao = criar_conexao_mysql()
        if conexao and conexao.is_connected():
            conexao.close()
            return True
        return False
    except Exception as e:
        print(f"Erro ao verificar conexão: {e}")
        return False

def configurar_mysql():
    """Verifica se o banco de dados existe e atualiza as configurações de conexão"""
    try:
        # Criar conexão sem especificar banco de dados
        conexao = mysql.connector.connect(
            host=config_db["host"],
            user=config_db["user"],
            password=config_db["password"]
        )
        
        if conexao.is_connected():
            cursor = conexao.cursor()
            
            # Verificar se o banco de dados existe
            cursor.execute("SHOW DATABASES LIKE 'sistema_miro'")
            resultado = cursor.fetchone()
            
            if not resultado:
                print("Banco de dados 'sistema_miro' não existe.")
                print("Execute o utilitário 'configurar_db.py' para criar e configurar o banco de dados.")
                cursor.close()
                conexao.close()
                return False
            
            # Se o banco de dados existe, atualizar a configuração
            config_db["database"] = "sistema_miro"
            
            # Salvar configurações em arquivo
            try:
                with open("config_db.json", "w") as f:
                    json.dump(config_db, f, indent=4)
            except Exception as e:
                print(f"Aviso: Não foi possível salvar o arquivo de configuração: {e}")
            
            print("Configuração de conexão atualizada com sucesso!")
            
            cursor.close()
            conexao.close()
            return True
    except Error as e:
        print(f"Erro ao configurar conexão com MySQL: {e}")
        return False
    finally:
        if 'conexao' in locals() and conexao.is_connected():
            cursor.close()
            conexao.close()

def configurar_mysql_gui():
    global janelas_abertas
    
    # Verificar se já existe uma janela de configuração aberta
    if "config_mysql" in janelas_abertas and janelas_abertas["config_mysql"].winfo_exists():
        janelas_abertas["config_mysql"].lift()
        return
    
    janela_config = ctk.CTkToplevel()
    janela_config.title("Configurar Conexão MySQL")
    janela_config.geometry("400x400")
    centralizar_janela(janela_config, 400, 400)
    janela_config.grab_set()  # Torna a janela modal
    janela_config.attributes("-topmost", True)
    
    # Registrar a janela na lista de janelas abertas
    janelas_abertas["config_mysql"] = janela_config
    
    # Configurar protocolo de fechamento
    def ao_fechar_janela_config():
        if "config_mysql" in janelas_abertas:
            del janelas_abertas["config_mysql"]
        janela_config.destroy()
    
    janela_config.protocol("WM_DELETE_WINDOW", ao_fechar_janela_config)
    
    frame = ctk.CTkFrame(janela_config)
    frame.pack(padx=20, pady=20, fill="both", expand=True)
    
    # Instruções
    lbl_instrucoes = ctk.CTkLabel(
        frame,
        text=(
            "Configure a conexão com o banco de dados MySQL.\n"
            "Esses dados serão usados APENAS para conectar ao servidor MySQL.\n\n"
            "IMPORTANTE: Este aplicativo NÃO cria tabelas nem configura o banco de dados.\n"
            "Para criar o banco de dados completo, use o botão 'Abrir Utilitário de Configuração' abaixo."
        ),
        font=ctk.CTkFont(size=12),
        justify="left"
    )
    lbl_instrucoes.pack(pady=(0, 15), anchor="w")
    
    # Carregar configurações atuais
    lbl_titulo = ctk.CTkLabel(frame, text="Configuração do MySQL", font=ctk.CTkFont(size=16, weight="bold"))
    lbl_titulo.pack(pady=10)
    
    lbl_host = ctk.CTkLabel(frame, text="Host:")
    lbl_host.pack(anchor="w", padx=10, pady=5)
    txt_host = ctk.CTkEntry(frame, width=300)
    txt_host.insert(0, config_db["host"])
    txt_host.pack(padx=10, pady=5)
    
    lbl_usuario = ctk.CTkLabel(frame, text="Usuário:")
    lbl_usuario.pack(anchor="w", padx=10, pady=5)
    txt_usuario = ctk.CTkEntry(frame, width=300)
    txt_usuario.insert(0, config_db["user"])
    txt_usuario.pack(padx=10, pady=5)
    
    lbl_senha = ctk.CTkLabel(frame, text="Senha:")
    lbl_senha.pack(anchor="w", padx=10, pady=5)
    txt_senha = ctk.CTkEntry(frame, width=300, show="*")
    txt_senha.insert(0, config_db["password"])
    txt_senha.pack(padx=10, pady=5)
    
    def salvar_configuracoes():
        global config_db
        config_db["host"] = txt_host.get()
        config_db["user"] = txt_usuario.get()
        config_db["password"] = txt_senha.get()
        
        # Salvar configurações em arquivo JSON
        try:
            with open("config_db.json", "w") as f:
                json.dump(config_db, f, indent=4)
            
            if configurar_mysql():
                exibir_mensagem("Sucesso", "Configurações de conexão salvas com sucesso!\n\nPara configurar as tabelas do banco de dados, execute o utilitário 'configurar_db.py'")
                ao_fechar_janela_config()
            else:
                exibir_erro("Atenção", "As configurações de conexão foram salvas, mas o banco de dados 'sistema_miro' não foi encontrado.\n\nPor favor, execute o utilitário 'configurar_db.py' para criar e configurar o banco de dados.")
        except Exception as e:
            exibir_erro("Erro", f"Erro ao salvar configurações: {e}")
    
    def testar_conexao():
        host = txt_host.get()
        user = txt_usuario.get()
        password = txt_senha.get()
        
        try:
            conexao = mysql.connector.connect(
                host=host,
                user=user,
                password=password
            )
            
            if conexao.is_connected():
                exibir_mensagem("Sucesso", "Conexão estabelecida com sucesso!")
                conexao.close()
        except Error as e:
            exibir_erro("Erro de Conexão", f"Falha na conexão: {e}")
    
    # Dica sobre configuração padrão
    lbl_dica = ctk.CTkLabel(
        frame,
        text="Dica: Para instâncias locais do MySQL, normalmente\nhost='localhost', usuário='root', senha='' (vazia)",
        font=ctk.CTkFont(size=11, slant="italic"),
        justify="left",
        text_color=("gray50", "gray70")
    )
    lbl_dica.pack(pady=(10, 15), anchor="w")
    
    frame_botoes = ctk.CTkFrame(frame, fg_color="transparent")
    frame_botoes.pack(pady=10)
    
    btn_testar = ctk.CTkButton(frame_botoes, text="Testar Conexão", command=testar_conexao)
    btn_testar.grid(row=0, column=0, padx=10, pady=10)
    
    btn_salvar = ctk.CTkButton(
        frame_botoes, 
        text="Salvar e Configurar",
        command=salvar_configuracoes,
        fg_color=("#4a98d3", "#1f538d"),
        hover_color=("#3a7db5", "#174f7c"),
        font=ctk.CTkFont(weight="bold")
    )
    btn_salvar.grid(row=0, column=1, padx=10, pady=10)
    
    # Função para executar o configurador de banco de dados
    def executar_configurador():
        try:
            import subprocess
            subprocess.Popen(["python", "configurar_db.py"], shell=True)
            exibir_mensagem("Iniciando Configurador", "O utilitário de configuração está sendo iniciado.\nPor favor, complete a configuração e depois reinicie este aplicativo.")
        except Exception as e:
            exibir_erro("Erro", f"Não foi possível iniciar o configurador: {e}")
    
    # Botão para abrir o configurador
    btn_abrir_configurador = ctk.CTkButton(
        frame,
        text="Abrir Utilitário de Configuração",
        command=executar_configurador,
        fg_color=("gray70", "gray40"),
        hover_color=("gray60", "gray30"),
        font=ctk.CTkFont(size=12)
    )
    btn_abrir_configurador.pack(pady=(15, 5))

def carregar_configuracoes_db():
    """Carrega as configurações do banco de dados do arquivo config_db.json"""
    global config_db
    try:
        if os.path.exists("config_db.json"):
            with open("config_db.json", "r") as f:
                config_db = json.load(f)
            return True
        else:
            print("Arquivo de configuração config_db.json não encontrado.")
            print("É necessário configurar a conexão com o banco de dados.")
            return False
    except Exception as e:
        print(f"Erro ao carregar configurações: {e}")
        return False

def verificar_login(usuario, senha):
    """Verifica o login do usuário e retorna o resultado"""
    try:
        conexao = criar_conexao_mysql()
        if not conexao:
            return {
                "sucesso": False,
                "mensagem": "Erro de conexão com o banco de dados. Verifique as configurações."
            }
        
        cursor = conexao.cursor(dictionary=True)
        
        # Buscar o usuário pelo nome de usuário
        cursor.execute("SELECT * FROM usuarios WHERE username = %s", (usuario,))
        usuario_encontrado = cursor.fetchone()
        
        if not usuario_encontrado:
            return {
                "sucesso": False,
                "mensagem": "Usuário ou senha incorretos"
            }
        
        # Verificar a senha
        senha_hash = criar_hash_senha(senha)
        if senha_hash == usuario_encontrado["senha_hash"]:
            return {
                "sucesso": True,
                "mensagem": "Login realizado com sucesso",
                "usuario": usuario_encontrado
            }
        else:
            return {
                "sucesso": False,
                "mensagem": "Usuário ou senha incorretos"
            }
    
    except Exception as e:
        return {
            "sucesso": False,
            "mensagem": f"Erro ao verificar login: {e}"
        }
    finally:
        if 'conexao' in locals() and conexao:
            if 'cursor' in locals() and cursor:
                cursor.close()
            conexao.close()

# Funções para carregar as telas
def carregar_tela_login():
    # Fechar janelas abertas
    fechar_janelas_abertas()
    
    # Definir layout da janela de login
    janela.title("Gestão de Pessoas - Login")
    
    # Remover frames existentes
    for widget in janela.winfo_children():
        widget.destroy()
    
    # Garantir que a janela permaneça em tela cheia
    janela.attributes('-fullscreen', True)

    # Frame principal para centralizar o conteúdo
    frame_principal = ctk.CTkFrame(janela)
    frame_principal.pack(fill="both", expand=True)
    
    # Frame para o formulário de login
    frame_login = ctk.CTkFrame(frame_principal, width=350, height=400)
    frame_login.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    
    # Logo ou título
    lbl_titulo = ctk.CTkLabel(
        frame_login,
        text="Gestão de Pessoas",
        font=ctk.CTkFont(size=28, weight="bold"),
        text_color=("#4a98d3", "#1f538d")
    )
    lbl_titulo.pack(pady=(40, 30))
    
    # Formulário de login
    frame_form = ctk.CTkFrame(frame_login, fg_color="transparent")
    frame_form.pack(padx=30, pady=5, fill="both")
    
    # Instruções simplificadas
    if not checar_conexao_mysql():
        lbl_instrucao = ctk.CTkLabel(
            frame_form,
            text="Erro de conexão com o banco de dados. Contacte o administrador do sistema.",
            font=ctk.CTkFont(size=12),
            text_color=("red", "#ff6e6e"),
            wraplength=300,
            justify="center"
        )
        lbl_instrucao.pack(pady=(0, 15))
    
    # Usuário
    lbl_usuario = ctk.CTkLabel(frame_form, text="Usuário:")
    lbl_usuario.pack(anchor="w", pady=(5, 0))
    
    txt_usuario = ctk.CTkEntry(frame_form, width=290, placeholder_text="Digite seu nome de usuário")
    txt_usuario.pack(pady=(0, 15))
    
    # Senha
    lbl_senha = ctk.CTkLabel(frame_form, text="Senha:")
    lbl_senha.pack(anchor="w", pady=(5, 0))
    
    txt_senha = ctk.CTkEntry(frame_form, width=290, show="•", placeholder_text="Digite sua senha")
    txt_senha.pack(pady=(0, 20))
    
    # Configuração para Enter fazer login
    def on_enter(event):
        realizar_login()
        
    txt_usuario.bind("<Return>", on_enter)
    txt_senha.bind("<Return>", on_enter)
    
    # Função para realizar o login
    def realizar_login():
        usuario = txt_usuario.get().strip()
        senha = txt_senha.get()
        
        if not usuario or not senha:
            exibir_erro("Erro", "Por favor, preencha todos os campos")
            return
            
        # Verificar login
        resultado_login = verificar_login(usuario, senha)
        if resultado_login["sucesso"]:
            # Login bem-sucedido
            txt_usuario.delete(0, "end")
            txt_senha.delete(0, "end")
            
            # Carregar a tela principal
            carregar_tela_principal(resultado_login["usuario"])
        else:
            # Login falhou
            exibir_erro("Erro de Login", resultado_login["mensagem"])
    
    # Botão de login
    btn_login = ctk.CTkButton(
        frame_form,
        text="ENTRAR",
        command=realizar_login,
        width=290,
        height=45,
        font=ctk.CTkFont(size=14, weight="bold"),
        fg_color=("#4a98d3", "#1f538d"),
        hover_color=("#3a7db5", "#174f7c")
    )
    btn_login.pack(padx=10, pady=10)
    
    # Vincular tecla Enter
    txt_senha.bind("<Return>", lambda event: realizar_login())
    
    # Colocar foco no campo de usuário
    txt_usuario.focus_set()

def limpar_frame(frame):
    # Limpa todos os widgets do frame
    for widget in frame.winfo_children():
        widget.destroy()

def trocar_aba(aba_para_exibir):
    global frame_atual
    
    for widget in frame_atual.winfo_children():
        if isinstance(widget, ctk.CTkFrame) and widget.winfo_name() in ["aba_home", "aba_funcionarios", "aba_departamentos", "aba_usuarios"]:
            if widget.winfo_name() == aba_para_exibir:
                widget.pack(fill="both", expand=True)
            else:
                widget.pack_forget()

def fechar_janelas_abertas():
    """Fecha todas as janelas abertas"""
    global janelas_abertas
    
    # Fechar todas as janelas abertas
    for nome, janela_aberta in list(janelas_abertas.items()):
        try:
            if janela_aberta is not None and janela_aberta.winfo_exists():
                janela_aberta.destroy()
        except:
            pass
    
    # Limpar o dicionário
    janelas_abertas.clear()

def carregar_tela_principal(usuario):
    """Carrega a tela principal do sistema após o login"""
    global janela, usuario_logado, frame_atual
    
    # Atualizar usuário logado
    usuario_logado = usuario
    
    # Fechar janelas abertas
    fechar_janelas_abertas()
    
    # Configurar janela principal
    janela.title(f"Gestão de Pessoas | Usuário: {usuario['nome']}")
    
    # Garantir que a janela permaneça em tela cheia
    janela.attributes('-fullscreen', True)
    
    # Remover frames existentes
    for widget in janela.winfo_children():
        widget.destroy()
    
    # Criar layout principal com dois frames: sidebar e conteúdo
    frame_principal = ctk.CTkFrame(janela)
    frame_principal.pack(fill="both", expand=True)
    
    # Frame da barra lateral (sidebar)
    sidebar_width = 250
    sidebar = ctk.CTkFrame(frame_principal, width=sidebar_width, corner_radius=0)
    sidebar.pack(side="left", fill="y", padx=0, pady=0)
    sidebar.pack_propagate(False)  # Mantem o tamanho fixo
    
    # Frame de conteúdo com barra superior e inferior
    frame_conteudo_wrapper = ctk.CTkFrame(frame_principal, fg_color="transparent")
    frame_conteudo_wrapper.pack(side="right", fill="both", expand=True)
    
    # Barra superior para o botão de sair
    frame_superior = ctk.CTkFrame(frame_conteudo_wrapper, height=40, fg_color=("gray90", "gray20"))
    frame_superior.pack(fill="x", pady=0)
    
    # Botão de sair no canto superior direito
    def encerrar_sessao():
        """Encerra a sessão e volta para a tela de login"""
        global usuario_logado
        usuario_logado = None
        carregar_tela_login()
    
    btn_sair = ctk.CTkButton(
        frame_superior,
        text="Encerrar Sessão",
        command=encerrar_sessao,
        width=150,
        height=30,
        fg_color=("#ff5a5a", "#992c2c"),
        hover_color=("#ff3030", "#6e1f1f")
    )
    btn_sair.pack(side="right", padx=10, pady=5)
    
    # Frame principal de conteúdo
    frame_conteudo = ctk.CTkFrame(frame_conteudo_wrapper, corner_radius=0, fg_color=("gray95", "gray15"))
    frame_conteudo.pack(fill="both", expand=True)
    frame_atual = frame_conteudo
    
    # Barra inferior para o botão de tema
    frame_inferior = ctk.CTkFrame(frame_conteudo_wrapper, height=40, fg_color=("gray90", "gray20"))
    frame_inferior.pack(fill="x", pady=0)
    
    # Botão de tema no canto inferior direito
    def alternar_tema():
        """Alterna entre tema claro e escuro"""
        if ctk.get_appearance_mode() == "Dark":
            ctk.set_appearance_mode("Light")
        else:
            ctk.set_appearance_mode("Dark")
    
    btn_tema = ctk.CTkButton(
        frame_inferior,
        text="Alternar Tema",
        command=alternar_tema,
        width=120,
        height=30
    )
    btn_tema.pack(side="right", padx=10, pady=5)
    
    # Logotipo ou nome do sistema na sidebar
    frame_logo = ctk.CTkFrame(sidebar, fg_color="transparent")
    frame_logo.pack(fill="x", padx=20, pady=(20, 10))
    
    lbl_logo = ctk.CTkLabel(
        frame_logo, 
        text="Gestão de Pessoas", 
        font=ctk.CTkFont(size=20, weight="bold"),
        text_color=("#4a98d3", "#1f538d")
    )
    lbl_logo.pack(side="left")
    
    # Separador após o logo
    separador1 = ctk.CTkFrame(sidebar, height=1, fg_color=("gray80", "gray30"))
    separador1.pack(fill="x", padx=20, pady=(10, 20))
    
    # Frame para botões da sidebar
    frame_botoes = ctk.CTkFrame(sidebar, fg_color="transparent")
    frame_botoes.pack(fill="x", padx=10, pady=10)
    
    # Função para criar botões da sidebar
    def criar_botao_sidebar(texto, imagem, comando):
        botao = ctk.CTkButton(
            frame_botoes,
            text=texto,
            command=comando,
            height=40,
            anchor="w",
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray75", "gray35"),
            corner_radius=5
        )
        botao.pack(fill="x", padx=5, pady=5)
        return botao
    
    # Funções para carregar diferentes conteúdos
    def carregar_home():
        for widget in frame_conteudo.winfo_children():
            widget.destroy()
        carregar_conteudo_home(frame_conteudo)
    
    def carregar_funcionarios():
        for widget in frame_conteudo.winfo_children():
            widget.destroy()
        carregar_conteudo_funcionarios(frame_conteudo)
    
    def carregar_departamentos():
        for widget in frame_conteudo.winfo_children():
            widget.destroy()
        carregar_conteudo_departamentos(frame_conteudo)
    
    def carregar_usuarios():
        for widget in frame_conteudo.winfo_children():
            widget.destroy()
        carregar_conteudo_usuarios(frame_conteudo)
    
    # Botões da sidebar
    btn_home = criar_botao_sidebar("Dashboard", None, carregar_home)
    btn_funcionarios = criar_botao_sidebar("Funcionários", None, carregar_funcionarios)
    btn_departamentos = criar_botao_sidebar("Departamentos", None, carregar_departamentos)
    
    # Se o usuário for admin, mostrar botão de gerenciar usuários
    if usuario['nivel_acesso'] == 'admin':
        btn_usuarios = criar_botao_sidebar("Usuários", None, carregar_usuarios)
    
    # Informações do usuário na parte inferior da sidebar
    frame_usuario = ctk.CTkFrame(sidebar, fg_color=("gray85", "gray25"))
    frame_usuario.pack(side="bottom", fill="x", padx=10, pady=10)
    
    lbl_usuario_nome = ctk.CTkLabel(
        frame_usuario, 
        text=f"Usuário: {usuario['nome']}",
        font=ctk.CTkFont(size=12, weight="bold")
    )
    lbl_usuario_nome.pack(anchor="w", padx=10, pady=(10, 0))
    
    lbl_usuario_tipo = ctk.CTkLabel(
        frame_usuario, 
        text=f"Nível: {'Administrador' if usuario['nivel_acesso'] == 'admin' else 'Usuário'}",
        font=ctk.CTkFont(size=11)
    )
    lbl_usuario_tipo.pack(anchor="w", padx=10, pady=(0, 10))
    
    # Iniciar com a tela Home
    carregar_home()

# Funções para carregar conteúdo das abas
def carregar_conteudo_home(frame):
    """Carrega o conteúdo da tela inicial"""
    # Limpar frame
    limpar_frame(frame)
    
    # Criar grid para layout
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=0)  # Cabeçalho
    frame.rowconfigure(1, weight=1)  # Conteúdo
    frame.rowconfigure(2, weight=0)  # Rodapé
    
    # Cabeçalho da página
    frame_cabecalho = ctk.CTkFrame(frame, fg_color="transparent")
    frame_cabecalho.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 0))
    
    lbl_titulo = ctk.CTkLabel(
        frame_cabecalho,
        text="Dashboard",
        font=ctk.CTkFont(size=24, weight="bold"),
        text_color=("#4a98d3", "#1f538d")
    )
    lbl_titulo.pack(anchor="w", pady=(0, 5))
    
    lbl_descricao = ctk.CTkLabel(
        frame_cabecalho,
        text="Bem-vindo ao Sistema de Gestão de Pessoas. Utilize o menu lateral para navegar entre as funcionalidades.",
        font=ctk.CTkFont(size=14),
        text_color=("gray40", "gray70")
    )
    lbl_descricao.pack(anchor="w", pady=(0, 10))
    
    separador = ctk.CTkFrame(frame_cabecalho, height=2, fg_color=("gray80", "gray30"))
    separador.pack(fill="x", pady=(0, 10))
    
    # Conteúdo principal
    frame_conteudo = ctk.CTkFrame(frame, fg_color=("gray95", "gray15"))
    frame_conteudo.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
    
    # Configurar grid do conteúdo
    frame_conteudo.columnconfigure(0, weight=1)
    frame_conteudo.columnconfigure(1, weight=1)
    frame_conteudo.rowconfigure(0, weight=1)
    
    # Painel de informações
    frame_info = ctk.CTkFrame(frame_conteudo)
    frame_info.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
    
    lbl_info_titulo = ctk.CTkLabel(
        frame_info,
        text="Informações do Sistema",
        font=ctk.CTkFont(size=18, weight="bold")
    )
    lbl_info_titulo.pack(anchor="w", padx=20, pady=(20, 10))
    
    # Mostrar estatísticas do sistema
    try:
        conexao = criar_conexao_mysql()
        if conexao:
            cursor = conexao.cursor()
            
            # Número de funcionários
            cursor.execute("SELECT COUNT(*) FROM funcionarios")
            num_funcionarios = cursor.fetchone()[0]
            
            # Número de departamentos
            cursor.execute("SELECT COUNT(*) FROM departamentos")
            num_departamentos = cursor.fetchone()[0]
            
            # Número de usuários
            cursor.execute("SELECT COUNT(*) FROM usuarios")
            num_usuarios = cursor.fetchone()[0]
            
            # Frame para mostrar os números
            frame_numeros = ctk.CTkFrame(frame_info, fg_color="transparent")
            frame_numeros.pack(fill="x", padx=20, pady=10)
            
            # Estilos para os cards de estatísticas
            estilo_card = {
                "width": 150,
                "height": 100,
                "corner_radius": 10,
                "border_width": 1,
                "border_color": ("gray80", "gray30"),
                "fg_color": ("white", "gray20")
            }
            
            estilo_numero = ctk.CTkFont(size=32, weight="bold")
            estilo_legenda = ctk.CTkFont(size=14)
            
            # Card de funcionários
            card_funcionarios = ctk.CTkFrame(frame_numeros, **estilo_card)
            card_funcionarios.pack(side="left", padx=10, pady=10)
            
            lbl_num_funcionarios = ctk.CTkLabel(
                card_funcionarios,
                text=str(num_funcionarios),
                font=estilo_numero,
                text_color=("#4a98d3", "#1f538d")
            )
            lbl_num_funcionarios.pack(pady=(15, 5))
            
            lbl_funcionarios = ctk.CTkLabel(
                card_funcionarios,
                text="Funcionários",
                font=estilo_legenda
            )
            lbl_funcionarios.pack()
            
            # Card de departamentos
            card_departamentos = ctk.CTkFrame(frame_numeros, **estilo_card)
            card_departamentos.pack(side="left", padx=10, pady=10)
            
            lbl_num_departamentos = ctk.CTkLabel(
                card_departamentos,
                text=str(num_departamentos),
                font=estilo_numero,
                text_color=("#4a98d3", "#1f538d")
            )
            lbl_num_departamentos.pack(pady=(15, 5))
            
            lbl_departamentos = ctk.CTkLabel(
                card_departamentos,
                text="Departamentos",
                font=estilo_legenda
            )
            lbl_departamentos.pack()
            
            # Card de usuários (apenas para admins)
            if usuario_logado and usuario_logado.get('nivel_acesso') == 'admin':
                card_usuarios = ctk.CTkFrame(frame_numeros, **estilo_card)
                card_usuarios.pack(side="left", padx=10, pady=10)
                
                lbl_num_usuarios = ctk.CTkLabel(
                    card_usuarios,
                    text=str(num_usuarios),
                    font=estilo_numero,
                    text_color=("#4a98d3", "#1f538d")
                )
                lbl_num_usuarios.pack(pady=(15, 5))
                
                lbl_usuarios = ctk.CTkLabel(
                    card_usuarios,
                    text="Usuários",
                    font=estilo_legenda
                )
                lbl_usuarios.pack()
            
            cursor.close()
            conexao.close()
    except Exception as e:
        print(f"Erro ao buscar estatísticas: {e}")
        lbl_erro = ctk.CTkLabel(
            frame_info,
            text=f"Erro ao carregar estatísticas: {e}",
            text_color=("red", "#ff6e6e")
        )
        lbl_erro.pack(padx=20, pady=10)
    
    # Painel de atividades recentes
    frame_atividades = ctk.CTkFrame(frame_conteudo)
    frame_atividades.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
    
    lbl_atividades_titulo = ctk.CTkLabel(
        frame_atividades,
        text="Guia Rápido",
        font=ctk.CTkFont(size=18, weight="bold")
    )
    lbl_atividades_titulo.pack(anchor="w", padx=20, pady=(20, 10))
    
    # Lista de instruções
    frame_instrucoes = ctk.CTkFrame(frame_atividades, fg_color="transparent")
    frame_instrucoes.pack(fill="both", expand=True, padx=20, pady=10)
    
    instrucoes = [
        ("Funcionários", "Cadastre e gerencie os funcionários da empresa."),
        ("Departamentos", "Organize sua empresa criando departamentos."),
        ("Usuários", "Gerencie os usuários que têm acesso ao sistema (somente admins)."),
        ("Tema", "Alterne entre o tema claro e escuro conforme sua preferência.")
    ]
    
    for i, (titulo, descricao) in enumerate(instrucoes):
        frame_item = ctk.CTkFrame(frame_instrucoes)
        frame_item.pack(fill="x", padx=5, pady=5)
        
        lbl_numero = ctk.CTkLabel(
            frame_item,
            text=f"{i+1}",
            width=30,
            height=30,
            fg_color=("#4a98d3", "#1f538d"),
            corner_radius=15,
            text_color=("white", "white")
        )
        lbl_numero.pack(side="left", padx=(10, 15), pady=10)
        
        frame_texto = ctk.CTkFrame(frame_item, fg_color="transparent")
        frame_texto.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=10)
        
        lbl_item_titulo = ctk.CTkLabel(
            frame_texto,
            text=titulo,
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        lbl_item_titulo.pack(anchor="w")
        
        lbl_item_descricao = ctk.CTkLabel(
            frame_texto,
            text=descricao,
            font=ctk.CTkFont(size=12),
            anchor="w",
            justify="left"
        )
        lbl_item_descricao.pack(anchor="w")
    
    # Rodapé
    frame_rodape = ctk.CTkFrame(frame, height=30, fg_color="transparent")
    frame_rodape.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
    
    lbl_copyright = ctk.CTkLabel(
        frame_rodape,
        text="© 2025 ThTweaks - Sistema de Gestão. Todos os direitos reservados.",
        font=ctk.CTkFont(size=10),
        text_color=("gray40", "gray70")
    )
    lbl_copyright.pack(side="right")

def criar_card_estatistica(frame, row, column, titulo, valor, cor_fundo):
    card = ctk.CTkFrame(frame, fg_color=cor_fundo)
    card.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")
    
    lbl_titulo = ctk.CTkLabel(
        card,
        text=titulo,
        font=ctk.CTkFont(size=14, weight="bold"),
        text_color="white"
    )
    lbl_titulo.pack(padx=20, pady=(20, 10))
    
    lbl_valor = ctk.CTkLabel(
        card,
        text=valor,
        font=ctk.CTkFont(size=24, weight="bold"),
        text_color="white"
    )
    lbl_valor.pack(padx=20, pady=(10, 20))
    
    # Configurar tamanho mínimo para o card
    card.configure(width=200, height=120)
    card.pack_propagate(False)

def carregar_conteudo_funcionarios(frame):
    # Limpar o frame
    limpar_frame(frame)
    
    # Criação da grid principal
    frame.grid_columnconfigure(0, weight=1)  # Coluna de cadastro
    frame.grid_columnconfigure(1, weight=2)  # Coluna de listagem
    
    # Frame de cadastro de funcionário
    frame_cadastro = ctk.CTkFrame(frame)
    frame_cadastro.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
    
    # Título do cadastro
    lbl_titulo_cadastro = ctk.CTkLabel(
        frame_cadastro,
        text="Cadastro de Funcionário",
        font=ctk.CTkFont(size=18, weight="bold"),
        text_color=("#4a98d3", "#1f538d")
    )
    lbl_titulo_cadastro.pack(padx=20, pady=(20, 20))
    
    # Ajuda para cadastro
    lbl_ajuda = ctk.CTkLabel(
        frame_cadastro,
        text="Preencha os dados abaixo para cadastrar um novo funcionário.",
        font=ctk.CTkFont(size=12),
        justify="left"
    )
    lbl_ajuda.pack(anchor="w", padx=20, pady=(0, 10))
    
    # Campos de cadastro
    # Nome
    lbl_nome = ctk.CTkLabel(frame_cadastro, text="Nome:")
    lbl_nome.pack(anchor="w", padx=20, pady=(10, 0))
    
    txt_nome = ctk.CTkEntry(frame_cadastro, width=300)
    txt_nome.pack(padx=20, pady=(0, 10))
    
    # Email
    lbl_email = ctk.CTkLabel(frame_cadastro, text="Email:")
    lbl_email.pack(anchor="w", padx=20, pady=(10, 0))
    
    txt_email = ctk.CTkEntry(frame_cadastro, width=300)
    txt_email.pack(padx=20, pady=(0, 10))
    
    # Data de Nascimento
    lbl_data_nascimento = ctk.CTkLabel(frame_cadastro, text="Data de Nascimento (DD/MM/AAAA):")
    lbl_data_nascimento.pack(anchor="w", padx=20, pady=(10, 0))
    
    txt_data_nascimento = ctk.CTkEntry(frame_cadastro, width=300)
    txt_data_nascimento.pack(padx=20, pady=(0, 10))
    
    # Cargo
    lbl_cargo = ctk.CTkLabel(frame_cadastro, text="Cargo:")
    lbl_cargo.pack(anchor="w", padx=20, pady=(10, 0))
    
    txt_cargo = ctk.CTkEntry(frame_cadastro, width=300)
    txt_cargo.pack(padx=20, pady=(0, 10))
    
    # Salário
    lbl_salario = ctk.CTkLabel(frame_cadastro, text="Salário (R$):")
    lbl_salario.pack(anchor="w", padx=20, pady=(10, 0))
    
    txt_salario = ctk.CTkEntry(frame_cadastro, width=300)
    txt_salario.pack(padx=20, pady=(0, 10))
    
    # Observações
    lbl_observacoes = ctk.CTkLabel(frame_cadastro, text="Observações:")
    lbl_observacoes.pack(anchor="w", padx=20, pady=(10, 0))
    
    txt_observacoes = ctk.CTkTextbox(frame_cadastro, width=300, height=80)
    txt_observacoes.pack(padx=20, pady=(0, 10))
    
    # Departamento (dropdown)
    lbl_departamento = ctk.CTkLabel(frame_cadastro, text="Departamento:")
    lbl_departamento.pack(anchor="w", padx=20, pady=(10, 0))
    
    # Buscar departamentos para o dropdown
    departamentos = buscar_departamentos()
    
    departamento_var = ctk.StringVar(value="")
    opcoes_departamento = [nome for _, nome in departamentos]
    if opcoes_departamento:
        departamento_var.set(opcoes_departamento[0])
    else:
        # Adiciona uma opção padrão se não houver departamentos
        opcoes_departamento = ["Nenhum departamento disponível"]
        departamento_var.set(opcoes_departamento[0])
    
    dropdown_departamento = ctk.CTkOptionMenu(
        frame_cadastro, 
        variable=departamento_var,
        values=opcoes_departamento,
        width=300
    )
    dropdown_departamento.pack(padx=20, pady=(0, 20))
    
    # Função para adicionar funcionário
    def adicionar_funcionario():
        # Validar campos
        nome = txt_nome.get().strip()
        email = txt_email.get().strip()
        data_nascimento_br = txt_data_nascimento.get().strip()
        cargo = txt_cargo.get().strip()
        salario_str = txt_salario.get().strip().replace(',', '.')
        observacoes = txt_observacoes.get("0.0", "end").strip()
        departamento_nome = departamento_var.get()
        
        # Validação básica
        if not nome:
            exibir_erro("Erro", "O nome é obrigatório")
            return
        
        if not email or '@' not in email:
            exibir_erro("Erro", "O email é inválido")
            return
        
        # Validar data de nascimento
        if not data_nascimento_br:
            exibir_erro("Erro", "A data de nascimento é obrigatória")
            return
        
        # Converter data para formato do banco
        data_nascimento = converter_data_para_banco(data_nascimento_br)
        if not data_nascimento:
            exibir_erro("Erro", "Data de nascimento inválida. Use o formato DD/MM/AAAA")
            return
        
        # Validar salário
        try:
            salario = float(salario_str)
            if salario <= 0:
                exibir_erro("Erro", "Salário deve ser maior que zero")
                return
        except ValueError:
            exibir_erro("Erro", "Salário inválido")
            return
        
        # Validar departamento
        if departamento_nome == "Nenhum departamento disponível":
            exibir_erro("Erro", "Nenhum departamento disponível. Cadastre um departamento primeiro.")
            return
        
        # Buscar ID do departamento
        departamento_id = None
        for dep_id, dep_nome in departamentos:
            if dep_nome == departamento_nome:
                departamento_id = dep_id
                break
        
        if not departamento_id:
            exibir_erro("Erro", "Departamento não encontrado")
            return
        
        try:
            conexao = criar_conexao_mysql()
            if conexao:
                cursor = conexao.cursor()
                
                # Verificar se já existe um funcionário com este email
                cursor.execute("SELECT COUNT(*) FROM funcionarios WHERE email = %s", (email,))
                if cursor.fetchone()[0] > 0:
                    exibir_erro("Erro", "Já existe um funcionário com este email")
                    return
                
                # Inserir funcionário
                cursor.execute("""
                    INSERT INTO funcionarios (nome, email, data_nascimento, cargo, salario, observacoes, departamento_id) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (nome, email, data_nascimento, cargo, salario, observacoes, departamento_id))
                
                conexao.commit()
                exibir_mensagem("Sucesso", "Funcionário cadastrado com sucesso!")
                
                # Limpar campos após o cadastro
                txt_nome.delete(0, 'end')
                txt_email.delete(0, 'end')
                txt_data_nascimento.delete(0, 'end')
                txt_cargo.delete(0, 'end')
                txt_salario.delete(0, 'end')
                txt_observacoes.delete("0.0", "end")
                
                # Atualizar tabela de funcionários
                listar_funcionarios(tv_funcionarios)
                
                cursor.close()
                conexao.close()
        except Exception as e:
            exibir_erro("Erro", f"Erro ao cadastrar funcionário: {e}")
    
    # Botões de ação
    frame_botoes = ctk.CTkFrame(frame_cadastro, fg_color="transparent")
    frame_botoes.pack(pady=20)
    
    # Botão de adicionar com destaque
    btn_adicionar = ctk.CTkButton(
        frame_botoes,
        text="CADASTRAR FUNCIONÁRIO",
        command=adicionar_funcionario,
        width=250,
        height=50,
        font=ctk.CTkFont(size=14, weight="bold"),
        fg_color=("#4a98d3", "#1f538d"),
        hover_color=("#3a7db5", "#174f7c")
    )
    btn_adicionar.grid(row=0, column=0, padx=10)
    
    def limpar_campos():
        txt_nome.delete(0, 'end')
        txt_email.delete(0, 'end')
        txt_data_nascimento.delete(0, 'end')
        txt_cargo.delete(0, 'end')
        txt_salario.delete(0, 'end')
        txt_observacoes.delete("0.0", "end")
    
    btn_limpar = ctk.CTkButton(
        frame_botoes,
        text="Limpar Campos",
        command=limpar_campos,
        fg_color="gray60",
        hover_color="gray40",
        width=150,
        height=50
    )
    btn_limpar.grid(row=0, column=1, padx=10)
    
    # Frame para listagem de funcionários
    frame_listagem = ctk.CTkFrame(frame)
    frame_listagem.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
    
    lbl_titulo_listagem = ctk.CTkLabel(
        frame_listagem,
        text="Funcionários Cadastrados",
        font=ctk.CTkFont(size=16, weight="bold")
    )
    lbl_titulo_listagem.pack(padx=20, pady=20)
    
    # Campo de busca
    frame_busca = ctk.CTkFrame(frame_listagem, fg_color="transparent")
    frame_busca.pack(fill="x", padx=20, pady=(0, 10))
    
    lbl_buscar = ctk.CTkLabel(frame_busca, text="Buscar:")
    lbl_buscar.pack(side="left", padx=(0, 10))
    
    txt_buscar = ctk.CTkEntry(frame_busca, width=200)
    txt_buscar.pack(side="left", padx=(0, 10))
    
    def buscar_funcionarios():
        termo_busca = txt_buscar.get().strip()
        listar_funcionarios(tv_funcionarios, termo_busca)
    
    btn_buscar = ctk.CTkButton(
        frame_busca,
        text="Buscar",
        command=buscar_funcionarios,
        width=100
    )
    btn_buscar.pack(side="left")
    
    # Criar treeview para listagem de funcionários
    frame_tabela = ctk.CTkFrame(frame_listagem)
    frame_tabela.pack(fill="both", expand=True, padx=20, pady=(10, 20))
    
    style = ttk.Style()
    style.configure("Treeview", font=('Arial', 10))
    style.configure("Treeview.Heading", font=('Arial', 10, 'bold'))
    
    # Configurar cores baseadas no tema atual
    if ctk.get_appearance_mode() == "Dark":
        style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b")
        style.map('Treeview', background=[('selected', '#3a7ebf')])
    
    # Scrollbar para a tabela
    scrollbar = ttk.Scrollbar(frame_tabela)
    scrollbar.pack(side="right", fill="y")
    
    # Treeview
    colunas = ("id", "nome", "email", "departamento", "data_nascimento", "salario")
    tv_funcionarios = ttk.Treeview(
        frame_tabela,
        columns=colunas,
        show="headings",
        height=15,
        yscrollcommand=scrollbar.set
    )
    
    # Configura as colunas
    tv_funcionarios.column("id", width=40)
    tv_funcionarios.column("nome", width=160)
    tv_funcionarios.column("email", width=180)
    tv_funcionarios.column("departamento", width=120)
    tv_funcionarios.column("data_nascimento", width=120)
    tv_funcionarios.column("salario", width=80)
    
    # Configura os cabeçalhos
    tv_funcionarios.heading("id", text="ID")
    tv_funcionarios.heading("nome", text="Nome")
    tv_funcionarios.heading("email", text="Email")
    tv_funcionarios.heading("departamento", text="Departamento")
    tv_funcionarios.heading("data_nascimento", text="Data Nasc.")
    tv_funcionarios.heading("salario", text="Salário")
    
    tv_funcionarios.pack(fill="both", expand=True)
    scrollbar.config(command=tv_funcionarios.yview)
    
    # Carregar funcionários
    listar_funcionarios(tv_funcionarios)
    
    # Instrução de uso do clique direito
    lbl_dica = ctk.CTkLabel(
        frame_listagem,
        text="* Clique com o botão direito em um funcionário para ver opções adicionais",
        font=ctk.CTkFont(size=10, slant="italic"),
        text_color=("gray40", "gray70")
    )
    lbl_dica.pack(pady=(0, 10), anchor="e", padx=20)
    
    # Menu de contexto para a tabela
    menu_contexto = tk.Menu(tv_funcionarios, tearoff=0)
    
    def menu_popup(event):
        # Selecionar item clicado
        item = tv_funcionarios.identify_row(event.y)
        if item:
            tv_funcionarios.selection_set(item)
            menu_contexto.post(event.x_root, event.y_root)
    
    tv_funcionarios.bind("<Button-3>", menu_popup)
    
    def excluir_funcionario():
        selecionado = tv_funcionarios.selection()
        if not selecionado:
            exibir_erro("Erro", "Selecione um funcionário para excluir")
            return
        
        funcionario_id = tv_funcionarios.item(selecionado, "values")[0]
        nome_funcionario = tv_funcionarios.item(selecionado, "values")[1]
        
        # Confirmar exclusão
        if not messagebox.askyesno("Confirmação", f"Deseja realmente excluir o funcionário '{nome_funcionario}'?"):
            return
        
        try:
            conexao = criar_conexao_mysql()
            if conexao:
                cursor = conexao.cursor()
                # Converter o ID para inteiro para evitar o erro de tipo DOUBLE
                # O erro "Truncated incorrect DOUBLE value" ocorre quando tentamos
                # usar um valor não numérico como um número na query SQL
                try:
                    funcionario_id = int(funcionario_id)
                except ValueError:
                    exibir_erro("Erro", "ID do funcionário inválido")
                    return
                
                cursor.execute("DELETE FROM funcionarios WHERE id = %s", (funcionario_id,))
                conexao.commit()
                cursor.close()
                conexao.close()
                
                # Atualizar tabela
                listar_funcionarios(tv_funcionarios)
                exibir_mensagem("Sucesso", "Funcionário excluído com sucesso!")
        except Exception as e:
            exibir_erro("Erro", f"Erro ao excluir funcionário: {e}")
    
    def editar_funcionario_selecionado():
        selecionado = tv_funcionarios.selection()
        if not selecionado:
            exibir_erro("Erro", "Selecione um funcionário para editar")
            return
        
        funcionario_id = tv_funcionarios.item(selecionado, "values")[0]
        try:
            funcionario_id = int(funcionario_id)
            editar_funcionario(funcionario_id, tv_funcionarios)
        except ValueError:
            exibir_erro("Erro", "ID do funcionário inválido")
    
    menu_contexto.add_command(label="Editar", command=editar_funcionario_selecionado)
    menu_contexto.add_command(label="Excluir", command=excluir_funcionario)
    
    # Adicionar evento para atualização quando o tema for alterado
    def atualizar_cores_tabela(event=None):
        if ctk.get_appearance_mode() == "Dark":
            style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b")
        else:
            style.configure("Treeview", background="white", foreground="black", fieldbackground="white")
    
    frame.bind("<Configure>", atualizar_cores_tabela)

def listar_funcionarios(treeview, termo_busca=""):
    """
    Lista os funcionários no treeview, opcionalmente filtrando por um termo de busca.
    
    Args:
        treeview: O widget Treeview onde os funcionários serão exibidos
        termo_busca: Termo opcional para filtrar os funcionários
    """
    # Limpar itens existentes
    for item in treeview.get_children():
        treeview.delete(item)
    
    try:
        conexao = criar_conexao_mysql()
        if not conexao:
            print("Não foi possível conectar ao banco de dados")
            return
            
        cursor = conexao.cursor()
        
        # Query base modificada para buscar funcionários usando apenas colunas existentes
        query = """
            SELECT f.id, f.nome, f.email, 
                   d.nome as departamento, 
                   f.data_nascimento, 
                   f.salario,
                   f.cargo
            FROM funcionarios f
            LEFT JOIN departamentos d ON f.departamento_id = d.id
        """
        
        # Adicionar filtro de busca se necessário
        params = ()
        if termo_busca:
            query += """ WHERE f.nome LIKE %s OR f.email LIKE %s OR d.nome LIKE %s OR f.cargo LIKE %s"""
            termo_busca = f"%{termo_busca}%"
            params = (termo_busca, termo_busca, termo_busca, termo_busca)
        
        query += " ORDER BY f.nome"
        
        cursor.execute(query, params)
        
        # Inserir dados na tabela
        for row in cursor.fetchall():
            # Ajustar o formato dos dados para exibição
            id, nome, email, departamento, data_nascimento, salario, cargo = row
            
            # Converter data para o formato brasileiro
            data_formatada = converter_data_para_exibicao(data_nascimento)
            
            # Preparar os valores para as colunas do treeview
            valores = (id, nome, email, departamento, 
                      data_formatada, 
                      f"R$ {salario}" if salario else "")
                      
            treeview.insert("", "end", values=valores)
        
        cursor.close()
        conexao.close()
    except Exception as e:
        print(f"Erro ao listar funcionários: {e}")
        # Mostrar ao usuário que ocorreu um erro
        treeview.insert("", "end", values=("Erro", f"Não foi possível carregar os funcionários", "", "", "", ""))

def buscar_departamentos():
    """
    Busca todos os departamentos cadastrados no banco de dados.
    
    Returns:
        list: Lista de tuplas (id, nome) dos departamentos encontrados
    """
    departamentos = []
    try:
        conexao = criar_conexao_mysql()
        if not conexao:
            print("Não foi possível conectar ao banco de dados")
            return departamentos
            
        cursor = conexao.cursor()
        cursor.execute("SELECT id, nome FROM departamentos ORDER BY nome")
        departamentos = [(str(id), nome) for id, nome in cursor.fetchall()]
        cursor.close()
        conexao.close()
    except Exception as e:
        print(f"Erro ao carregar departamentos: {e}")
    
    return departamentos

def listar_departamentos(treeview, termo_busca=""):
    """
    Lista os departamentos no treeview, opcionalmente filtrando por um termo de busca.
    
    Args:
        treeview: O widget Treeview onde os departamentos serão exibidos
        termo_busca: Termo opcional para filtrar os departamentos
    """
    # Limpar itens existentes
    for item in treeview.get_children():
        treeview.delete(item)
    
    try:
        conexao = criar_conexao_mysql()
        if not conexao:
            print("Não foi possível conectar ao banco de dados")
            return
            
        cursor = conexao.cursor()
        
        # Query base para buscar departamentos e contar funcionários em cada um
        query = """
            SELECT d.id, d.nome, d.descricao, 
                   (SELECT COUNT(*) FROM funcionarios f WHERE f.departamento_id = d.id) as num_funcionarios
            FROM departamentos d
        """
        
        # Adicionar filtro de busca se necessário
        params = ()
        if termo_busca:
            query += " WHERE d.nome LIKE %s OR d.descricao LIKE %s"
            termo_busca = f"%{termo_busca}%"
            params = (termo_busca, termo_busca)
        
        query += " ORDER BY d.nome"
        
        cursor.execute(query, params)
        
        # Inserir dados na tabela
        for row in cursor.fetchall():
            treeview.insert("", "end", values=row)
        
        cursor.close()
        conexao.close()
    except Exception as e:
        print(f"Erro ao listar departamentos: {e}")
        # Mostrar ao usuário que ocorreu um erro
        treeview.insert("", "end", values=("Erro", f"Não foi possível carregar os departamentos", "", ""))

def carregar_conteudo_departamentos(frame):
    """
    Carrega o conteúdo da página de departamentos, incluindo formulário de cadastro
    e lista de departamentos existentes.
    
    Args:
        frame: O frame onde o conteúdo será carregado
    """
    # Limpar o frame
    limpar_frame(frame)
    
    # Criar grid para conteúdo
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_columnconfigure(1, weight=1)
    
    # Criar frame para cadastro de departamento
    frame_cadastro = ctk.CTkFrame(frame)
    frame_cadastro.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
    
    lbl_titulo_cadastro = ctk.CTkLabel(
        frame_cadastro,
        text="Cadastro de Departamento",
        font=ctk.CTkFont(size=18, weight="bold"),
        text_color=("#4a98d3", "#1f538d")
    )
    lbl_titulo_cadastro.pack(padx=20, pady=(20, 20))
    
    # Ajuda para cadastro
    lbl_ajuda = ctk.CTkLabel(
        frame_cadastro,
        text="Preencha os dados abaixo para cadastrar um novo departamento.",
        font=ctk.CTkFont(size=12),
        justify="left"
    )
    lbl_ajuda.pack(anchor="w", padx=20, pady=(0, 10))
    
    # Campos de cadastro
    # Nome
    lbl_nome = ctk.CTkLabel(frame_cadastro, text="Nome:")
    lbl_nome.pack(anchor="w", padx=20, pady=(10, 0))
    
    txt_nome = ctk.CTkEntry(frame_cadastro, width=300)
    txt_nome.pack(padx=20, pady=(0, 10))
    
    # Descrição
    lbl_descricao = ctk.CTkLabel(frame_cadastro, text="Descrição:")
    lbl_descricao.pack(anchor="w", padx=20, pady=(10, 0))
    
    txt_descricao = ctk.CTkTextbox(frame_cadastro, width=300, height=100)
    txt_descricao.pack(padx=20, pady=(0, 10))
    
    # Função para adicionar departamento
    def adicionar_departamento():
        # Validar campos
        nome = txt_nome.get().strip()
        descricao = txt_descricao.get("0.0", "end").strip()
        
        # Validação básica
        if not nome:
            exibir_erro("Erro", "O nome é obrigatório")
            return
        
        try:
            conexao = criar_conexao_mysql()
            if not conexao:
                exibir_erro("Erro", "Não foi possível conectar ao banco de dados")
                return
                
            cursor = conexao.cursor()
            
            # Verificar se já existe um departamento com este nome
            cursor.execute("SELECT COUNT(*) FROM departamentos WHERE nome = %s", (nome,))
            if cursor.fetchone()[0] > 0:
                exibir_erro("Erro", "Já existe um departamento com este nome")
                return
            
            # Inserir departamento
            cursor.execute("""
                INSERT INTO departamentos (nome, descricao) 
                VALUES (%s, %s)
            """, (nome, descricao))
            
            conexao.commit()
            exibir_mensagem("Sucesso", "Departamento cadastrado com sucesso!")
            
            # Limpar campos após o cadastro
            txt_nome.delete(0, 'end')
            txt_descricao.delete("0.0", "end")
            
            # Atualizar tabela de departamentos
            listar_departamentos(tv_departamentos)
            
            cursor.close()
            conexao.close()
        except Exception as e:
            exibir_erro("Erro", f"Erro ao cadastrar departamento: {e}")
    
    # Botões
    frame_botoes = ctk.CTkFrame(frame_cadastro, fg_color="transparent")
    frame_botoes.pack(pady=20)
    
    # Botão de adicionar com destaque
    btn_adicionar = ctk.CTkButton(
        frame_botoes,
        text="CADASTRAR DEPARTAMENTO",
        command=adicionar_departamento,
        width=250,
        height=50,
        font=ctk.CTkFont(size=14, weight="bold"),
        fg_color=("#4a98d3", "#1f538d"),
        hover_color=("#3a7db5", "#174f7c")
    )
    btn_adicionar.grid(row=0, column=0, padx=10)
    
    def limpar_campos():
        txt_nome.delete(0, 'end')
        txt_descricao.delete("0.0", "end")
    
    btn_limpar = ctk.CTkButton(
        frame_botoes,
        text="Limpar Campos",
        command=limpar_campos,
        fg_color="gray60",
        hover_color="gray40",
        width=150,
        height=50
    )
    btn_limpar.grid(row=0, column=1, padx=10)
    
    # Frame para listagem de departamentos
    frame_listagem = ctk.CTkFrame(frame)
    frame_listagem.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
    
    lbl_titulo_listagem = ctk.CTkLabel(
        frame_listagem,
        text="Departamentos Cadastrados",
        font=ctk.CTkFont(size=16, weight="bold")
    )
    lbl_titulo_listagem.pack(padx=20, pady=20)
    
    # Campo de busca
    frame_busca = ctk.CTkFrame(frame_listagem, fg_color="transparent")
    frame_busca.pack(fill="x", padx=20, pady=(0, 10))
    
    lbl_buscar = ctk.CTkLabel(frame_busca, text="Buscar:")
    lbl_buscar.pack(side="left", padx=(0, 10))
    
    txt_buscar = ctk.CTkEntry(frame_busca, width=200)
    txt_buscar.pack(side="left", padx=(0, 10))
    
    def buscar_departamentos_local():
        termo_busca = txt_buscar.get().strip()
        listar_departamentos(tv_departamentos, termo_busca)
    
    btn_buscar = ctk.CTkButton(
        frame_busca,
        text="Buscar",
        command=buscar_departamentos_local,
        width=100
    )
    btn_buscar.pack(side="left")
    
    # Criar treeview para listagem de departamentos
    frame_tabela = ctk.CTkFrame(frame_listagem)
    frame_tabela.pack(fill="both", expand=True, padx=20, pady=(10, 20))
    
    style = ttk.Style()
    style.configure("Treeview", font=('Arial', 10))
    style.configure("Treeview.Heading", font=('Arial', 10, 'bold'))
    
    # Configurar cores baseadas no tema atual
    if ctk.get_appearance_mode() == "Dark":
        style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b")
        style.map('Treeview', background=[('selected', '#3a7ebf')])
    
    # Scrollbar para a tabela
    scrollbar = ttk.Scrollbar(frame_tabela)
    scrollbar.pack(side="right", fill="y")
    
    # Treeview
    colunas = ("id", "nome", "descricao", "num_funcionarios")
    tv_departamentos = ttk.Treeview(
        frame_tabela,
        columns=colunas,
        show="headings",
        height=15,
        yscrollcommand=scrollbar.set
    )
    
    # Configura as colunas
    tv_departamentos.column("id", width=40)
    tv_departamentos.column("nome", width=150)
    tv_departamentos.column("descricao", width=250)
    tv_departamentos.column("num_funcionarios", width=100)
    
    # Configura os cabeçalhos
    tv_departamentos.heading("id", text="ID")
    tv_departamentos.heading("nome", text="Nome")
    tv_departamentos.heading("descricao", text="Descrição")
    tv_departamentos.heading("num_funcionarios", text="Funcionários")
    
    tv_departamentos.pack(fill="both", expand=True)
    scrollbar.config(command=tv_departamentos.yview)
    
    # Carregar departamentos
    listar_departamentos(tv_departamentos)
    
    # Instrução de uso do clique direito
    lbl_dica = ctk.CTkLabel(
        frame_listagem,
        text="* Clique com o botão direito em um departamento para ver opções adicionais",
        font=ctk.CTkFont(size=10, slant="italic"),
        text_color=("gray40", "gray70")
    )
    lbl_dica.pack(pady=(0, 10), anchor="e", padx=20)
    
    # Menu de contexto para a tabela
    menu_contexto = tk.Menu(tv_departamentos, tearoff=0)
    
    def menu_popup(event):
        # Selecionar item clicado
        item = tv_departamentos.identify_row(event.y)
        if item:
            tv_departamentos.selection_set(item)
            menu_contexto.post(event.x_root, event.y_root)
    
    tv_departamentos.bind("<Button-3>", menu_popup)
    
    def excluir_departamento():
        selecionado = tv_departamentos.selection()
        if not selecionado:
            exibir_erro("Erro", "Selecione um departamento para excluir")
            return
        
        valores = tv_departamentos.item(selecionado, "values")
        departamento_id = valores[0]
        departamento_nome = valores[1]
        num_funcionarios = int(valores[3])
        
        # Não permitir excluir departamento com funcionários
        if num_funcionarios > 0:
            exibir_erro("Erro", f"Não é possível excluir o departamento '{departamento_nome}' pois ele possui {num_funcionarios} funcionário(s) associado(s).")
            return
        
        # Confirmar exclusão
        if not messagebox.askyesno("Confirmação", f"Deseja realmente excluir o departamento '{departamento_nome}'?"):
            return
        
        try:
            conexao = criar_conexao_mysql()
            if conexao:
                cursor = conexao.cursor()
                
                # Excluir departamento
                cursor.execute("DELETE FROM departamentos WHERE id = %s", (departamento_id,))
                conexao.commit()
                cursor.close()
                conexao.close()
                
                # Atualizar tabela
                listar_departamentos(tv_departamentos)
                exibir_mensagem("Sucesso", "Departamento excluído com sucesso!")
        except Exception as e:
            exibir_erro("Erro", f"Erro ao excluir departamento: {e}")
    
    def editar_departamento_selecionado():
        selecionado = tv_departamentos.selection()
        if not selecionado:
            exibir_erro("Erro", "Selecione um departamento para editar")
            return
        
        departamento_id = tv_departamentos.item(selecionado, "values")[0]
        try:
            departamento_id = int(departamento_id)
            editar_departamento(departamento_id, tv_departamentos)
        except ValueError:
            exibir_erro("Erro", "ID do departamento inválido")
    
    menu_contexto.add_command(label="Editar", command=editar_departamento_selecionado)
    menu_contexto.add_command(label="Excluir", command=excluir_departamento)
    
    # Adicionar evento para atualização quando o tema for alterado
    def atualizar_cores_tabela(event=None):
        if ctk.get_appearance_mode() == "Dark":
            style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b")
        else:
            style.configure("Treeview", background="white", foreground="black", fieldbackground="white")
    
    frame.bind("<Configure>", atualizar_cores_tabela)

def listar_usuarios(treeview):
    # Limpar dados existentes
    for item in treeview.get_children():
        treeview.delete(item)
    
    try:
        conexao = criar_conexao_mysql()
        if conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT id, nome, username, nivel_acesso FROM usuarios
                ORDER BY nome
            """)
            
            # Inserir dados na tabela
            for linha in cursor.fetchall():
                treeview.insert("", "end", values=linha)
            
            cursor.close()
            conexao.close()
    except Exception as e:
        print(f"Erro ao listar usuários: {e}")

def configurar_banco_de_dados():
    """Verifica se as tabelas necessárias já existem no banco de dados, sem tentar criá-las"""
    try:
        # Verificar se a conexão funciona com as configurações atuais
        conexao = criar_conexao_mysql()
        if not conexao:
            print("Configuração do MySQL necessária")
            return False
        
        cursor = conexao.cursor()
        print("Verificando tabelas do banco de dados...")
        print("NOTA: Este aplicativo não cria tabelas, apenas verifica sua existência.")
        
        # Verificar se as tabelas existem
        tabelas_necessarias = ['usuarios', 'departamentos', 'funcionarios']
        tabelas_ausentes = []
        
        # Verificar tabelas existentes no banco
        cursor.execute("SHOW TABLES")
        tabelas_existentes = [tabela[0] for tabela in cursor.fetchall()]
        
        for tabela in tabelas_necessarias:
            if tabela not in tabelas_existentes:
                tabelas_ausentes.append(tabela)
        
        if tabelas_ausentes:
            print(f"Tabelas ausentes no banco: {', '.join(tabelas_ausentes)}")
            print("IMPORTANTE: Este aplicativo (app_miro.py) não cria tabelas automaticamente.")
            print("Execute o utilitário 'configurar_db.py' para criar as tabelas necessárias.")
            cursor.close()
            conexao.close()
            return False
        
        # Verificar se há um usuário admin
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE nivel_acesso = 'admin'")
        if cursor.fetchone()[0] == 0:
            print("Nenhum usuário administrador encontrado.")
            print("Execute o utilitário 'configurar_db.py' para criar um usuário administrador.")
            cursor.close()
            conexao.close()
            return False
        
        cursor.close()
        conexao.close()
        print("Verificação do banco de dados concluída com sucesso!")
        print("Todas as tabelas necessárias foram encontradas.")
        
        return True
    
    except Exception as e:
        print(f"Erro ao verificar o banco de dados: {e}")
        return False

def iniciar_aplicacao():
    """Função principal para iniciar a aplicação"""
    global janela, usuario_logado
    
    # Fechar janelas existentes
    fechar_janelas_abertas()
    
    # Carregar configurações do banco de dados do arquivo JSON
    print("Carregando configurações do banco de dados do arquivo config_db.json...")
    carregar_configuracoes_db()
    
    # Configurar a janela principal
    janela = ctk.CTk()
    janela.title("Gestão de Pessoas")
    
    # Configuração para tela cheia
    janela.attributes('-fullscreen', True)  # Usar modo fullscreen em vez de zoomed
    
    # Adicionar handler para a tecla ESC (sair da aplicação)
    def sair_aplicacao(event=None):
        if messagebox.askyesno("Confirmação", "Deseja realmente sair da aplicação?"):
            janela.destroy()
    
    janela.bind("<Escape>", sair_aplicacao)
    
    # Verificar se o banco de dados está configurado
    if not configurar_banco_de_dados():
        # Mostrar mensagem informativa sobre a necessidade de configurar o banco
        frame_erro = ctk.CTkFrame(janela)
        frame_erro.pack(fill="both", expand=True, padx=20, pady=20)
        
        lbl_erro_titulo = ctk.CTkLabel(
            frame_erro,
            text="Banco de Dados Não Configurado",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("red", "#ff6e6e")
        )
        lbl_erro_titulo.pack(pady=(20, 10))
        
        lbl_erro_descricao = ctk.CTkLabel(
            frame_erro,
            text=(
                "O sistema não encontrou as tabelas necessárias no banco de dados.\n\n"

                "Se você ainda não configurou a conexão com o MySQL, use o botão abaixo:"
            ),
            font=ctk.CTkFont(size=14),
            wraplength=500,
            justify="center"
        )
        lbl_erro_descricao.pack(pady=20)
        
        # Frame para botões
        frame_botoes = ctk.CTkFrame(frame_erro, fg_color="transparent")
        frame_botoes.pack(pady=10)
        
        # Botão para configurar conexão MySQL
        btn_config = ctk.CTkButton(
            frame_botoes,
            text="Configurar Conexão MySQL",
            command=configurar_mysql_gui,
            width=250,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        btn_config.pack(side="left", padx=10)
        
        # Botão para executar o configurador de BD
        def executar_configurador():
            try:
                import subprocess
                subprocess.Popen(["python", "configurar_db.py"], shell=True)
                exibir_mensagem("Iniciando Configurador", "O utilitário de configuração está sendo iniciado.\nPor favor, complete a configuração e depois reinicie este aplicativo.")
            except Exception as e:
                exibir_erro("Erro", f"Não foi possível iniciar o configurador: {e}")
        
        btn_executar = ctk.CTkButton(
            frame_botoes,
            text="Executar Configurador",
            command=executar_configurador,
            width=250,
            height=40,
            fg_color=("#4a98d3", "#1f538d"),
            hover_color=("#3a7db5", "#174f7c"),
            font=ctk.CTkFont(size=14, weight="bold")
        )
        btn_executar.pack(side="left", padx=10)
        
        janela.mainloop()
        return
    
    # Se o banco de dados estiver configurado, continuar com o login
    # Manter o modo tela cheia
    
    # Iniciar com a tela de login
    carregar_tela_login()
    
    # Iniciar loop principal
    janela.mainloop()

def carregar_conteudo_usuarios(frame):
    """
    Carrega o conteúdo da página de usuários, incluindo formulário de cadastro
    e lista de usuários existentes.
    
    Args:
        frame: O frame onde o conteúdo será carregado
    """
    # Verificar se o usuário é administrador
    if not (usuario_logado and usuario_logado.get('nivel_acesso') == 'admin'):
        limpar_frame(frame)
        lbl_sem_acesso = ctk.CTkLabel(
            frame,
            text="Você não tem permissão para acessar esta área.\nSomente administradores podem gerenciar usuários.",
            font=ctk.CTkFont(size=16),
            justify="center"
        )
        lbl_sem_acesso.pack(expand=True, pady=50)
        return
    
    # Limpar o frame
    limpar_frame(frame)
    
    # Criar grid para conteúdo
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_columnconfigure(1, weight=1)
    
    # Criar frame para cadastro de usuário
    frame_cadastro = ctk.CTkFrame(frame)
    frame_cadastro.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
    
    lbl_titulo_cadastro = ctk.CTkLabel(
        frame_cadastro,
        text="Cadastro de Usuário",
        font=ctk.CTkFont(size=18, weight="bold"),
        text_color=("#4a98d3", "#1f538d")
    )
    lbl_titulo_cadastro.pack(padx=20, pady=(20, 20))
    
    # Ajuda para cadastro
    lbl_ajuda = ctk.CTkLabel(
        frame_cadastro,
        text="Preencha os dados abaixo para cadastrar um novo usuário do sistema.\n"+
        "O nome de usuário será utilizado para login no sistema.",
        font=ctk.CTkFont(size=12),
        justify="left"
    )
    lbl_ajuda.pack(anchor="w", padx=20, pady=(0, 10))
    
    # Campos de cadastro
    # Nome Completo
    lbl_nome = ctk.CTkLabel(frame_cadastro, text="Nome Completo:")
    lbl_nome.pack(anchor="w", padx=20, pady=(10, 0))
    
    txt_nome = ctk.CTkEntry(frame_cadastro, width=300)
    txt_nome.pack(padx=20, pady=(0, 10))
    
    # Nome de Usuário
    lbl_username = ctk.CTkLabel(frame_cadastro, text="Nome de Usuário:")
    lbl_username.pack(anchor="w", padx=20, pady=(10, 0))
    
    txt_username = ctk.CTkEntry(frame_cadastro, width=300)
    txt_username.pack(padx=20, pady=(0, 10))
    
    # Senha
    lbl_senha = ctk.CTkLabel(frame_cadastro, text="Senha:")
    lbl_senha.pack(anchor="w", padx=20, pady=(10, 0))
    
    txt_senha = ctk.CTkEntry(frame_cadastro, width=300, show="•")
    txt_senha.pack(padx=20, pady=(0, 10))
    
    # Confirmação de Senha
    lbl_confirmar_senha = ctk.CTkLabel(frame_cadastro, text="Confirmar Senha:")
    lbl_confirmar_senha.pack(anchor="w", padx=20, pady=(10, 0))
    
    txt_confirmar_senha = ctk.CTkEntry(frame_cadastro, width=300, show="•")
    txt_confirmar_senha.pack(padx=20, pady=(0, 10))
    
    # Nível de Acesso
    lbl_nivel_acesso = ctk.CTkLabel(frame_cadastro, text="Nível de Acesso:")
    lbl_nivel_acesso.pack(anchor="w", padx=20, pady=(10, 0))
    
    nivel_var = ctk.StringVar(value="user")
    
    frame_radio = ctk.CTkFrame(frame_cadastro, fg_color="transparent")
    frame_radio.pack(fill="x", padx=20, pady=(0, 10))
    
    # Adicionar explicação sobre níveis de acesso
    rb_user = ctk.CTkRadioButton(frame_radio, text="Usuário", variable=nivel_var, value="user")
    rb_user.pack(side="left", padx=(0, 20))
    
    rb_admin = ctk.CTkRadioButton(frame_radio, text="Administrador", variable=nivel_var, value="admin")
    rb_admin.pack(side="left")
    
    # Dica sobre níveis de acesso
    lbl_dica_acesso = ctk.CTkLabel(
        frame_cadastro,
        text="Usuário: Acesso somente às áreas de funcionários e departamentos.\nAdministrador: Acesso completo ao sistema, incluindo cadastro de usuários.",
        font=ctk.CTkFont(size=10, slant="italic"),
        justify="left",
        text_color=("gray40", "gray70")
    )
    lbl_dica_acesso.pack(anchor="w", padx=20, pady=(0, 20))
    
    # Função para adicionar usuário
    def adicionar_usuario():
        # Validar campos
        nome = txt_nome.get().strip()
        username = txt_username.get().strip()
        senha = txt_senha.get()
        confirmar_senha = txt_confirmar_senha.get()
        nivel_acesso = nivel_var.get()
        
        # Validação básica
        if not nome or not username:
            exibir_erro("Erro", "Nome e nome de usuário são obrigatórios")
            return
        
        if len(username) < 4:
            exibir_erro("Erro", "O nome de usuário deve ter pelo menos 4 caracteres")
            return
        
        if len(senha) < 6:
            exibir_erro("Erro", "A senha deve ter pelo menos 6 caracteres")
            return
        
        if senha != confirmar_senha:
            exibir_erro("Erro", "As senhas não coincidem")
            return
        
        try:
            conexao = criar_conexao_mysql()
            if not conexao:
                exibir_erro("Erro", "Não foi possível conectar ao banco de dados")
                return
                
            cursor = conexao.cursor()
            
            # Verificar se já existe um usuário com este username
            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE username = %s", (username,))
            if cursor.fetchone()[0] > 0:
                exibir_erro("Erro", "Nome de usuário já existe")
                return
            
            # Criar hash da senha
            senha_hash = criar_hash_senha(senha)
            
            # Inserir usuário
            cursor.execute("""
                INSERT INTO usuarios (nome, username, senha_hash, nivel_acesso) 
                VALUES (%s, %s, %s, %s)
            """, (nome, username, senha_hash, nivel_acesso))
            
            conexao.commit()
            exibir_mensagem("Sucesso", "Usuário cadastrado com sucesso!")
            
            # Limpar campos após o cadastro
            txt_nome.delete(0, 'end')
            txt_username.delete(0, 'end')
            txt_senha.delete(0, 'end')
            txt_confirmar_senha.delete(0, 'end')
            nivel_var.set("user")
            
            # Atualizar tabela de usuários
            listar_usuarios(tv_usuarios)
            
            cursor.close()
            conexao.close()
        except Exception as e:
            exibir_erro("Erro", f"Erro ao cadastrar usuário: {e}")
    
    # Botões
    frame_botoes = ctk.CTkFrame(frame_cadastro, fg_color="transparent")
    frame_botoes.pack(pady=20)
    
    # Botão de adicionar com destaque
    btn_adicionar = ctk.CTkButton(
        frame_botoes,
        text="CADASTRAR USUÁRIO",
        command=adicionar_usuario,
        width=250,
        height=50,
        font=ctk.CTkFont(size=14, weight="bold"),
        fg_color=("#4a98d3", "#1f538d"),
        hover_color=("#3a7db5", "#174f7c")
    )
    btn_adicionar.grid(row=0, column=0, padx=10)
    
    def limpar_campos():
        txt_nome.delete(0, 'end')
        txt_username.delete(0, 'end')
        txt_senha.delete(0, 'end')
        txt_confirmar_senha.delete(0, 'end')
        nivel_var.set("user")
    
    btn_limpar = ctk.CTkButton(
        frame_botoes,
        text="Limpar Campos",
        command=limpar_campos,
        fg_color="gray60",
        hover_color="gray40",
        width=150,
        height=50
    )
    btn_limpar.grid(row=0, column=1, padx=10)
    
    # Frame para listagem de usuários
    frame_listagem = ctk.CTkFrame(frame)
    frame_listagem.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
    
    lbl_titulo_listagem = ctk.CTkLabel(
        frame_listagem,
        text="Usuários Cadastrados",
        font=ctk.CTkFont(size=16, weight="bold")
    )
    lbl_titulo_listagem.pack(padx=20, pady=20)
    
    # Criar treeview para listagem de usuários
    frame_tabela = ctk.CTkFrame(frame_listagem)
    frame_tabela.pack(fill="both", expand=True, padx=20, pady=(10, 20))
    
    style = ttk.Style()
    style.configure("Treeview", font=('Arial', 10))
    style.configure("Treeview.Heading", font=('Arial', 10, 'bold'))
    
    # Configurar cores baseadas no tema atual
    if ctk.get_appearance_mode() == "Dark":
        style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b")
        style.map('Treeview', background=[('selected', '#3a7ebf')])
    
    # Scrollbar para a tabela
    scrollbar = ttk.Scrollbar(frame_tabela)
    scrollbar.pack(side="right", fill="y")
    
    # Treeview
    colunas = ("id", "nome", "username", "nivel_acesso")
    tv_usuarios = ttk.Treeview(
        frame_tabela,
        columns=colunas,
        show="headings",
        height=15,
        yscrollcommand=scrollbar.set
    )
    
    # Configura as colunas
    tv_usuarios.column("id", width=40)
    tv_usuarios.column("nome", width=200)
    tv_usuarios.column("username", width=150)
    tv_usuarios.column("nivel_acesso", width=100)
    
    # Configura os cabeçalhos
    tv_usuarios.heading("id", text="ID")
    tv_usuarios.heading("nome", text="Nome Completo")
    tv_usuarios.heading("username", text="Nome de Usuário")
    tv_usuarios.heading("nivel_acesso", text="Nível de Acesso")
    
    tv_usuarios.pack(fill="both", expand=True)
    scrollbar.config(command=tv_usuarios.yview)
    
    # Carregar usuários
    listar_usuarios(tv_usuarios)
    
    # Instrução de uso do clique direito
    lbl_dica = ctk.CTkLabel(
        frame_listagem,
        text="* Clique com o botão direito em um usuário para ver opções adicionais",
        font=ctk.CTkFont(size=10, slant="italic"),
        text_color=("gray40", "gray70")
    )
    lbl_dica.pack(pady=(0, 10), anchor="e", padx=20)
    
    # Menu de contexto para a tabela
    menu_contexto = tk.Menu(tv_usuarios, tearoff=0)
    
    def menu_popup(event):
        # Selecionar item clicado
        item = tv_usuarios.identify_row(event.y)
        if item:
            tv_usuarios.selection_set(item)
            menu_contexto.post(event.x_root, event.y_root)
    
    tv_usuarios.bind("<Button-3>", menu_popup)
    
    def excluir_usuario():
        selecionado = tv_usuarios.selection()
        if not selecionado:
            exibir_erro("Erro", "Selecione um usuário para excluir")
            return
        
        usuario_id = tv_usuarios.item(selecionado, "values")[0]
        nome_usuario = tv_usuarios.item(selecionado, "values")[1]
        
        # Não permitir excluir o próprio usuário
        if usuario_logado and str(usuario_logado.get('id')) == str(usuario_id):
            exibir_erro("Erro", "Você não pode excluir seu próprio usuário")
            return
        
        # Confirmar exclusão
        if not messagebox.askyesno("Confirmação", f"Deseja realmente excluir o usuário '{nome_usuario}'?"):
            return
        
        try:
            conexao = criar_conexao_mysql()
            if not conexao:
                exibir_erro("Erro", "Não foi possível conectar ao banco de dados")
                return
                
            cursor = conexao.cursor()
            
            # Verificar se é o último administrador
            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE nivel_acesso = 'admin'")
            total_admins = cursor.fetchone()[0]
            
            cursor.execute("SELECT nivel_acesso FROM usuarios WHERE id = %s", (usuario_id,))
            nivel_usuario = cursor.fetchone()[0]
            
            if nivel_usuario == 'admin' and total_admins <= 1:
                exibir_erro("Erro", "Não é possível excluir o último administrador do sistema")
                return
            
            # Excluir usuário
            cursor.execute("DELETE FROM usuarios WHERE id = %s", (usuario_id,))
            conexao.commit()
            cursor.close()
            conexao.close()
            
            # Atualizar tabela
            listar_usuarios(tv_usuarios)
            exibir_mensagem("Sucesso", "Usuário excluído com sucesso!")
        except Exception as e:
            exibir_erro("Erro", f"Erro ao excluir usuário: {e}")
    
    def redefinir_senha():
        selecionado = tv_usuarios.selection()
        if not selecionado:
            exibir_erro("Erro", "Selecione um usuário para redefinir a senha")
            return
        
        usuario_id = tv_usuarios.item(selecionado, "values")[0]
        nome_usuario = tv_usuarios.item(selecionado, "values")[2]  # username
        
        # Confirmar redefinição
        if not messagebox.askyesno("Confirmação", f"Deseja realmente redefinir a senha do usuário '{nome_usuario}'?"):
            return
        
        # Nova senha padrão
        nova_senha = "123456"
        
        try:
            conexao = criar_conexao_mysql()
            if not conexao:
                exibir_erro("Erro", "Não foi possível conectar ao banco de dados")
                return
                
            cursor = conexao.cursor()
            
            # Criar hash da nova senha
            senha_hash = criar_hash_senha(nova_senha)
            
            # Atualizar senha
            cursor.execute("UPDATE usuarios SET senha_hash = %s WHERE id = %s", (senha_hash, usuario_id))
            conexao.commit()
            cursor.close()
            conexao.close()
            
            exibir_mensagem("Sucesso", f"Senha do usuário '{nome_usuario}' redefinida para '{nova_senha}'")
        except Exception as e:
            exibir_erro("Erro", f"Erro ao redefinir senha: {e}")
    
    def editar_usuario_selecionado():
        selecionado = tv_usuarios.selection()
        if not selecionado:
            exibir_erro("Erro", "Selecione um usuário para editar")
            return
        
        usuario_id = tv_usuarios.item(selecionado, "values")[0]
        try:
            usuario_id = int(usuario_id)
            editar_usuario(usuario_id, tv_usuarios)
        except ValueError:
            exibir_erro("Erro", "ID do usuário inválido")
    
    menu_contexto.add_command(label="Editar", command=editar_usuario_selecionado)
    menu_contexto.add_command(label="Excluir", command=excluir_usuario)
    menu_contexto.add_command(label="Redefinir Senha", command=redefinir_senha)
    
    # Adicionar evento para atualização quando o tema for alterado
    def atualizar_cores_tabela(event=None):
        # Aplicar cores baseadas no tema atual
        if ctk.get_appearance_mode() == "Dark":
            tv_usuarios.configure(
                selectbackground="#1f538d",
                selectforeground="white"
            )
        else:
            tv_usuarios.configure(
                selectbackground="#4a98d3",
                selectforeground="white"
            )
    
    frame.bind("<Configure>", atualizar_cores_tabela)

def editar_funcionario(funcionario_id, tv_funcionarios):
    """
    Abre uma janela para editar os dados de um funcionário específico.
    
    Args:
        funcionario_id: ID do funcionário a ser editado
        tv_funcionarios: TreeView para atualizar após a edição
    """
    global janelas_abertas
    
    # Verificar se já existe uma janela de edição aberta para este funcionário
    chave_janela = f"editar_funcionario_{funcionario_id}"
    if chave_janela in janelas_abertas and janelas_abertas[chave_janela].winfo_exists():
        janelas_abertas[chave_janela].lift()
        return
    
    # Buscar dados atuais do funcionário
    try:
        conexao = criar_conexao_mysql()
        if not conexao:
            exibir_erro("Erro", "Não foi possível conectar ao banco de dados")
            return
            
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("""
            SELECT f.*, d.nome as departamento_nome 
            FROM funcionarios f
            LEFT JOIN departamentos d ON f.departamento_id = d.id
            WHERE f.id = %s
        """, (funcionario_id,))
        
        funcionario = cursor.fetchone()
        if not funcionario:
            exibir_erro("Erro", "Funcionário não encontrado")
            return
        
        cursor.close()
        conexao.close()
    except Exception as e:
        exibir_erro("Erro", f"Erro ao buscar dados do funcionário: {e}")
        return
    
    # Criar janela de edição
    janela_edicao = ctk.CTkToplevel()
    janela_edicao.title(f"Editar Funcionário - {funcionario['nome']}")
    janela_edicao.geometry("500x600")
    centralizar_janela(janela_edicao, 500, 600)
    janela_edicao.grab_set()
    janela_edicao.attributes("-topmost", True)
    
    # Registrar a janela
    janelas_abertas[chave_janela] = janela_edicao
    
    def ao_fechar_janela():
        if chave_janela in janelas_abertas:
            del janelas_abertas[chave_janela]
        janela_edicao.destroy()
    
    janela_edicao.protocol("WM_DELETE_WINDOW", ao_fechar_janela)
    
    # Frame principal
    frame = ctk.CTkFrame(janela_edicao)
    frame.pack(padx=20, pady=20, fill="both", expand=True)
    
    # Título
    lbl_titulo = ctk.CTkLabel(
        frame,
        text="Editar Funcionário",
        font=ctk.CTkFont(size=18, weight="bold"),
        text_color=("#4a98d3", "#1f538d")
    )
    lbl_titulo.pack(pady=(20, 20))
    
    # Campos de edição
    # Nome
    lbl_nome = ctk.CTkLabel(frame, text="Nome:")
    lbl_nome.pack(anchor="w", padx=20, pady=(10, 0))
    
    txt_nome = ctk.CTkEntry(frame, width=400)
    txt_nome.insert(0, funcionario['nome'])
    txt_nome.pack(padx=20, pady=(0, 10))
    
    # Email
    lbl_email = ctk.CTkLabel(frame, text="Email:")
    lbl_email.pack(anchor="w", padx=20, pady=(10, 0))
    
    txt_email = ctk.CTkEntry(frame, width=400)
    txt_email.insert(0, funcionario['email'])
    txt_email.pack(padx=20, pady=(0, 10))
    
    # Data de Nascimento
    lbl_data_nascimento = ctk.CTkLabel(frame, text="Data de Nascimento (DD/MM/AAAA):")
    lbl_data_nascimento.pack(anchor="w", padx=20, pady=(10, 0))
    
    txt_data_nascimento = ctk.CTkEntry(frame, width=400)
    txt_data_nascimento.insert(0, converter_data_para_exibicao(funcionario['data_nascimento']))
    txt_data_nascimento.pack(padx=20, pady=(0, 10))
    
    # Cargo
    lbl_cargo = ctk.CTkLabel(frame, text="Cargo:")
    lbl_cargo.pack(anchor="w", padx=20, pady=(10, 0))
    
    txt_cargo = ctk.CTkEntry(frame, width=400)
    txt_cargo.insert(0, funcionario['cargo'] if funcionario['cargo'] else "")
    txt_cargo.pack(padx=20, pady=(0, 10))
    
    # Salário
    lbl_salario = ctk.CTkLabel(frame, text="Salário (R$):")
    lbl_salario.pack(anchor="w", padx=20, pady=(10, 0))
    
    txt_salario = ctk.CTkEntry(frame, width=400)
    txt_salario.insert(0, str(funcionario['salario']) if funcionario['salario'] else "")
    txt_salario.pack(padx=20, pady=(0, 10))
    
    # Observações
    lbl_observacoes = ctk.CTkLabel(frame, text="Observações:")
    lbl_observacoes.pack(anchor="w", padx=20, pady=(10, 0))
    
    txt_observacoes = ctk.CTkTextbox(frame, width=400, height=80)
    txt_observacoes.insert("0.0", funcionario['observacoes'] if funcionario['observacoes'] else "")
    txt_observacoes.pack(padx=20, pady=(0, 10))
    
    # Departamento
    lbl_departamento = ctk.CTkLabel(frame, text="Departamento:")
    lbl_departamento.pack(anchor="w", padx=20, pady=(10, 0))
    
    departamentos = buscar_departamentos()
    departamento_var = ctk.StringVar()
    opcoes_departamento = [nome for _, nome in departamentos]
    
    if opcoes_departamento:
        departamento_var.set(funcionario['departamento_nome'] if funcionario['departamento_nome'] else opcoes_departamento[0])
    else:
        opcoes_departamento = ["Nenhum departamento disponível"]
        departamento_var.set(opcoes_departamento[0])
    
    dropdown_departamento = ctk.CTkOptionMenu(
        frame, 
        variable=departamento_var,
        values=opcoes_departamento,
        width=400
    )
    dropdown_departamento.pack(padx=20, pady=(0, 20))
    
    # Função para salvar alterações
    def salvar_alteracoes():
        # Validar campos
        nome = txt_nome.get().strip()
        email = txt_email.get().strip()
        data_nascimento_br = txt_data_nascimento.get().strip()
        cargo = txt_cargo.get().strip()
        salario_str = txt_salario.get().strip().replace(',', '.')
        observacoes = txt_observacoes.get("0.0", "end").strip()
        departamento_nome = departamento_var.get()
        
        # Validação básica
        if not nome:
            exibir_erro("Erro", "O nome é obrigatório")
            return
        
        if not email or '@' not in email:
            exibir_erro("Erro", "O email é inválido")
            return
        
        # Validar data de nascimento
        if not data_nascimento_br:
            exibir_erro("Erro", "A data de nascimento é obrigatória")
            return
        
        data_nascimento = converter_data_para_banco(data_nascimento_br)
        if not data_nascimento:
            exibir_erro("Erro", "Data de nascimento inválida. Use o formato DD/MM/AAAA")
            return
        
        # Validar salário
        try:
            salario = float(salario_str) if salario_str else 0
            if salario < 0:
                exibir_erro("Erro", "Salário não pode ser negativo")
                return
        except ValueError:
            exibir_erro("Erro", "Salário inválido")
            return
        
        # Buscar ID do departamento
        departamento_id = None
        if departamento_nome != "Nenhum departamento disponível":
            for dep_id, dep_nome in departamentos:
                if dep_nome == departamento_nome:
                    departamento_id = dep_id
                    break
        
        try:
            conexao = criar_conexao_mysql()
            if not conexao:
                exibir_erro("Erro", "Não foi possível conectar ao banco de dados")
                return
                
            cursor = conexao.cursor()
            
            # Verificar se já existe outro funcionário com este email
            cursor.execute("SELECT COUNT(*) FROM funcionarios WHERE email = %s AND id != %s", (email, funcionario_id))
            if cursor.fetchone()[0] > 0:
                exibir_erro("Erro", "Já existe outro funcionário com este email")
                return
            
            # Atualizar funcionário
            cursor.execute("""
                UPDATE funcionarios 
                SET nome = %s, email = %s, data_nascimento = %s, cargo = %s, 
                    salario = %s, observacoes = %s, departamento_id = %s
                WHERE id = %s
            """, (nome, email, data_nascimento, cargo, salario, observacoes, departamento_id, funcionario_id))
            
            conexao.commit()
            cursor.close()
            conexao.close()
            
            exibir_mensagem("Sucesso", "Funcionário atualizado com sucesso!")
            
            # Atualizar tabela
            listar_funcionarios(tv_funcionarios)
            
            # Fechar janela
            ao_fechar_janela()
            
        except Exception as e:
            exibir_erro("Erro", f"Erro ao atualizar funcionário: {e}")
    
    # Botões
    frame_botoes = ctk.CTkFrame(frame, fg_color="transparent")
    frame_botoes.pack(pady=20)
    
    btn_salvar = ctk.CTkButton(
        frame_botoes,
        text="SALVAR ALTERAÇÕES",
        command=salvar_alteracoes,
        width=200,
        height=40,
        font=ctk.CTkFont(size=14, weight="bold"),
        fg_color=("#4a98d3", "#1f538d"),
        hover_color=("#3a7db5", "#174f7c")
    )
    btn_salvar.grid(row=0, column=0, padx=10)
    
    btn_cancelar = ctk.CTkButton(
        frame_botoes,
        text="Cancelar",
        command=ao_fechar_janela,
        width=120,
        height=40,
        fg_color="gray60",
        hover_color="gray40"
    )
    btn_cancelar.grid(row=0, column=1, padx=10)

def editar_departamento(departamento_id, tv_departamentos):
    """
    Abre uma janela para editar os dados de um departamento específico.
    
    Args:
        departamento_id: ID do departamento a ser editado
        tv_departamentos: TreeView para atualizar após a edição
    """
    global janelas_abertas
    
    # Verificar se já existe uma janela de edição aberta para este departamento
    chave_janela = f"editar_departamento_{departamento_id}"
    if chave_janela in janelas_abertas and janelas_abertas[chave_janela].winfo_exists():
        janelas_abertas[chave_janela].lift()
        return
    
    # Buscar dados atuais do departamento
    try:
        conexao = criar_conexao_mysql()
        if not conexao:
            exibir_erro("Erro", "Não foi possível conectar ao banco de dados")
            return
            
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("SELECT * FROM departamentos WHERE id = %s", (departamento_id,))
        
        departamento = cursor.fetchone()
        if not departamento:
            exibir_erro("Erro", "Departamento não encontrado")
            return
        
        cursor.close()
        conexao.close()
    except Exception as e:
        exibir_erro("Erro", f"Erro ao buscar dados do departamento: {e}")
        return
    
    # Criar janela de edição
    janela_edicao = ctk.CTkToplevel()
    janela_edicao.title(f"Editar Departamento - {departamento['nome']}")
    janela_edicao.geometry("450x400")
    centralizar_janela(janela_edicao, 450, 400)
    janela_edicao.grab_set()
    janela_edicao.attributes("-topmost", True)
    
    # Registrar a janela
    janelas_abertas[chave_janela] = janela_edicao
    
    def ao_fechar_janela():
        if chave_janela in janelas_abertas:
            del janelas_abertas[chave_janela]
        janela_edicao.destroy()
    
    janela_edicao.protocol("WM_DELETE_WINDOW", ao_fechar_janela)
    
    # Frame principal
    frame = ctk.CTkFrame(janela_edicao)
    frame.pack(padx=20, pady=20, fill="both", expand=True)
    
    # Título
    lbl_titulo = ctk.CTkLabel(
        frame,
        text="Editar Departamento",
        font=ctk.CTkFont(size=18, weight="bold"),
        text_color=("#4a98d3", "#1f538d")
    )
    lbl_titulo.pack(pady=(20, 20))
    
    # Campos de edição
    # Nome
    lbl_nome = ctk.CTkLabel(frame, text="Nome:")
    lbl_nome.pack(anchor="w", padx=20, pady=(10, 0))
    
    txt_nome = ctk.CTkEntry(frame, width=350)
    txt_nome.insert(0, departamento['nome'])
    txt_nome.pack(padx=20, pady=(0, 10))
    
    # Descrição
    lbl_descricao = ctk.CTkLabel(frame, text="Descrição:")
    lbl_descricao.pack(anchor="w", padx=20, pady=(10, 0))
    
    txt_descricao = ctk.CTkTextbox(frame, width=350, height=120)
    txt_descricao.insert("0.0", departamento['descricao'] if departamento['descricao'] else "")
    txt_descricao.pack(padx=20, pady=(0, 20))
    
    # Função para salvar alterações
    def salvar_alteracoes():
        # Validar campos
        nome = txt_nome.get().strip()
        descricao = txt_descricao.get("0.0", "end").strip()
        
        if not nome:
            exibir_erro("Erro", "O nome é obrigatório")
            return
        
        try:
            conexao = criar_conexao_mysql()
            if not conexao:
                exibir_erro("Erro", "Não foi possível conectar ao banco de dados")
                return
                
            cursor = conexao.cursor()
            
            # Verificar se já existe outro departamento com este nome
            cursor.execute("SELECT COUNT(*) FROM departamentos WHERE nome = %s AND id != %s", (nome, departamento_id))
            if cursor.fetchone()[0] > 0:
                exibir_erro("Erro", "Já existe outro departamento com este nome")
                return
            
            # Atualizar departamento
            cursor.execute("""
                UPDATE departamentos 
                SET nome = %s, descricao = %s
                WHERE id = %s
            """, (nome, descricao, departamento_id))
            
            conexao.commit()
            cursor.close()
            conexao.close()
            
            exibir_mensagem("Sucesso", "Departamento atualizado com sucesso!")
            
            # Atualizar tabela
            listar_departamentos(tv_departamentos)
            
            # Fechar janela
            ao_fechar_janela()
            
        except Exception as e:
            exibir_erro("Erro", f"Erro ao atualizar departamento: {e}")
    
    # Botões
    frame_botoes = ctk.CTkFrame(frame, fg_color="transparent")
    frame_botoes.pack(pady=20)
    
    btn_salvar = ctk.CTkButton(
        frame_botoes,
        text="SALVAR ALTERAÇÕES",
        command=salvar_alteracoes,
        width=200,
        height=40,
        font=ctk.CTkFont(size=14, weight="bold"),
        fg_color=("#4a98d3", "#1f538d"),
        hover_color=("#3a7db5", "#174f7c")
    )
    btn_salvar.grid(row=0, column=0, padx=10)
    
    btn_cancelar = ctk.CTkButton(
        frame_botoes,
        text="Cancelar",
        command=ao_fechar_janela,
        width=120,
        height=40,
        fg_color="gray60",
        hover_color="gray40"
    )
    btn_cancelar.grid(row=0, column=1, padx=10)

def editar_usuario(usuario_id, tv_usuarios):
    """
    Abre uma janela para editar os dados de um usuário específico.
    
    Args:
        usuario_id: ID do usuário a ser editado
        tv_usuarios: TreeView para atualizar após a edição
    """
    global janelas_abertas
    
    # Verificar se já existe uma janela de edição aberta para este usuário
    chave_janela = f"editar_usuario_{usuario_id}"
    if chave_janela in janelas_abertas and janelas_abertas[chave_janela].winfo_exists():
        janelas_abertas[chave_janela].lift()
        return
    
    # Buscar dados atuais do usuário
    try:
        conexao = criar_conexao_mysql()
        if not conexao:
            exibir_erro("Erro", "Não foi possível conectar ao banco de dados")
            return
            
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE id = %s", (usuario_id,))
        
        usuario = cursor.fetchone()
        if not usuario:
            exibir_erro("Erro", "Usuário não encontrado")
            return
        
        cursor.close()
        conexao.close()
    except Exception as e:
        exibir_erro("Erro", f"Erro ao buscar dados do usuário: {e}")
        return
    
    # Criar janela de edição
    janela_edicao = ctk.CTkToplevel()
    janela_edicao.title(f"Editar Usuário - {usuario['nome']}")
    janela_edicao.geometry("450x500")
    centralizar_janela(janela_edicao, 450, 500)
    janela_edicao.grab_set()
    janela_edicao.attributes("-topmost", True)
    
    # Registrar a janela
    janelas_abertas[chave_janela] = janela_edicao
    
    def ao_fechar_janela():
        if chave_janela in janelas_abertas:
            del janelas_abertas[chave_janela]
        janela_edicao.destroy()
    
    janela_edicao.protocol("WM_DELETE_WINDOW", ao_fechar_janela)
    
    # Frame principal
    frame = ctk.CTkFrame(janela_edicao)
    frame.pack(padx=20, pady=20, fill="both", expand=True)
    
    # Título
    lbl_titulo = ctk.CTkLabel(
        frame,
        text="Editar Usuário",
        font=ctk.CTkFont(size=18, weight="bold"),
        text_color=("#4a98d3", "#1f538d")
    )
    lbl_titulo.pack(pady=(20, 20))
    
    # Campos de edição
    # Nome Completo
    lbl_nome = ctk.CTkLabel(frame, text="Nome Completo:")
    lbl_nome.pack(anchor="w", padx=20, pady=(10, 0))
    
    txt_nome = ctk.CTkEntry(frame, width=350)
    txt_nome.insert(0, usuario['nome'])
    txt_nome.pack(padx=20, pady=(0, 10))
    
    # Nome de Usuário
    lbl_username = ctk.CTkLabel(frame, text="Nome de Usuário:")
    lbl_username.pack(anchor="w", padx=20, pady=(10, 0))
    
    txt_username = ctk.CTkEntry(frame, width=350)
    txt_username.insert(0, usuario['username'])
    txt_username.pack(padx=20, pady=(0, 10))
    
    # Nova Senha (opcional)
    lbl_senha = ctk.CTkLabel(frame, text="Nova Senha (deixe em branco para manter a atual):")
    lbl_senha.pack(anchor="w", padx=20, pady=(10, 0))
    
    txt_senha = ctk.CTkEntry(frame, width=350, show="•")
    txt_senha.pack(padx=20, pady=(0, 10))
    
    # Confirmar Nova Senha
    lbl_confirmar_senha = ctk.CTkLabel(frame, text="Confirmar Nova Senha:")
    lbl_confirmar_senha.pack(anchor="w", padx=20, pady=(10, 0))
    
    txt_confirmar_senha = ctk.CTkEntry(frame, width=350, show="•")
    txt_confirmar_senha.pack(padx=20, pady=(0, 10))
    
    # Nível de Acesso
    lbl_nivel_acesso = ctk.CTkLabel(frame, text="Nível de Acesso:")
    lbl_nivel_acesso.pack(anchor="w", padx=20, pady=(10, 0))
    
    nivel_var = ctk.StringVar(value=usuario['nivel_acesso'])
    
    frame_radio = ctk.CTkFrame(frame, fg_color="transparent")
    frame_radio.pack(fill="x", padx=20, pady=(0, 20))
    
    rb_user = ctk.CTkRadioButton(frame_radio, text="Usuário", variable=nivel_var, value="user")
    rb_user.pack(side="left", padx=(0, 20))
    
    rb_admin = ctk.CTkRadioButton(frame_radio, text="Administrador", variable=nivel_var, value="admin")
    rb_admin.pack(side="left")
    
    # Função para salvar alterações
    def salvar_alteracoes():
        # Validar campos
        nome = txt_nome.get().strip()
        username = txt_username.get().strip()
        senha = txt_senha.get()
        confirmar_senha = txt_confirmar_senha.get()
        nivel_acesso = nivel_var.get()
        
        if not nome or not username:
            exibir_erro("Erro", "Nome e nome de usuário são obrigatórios")
            return
        
        if len(username) < 4:
            exibir_erro("Erro", "O nome de usuário deve ter pelo menos 4 caracteres")
            return
        
        # Verificar senha apenas se foi fornecida
        if senha or confirmar_senha:
            if len(senha) < 6:
                exibir_erro("Erro", "A nova senha deve ter pelo menos 6 caracteres")
                return
            
            if senha != confirmar_senha:
                exibir_erro("Erro", "As senhas não coincidem")
                return
        
        try:
            conexao = criar_conexao_mysql()
            if not conexao:
                exibir_erro("Erro", "Não foi possível conectar ao banco de dados")
                return
                
            cursor = conexao.cursor()
            
            # Verificar se já existe outro usuário com este username
            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE username = %s AND id != %s", (username, usuario_id))
            if cursor.fetchone()[0] > 0:
                exibir_erro("Erro", "Nome de usuário já existe")
                return
            
            # Verificar se é o último admin e está tentando alterar para user
            if usuario['nivel_acesso'] == 'admin' and nivel_acesso == 'user':
                cursor.execute("SELECT COUNT(*) FROM usuarios WHERE nivel_acesso = 'admin'")
                total_admins = cursor.fetchone()[0]
                if total_admins <= 1:
                    exibir_erro("Erro", "Não é possível alterar o último administrador para usuário comum")
                    return
            
            # Preparar query de atualização
            if senha:
                # Atualizar com nova senha
                senha_hash = criar_hash_senha(senha)
                cursor.execute("""
                    UPDATE usuarios 
                    SET nome = %s, username = %s, senha_hash = %s, nivel_acesso = %s
                    WHERE id = %s
                """, (nome, username, senha_hash, nivel_acesso, usuario_id))
            else:
                # Atualizar sem alterar senha
                cursor.execute("""
                    UPDATE usuarios 
                    SET nome = %s, username = %s, nivel_acesso = %s
                    WHERE id = %s
                """, (nome, username, nivel_acesso, usuario_id))
            
            conexao.commit()
            cursor.close()
            conexao.close()
            
            exibir_mensagem("Sucesso", "Usuário atualizado com sucesso!")
            
            # Atualizar tabela
            listar_usuarios(tv_usuarios)
            
            # Fechar janela
            ao_fechar_janela()
            
        except Exception as e:
            exibir_erro("Erro", f"Erro ao atualizar usuário: {e}")
    
    # Botões
    frame_botoes = ctk.CTkFrame(frame, fg_color="transparent")
    frame_botoes.pack(pady=20)
    
    btn_salvar = ctk.CTkButton(
        frame_botoes,
        text="SALVAR ALTERAÇÕES",
        command=salvar_alteracoes,
        width=200,
        height=40,
        font=ctk.CTkFont(size=14, weight="bold"),
        fg_color=("#4a98d3", "#1f538d"),
        hover_color=("#3a7db5", "#174f7c")
    )
    btn_salvar.grid(row=0, column=0, padx=10)
    
    btn_cancelar = ctk.CTkButton(
        frame_botoes,
        text="Cancelar",
        command=ao_fechar_janela,
        width=120,
        height=40,
        fg_color="gray60",
        hover_color="gray40"
    )
    btn_cancelar.grid(row=0, column=1, padx=10)

# Iniciar aplicação quando o script for executado diretamente
if __name__ == "__main__":
    iniciar_aplicacao() 