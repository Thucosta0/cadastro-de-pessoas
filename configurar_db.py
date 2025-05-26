import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error
import json
import os
import hashlib
import time

# Configurações do tema
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Configurações do banco de dados
config_db = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "sistema_miro"
}

# Funções de utilidade
def criar_hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def carregar_configuracoes_db():
    global config_db
    try:
        if os.path.exists("config_db.json"):
            with open("config_db.json", "r") as f:
                config_db = json.load(f)
            return True
        return False
    except Exception as e:
        print(f"Erro ao carregar configurações: {e}")
        return False

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
        print(f"Erro ao conectar ao MySQL: {e}")
        return None

def configurar_mysql_inicial():
    try:
        # Criar conexão sem especificar banco de dados
        conexao = mysql.connector.connect(
            host=config_db["host"],
            user=config_db["user"],
            password=config_db["password"]
        )
        
        if conexao.is_connected():
            cursor = conexao.cursor()
            
            # Criar banco de dados se não existir
            cursor.execute("CREATE DATABASE IF NOT EXISTS sistema_miro")
            cursor.execute("USE sistema_miro")
            
            # Atualizar a configuração para incluir o nome do banco de dados
            config_db["database"] = "sistema_miro"
            
            # Salvar configurações em arquivo
            try:
                with open("config_db.json", "w") as f:
                    json.dump(config_db, f, indent=4)
            except Exception as e:
                print(f"Aviso: Não foi possível salvar o arquivo de configuração: {e}")
            
            cursor.close()
            conexao.close()
            return True
    except Error as e:
        print(f"Erro ao configurar banco de dados inicial: {e}")
        return False

def centralizar_janela(janela, largura, altura):
    largura_tela = janela.winfo_screenwidth()
    altura_tela = janela.winfo_screenheight()
    x = (largura_tela - largura) // 2
    y = (altura_tela - altura) // 2
    janela.geometry(f'{largura}x{altura}+{x}+{y}')

class ConfiguradorBD:
    def __init__(self, janela_root=None):
        self.resultado_final = False
        self.log_mensagens = []
        
        # Criar janela principal se não for fornecida
        if janela_root is None:
            self.janela = ctk.CTk()
            self.janela.title("Gestão de Pessoas - Configuração do Banco de Dados")
            
            # Configurar para tela cheia
            self.janela.attributes('-fullscreen', True)  # Modo fullscreen real
            
            # Adicionar handler para a tecla ESC (sair da aplicação)
            def sair_aplicacao(event=None):
                if messagebox.askyesno("Confirmação", "Deseja realmente sair da aplicação?"):
                    self.janela.destroy()
            
            self.janela.bind("<Escape>", sair_aplicacao)
            
            self.deve_destruir = True
        else:
            self.janela = janela_root
            self.deve_destruir = False
        
        self.criar_interface()
    
    def criar_interface(self):
        # Frame principal
        self.frame_principal = ctk.CTkFrame(self.janela)
        self.frame_principal.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        lbl_titulo = ctk.CTkLabel(
            self.frame_principal,
            text="Configuração do Banco de Dados - Gestão de Pessoas",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=("#4a98d3", "#1f538d")
        )
        lbl_titulo.pack(pady=20)
        
        # Descrição
        lbl_descricao = ctk.CTkLabel(
            self.frame_principal,
            text="Este utilitário irá configurar o banco de dados para o sistema Gestão de Pessoas.\n"
                 "Serão criadas apenas as tabelas necessárias, sem inserir nenhum dado padrão.\n"
                 "Após a criação das tabelas, você precisará criar manualmente um usuário administrador.",
            font=ctk.CTkFont(size=14),
            wraplength=700,
            justify="center"
        )
        lbl_descricao.pack(pady=10)
        
        # Frame para informações de conexão
        frame_conexao = ctk.CTkFrame(self.frame_principal)
        frame_conexao.pack(fill="x", padx=20, pady=10)
        
        lbl_conexao = ctk.CTkLabel(
            frame_conexao,
            text="Informações de Conexão com MySQL",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        lbl_conexao.pack(pady=10)
        
        # Carregar configurações existentes
        carregar_configuracoes_db()
        
        # Host
        frame_host = ctk.CTkFrame(frame_conexao, fg_color="transparent")
        frame_host.pack(fill="x", padx=20, pady=5)
        
        lbl_host = ctk.CTkLabel(frame_host, text="Host:", width=100, anchor="e")
        lbl_host.pack(side="left", padx=(0, 10))
        
        self.txt_host = ctk.CTkEntry(frame_host, width=300)
        self.txt_host.insert(0, config_db["host"])
        self.txt_host.pack(side="left")
        
        # Usuário
        frame_usuario = ctk.CTkFrame(frame_conexao, fg_color="transparent")
        frame_usuario.pack(fill="x", padx=20, pady=5)
        
        lbl_usuario = ctk.CTkLabel(frame_usuario, text="Usuário:", width=100, anchor="e")
        lbl_usuario.pack(side="left", padx=(0, 10))
        
        self.txt_usuario = ctk.CTkEntry(frame_usuario, width=300)
        self.txt_usuario.insert(0, config_db["user"])
        self.txt_usuario.pack(side="left")
        
        # Senha
        frame_senha = ctk.CTkFrame(frame_conexao, fg_color="transparent")
        frame_senha.pack(fill="x", padx=20, pady=5)
        
        lbl_senha = ctk.CTkLabel(frame_senha, text="Senha:", width=100, anchor="e")
        lbl_senha.pack(side="left", padx=(0, 10))
        
        self.txt_senha = ctk.CTkEntry(frame_senha, width=300, show="*")
        self.txt_senha.insert(0, config_db["password"])
        self.txt_senha.pack(side="left")
        
        # Banco de dados
        frame_banco = ctk.CTkFrame(frame_conexao, fg_color="transparent")
        frame_banco.pack(fill="x", padx=20, pady=5)
        
        lbl_banco = ctk.CTkLabel(frame_banco, text="Banco:", width=100, anchor="e")
        lbl_banco.pack(side="left", padx=(0, 10))
        
        self.txt_banco = ctk.CTkEntry(frame_banco, width=300)
        self.txt_banco.insert(0, config_db.get("database", "sistema_miro"))
        self.txt_banco.pack(side="left")
        
        # Botão testar conexão
        btn_testar = ctk.CTkButton(
            frame_conexao,
            text="Testar Conexão",
            command=self.testar_conexao,
            width=150
        )
        btn_testar.pack(pady=15)
        
        # Frame para área de log
        frame_log = ctk.CTkFrame(self.frame_principal)
        frame_log.pack(fill="both", expand=True, padx=20, pady=10)
        
        lbl_log = ctk.CTkLabel(
            frame_log,
            text="Log de Configuração",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        lbl_log.pack(pady=10)
        
        # Área de texto para log
        self.txt_log = ctk.CTkTextbox(frame_log, height=200)
        self.txt_log.pack(fill="both", expand=True, padx=10, pady=10)
        self.txt_log.configure(state="disabled")
        
        # Frame para barra de progresso
        frame_progresso = ctk.CTkFrame(self.frame_principal, fg_color="transparent")
        frame_progresso.pack(fill="x", padx=20, pady=10)
        
        # Barra de progresso
        self.progresso = ctk.CTkProgressBar(frame_progresso)
        self.progresso.pack(fill="x", padx=10, pady=10)
        self.progresso.set(0)
        
        # Frame para botões
        frame_botoes = ctk.CTkFrame(self.frame_principal, fg_color="transparent")
        frame_botoes.pack(pady=20)
        
        # Botão configurar
        self.btn_configurar = ctk.CTkButton(
            frame_botoes,
            text="CONFIGURAR BANCO DE DADOS",
            command=self.iniciar_configuracao,
            width=300,
            height=50,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#4a98d3", "#1f538d"),
            hover_color=("#3a7db5", "#174f7c")
        )
        self.btn_configurar.grid(row=0, column=0, padx=10)
        
        # Botão sair
        self.btn_sair = ctk.CTkButton(
            frame_botoes,
            text="Sair",
            command=self.sair,
            width=150,
            height=50,
            fg_color="gray60",
            hover_color="gray40"
        )
        self.btn_sair.grid(row=0, column=1, padx=10)
    
    def adicionar_log(self, mensagem):
        """Adiciona mensagem ao log"""
        self.log_mensagens.append(mensagem)
        self.txt_log.configure(state="normal")
        self.txt_log.insert("end", f"{mensagem}\n")
        self.txt_log.see("end")  # Rolar para o final
        self.txt_log.configure(state="disabled")
        self.janela.update()
    
    def atualizar_progresso(self, valor):
        """Atualiza a barra de progresso"""
        self.progresso.set(valor)
        self.janela.update()
    
    def testar_conexao(self):
        """Testa a conexão com o banco de dados"""
        # Atualizar configurações com valores dos campos
        config_db["host"] = self.txt_host.get()
        config_db["user"] = self.txt_usuario.get()
        config_db["password"] = self.txt_senha.get()
        
        try:
            conexao = mysql.connector.connect(
                host=config_db["host"],
                user=config_db["user"],
                password=config_db["password"]
            )
            
            if conexao.is_connected():
                messagebox.showinfo("Sucesso", "Conexão estabelecida com sucesso!")
                conexao.close()
        except Error as e:
            messagebox.showerror("Erro de Conexão", f"Falha na conexão: {e}")
    
    def iniciar_configuracao(self):
        """Inicia o processo de configuração do banco de dados"""
        # Atualizar configurações com valores dos campos
        config_db["host"] = self.txt_host.get()
        config_db["user"] = self.txt_usuario.get()
        config_db["password"] = self.txt_senha.get()
        config_db["database"] = self.txt_banco.get()
        
        # Desabilitar botões durante a configuração
        self.btn_configurar.configure(state="disabled")
        self.btn_sair.configure(state="disabled")
        
        # Limpar log
        self.log_mensagens = []
        self.txt_log.configure(state="normal")
        self.txt_log.delete("0.0", "end")
        self.txt_log.configure(state="disabled")
        
        # Iniciar o processo de configuração
        self.adicionar_log("Iniciando configuração do banco de dados...")
        self.atualizar_progresso(0.1)
        
        # Criar banco de dados e tabelas
        resultado = self.configurar_banco_dados()
        
        # Atualizar botões
        self.btn_configurar.configure(state="normal")
        self.btn_sair.configure(state="normal")
        
        # Resultado final
        if resultado:
            messagebox.showinfo("Sucesso", "Banco de dados configurado com sucesso! As tabelas foram criadas, mas nenhum dado foi inserido. Você precisará criar manualmente um usuário administrador para acessar o sistema.")
            self.resultado_final = True
            
            # Se estiver em uma janela independente, fechar automaticamente após sucesso
            if self.deve_destruir:
                self.janela.after(2000, self.janela.destroy)
        else:
            messagebox.showerror("Erro", "Falha na configuração do banco de dados.")
    
    def configurar_banco_dados(self):
        """Configura o banco de dados, criando tabelas e usuário padrão"""
        try:
            # Primeiro verificar se é possível conectar
            self.adicionar_log("Verificando conexão com o servidor MySQL...")
            
            try:
                conexao = mysql.connector.connect(
                    host=config_db["host"],
                    user=config_db["user"],
                    password=config_db["password"]
                )
                
                if not conexao.is_connected():
                    self.adicionar_log("Erro: Não foi possível conectar ao servidor MySQL.")
                    return False
            except Error as e:
                self.adicionar_log(f"Erro de conexão com MySQL: {e}")
                return False
            
            self.adicionar_log("Conexão estabelecida com sucesso!")
            self.atualizar_progresso(0.2)
            
            # Criar o banco de dados
            cursor = conexao.cursor()
            self.adicionar_log(f"Criando banco de dados '{config_db['database']}'...")
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {config_db['database']}")
            
            # Usar o banco de dados
            self.adicionar_log(f"Selecionando banco de dados '{config_db['database']}'...")
            cursor.execute(f"USE {config_db['database']}")
            
            # Salvar a configuração
            try:
                with open("config_db.json", "w") as f:
                    json.dump(config_db, f, indent=4)
                self.adicionar_log("Configurações de conexão salvas em 'config_db.json'")
            except Exception as e:
                self.adicionar_log(f"Aviso: Não foi possível salvar o arquivo de configuração: {e}")
            
            self.atualizar_progresso(0.3)
            
            # Criar tabela de usuários
            self.adicionar_log("Criando tabela 'usuarios'...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nome VARCHAR(100) NOT NULL,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    senha_hash VARCHAR(128) NOT NULL,
                    nivel_acesso VARCHAR(20) NOT NULL,
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            self.atualizar_progresso(0.4)
            time.sleep(0.5)  # Pequena pausa para visualização
            
            # Criar tabela de departamentos
            self.adicionar_log("Criando tabela 'departamentos'...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS departamentos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nome VARCHAR(100) UNIQUE NOT NULL,
                    descricao TEXT,
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            self.atualizar_progresso(0.5)
            time.sleep(0.5)  # Pequena pausa para visualização
            
            # Criar tabela de funcionários
            self.adicionar_log("Criando tabela 'funcionarios'...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS funcionarios (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nome VARCHAR(100) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    telefone VARCHAR(20),
                    cargo VARCHAR(100),
                    salario DECIMAL(10,2),
                    observacoes TEXT,
                    departamento_id INT,
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (departamento_id) REFERENCES departamentos(id)
                )
            """)
            
            self.atualizar_progresso(0.6)
            time.sleep(0.5)  # Pequena pausa para visualização
            
            # Atualizar para mostrar que não estamos inserindo dados
            self.adicionar_log("Todas as tabelas foram criadas com sucesso!")
            self.adicionar_log("IMPORTANTE: Nenhum dado padrão foi inserido nas tabelas.")
            self.adicionar_log("Você precisará criar manualmente os usuários administradores e departamentos.")
            
            # Confirmar alterações
            conexao.commit()
            self.adicionar_log("Alterações confirmadas no banco de dados!")
            
            # Fechar conexão
            cursor.close()
            conexao.close()
            
            self.atualizar_progresso(1.0)
            self.adicionar_log("Configuração concluída com sucesso!")
            
            return True
            
        except Exception as e:
            self.adicionar_log(f"Erro durante a configuração: {e}")
            return False
    
    def sair(self):
        """Fecha a janela"""
        if self.deve_destruir:
            self.janela.destroy()
    
    def executar(self):
        """Inicia a interface e retorna o resultado"""
        if self.deve_destruir:
            self.janela.mainloop()
        return self.resultado_final

# Função para iniciar o configurador como aplicação independente
def iniciar_configurador():
    configurador = ConfiguradorBD()
    return configurador.executar()

# Iniciar a aplicação quando o script for executado diretamente
if __name__ == "__main__":
    iniciar_configurador() 