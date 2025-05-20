import sys
import re

#setei as "variáveis" aos seus respectivos grupos
RESERVADAS = {"main", "int", "float", "char", "if", "else", "while", "do", "for"}
OPERADORES_ARIT = {'+', '-', '*', '/'}
OPERADORES_REL = {'<', '<=', '>', '>=', '==', '!='}
MARCADORES = {'(', ')', '{', '}', ',', ';'}

def erro(msg, linha, coluna):
    print(f"[Erro Léxico] Linha {linha}, Coluna {coluna}: {msg}")

#fullmatch -> biblioteca "re" para expressões regulares
def classificar_token(token):
    if token in RESERVADAS:
        return "PALAVRA_RESERVADA"
    elif re.fullmatch(r"\d+", token):
        return "CONST_INTEIRA"
    elif re.fullmatch(r"\d+\.\d+", token):
        return "CONST_REAL"
    elif re.fullmatch(r"'(.)'", token):
        return "CONST_CARACTERE"
    elif re.fullmatch(r"[a-zA-Z_]\w*", token):
        return "IDENTIFICADOR"
    elif token in OPERADORES_ARIT:
        return "OP_ARITMETICO"
    elif token in OPERADORES_REL:
        return "OP_RELACIONAL"
    elif token in MARCADORES:
        return "MARCADOR"
    return None

#código meio que "começa" aqui, antes só tava setando as váriaveis, aqui vai ler o texto do código-fonte 
def scanner(codigo):
    linha = 1
    coluna = 1
    i = 0
    tamanho = len(codigo)

    while i < tamanho:
        c = codigo[i]

        #ignorar os espaços que pode ter entre
        if c in ' \t':
            i += 1
            coluna += 1
            continue

        #nova linha
        if c == '\n':
            linha += 1
            coluna = 1
            i += 1
            continue

        #le comentário de linha
        if codigo[i:i+2] == "//":
            while i < tamanho and codigo[i] != '\n':
                i += 1
            continue

        #comentário em bloco
        if codigo[i:i+2] == "/*":
            fim = codigo.find("*/", i+2)
            if fim == -1:
                erro("Comentário de bloco não encerrado", linha, coluna)
                return
            bloco = codigo[i:fim+2]
            linha += bloco.count('\n')
            i = fim + 2
            coluna = 1
            continue

        #operadores relacionais de dois caracteres
        if codigo[i:i+2] in OPERADORES_REL:
            print(f"{codigo[i:i+2]} -> {classificar_token(codigo[i:i+2])}")
            i += 2
            coluna += 2
            continue

        #operadores aritméticos (relacionais simples e marcadores)
        if c in OPERADORES_ARIT or c in {'<', '>', '=', '!'} or c in MARCADORES:
            #detecta ! que tá isolada
            if c == '!' and (i+1 >= tamanho or codigo[i+1] != '='):
                erro("Exclamação isolada (!)", linha, coluna)
                i += 1
                coluna += 1
                continue

            print(f"{c} -> {classificar_token(c)}")
            i += 1
            coluna += 1
            continue

        #constante caractere
        if c == "'":
            if i + 2 < tamanho and codigo[i+2] == "'":
                token = codigo[i:i+3]
                print(f"{token} -> {classificar_token(token)}")
                i += 3
                coluna += 3
                continue
            else:
                erro("Constante de caractere mal formada", linha, coluna)
                i += 1
                coluna += 1
                continue

        #numero (int ou real)
        if c.isdigit():
            start = i
            while i < tamanho and codigo[i].isdigit():
                i += 1
            if i < tamanho and codigo[i] == '.':
                i += 1
                if i < tamanho and codigo[i].isdigit():
                    while i < tamanho and codigo[i].isdigit():
                        i += 1
                    token = codigo[start:i]
                    print(f"{token} -> {classificar_token(token)}")
                else:
                    erro("Float mal formado", linha, coluna)
            else:
                token = codigo[start:i]
                print(f"{token} -> {classificar_token(token)}")
            coluna += i - start
            continue

        #palavras reservadas
        if c.isalpha() or c == '_':
            start = i
            while i < tamanho and (codigo[i].isalnum() or codigo[i] == '_'):
                i += 1
            token = codigo[start:i]
            print(f"{token} -> {classificar_token(token)}")
            coluna += i - start
            continue

        #aqui, qualquer outra coisa vai da erro
        erro(f"Caractere inválido: {c!r}", linha, coluna)
        i += 1
        coluna += 1

    print("EOF -> FIM_DE_ARQUIVO")

#aqui aceita nome do arquivo
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python scanner.py <arquivo_de_entrada>")
        sys.exit(1)

    nome_arquivo = sys.argv[1]
    try:
        with open(nome_arquivo, 'r') as f:
            codigo = f.read()
            scanner(codigo)
    except FileNotFoundError:
        print(f"Erro: Arquivo '{nome_arquivo}' não encontrado.")
