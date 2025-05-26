# Sistema MIRO

## Descrição
Sistema de gerenciamento de recursos internos e organização, desenvolvido para controle de funcionários, departamentos e projetos.

## Características
- Interface gráfica moderna com CustomTkinter
- Sistema de autenticação de usuários
- Gestão de funcionários
- Gestão de departamentos
- Gestão de projetos
- Associação de funcionários a projetos
- Controle de acessos por nível de usuário
- Tema claro/escuro

## Estrutura do Banco de Dados
O sistema utiliza MySQL como banco de dados, com a seguinte estrutura:

### Tabelas Principais
- **departamentos**: Armazena os departamentos da empresa
- **funcionarios**: Cadastro de funcionários
- **projetos**: Cadastro de projetos
- **funcionarios_projetos**: Associação entre funcionários e projetos
- **contatos_funcionarios**: Contatos dos funcionários
- **usuarios**: Usuários do sistema

## Requisitos
- Python 3.8 ou superior
- MySQL 5.7 ou superior
- Bibliotecas Python (ver `requirements.txt`)

## Instalação

### 1. Clone o repositório
```bash
git clone https://github.com/SEU_USUARIO/sistema-miro.git
cd sistema-miro
```

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

### 3. Configure o banco de dados

#### Opção A: Usando o script SQL completo
1. Execute o script `database_schema.sql` no seu servidor MySQL:
```sql
mysql -u root -p < database_schema.sql
```

#### Opção B: Usando o utilitário de configuração
1. Execute o configurador:
```bash
python configurar_db.py
```

### 4. Configure a conexão com o banco
1. Copie o arquivo de exemplo:
```bash
cp config_db.example.json config_db.json
```

2. Edite o arquivo `config_db.json` com suas credenciais:
```json
{
    "host": "localhost",
    "user": "root",
    "password": "sua_senha_mysql",
    "database": "sistema_miro"
}
```

### 5. Execute o aplicativo
```bash
python app_miro.py
```

## Credenciais Padrão
Após a instalação do banco de dados, use as seguintes credenciais para o primeiro acesso:
- **Usuário**: admin
- **Senha**: admin123

⚠️ **IMPORTANTE**: Altere a senha padrão após o primeiro login!

## Funcionalidades

### Gestão de Funcionários
- Cadastro completo de funcionários
- Associação a departamentos
- Armazenamento de dados profissionais
- Controle de contatos

### Gestão de Departamentos
- Criação e edição de departamentos
- Visualização de departamentos
- Associação com funcionários e projetos

### Gestão de Projetos
- Cadastro de projetos
- Associação de funcionários a projetos
- Controle de status e prazos
- Visualização de membros do projeto

### Administração de Usuários
- Criação de contas de usuário
- Definição de níveis de acesso
- Gestão de permissões

## Estrutura do Projeto
```
sistema-miro/
├── app_miro.py                 # Aplicativo principal
├── configurar_db.py           # Utilitário de configuração do BD
├── criar_acesso_direto.py     # Utilitário para criar usuário admin
├── database_schema.sql        # Script SQL completo do banco
├── requirements.txt           # Dependências Python
├── config_db.example.json     # Exemplo de configuração do BD
├── config_db.json            # Configuração do BD (ignorado pelo Git)
├── README.md                 # Este arquivo
└── .gitignore               # Arquivos ignorados pelo Git
```

## Banco de Dados

### Schema Completo
O arquivo `database_schema.sql` contém:
- Criação do banco de dados
- Todas as tabelas necessárias
- Índices para performance
- Views para relatórios
- Dados iniciais (departamentos e usuário admin)
- Chaves estrangeiras com integridade referencial

### Backup e Restauração
Para fazer backup do banco:
```bash
mysqldump -u root -p sistema_miro > backup_sistema_miro.sql
```

Para restaurar:
```bash
mysql -u root -p sistema_miro < backup_sistema_miro.sql
```

## Desenvolvimento

### Contribuindo
1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Estrutura de Branches
- `main`: Branch principal (produção)
- `develop`: Branch de desenvolvimento
- `feature/*`: Branches para novas funcionalidades
- `hotfix/*`: Branches para correções urgentes

## Segurança
- Senhas armazenadas com hash SHA-256
- Controle de acesso por níveis de usuário
- Validação de dados de entrada
- Arquivo de configuração do BD ignorado pelo Git
- Integridade referencial no banco de dados

## Licença
Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## Suporte
Para suporte, abra uma issue no GitHub ou entre em contato através do email: suporte@sistema-miro.com

## Changelog
### v1.0.0
- Versão inicial do sistema
- Gestão completa de funcionários, departamentos e projetos
- Sistema de autenticação
- Interface gráfica moderna