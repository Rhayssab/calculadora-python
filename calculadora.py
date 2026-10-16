
import tkinter as tk
import math
import ast
import operator

# ==========================================
# CONFIGURACOES E CORES
# ==========================================

FUNDO = "#181825"
PAINEL = "#1E1E2E"
VISOR_COR = "#313244"
NUMERO = "#45475A"
OPERADOR = "#89B4FA"
ESPECIAL = "#F38BA8"
IGUAL = "#A6E3A1"
BRANCO = "#CDD6F4"
CINZA = "#A6ADC8"

janela = tk.Tk()
janela.title("Minha Calculadora")
janela.geometry("380x760")
janela.resizable(False, False)
janela.configure(bg=FUNDO)

expressao = tk.StringVar(value="0")
historico = []
nova_conta = True

# ==========================================
# CABECALHO E VISOR
# ==========================================

titulo = tk.Label(
    janela,
    text="MINHA CALCULADORA",
    font=("Arial", 12, "bold"),
    bg=FUNDO,
    fg=OPERADOR
)
titulo.pack(pady=(18, 4))

subtitulo = tk.Label(
    janela,
    text="Python • Tkinter",
    font=("Arial", 9),
    bg=FUNDO,
    fg=CINZA
)
subtitulo.pack(pady=(0, 12))

visor = tk.Entry(
    janela,
    textvariable=expressao,
    font=("Arial", 25, "bold"),
    justify="right",
    state="readonly",
    readonlybackground=VISOR_COR,
    fg=BRANCO,
    bd=0,
    relief="flat"
)
visor.pack(fill="x", padx=16, pady=(0, 14), ipady=17)


# ==========================================
# FUNCOES AUXILIARES
# ==========================================

def atualizar_visor(valor):
    expressao.set(str(valor))


def adicionar_historico(texto):
    historico.append(texto)
    lista_historico.insert(tk.END, texto)
    lista_historico.see(tk.END)


def limpar():
    global nova_conta
    atualizar_visor("0")
    nova_conta = True


def apagar():
    global nova_conta

    atual = expressao.get()

    if atual == "Erro" or len(atual) <= 1:
        limpar()
    else:
        atualizar_visor(atual[:-1])
        nova_conta = False


def adicionar(valor):
    global nova_conta

    atual = expressao.get()

    if atual == "Erro":
        atual = "0"
        atualizar_visor(atual)

    # Impede operadores no inicio,
    # exceto o sinal negativo.
    if valor in "+-*/":
        if atual == "0" or atual == "":
            if valor == "-":
                atualizar_visor("-")
                nova_conta = False
            return

        if atual[-1] in "+-*/":
            atualizar_visor(atual[:-1] + valor)
        else:
            atualizar_visor(atual + valor)

        nova_conta = False
        return

    # Permite apenas um ponto por numero.
    if valor == ".":
        ultimo = atual

        for op in "+-*/":
            ultimo = ultimo.split(op)[-1]

        if "." in ultimo:
            return

    if nova_conta:
        atualizar_visor("0" if valor == "." else valor)
        nova_conta = False
    elif atual == "0" and valor != ".":
        atualizar_visor(valor)
    else:
        atualizar_visor(atual + valor)


# ==========================================
# CALCULO SEGURO DAS OPERACOES
# ==========================================

def avaliar(expressao_texto):
    """
    Avalia somente operacoes matematicas permitidas.
    Nao executa comandos arbitrarios do Python.
    """

    arvore = ast.parse(expressao_texto, mode="eval")

    operadores = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
    }

    def visitar(no):
        if isinstance(no, ast.Expression):
            return visitar(no.body)

        if isinstance(no, ast.Constant):
            if type(no.value) in (int, float):
                return no.value
            raise ValueError("Numero invalido")

        if isinstance(no, ast.BinOp):
            tipo = type(no.op)

            if tipo not in operadores:
                raise ValueError("Operacao nao permitida")

            esquerda = visitar(no.left)
            direita = visitar(no.right)

            if tipo is ast.Div and direita == 0:
                raise ZeroDivisionError

            resultado = operadores[tipo](esquerda, direita)

            if isinstance(resultado, complex):
                raise ValueError("Resultado invalido")

            if not math.isfinite(resultado):
                raise ValueError("Resultado muito grande")

            return resultado

        if isinstance(no, ast.UnaryOp):
            valor = visitar(no.operand)

            if isinstance(no.op, ast.USub):
                return -valor

            if isinstance(no.op, ast.UAdd):
                return valor

        raise ValueError("Expressao invalida")

    return visitar(arvore)


def formatar_numero(valor):
    if isinstance(valor, float) and valor.is_integer():
        return str(int(valor))

    return str(round(valor, 10))


def calcular():
    global nova_conta

    conta = expressao.get()

    try:
        resultado = avaliar(conta)
        resultado_texto = formatar_numero(resultado)

        adicionar_historico(
            f"{conta} = {resultado_texto}"
        )

        atualizar_visor(resultado_texto)
        nova_conta = True

    except ZeroDivisionError:
        atualizar_visor("Erro: divisao por zero")
        nova_conta = True

    except (ValueError, SyntaxError, TypeError,
            OverflowError, ArithmeticError):
        atualizar_visor("Erro")
        nova_conta = True


def porcentagem():
    global nova_conta

    try:
        valor = avaliar(expressao.get())
        resultado = valor / 100
        resultado_texto = formatar_numero(resultado)

        adicionar_historico(
            f"{formatar_numero(valor)}% = {resultado_texto}"
        )

        atualizar_visor(resultado_texto)
        nova_conta = True

    except (ValueError, SyntaxError, TypeError,
            ZeroDivisionError, OverflowError):
        atualizar_visor("Erro")
        nova_conta = True


def raiz():
    global nova_conta

    try:
        valor = avaliar(expressao.get())

        if valor < 0:
            raise ValueError("Raiz negativa")

        resultado = math.sqrt(valor)
        resultado_texto = formatar_numero(resultado)

        adicionar_historico(
            f"√{formatar_numero(valor)} = {resultado_texto}"
        )

        atualizar_visor(resultado_texto)
        nova_conta = True

    except (ValueError, SyntaxError, TypeError,
            OverflowError):
        atualizar_visor("Erro")
        nova_conta = True


def limpar_historico():
    historico.clear()
    lista_historico.delete(0, tk.END)


# ==========================================
# PAINEL DE BOTOES
# ==========================================

painel = tk.Frame(janela, bg=FUNDO)
painel.pack(fill="both", padx=12, pady=(0, 12))

botoes = [
    ("C", limpar, ESPECIAL),
    ("⌫", apagar, ESPECIAL),
    ("%", porcentagem, OPERADOR),
    ("÷", lambda: adicionar("/"), OPERADOR),

    ("7", lambda: adicionar("7"), NUMERO),
    ("8", lambda: adicionar("8"), NUMERO),
    ("9", lambda: adicionar("9"), NUMERO),
    ("×", lambda: adicionar("*"), OPERADOR),

    ("4", lambda: adicionar("4"), NUMERO),
    ("5", lambda: adicionar("5"), NUMERO),
    ("6", lambda: adicionar("6"), NUMERO),
    ("−", lambda: adicionar("-"), OPERADOR),

    ("1", lambda: adicionar("1"), NUMERO),
    ("2", lambda: adicionar("2"), NUMERO),
    ("3", lambda: adicionar("3"), NUMERO),
    ("+", lambda: adicionar("+"), OPERADOR),

    ("√", raiz, OPERADOR),
    ("0", lambda: adicionar("0"), NUMERO),
    (".", lambda: adicionar("."), NUMERO),
    ("=", calcular, IGUAL),
]

for indice, (texto, comando, cor) in enumerate(botoes):
    botao = tk.Button(
        painel,
        text=texto,
        command=comando,
        font=("Arial", 16, "bold"),
        bg=cor,
        fg=FUNDO if cor in (OPERADOR, IGUAL) else BRANCO,
        activebackground="#B4BEFE",
        activeforeground=FUNDO,
        bd=0,
        relief="flat",
        cursor="hand2"
    )

    botao.grid(
        row=indice // 4,
        column=indice % 4,
        sticky="nsew",
        padx=4,
        pady=4,
        ipady=8
    )

for coluna in range(4):
    painel.columnconfigure(coluna, weight=1)

for linha in range(5):
    painel.rowconfigure(linha, weight=1)


# ==========================================
# HISTORICO DE CALCULOS
# ==========================================

titulo_historico = tk.Label(
    janela,
    text="HISTORICO DE CALCULOS",
    font=("Arial", 10, "bold"),
    bg=FUNDO,
    fg=OPERADOR
)
titulo_historico.pack(anchor="w", padx=16, pady=(0, 6))

lista_historico = tk.Listbox(
    janela,
    height=5,
    font=("Consolas", 10),
    bg=VISOR_COR,
    fg=BRANCO,
    selectbackground=OPERADOR,
    selectforeground=FUNDO,
    bd=0,
    highlightthickness=0
)
lista_historico.pack(fill="x", padx=16, pady=(0, 6))

botao_limpar_historico = tk.Button(
    janela,
    text="Limpar historico",
    command=limpar_historico,
    font=("Arial", 9, "bold"),
    bg=NUMERO,
    fg=BRANCO,
    activebackground=OPERADOR,
    bd=0,
    relief="flat",
    cursor="hand2"
)
botao_limpar_historico.pack(anchor="e", padx=16, pady=(0, 12))


# ==========================================
# SUPORTE AO TECLADO
# ==========================================

def tecla_pressionada(evento):
    tecla = evento.keysym
    caractere = evento.char

    if tecla in ("Return", "KP_Enter", "equal"):
        calcular()
        return "break"

    if tecla in ("BackSpace",):
        apagar()
        return "break"

    if tecla == "Escape":
        limpar()
        return "break"

    if caractere in "0123456789.":
        adicionar(caractere)
        return "break"

    if caractere in "+-*/":
        adicionar(caractere)
        return "break"


janela.bind("<Key>", tecla_pressionada)

# Iniciar a aplicacao
janela.mainloop()

