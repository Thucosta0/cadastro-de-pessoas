#conexão com banco de dados
import re
import customtkinter as ctk
from tkinter import messagebox
from tkinter import StringVar
import tkinter as tk
from tkinter import ttk
import db

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

janela = None
frm_cadastro = None
frm_consulta = None
frm_bottom = None

var_id = None
txt_nome = None
txt_email = None
txt_telefone = None
cmb_categoria = None

tree_pessoas = None
ent_busca = None
lbl_status = None
btn_adicionar = None
cmb_filtro = None

#centralizar janela
def centralizar_janela(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    
    window.geometry(f'{width}x{height}+{x}+{y}')

#limpar campos
def limpar_campos():
    global var_id
    
    var_id.set("")
    txt_nome.delete(0, "end")
    txt_email.delete(0, "end")
    txt_telefone.delete(0, "end")
    cmb_categoria.set("Cliente")
    txt_nome.focus_set()
    btn_adicionar.configure(text="Adicionar Pessoa")
    atualizar_status("Campos limpos")

#atualizar status
def atualizar_status(mensagem):
    global lbl_status
    if lbl_status is not None:
        lbl_status.configure(text=mensagem)

#atualizar treeview
def atualizar_treeview(pessoas):
    for item in tree_pessoas.get_children():
        tree_pessoas.delete(item)
    
    for pessoa in pessoas:
        tree_pessoas.insert("", "end", values=pessoa)

#validar telefone                                           
def validar_telefone(event):
    if event.char and not (event.char.isdigit() or event.char in "()-+" or event.keysym in ('BackSpace', 'Delete')):
        return "break"
    
    if event.char and event.char.isdigit():
        janela.after(1, formatar_telefone)
    
    return None

#formatar telefone
def formatar_telefone():
    texto = txt_telefone.get().replace(" ", "").replace("(", "").replace(")", "").replace("-", "").replace("+", "")
    formato = ""
    
    apenas_numeros = re.sub(r'\D', '', texto)
    
    if len(apenas_numeros) <= 2:
        formato = "+" + apenas_numeros
    elif len(apenas_numeros) <= 4:
        formato = "+" + apenas_numeros[:2] + " (" + apenas_numeros[2:] + ")"
    elif len(apenas_numeros) <= 9:
        formato = "+" + apenas_numeros[:2] + " (" + apenas_numeros[2:4] + ") " + apenas_numeros[4:]
    else:
        formato = "+" + apenas_numeros[:2] + " (" + apenas_numeros[2:4] + ") " + apenas_numeros[4:9] + "-" + apenas_numeros[9:13]
    
    txt_telefone.delete(0, "end")
    txt_telefone.insert(0, formato)

#adicionar ou atualizar pessoa
def adicionar_ou_atualizar_pessoa():
    global var_id
    
    nome = txt_nome.get().strip()
    email = txt_email.get().strip()
    telefone = txt_telefone.get().strip()
    categoria = cmb_categoria.get().strip()
    
    if not nome:
        messagebox.showerror("Erro", "O nome não pode estar vazio!")
        txt_nome.focus_set()
        return
        
    if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        messagebox.showerror("Erro", "E-mail inválido!")
        txt_email.focus_set()
        return
        
    id_pessoa = var_id.get()
    
    if id_pessoa and btn_adicionar.cget("text") == "Atualizar Cadastro":
        if db.atualizar_pessoa(int(id_pessoa), nome, email, telefone, categoria):
            limpar_campos()
            carregar_pessoas()
            atualizar_status(f"Cadastro ID: {id_pessoa} atualizado")
    else:
        if db.adicionar_pessoa(nome, email, telefone, categoria):
            limpar_campos()
            carregar_pessoas()
            atualizar_status("Novo cadastro adicionado")

#excluir pessoa
def excluir_pessoa():
    global var_id
    
    id_pessoa = var_id.get()
    
    if not id_pessoa:
        messagebox.showerror("Erro", "Nenhum cadastro selecionado!")
        return
      
    if messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir este cadastro?"):
        if db.excluir_pessoa(int(id_pessoa)):
            limpar_campos()
            carregar_pessoas()
            atualizar_status(f"Cadastro ID: {id_pessoa} excluído")

def selecionar_pessoa(event):
    global var_id
    
    limpar_campos()
    
    selected_item = tree_pessoas.selection()
    if not selected_item:
        return
    
    values = tree_pessoas.item(selected_item, "values")
    
    id_pessoa = values[0]
    
    pessoa = db.obter_pessoa_por_id(id_pessoa)
    if not pessoa:
        return
    
    var_id.set(pessoa[0])
    
    txt_nome.delete(0, "end")
    txt_nome.insert(0, pessoa[1] or "")
    
    txt_email.delete(0, "end")
    txt_email.insert(0, pessoa[2] or "")
    
    txt_telefone.delete(0, "end")
    txt_telefone.insert(0, pessoa[3] or "")
    
    cmb_categoria.set(pessoa[4] or "Cliente")
    
    btn_adicionar.configure(text="Atualizar Cadastro")
    
    atualizar_status(f"Cadastro ID: {id_pessoa} selecionado")

#filtrar por categoria
def filtrar_por_categoria():
    categoria_selecionada = cmb_filtro.get()
    
    if categoria_selecionada == "Todas":
        pessoas = db.obter_todas_pessoas()
        atualizar_status(f"Mostrando todos os cadastros")
    else:
        pessoas = db.filtrar_pessoas_por_categoria(categoria_selecionada)
        atualizar_status(f"Filtrado por: {categoria_selecionada}")
    
    atualizar_treeview(pessoas)

def buscar_pessoas():
    termo = ent_busca.get().strip()
    
    if not termo:
        carregar_pessoas()
        return
    
    pessoas = db.buscar_pessoas(termo)
    
    atualizar_treeview(pessoas)
    atualizar_status(f"Busca por: '{termo}'")

#carregar pessoas
def carregar_pessoas():
    pessoas = db.obter_todas_pessoas()
    
    atualizar_treeview(pessoas)
    
    atualizar_status(f"Total de cadastros: {len(pessoas)}")

#alternar tema
def alternar_tema():
    tema_atual = ctk.get_appearance_mode()
    
    if tema_atual == "Dark":
        ctk.set_appearance_mode("Light")
        atualizar_status("Tema alterado para: Claro")
        atualizar_estilo_treeview("Light")
    else:
        ctk.set_appearance_mode("Dark")
        atualizar_status("Tema alterado para: Escuro")
        atualizar_estilo_treeview("Dark")

#atualizar estilo treeview
def atualizar_estilo_treeview(tema):
    style = ttk.Style()
    
    if tema == "Dark":
        style.configure("Treeview", 
                     background="#2a2d2e",
                     foreground="white",
                     fieldbackground="#2a2d2e")
        style.map('Treeview', 
                background=[('selected', '#1f538d')],
                foreground=[('selected', 'white')])
    else:
        style.configure("Treeview", 
                     background="#f0f0f0",
                     foreground="black",
                     fieldbackground="#f0f0f0")
        style.map('Treeview', 
                background=[('selected', '#3b8ed0')],
                foreground=[('selected', 'white')])

#criar interface        
def criar_interface():
    global janela, frm_cadastro, frm_consulta, frm_bottom
    global var_id, txt_nome, txt_email, txt_telefone, cmb_categoria
    global tree_pessoas, ent_busca, lbl_status, btn_adicionar, cmb_filtro
    
    janela = ctk.CTk()
    janela.title("Sistema de Cadastro de Pessoas")
    
    janela.resizable(True, True)
    
    janela.minsize(900, 500)
    
    janela.grid_columnconfigure(0, weight=1)
    janela.grid_rowconfigure(0, weight=0)
    janela.grid_rowconfigure(1, weight=1)
    janela.grid_rowconfigure(2, weight=0)
    
    centralizar_janela(janela, 1400, 590)
    
    var_id = StringVar()
    
    frm_header = ctk.CTkFrame(janela, fg_color=("#3b8ed0", "#1f538d"), height=60)
    frm_header.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
    frm_header.grid_columnconfigure(0, weight=1)
    
    #criar label de titulo
    lbl_app_title = ctk.CTkLabel(
        frm_header, 
        text="SISTEMA DE CADASTRO DE PESSOAS", 
        font=ctk.CTkFont(size=20, weight="bold"),
        text_color="white"
    )
    lbl_app_title.grid(row=0, column=0, pady=15)
    
    #criar frame principal
    frm_main = ctk.CTkFrame(janela)
    frm_main.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
    frm_main.grid_columnconfigure(0, weight=2)
    frm_main.grid_columnconfigure(1, weight=5)
    frm_main.grid_rowconfigure(0, weight=1)
    
    #criar frame de cadastro
    frm_cadastro = ctk.CTkFrame(frm_main)
    frm_cadastro.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=0)
    
    #criar frame de cadastro
    frm_cadastro.grid_columnconfigure(0, weight=0)
    frm_cadastro.grid_columnconfigure(1, weight=1)
    
    #criar label de titulo
    lbl_titulo_form = ctk.CTkLabel(
        frm_cadastro, 
        text="Cadastro de Pessoas", 
        font=ctk.CTkFont(size=16, weight="bold")
    )
    lbl_titulo_form.grid(row=0, column=0, columnspan=2, pady=(10, 0), padx=15, sticky="w")
    
    pad_y = 3
    
    #criar label de nome
    lbl_nome = ctk.CTkLabel(frm_cadastro, text="Nome:")
    lbl_nome.grid(row=1, column=0, sticky="e", pady=pad_y, padx=(15, 5))
    txt_nome = ctk.CTkEntry(frm_cadastro, width=280)
    txt_nome.grid(row=1, column=1, sticky="ew", padx=(0, 15), pady=pad_y)
    
    #criar label de email
    lbl_email = ctk.CTkLabel(frm_cadastro, text="Email:")
    lbl_email.grid(row=2, column=0, sticky="e", pady=pad_y, padx=(15, 5))
    txt_email = ctk.CTkEntry(frm_cadastro, width=280)
    txt_email.grid(row=2, column=1, sticky="ew", padx=(0, 15), pady=pad_y)
    
    #criar label de telefone
    lbl_telefone = ctk.CTkLabel(frm_cadastro, text="Telefone:")
    lbl_telefone.grid(row=3, column=0, sticky="e", pady=pad_y, padx=(15, 5))
    txt_telefone = ctk.CTkEntry(frm_cadastro, width=150, placeholder_text="+** (**) *****-****")
    txt_telefone.grid(row=3, column=1, sticky="w", padx=(0, 15), pady=pad_y)
    txt_telefone.bind("<Key>", validar_telefone)
    txt_telefone.bind("<FocusIn>", lambda e: janela.after(100, formatar_telefone))
    
    #criar label de categoria
    lbl_categoria = ctk.CTkLabel(frm_cadastro, text="Categoria:")
    lbl_categoria.grid(row=4, column=0, sticky="e", pady=pad_y, padx=(15, 5))
    cmb_categoria = ctk.CTkOptionMenu(
        frm_cadastro, 
        values=["Cliente", "Usuário admin"],
        width=150
    )
    cmb_categoria.grid(row=4, column=1, sticky="w", padx=(0, 15), pady=pad_y)
    cmb_categoria.set("Cliente")
    
    #criar frame de botões
    frm_botoes = ctk.CTkFrame(frm_cadastro, fg_color="transparent")
    frm_botoes.grid(row=6, column=0, columnspan=2, pady=20, padx=15, sticky="ew")
    frm_botoes.columnconfigure((0, 1, 2, 3, 4), weight=1)
    
    frm_botoes_container = ctk.CTkFrame(frm_botoes, fg_color="transparent")
    frm_botoes_container.grid(row=0, column=1, columnspan=3, sticky="ns")
    frm_botoes_container.columnconfigure((0, 1, 2), weight=1)
    
    #adicionar pessoa   
    btn_adicionar = ctk.CTkButton(
        frm_botoes_container, 
        text="Adicionar Pessoa", 
        command=adicionar_ou_atualizar_pessoa,
        fg_color=("#3a7ebf", "#1f538d"),
        hover_color=("#325882", "#14375e"),
        width=110
    )
    btn_adicionar.grid(row=0, column=0, padx=5)
    
    #limpar campos  
    btn_limpar = ctk.CTkButton(
        frm_botoes_container, 
        text="Limpar Campos", 
        command=limpar_campos,
        fg_color=("#3a7ebf", "#1f538d"),
        hover_color=("#325882", "#14375e"),
        width=110
    )
    btn_limpar.grid(row=0, column=1, padx=5)
    
    #excluir pessoa
    btn_excluir = ctk.CTkButton(
        frm_botoes_container, 
        text="Excluir Cadastro", 
        command=excluir_pessoa,
        fg_color=("#D22B2B", "#AA2222"),
        hover_color=("#AA2222", "#881C1C"),
        width=110
    )
    btn_excluir.grid(row=0, column=2, padx=5)
    
    #criar frame de consulta
    frm_consulta = ctk.CTkFrame(frm_main)
    frm_consulta.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=0)
    frm_consulta.grid_columnconfigure(0, weight=1)
    frm_consulta.grid_rowconfigure(0, weight=0)
    frm_consulta.grid_rowconfigure(1, weight=1)
    
    frm_superior = ctk.CTkFrame(frm_consulta)
    frm_superior.grid(row=0, column=0, sticky="ew", padx=15, pady=15)
    frm_superior.grid_columnconfigure(0, weight=1)
    frm_superior.grid_columnconfigure(1, weight=1)
    
    frm_filtro = ctk.CTkFrame(frm_superior, fg_color="transparent")
    frm_filtro.grid(row=0, column=0, sticky="w")
    
    lbl_filtro = ctk.CTkLabel(frm_filtro, text="Filtrar por:")
    lbl_filtro.grid(row=0, column=0, sticky="w", padx=(0, 5))
    
    cmb_filtro = ctk.CTkOptionMenu(
        frm_filtro, 
        values=["Todas", "Cliente", "Usuário admin"],
        width=150
    )
    cmb_filtro.grid(row=0, column=1, sticky="w", padx=(0, 5))
    cmb_filtro.set("Todas")
    
    #filtrar por categoria
    btn_filtrar = ctk.CTkButton(
        frm_filtro, 
        text="Filtrar", 
        width=80, 
        command=filtrar_por_categoria,
        fg_color=("#3a7ebf", "#1f538d"),
        hover_color=("#325882", "#14375e")
    )
    btn_filtrar.grid(row=0, column=2, padx=5)
    
    frm_busca = ctk.CTkFrame(frm_superior, fg_color="transparent")
    frm_busca.grid(row=0, column=1, sticky="e")
    
    #criar label de busca
    lbl_busca = ctk.CTkLabel(frm_busca, text="Buscar:")
    lbl_busca.grid(row=0, column=0, sticky="w", padx=(0, 5))
    
    ent_busca = ctk.CTkEntry(frm_busca, width=180)
    ent_busca.grid(row=0, column=1, padx=5)
    ent_busca.bind("<Return>", lambda event: buscar_pessoas())
    
    btn_buscar = ctk.CTkButton(
        frm_busca, 
        text="Buscar", 
        width=80, 
        command=buscar_pessoas,
        fg_color=("#3a7ebf", "#1f538d"),
        hover_color=("#325882", "#14375e")
    )
    btn_buscar.grid(row=0, column=2, padx=5)
    
    #criar frame de tabela
    frm_tabela = ctk.CTkFrame(frm_consulta)
    frm_tabela.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
    frm_tabela.grid_rowconfigure(0, weight=1)
    frm_tabela.grid_columnconfigure(0, weight=1)
    
    tree_frame = tk.Frame(frm_tabela)
    tree_frame.pack(fill="both", expand=True, padx=5, pady=5)
    
    #criar scrollbar
    scrollbar = ttk.Scrollbar(tree_frame)
    scrollbar.pack(side="right", fill="y")
    
    #criar treeview 
    tree_pessoas = ttk.Treeview(tree_frame, yscrollcommand=scrollbar.set)
    tree_pessoas.pack(side="left", fill="both", expand=True)
    
    #configurar scrollbar   
    scrollbar.configure(command=tree_pessoas.yview)
    
    #configurar treeview    
    tree_pessoas["columns"] = ("ID", "Nome", "Email", "Telefone", "Categoria", "Data Criação")
    tree_pessoas["show"] = "headings"

    #configurar treeview
    tree_pessoas.column("ID", width=40, minwidth=40, anchor="center", stretch=False)
    tree_pessoas.column("Nome", width=150, minwidth=100, stretch=True)
    tree_pessoas.column("Email", width=150, minwidth=100, stretch=True)
    tree_pessoas.column("Telefone", width=120, minwidth=80, stretch=False)
    tree_pessoas.column("Categoria", width=100, minwidth=80, anchor="center", stretch=False)
    tree_pessoas.column("Data Criação", width=120, minwidth=100, anchor="center", stretch=False)
    
    #criar headings
    tree_pessoas.heading("ID", text="ID")
    tree_pessoas.heading("Nome", text="Nome")
    tree_pessoas.heading("Email", text="Email")
    tree_pessoas.heading("Telefone", text="Telefone")
    tree_pessoas.heading("Categoria", text="Categoria")
    tree_pessoas.heading("Data Criação", text="Data Criação")

    #configurar treeview
    tree_pessoas.bind("<<TreeviewSelect>>", selecionar_pessoa)
    
    frm_bottom = ctk.CTkFrame(janela, fg_color=("#3b8ed0", "#1f538d"), height=30)
    frm_bottom.grid(row=2, column=0, sticky="ew")
    frm_bottom.grid_propagate(False)
    frm_bottom.grid_columnconfigure(0, weight=1)
    frm_bottom.grid_columnconfigure(1, weight=0)
    
    #criar label de status
    lbl_status = ctk.CTkLabel(frm_bottom, text="Pronto", text_color="#FFFFFF")
    lbl_status.grid(row=0, column=0, sticky="w", padx=15, pady=5)
    
    #criar botão de tema
    btn_tema = ctk.CTkButton(
        frm_bottom, 
        text="Alternar Tema", 
        width=120, 
        command=alternar_tema,
        fg_color=("#325882", "#14375e"),
        hover_color=("#264066", "#0a2542")
    )
    btn_tema.grid(row=0, column=1, padx=15, pady=5)
    
    #carregar pessoas
    carregar_pessoas()
    
    return janela

#main
if __name__ == "__main__":
    conexao, cursor = db.conectar_banco()
    
    if not conexao:
        root = ctk.CTk()
        root.withdraw()
        
        if messagebox.askyesno(
            "Configuração do MySQL", 
            "Configurar banco de dados?"
        ):
            if db.configurar_mysql_gui():
                conexao, cursor = db.conectar_banco()
                
                if not conexao:
                    exit()
            else:
                exit()
        else:
            exit()
    
    if conexao:
        conexao.close()
    
    janela_app = criar_interface()
    
    janela_app.mainloop() 