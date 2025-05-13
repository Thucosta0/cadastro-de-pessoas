# Sistema de Cadastro de Pessoas

Um aplicativo simples para gerenciar pessoas em um banco de dados, com interface gráfica moderna.

## O que este programa faz?

Com este programa você pode:
- ✅ Adicionar novas pessoas ao banco de dados
- 📝 Editar informações de pessoas já cadastradas
- 🗑️ Apagar pessoas do banco de dados
- 🔍 Buscar pessoas pelo nome, e-mail ou telefone
- 🏷️ Filtrar pessoas por categorias (Cliente, Funcionário ou Admin)
- 🌓 Usar o tema claro ou escuro conforme sua preferência

## O que você precisa para usar?

- Python 3.6 (https://www.python.org/downloads/)
- Um servidor MySQL instalado e funcionando
- As bibliotecas Python necessárias:
- customtkinter (para a interface gráfica bonita)
- mysql-connector-python (para conectar ao banco de dados)

## Como instalar

### Passo 1: Instale o Python

Se você ainda não tem o Python instalado:
1. Baixe a versão mais recente do Python no (https://www.python.org/downloads/)
2. Durante a instalação, marque a opção "Add Python to PATH"
3. Conclua a instalação seguindo as instruções

### Passo 2: Instale o MySQL

1. Baixe o MySQL Community Server em (https://dev.mysql.com/downloads/mysql/)
2. Siga o assistente de instalação
3. Anote a senha que você definir para o usuário "root" (você precisará dela depois)

### Passo 3: Instale as bibliotecas Python

Abra o Prompt de Comando (CMD) ou PowerShell e digite:

```
pip install customtkinter mysql-connector-python

```

### Passo 4: Obtenha o programa

1. Baixe o código deste programa para seu computador
2. Descompacte em uma pasta de sua preferência

## Como usar o programa

1. Abra o Prompt de Comando (CMD) ou PowerShell
2. Navegue até a pasta onde você salvou o programa:

   ```
   cd caminho/para/a/pasta

   ```
3. Execute o aplicativo:

   ```
   python app.py
   
   ```

4. Na primeira execução, uma janela de configuração do MySQL aparecerá:
   - **Host**: Normalmente é "127.0.0.1" ou "localhost"
   - **Porta**: Normalmente é "3306"
   - **Usuário**: Normalmente é "root"
   - **Senha**: A senha que você criou durante a instalação do MySQL
   - **Banco de Dados**: Pode deixar como "cadastro_pessoas"

## Como usar as funções do programa

### Adicionar uma nova pessoa
1. Clique no botão "Adicionar Pessoa"
2. Preencha os campos solicitados (nome é obrigatório)
3. Escolha a categoria (Cliente, Funcionário ou Admin)
4. Clique em "Salvar"

### Editar uma pessoa
1. Selecione a pessoa na tabela
2. Clique no botão "Atualizar Cadastro"
3. Altere os campos desejados
4. Clique em "Salvar"

### Excluir uma pessoa
1. Selecione a pessoa na tabela
2. Clique no botão "Excluir Cadastro"
3. Confirme a exclusão

### Buscar uma pessoa
1. Digite um termo na caixa de busca (parte do nome, email ou telefone)
2. Clique no botão "Buscar" ou pressione Enter

### Filtrar por categoria
1. Clique no menu suspenso de categorias
2. Selecione a categoria desejada (Cliente, Funcionário, Admin ou Todas)

### Mudar o tema
1. Clique no botão "Alternar Tema" para trocar entre claro e escuro

## Estrutura do projeto

O projeto é composto por apenas 3 arquivos principais:

- **app.py**: Contém o código da interface gráfica bonita
- **db.py**: Gerencia a conexão com o banco de dados
- **db_config.json**: Arquivo criado automaticamente para guardar as configurações

## Sobre o banco de dados

O sistema usa uma única tabela chamada "pessoas" com os seguintes campos:
- **id**: Número único para cada pessoa (gerado automaticamente)
- **nome**: Nome da pessoa (obrigatório)
- **email**: Endereço de email
- **telefone**: Número de telefone
- **categoria**: Tipo de pessoa (Cliente, Funcionário ou Admin)
- **data_criacao**: Data e hora em que o cadastro foi feito

©thucosta tweaks 2025 | Todos os direitos reservados