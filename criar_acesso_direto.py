import mysql.connector
import json
import hashlib

def criar_hash_senha(senha):
    """Cria um hash SHA-256 da senha fornecida"""
    return hashlib.sha256(senha.encode()).hexdigest()

def criar_acesso_admin(nome="Administrador", username="admin", senha="admin123"):
    """
    Cria ou atualiza um usuário administrador no banco de dados.
    
    Args:
        nome (str): Nome do administrador
        username (str): Nome de usuário para login
        senha (str): Senha do usuário (será transformada em hash)
    
    Returns:
        bool: True se a operação foi bem-sucedida, False caso contrário
        str: Mensagem de status
    """
    try:
        # Carregar configurações
        with open('config_db.json') as f:
            config = json.load(f)
        
        # Conectar ao banco de dados
        conn = mysql.connector.connect(**config)
        
        if conn.is_connected():
            cursor = conn.cursor()
            
            # Verificar se a tabela de usuários existe
            cursor.execute("SHOW TABLES LIKE 'usuarios'")
            if not cursor.fetchone():
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
            
            # Verificar se o username já existe
            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE username = %s", (username,))
            if cursor.fetchone()[0] > 0:
                # Opção para redefinir a senha
                cursor.execute("""
                    UPDATE usuarios 
                    SET senha_hash = %s, nome = %s, nivel_acesso = 'admin'
                    WHERE username = %s
                """, (criar_hash_senha(senha), nome, username))
                
                conn.commit()
                mensagem = f"Senha do usuário '{username}' foi redefinida."
            else:
                # Criar hash da senha
                senha_hash = criar_hash_senha(senha)
                
                # Inserir usuário administrador
                cursor.execute("""
                    INSERT INTO usuarios (nome, username, senha_hash, nivel_acesso) 
                    VALUES (%s, %s, %s, 'admin')
                """, (nome, username, senha_hash))
                
                conn.commit()
                mensagem = "Usuário administrador criado com sucesso!"
            
            cursor.close()
            conn.close()
            return True, mensagem

    except Exception as e:
        return False, f"Erro: {e}"

# Se o script for executado diretamente, mostra instruções de uso
if __name__ == "__main__":
    print("Módulo para criação de acesso de administrador.")
    print("Este módulo deve ser importado e sua função criar_acesso_admin() utilizada.")
    print("Exemplo de uso:")
    print("    from criar_acesso_direto import criar_acesso_admin")
    print("    sucesso, mensagem = criar_acesso_admin('Nome', 'usuario', 'senha')") 