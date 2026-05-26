# ESTE ARQUIVO É APENAS UM TESTE POR ENQUANTO.

from usuario import Usuario

print("=== Cadastro de Usuários ===")

nome    = input("Nome: ")
email   = input("E-mail: ")
senha   = input("Senha: ")

usuario = Usuario(nome, email, senha)

print("\n=== Usuário cadastrado ===")
print(usuario)