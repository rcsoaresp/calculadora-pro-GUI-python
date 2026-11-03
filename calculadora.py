"""
Calculadora Completa com Interface Gráfica em Python (Tkinter)
Arquitetura Modular: Motor de Cálculo Matemático Seguro (AST) + Camada de Apresentação Visual.
Suporta operações básicas, porcentagem avançada, raiz quadrada, exponenciação, temas Claro/Escuro em tempo real,
display duplo com histórico, feedback sonoro e teclas realistas com efeito 3D.
"""

import ast
import math
import operator
import re
import threading
import tkinter as tk
from typing import Optional, Tuple


# ==============================================================================
# 1. MOTOR MATEMÁTICO E REGRAS DE NEGÓCIO (LÓGICA DESACOPLADA)
# ==============================================================================

class MotorCalculadora:
    """
    Núcleo matemático da calculadora.
    Isola todas as operações de parsing, AST e regras de negócio da interface gráfica.
    """

    OPERADORES_SUPORTADOS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    @classmethod
    def avaliar_nodo(cls, nodo) -> float:
        """Avalia nós da árvore sintática (AST) admitindo apenas aritmética pura."""
        if isinstance(nodo, ast.Expression):
            return cls.avaliar_nodo(nodo.body)
        elif isinstance(nodo, ast.Constant):
            if isinstance(nodo.value, (int, float)):
                return float(nodo.value)
            raise ValueError("Constante não numérica.")
        elif isinstance(nodo, ast.BinOp):
            tipo_op = type(nodo.op)
            if tipo_op not in cls.OPERADORES_SUPORTADOS:
                raise ValueError(f"Operador binário não suportado: {tipo_op}")
            esquerda = cls.avaliar_nodo(nodo.left)
            direita = cls.avaliar_nodo(nodo.right)
            return cls.OPERADORES_SUPORTADOS[tipo_op](esquerda, direita)
        elif isinstance(nodo, ast.UnaryOp):
            tipo_op = type(nodo.op)
            if tipo_op not in cls.OPERADORES_SUPORTADOS:
                raise ValueError(f"Operador unário não suportado: {tipo_op}")
            operando = cls.avaliar_nodo(nodo.operand)
            return cls.OPERADORES_SUPORTADOS[tipo_op](operando)
        raise ValueError(f"Expressão não autorizada: {type(nodo)}")

    @classmethod
    def formatar_numero(cls, valor: float) -> str:
        """
        Formata o número limitando a precisão a 10 casas decimais para evitar estouro
        de tela e drift de ponto flutuante (IEEE 754), removendo zeros desnecessários.
        Exemplo: 5.0 -> '5', 0.1 + 0.2 -> '0.3'.
        """
        if isinstance(valor, float):
            if valor.is_integer():
                return str(int(valor))
            arredondado = round(valor, 10)
            if arredondado.is_integer():
                return str(int(arredondado))
            texto = f"{arredondado:.10f}".rstrip('0').rstrip('.')
            return texto
        return str(valor)

    @classmethod
    def normalizar_porcentagem(cls, expressao: str) -> str:
        """
        Converte notações de porcentagem para aritmética padrão:
        - 1000 - 10% -> 1000 - (1000 * (10 / 100)) = 900
        - 1000 + 10% -> 1000 + (1000 * (10 / 100)) = 1100
        - 1000 * 10% -> 1000 * (10 / 100) = 100
        - 1000 / 10% -> 1000 / (10 / 100) = 10000
        - 50% avulso -> (50 / 100) = 0.5
        """
        # Trata Adição e Subtração percentual: A + B% ou A - B%
        padrao_aditivo = r'(\d+(?:\.\d+)?)\s*([+\-])\s*(\d+(?:\.\d+)?)\s*%'
        while re.search(padrao_aditivo, expressao):
            expressao = re.sub(padrao_aditivo, r'(\1 \2 (\1 * (\3 / 100)))', expressao)

        # Trata Multiplicação e Divisão percentual: A * B% ou A / B%
        padrao_mult = r'([*\/×÷])\s*(\d+(?:\.\d+)?)\s*%'
        expressao = re.sub(padrao_mult, r'\1 (\2 / 100)', expressao)

        # Trata porcentagem avulsa: B%
        padrao_avulso = r'(\d+(?:\.\d+)?)\s*%'
        expressao = re.sub(padrao_avulso, r'(\1 / 100)', expressao)

        return expressao

    @classmethod
    def resolver_expressao(cls, expressao: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Avalia uma expressão matemática com proteção completa contra erros:
        Retorna (resultado_formatado, erro).
        """
        if not expressao or expressao.strip() == "":
            return "0", None

        # Normaliza porcentagens
        expr_normalizada = cls.normalizar_porcentagem(expressao)

        # Converte operadores visuais para operadores Python
        expr_python = (
            expr_normalizada
            .replace('×', '*')
            .replace('÷', '/')
            .replace('^', '**')
        )

        try:
            arvore = ast.parse(expr_python, mode='eval')
            resultado_bruto = cls.avaliar_nodo(arvore)
            return cls.formatar_numero(resultado_bruto), None
        except ZeroDivisionError:
            return None, "Divisão por zero"
        except Exception:
            return None, "Entrada inválida"

    @classmethod
    def raiz_quadrada(cls, valor_str: str) -> Tuple[Optional[str], Optional[str]]:
        """Calcula a raiz quadrada de um número com proteção contra valores negativos."""
        try:
            val = float(valor_str)
            if val < 0:
                return None, "Entrada inválida"
            res = math.sqrt(val)
            return cls.formatar_numero(res), None
        except Exception:
            return None, "Entrada inválida"

    @classmethod
    def elevar_ao_quadrado(cls, valor_str: str) -> Tuple[Optional[str], Optional[str]]:
        """Calcula x² para o valor fornecido."""
        try:
            val = float(valor_str)
            res = val ** 2
            return cls.formatar_numero(res), None
        except Exception:
            return None, "Entrada inválida"

    @classmethod
    def inverter_sinal(cls, valor_str: str) -> str:
        """Inverte o sinal do número (+/-)."""
        try:
            val = float(valor_str)
            return cls.formatar_numero(-val)
        except Exception:
            return valor_str

    @classmethod
    def pode_inserir_ponto(cls, texto_atual: str) -> bool:
        """Verifica se o operando numérico atual já possui ponto decimal."""
        partes = re.split(r'[+\-×÷\^]', texto_atual)
        ultimo_termo = partes[-1] if partes else ""
        return "." not in ultimo_termo


# ==============================================================================
# 2. FEEDBACK AUDITIVO E SONORO (TOM SUAVE)
# ==============================================================================

def emitir_feedback_sonoro():
    """Emite um tom suave e curto ao pressionar teclas (executado em thread desacoplada)."""
    def _beep():
        try:
            import winsound
            # Frequência suave (900 Hz), duração ultracurta (18ms)
            winsound.Beep(900, 18)
        except Exception:
            pass

    threading.Thread(target=_beep, daemon=True).start()


# ==============================================================================
# 3. INTERFACE GRÁFICA (TKINTER) E DESIGN REALISTA
# ==============================================================================

class CalculadoraGUI:
    """Gerencia a janela, display duplo, teclas 3D e controle de temas."""

    # Paletas de cores equilibradas e com alto contraste
    TEMAS = {
        "dark": {
            "nome": "dark",
            "bg": "#18181b",               # Fundo geral grafite profundo
            "header_bg": "#18181b",
            "display_bg": "#09090b",        # Fundo do display preto ônix
            "display_border": "#27272a",
            "display_fg": "#f4f4f5",        # Texto do visor branco puro
            "historico_fg": "#a1a1aa",      # Texto do histórico cinza médio
            "slicer_bg": "#27272a",
            "slicer_active": "#3b82f6",     # Azul vibrante no tema ativo
            "slicer_fg": "#e4e4e7",
            # Cores de botões (Fundo, Texto, Borda 3D ativa)
            "btn_num_bg": "#27272a",
            "btn_num_fg": "#fafafa",
            "btn_num_active": "#3f3f46",
            "btn_op_bg": "#2563eb",         # Azul para operadores principais
            "btn_op_fg": "#ffffff",
            "btn_op_active": "#1d4ed8",
            "btn_func_bg": "#3f3f46",       # Cinza neutro para funções científicas
            "btn_func_fg": "#f4f4f5",
            "btn_func_active": "#52525b",
            "btn_clear_bg": "#dc2626",      # Vermelho para limpeza
            "btn_clear_fg": "#ffffff",
            "btn_clear_active": "#b91c1c",
            "btn_back_bg": "#ea580c",       # Laranja para apagar
            "btn_back_fg": "#ffffff",
            "btn_back_active": "#c2410c",
            "btn_equal_bg": "#059669",      # Verde esmeralda para resultado
            "btn_equal_fg": "#ffffff",
            "btn_equal_active": "#047857",
        },
        "light": {
            "nome": "light",
            "bg": "#f4f4f5",               # Fundo cinza suave
            "header_bg": "#f4f4f5",
            "display_bg": "#ffffff",        # Display branco puro
            "display_border": "#e4e4e7",
            "display_fg": "#09090b",        # Texto preto nítido
            "historico_fg": "#71717a",      # Histórico cinza grafite
            "slicer_bg": "#e4e4e7",
            "slicer_active": "#2563eb",
            "slicer_fg": "#18181b",
            # Cores de botões
            "btn_num_bg": "#ffffff",
            "btn_num_fg": "#18181b",
            "btn_num_active": "#e4e4e7",
            "btn_op_bg": "#2563eb",
            "btn_op_fg": "#ffffff",
            "btn_op_active": "#1d4ed8",
            "btn_func_bg": "#e4e4e7",
            "btn_func_fg": "#18181b",
            "btn_func_active": "#d4d4d8",
            "btn_clear_bg": "#ef4444",
            "btn_clear_fg": "#ffffff",
            "btn_clear_active": "#dc2626",
            "btn_back_bg": "#f97316",
            "btn_back_fg": "#ffffff",
            "btn_back_active": "#ea580c",
            "btn_equal_bg": "#10b981",
            "btn_equal_fg": "#ffffff",
            "btn_equal_active": "#059669",
        }
    }

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Calculadora Python Pro")
        self.root.geometry("380x560")
        self.root.resizable(False, False)

        # Estado da Calculadora
        self.tema_atual = "dark"
        self.motor = MotorCalculadora
        self.novo_calculo = True  # Flag para resetar visor após calcular resultado

        # Variáveis Reativas
        self.historico_var = tk.StringVar(value="")
        self.visor_var = tk.StringVar(value="0")

        # Registro de botões para re-estilização dinâmica
        self.botoes_widgets = {}

        # Construção da Interface
        self.criar_cabecalho_slicer()
        self.criar_display_duplo()
        self.criar_grade_botoes()
        self.vincular_atalhos_teclado()

        # Aplica o tema inicial
        self.aplicar_tema(self.tema_atual)

    # --------------------------------------------------------------------------
    # CONTROLE SLICER DE TEMA (MODO CLARO ☀️ / MODO ESCURO 🌙)
    # --------------------------------------------------------------------------
    def criar_cabecalho_slicer(self):
        """Cria a barra superior contendo o slicer interativo de alternância de tema."""
        self.header_frame = tk.Frame(self.root, pady=8, padx=14)
        self.header_frame.pack(fill="x")

        # Título discreto
        self.label_titulo = tk.Label(
            self.header_frame,
            text="CALCULADORA",
            font=("Segoe UI", 10, "bold"),
            letterspacing=1 if hasattr(tk.Label, 'letterspacing') else None
        )
        self.label_titulo.pack(side="left")

        # Cápsula Slicer (Alternador ☀️ / 🌙)
        self.slicer_container = tk.Frame(self.header_frame, bd=1, relief="ridge", padx=2, pady=2)
        self.slicer_container.pack(side="right")

        self.btn_slicer_claro = tk.Button(
            self.slicer_container,
            text="☀️ Claro",
            font=("Segoe UI", 8, "bold"),
            bd=0,
            padx=8,
            pady=2,
            cursor="hand2",
            command=lambda: self.alternar_tema("light")
        )
        self.btn_slicer_claro.pack(side="left")

        self.btn_slicer_escuro = tk.Button(
            self.slicer_container,
            text="🌙 Escuro",
            font=("Segoe UI", 8, "bold"),
            bd=0,
            padx=8,
            pady=2,
            cursor="hand2",
            command=lambda: self.alternar_tema("dark")
        )
        self.btn_slicer_escuro.pack(side="left")

    def alternar_tema(self, novo_tema: str):
        """Alterna o tema em tempo real."""
        if self.tema_atual != novo_tema:
            emitir_feedback_sonoro()
            self.aplicar_tema(novo_tema)

    def aplicar_tema(self, nome_tema: str):
        """Aplica cores aos elementos da interface."""
        self.tema_atual = nome_tema
        t = self.TEMAS[nome_tema]

        # Janela e cabeçalho
        self.root.config(bg=t["bg"])
        self.header_frame.config(bg=t["header_bg"])
        self.label_titulo.config(bg=t["header_bg"], fg=t["historico_fg"])

        # Slicer
        self.slicer_container.config(bg=t["slicer_bg"])
        if nome_tema == "light":
            self.btn_slicer_claro.config(bg=t["slicer_active"], fg="#ffffff")
            self.btn_slicer_escuro.config(bg=t["slicer_bg"], fg=t["slicer_fg"])
        else:
            self.btn_slicer_escuro.config(bg=t["slicer_active"], fg="#ffffff")
            self.btn_slicer_claro.config(bg=t["slicer_bg"], fg=t["slicer_fg"])

        # Display duplo
        self.display_frame.config(bg=t["display_bg"], highlightbackground=t["display_border"])
        self.historico_label.config(bg=t["display_bg"], fg=t["historico_fg"])
        self.visor_entry.config(
            bg=t["display_bg"],
            readonlybackground=t["display_bg"],
            disabledbackground=t["display_bg"],
            selectbackground=t["slicer_active"],
            selectforeground="#ffffff",
            fg=t["display_fg"],
            insertbackground=t["display_fg"]
        )

        # Frame de botões
        self.grid_frame.config(bg=t["bg"])

        # Teclas da grade com relevo 3D
        for rotulo, btn in self.botoes_widgets.items():
            if rotulo in ['+', '-', '×', '÷', '^']:
                bg_cor = t["btn_op_bg"]
                fg_cor = t["btn_op_fg"]
                active_bg = t["btn_op_active"]
            elif rotulo == '=':
                bg_cor = t["btn_equal_bg"]
                fg_cor = t["btn_equal_fg"]
                active_bg = t["btn_equal_active"]
            elif rotulo in ['C', 'CE']:
                bg_cor = t["btn_clear_bg"]
                fg_cor = t["btn_clear_fg"]
                active_bg = t["btn_clear_active"]
            elif rotulo == '⌫':
                bg_cor = t["btn_back_bg"]
                fg_cor = t["btn_back_fg"]
                active_bg = t["btn_back_active"]
            elif rotulo in ['√x', 'x²', '%', '±']:
                bg_cor = t["btn_func_bg"]
                fg_cor = t["btn_func_fg"]
                active_bg = t["btn_func_active"]
            else:  # Dígitos numéricos e ponto decimal
                bg_cor = t["btn_num_bg"]
                fg_cor = t["btn_num_fg"]
                active_bg = t["btn_num_active"]

            btn.config(
                bg=bg_cor,
                fg=fg_cor,
                activebackground=active_bg,
                activeforeground="#ffffff",
                relief="raised",
                bd=3
            )

    # --------------------------------------------------------------------------
    # DISPLAY DUPLO (HISTÓRICO SUPERIOR + VISOR PRINCIPAL DESTACADO)
    # --------------------------------------------------------------------------
    def criar_display_duplo(self):
        """Cria display integrado com histórico da expressão e valor atual."""
        self.display_frame = tk.Frame(
            self.root,
            bd=0,
            highlightthickness=1,
            padx=16,
            pady=10
        )
        self.display_frame.pack(fill="x", padx=14, pady=(0, 10))

        # Linha 1: Histórico da expressão em andamento
        self.historico_label = tk.Label(
            self.display_frame,
            textvariable=self.historico_var,
            font=("Segoe UI", 11),
            anchor="e"
        )
        self.historico_label.pack(fill="x")

        # Linha 2: Visor principal de resultado com tipografia destacada
        self.visor_entry = tk.Entry(
            self.display_frame,
            textvariable=self.visor_var,
            font=("Segoe UI", 26, "bold"),
            justify="right",
            bd=0,
            highlightthickness=0,
            state="readonly"  # Somente leitura para evitar edição descontrolada
        )
        self.visor_entry.pack(fill="x", pady=(2, 0))

    # --------------------------------------------------------------------------
    # GRADE DE BOTÕES REALISTAS EM 3D (MATRIZ 6x4)
    # --------------------------------------------------------------------------
    def criar_grade_botoes(self):
        """Monta a grade 6x4 com efeito realista em relevo (raised/sunken)."""
        self.grid_frame = tk.Frame(self.root, padx=14, pady=4)
        self.grid_frame.pack(fill="both", expand=True, pady=(0, 10))

        # Matriz declarativa de teclas: 6 linhas x 4 colunas
        matriz = [
            [('C', self.limpar_tudo), ('CE', self.limpar_visor), ('⌫', self.apagar_ultimo), ('÷', lambda: self.inserir_operador('÷'))],
            [('√x', self.executar_raiz), ('x²', self.executar_quadrado), ('^', lambda: self.inserir_operador('^')), ('%', self.inserir_porcentagem)],
            [('7', lambda: self.inserir_digito('7')), ('8', lambda: self.inserir_digito('8')), ('9', lambda: self.inserir_digito('9')), ('×', lambda: self.inserir_operador('×'))],
            [('4', lambda: self.inserir_digito('4')), ('5', lambda: self.inserir_digito('5')), ('6', lambda: self.inserir_digito('6')), ('-', lambda: self.inserir_operador('-'))],
            [('1', lambda: self.inserir_digito('1')), ('2', lambda: self.inserir_digito('2')), ('3', lambda: self.inserir_digito('3')), ('+', lambda: self.inserir_operador('+'))],
            [('±', self.inverter_sinal), ('0', lambda: self.inserir_digito('0')), ('.', self.inserir_ponto), ('=', self.calcular_resultado)]
        ]

        for i in range(4):
            self.grid_frame.grid_columnconfigure(i, weight=1)
        for i in range(6):
            self.grid_frame.grid_rowconfigure(i, weight=1)

        for linha_idx, linha in enumerate(matriz):
            for col_idx, (rotulo, acao) in enumerate(linha):
                btn = tk.Button(
                    self.grid_frame,
                    text=rotulo,
                    font=("Segoe UI", 13, "bold"),
                    cursor="hand2",
                    command=lambda a=acao: self.acionar_tecla(a)
                )
                btn.grid(row=linha_idx, column=col_idx, padx=4, pady=4, sticky="nsew")
                self.botoes_widgets[rotulo] = btn

    def acionar_tecla(self, comando):
        """Emite o som suave de clique físico e dispara o comando associado."""
        emitir_feedback_sonoro()
        comando()

    # --------------------------------------------------------------------------
    # CONTROLES DE ENTRADA E OPERAÇÕES DA CALCULADORA
    # --------------------------------------------------------------------------
    def definir_visor(self, texto: str):
        """Atualiza o visor permitindo escrita em campo somente leitura."""
        self.visor_entry.config(state="normal")
        self.visor_var.set(texto)
        self.visor_entry.config(state="readonly")
        self.novo_calculo = False

    def inserir_digito(self, digito: str):
        """Insere dígitos de 0 a 9."""
        texto_atual = self.visor_var.get()

        # Se acabou de calcular ou visor contém mensagem de erro/zero inicial
        if self.novo_calculo or texto_atual == "0" or "inválida" in texto_atual or "zero" in texto_atual:
            self.definir_visor(digito)
            self.novo_calculo = False
        else:
            self.definir_visor(texto_atual + digito)

    def inserir_ponto(self):
        """Insere ponto decimal com proteção contra inserções repetidas no mesmo número."""
        texto_atual = self.visor_var.get().strip()

        if self.novo_calculo or texto_atual == "0" or "inválida" in texto_atual or "zero" in texto_atual:
            self.definir_visor("0.")
            self.novo_calculo = False
            return

        # Se o último caractere for operador, inicia o novo número como '0.'
        if texto_atual[-1] in ['+', '-', '×', '÷', '^']:
            self.definir_visor(texto_atual + " 0.")
            return

        # Bloqueia inserção repetida caso o termo numérico atual já possua ponto
        if self.motor.pode_inserir_ponto(texto_atual):
            self.definir_visor(texto_atual + ".")

    def inserir_operador(self, operador: str):
        """Insere operador aritmético (+, -, ×, ÷, ^) com espaçamento limpo."""
        texto_atual = self.visor_var.get().strip()

        if "inválida" in texto_atual or "zero" in texto_atual:
            return

        self.novo_calculo = False

        # Se o texto já terminar com operador, substitui pelo novo
        if texto_atual and texto_atual[-1] in ['+', '-', '×', '÷', '^']:
            self.definir_visor(texto_atual[:-1] + operador + " ")
        else:
            self.definir_visor(texto_atual + f" {operador} ")

    def inserir_porcentagem(self):
        """Insere o símbolo de porcentagem (%)."""
        texto_atual = self.visor_var.get().strip()
        if "inválida" in texto_atual or "zero" in texto_atual:
            return

        # Só adiciona se o último caractere for dígito
        if texto_atual and (texto_atual[-1].isdigit() or texto_atual[-1] == '.'):
            self.definir_visor(texto_atual + "%")
            self.novo_calculo = False

    def executar_raiz(self):
        """Calcula a raiz quadrada (√x) do valor atual."""
        texto_atual = self.visor_var.get().strip()
        resultado, erro = self.motor.raiz_quadrada(texto_atual)

        if erro:
            self.historico_var.set(f"√({texto_atual})")
            self.definir_visor(erro)
        else:
            self.historico_var.set(f"√({texto_atual}) = {resultado}")
            self.definir_visor(resultado)

        self.novo_calculo = True

    def executar_quadrado(self):
        """Calcula x² do valor atual."""
        texto_atual = self.visor_var.get().strip()
        resultado, erro = self.motor.elevar_ao_quadrado(texto_atual)

        if erro:
            self.definir_visor(erro)
        else:
            self.historico_var.set(f"sqr({texto_atual}) = {resultado}")
            self.definir_visor(resultado)

        self.novo_calculo = True

    def inverter_sinal(self):
        """Inverte o sinal (+/-) do valor no visor."""
        texto_atual = self.visor_var.get().strip()
        if "inválida" in texto_atual or "zero" in texto_atual:
            return
        novo_valor = self.motor.inverter_sinal(texto_atual)
        self.definir_visor(novo_valor)

    def apagar_ultimo(self):
        """Apaga o último caractere digitado (botão ⌫ / Backspace)."""
        texto_atual = self.visor_var.get().strip()
        if len(texto_atual) > 1 and "inválida" not in texto_atual and "zero" not in texto_atual:
            novo_texto = texto_atual[:-1].rstrip()
            self.definir_visor(novo_texto if novo_texto else "0")
        else:
            self.definir_visor("0")

    def limpar_visor(self):
        """Limpa o visor atual (botão CE)."""
        self.definir_visor("0")

    def limpar_tudo(self):
        """Limpa o visor e o histórico (botão C)."""
        self.historico_var.set("")
        self.definir_visor("0")
        self.novo_calculo = True

    def calcular_resultado(self):
        """
        Calcula o resultado final da expressão em andamento.
        Atualiza o visor e o display de histórico superior (ex: '1000 - 10% = 900').
        """
        expressao = self.visor_var.get().strip()

        if "inválida" in expressao or "zero" in expressao:
            return

        resultado, erro = self.motor.resolver_expressao(expressao)

        # Normaliza espaços na expressão exibida no histórico
        expr_formatada = re.sub(r'\s*([+\-×÷^])\s*', r' \1 ', expressao)
        expr_formatada = re.sub(r'\s*%', '%', expr_formatada)

        if erro:
            self.historico_var.set(f"{expr_formatada} =")
            self.definir_visor(erro)
        else:
            self.historico_var.set(f"{expr_formatada} = {resultado}")
            self.definir_visor(resultado)

        self.novo_calculo = True

    # --------------------------------------------------------------------------
    # ATALHOS DE TECLADO FÍSICO E NUMPAD
    # --------------------------------------------------------------------------
    def vincular_atalhos_teclado(self):
        """Vincula todas as teclas físicas e do teclado numérico (Numpad)."""
        # Dígitos
        for digito in range(10):
            self.root.bind(str(digito), lambda e, d=str(digito): self.acionar_tecla(lambda: self.inserir_digito(d)))
            self.root.bind(f"<KP_{digito}>", lambda e, d=str(digito): self.acionar_tecla(lambda: self.inserir_digito(d)))

        # Operadores
        self.root.bind("+", lambda e: self.acionar_tecla(lambda: self.inserir_operador("+")))
        self.root.bind("<KP_Add>", lambda e: self.acionar_tecla(lambda: self.inserir_operador("+")))
        self.root.bind("-", lambda e: self.acionar_tecla(lambda: self.inserir_operador("-")))
        self.root.bind("<KP_Subtract>", lambda e: self.acionar_tecla(lambda: self.inserir_operador("-")))
        self.root.bind("*", lambda e: self.acionar_tecla(lambda: self.inserir_operador("×")))
        self.root.bind("<KP_Multiply>", lambda e: self.acionar_tecla(lambda: self.inserir_operador("×")))
        self.root.bind("/", lambda e: self.acionar_tecla(lambda: self.inserir_operador("÷")))
        self.root.bind("<KP_Divide>", lambda e: self.acionar_tecla(lambda: self.inserir_operador("÷")))
        self.root.bind("^", lambda e: self.acionar_tecla(lambda: self.inserir_operador("^")))
        self.root.bind("%", lambda e: self.acionar_tecla(self.inserir_porcentagem))

        # Ponto e vírgula decimal
        self.root.bind(".", lambda e: self.acionar_tecla(self.inserir_ponto))
        self.root.bind(",", lambda e: self.acionar_tecla(self.inserir_ponto))
        self.root.bind("<KP_Decimal>", lambda e: self.acionar_tecla(self.inserir_ponto))

        # Ações
        self.root.bind("<Return>", lambda e: self.acionar_tecla(self.calcular_resultado))
        self.root.bind("<KP_Enter>", lambda e: self.acionar_tecla(self.calcular_resultado))
        self.root.bind("=", lambda e: self.acionar_tecla(self.calcular_resultado))
        self.root.bind("<BackSpace>", lambda e: self.acionar_tecla(self.apagar_ultimo))
        self.root.bind("<Escape>", lambda e: self.acionar_tecla(self.limpar_tudo))
        self.root.bind("<Delete>", lambda e: self.acionar_tecla(self.limpar_visor))

        # Atalhos auxiliares
        self.root.bind("r", lambda e: self.acionar_tecla(self.executar_raiz))
        self.root.bind("R", lambda e: self.acionar_tecla(self.executar_raiz))
        self.root.bind("q", lambda e: self.acionar_tecla(self.executar_quadrado))
        self.root.bind("Q", lambda e: self.acionar_tecla(self.executar_quadrado))


# ==============================================================================
# 4. INICIALIZAÇÃO DA APLICAÇÃO
# ==============================================================================
if __name__ == "__main__":
    janela_raiz = tk.Tk()
    app = CalculadoraGUI(janela_raiz)
    janela_raiz.mainloop()
