"""
Suíte de Testes Automatizados para a Calculadora Pro Tkinter
Validação completa de operações matemáticas, porcentagem avançada, raiz quadrada,
exponenciação, tratamento de erros, temas, display duplo e atalhos de teclado.
"""

import unittest
import tkinter as tk
from calculadora import MotorCalculadora, CalculadoraGUI


class TestMotorCalculadora(unittest.TestCase):
    """Testes unitários desacoplados da lógica matemática pura (MotorCalculadora)."""

    def setUp(self):
        self.motor = MotorCalculadora

    # --------------------------------------------------------------------------
    # 1. OPERAÇÕES BÁSICAS
    # --------------------------------------------------------------------------
    def test_adicao(self):
        res, erro = self.motor.resolver_expressao("15 + 27")
        self.assertIsNone(erro)
        self.assertEqual(res, "42")

    def test_subtracao(self):
        res, erro = self.motor.resolver_expressao("50 - 18")
        self.assertIsNone(erro)
        self.assertEqual(res, "32")

    def test_multiplicacao(self):
        res, erro = self.motor.resolver_expressao("6 × 7")
        self.assertIsNone(erro)
        self.assertEqual(res, "42")

    def test_divisao_exata(self):
        res, erro = self.motor.resolver_expressao("84 ÷ 2")
        self.assertIsNone(erro)
        self.assertEqual(res, "42")

    def test_divisao_fracionaria(self):
        res, erro = self.motor.resolver_expressao("7 ÷ 2")
        self.assertIsNone(erro)
        self.assertEqual(res, "3.5")

    # --------------------------------------------------------------------------
    # 2. CÁLCULO DE PORCENTAGEM
    # --------------------------------------------------------------------------
    def test_porcentagem_subtracao_especificacao(self):
        """Validação obrigatória: 1000 - 10% = 900."""
        res, erro = self.motor.resolver_expressao("1000 - 10%")
        self.assertIsNone(erro)
        self.assertEqual(res, "900")

    def test_porcentagem_adicao(self):
        """Validação: 1000 + 10% = 1100."""
        res, erro = self.motor.resolver_expressao("1000 + 10%")
        self.assertIsNone(erro)
        self.assertEqual(res, "1100")

    def test_porcentagem_multiplicacao(self):
        """Validação: 1000 × 10% = 100."""
        res, erro = self.motor.resolver_expressao("1000 × 10%")
        self.assertIsNone(erro)
        self.assertEqual(res, "100")

    def test_porcentagem_divisao(self):
        """Validação: 1000 ÷ 10% = 10000."""
        res, erro = self.motor.resolver_expressao("1000 ÷ 10%")
        self.assertIsNone(erro)
        self.assertEqual(res, "10000")

    def test_porcentagem_avulsa(self):
        """Validação: 50% = 0.5."""
        res, erro = self.motor.resolver_expressao("50%")
        self.assertIsNone(erro)
        self.assertEqual(res, "0.5")

    # --------------------------------------------------------------------------
    # 3. OPERAÇÕES AVANÇADAS: EXPONENCIAÇÃO E RAIZ QUADRADA
    # --------------------------------------------------------------------------
    def test_exponenciacao_generica(self):
        """Validação: 2 ^ 3 = 8."""
        res, erro = self.motor.resolver_expressao("2 ^ 3")
        self.assertIsNone(erro)
        self.assertEqual(res, "8")

    def test_quadrado_imediato(self):
        """Validação: sqr(5) = 25."""
        res, erro = self.motor.elevar_ao_quadrado("5")
        self.assertIsNone(erro)
        self.assertEqual(res, "25")

    def test_raiz_quadrada_positiva(self):
        """Validação: √(16) = 4."""
        res, erro = self.motor.raiz_quadrada("16")
        self.assertIsNone(erro)
        self.assertEqual(res, "4")

    def test_raiz_quadrada_negativa_bloqueio(self):
        """Validação obrigatória: raiz de número negativo exibe 'Entrada inválida'."""
        res, erro = self.motor.raiz_quadrada("-16")
        self.assertEqual(erro, "Entrada inválida")
        self.assertIsNone(res)

    def test_inversao_sinal(self):
        """Validação: +/- de 42 vira -42, e de -42 vira 42."""
        self.assertEqual(self.motor.inverter_sinal("42"), "-42")
        self.assertEqual(self.motor.inverter_sinal("-42"), "42")
        self.assertEqual(self.motor.inverter_sinal("3.14"), "-3.14")

    # --------------------------------------------------------------------------
    # 4. TRATAMENTO DE ERROS E CASAS DECIMAIS
    # --------------------------------------------------------------------------
    def test_divisao_por_zero(self):
        """Validação obrigatória: divisão por zero exibe 'Divisão por zero'."""
        res, erro = self.motor.resolver_expressao("10 ÷ 0")
        self.assertEqual(erro, "Divisão por zero")
        self.assertIsNone(res)

    def test_tratamento_float_drift_ieee754(self):
        """Validação: 0.1 + 0.2 formatado como 0.3 (sem drift de 0.30000000000000004)."""
        res, erro = self.motor.resolver_expressao("0.1 + 0.2")
        self.assertIsNone(erro)
        self.assertEqual(res, "0.3")

    def test_normalizacao_inteiro(self):
        """Validação: 5.0 deve ser exibido como 5."""
        self.assertEqual(self.motor.formatar_numero(5.0), "5")

    def test_bloqueio_ponto_decimal_repetido(self):
        """Validação: impede inserção de múltiplos pontos no mesmo termo numérico."""
        self.assertTrue(self.motor.pode_inserir_ponto("123"))
        self.assertFalse(self.motor.pode_inserir_ponto("123.45"))
        self.assertTrue(self.motor.pode_inserir_ponto("123.45 + 67"))
        self.assertFalse(self.motor.pode_inserir_ponto("123.45 + 67.8"))

    def test_seguranca_ast_injecao(self):
        """Validação de segurança: comandos maliciosos são interceptados."""
        res, erro = self.motor.resolver_expressao("__import__('os').system('dir')")
        self.assertEqual(erro, "Entrada inválida")
        self.assertIsNone(res)


class TestCalculadoraGUI(unittest.TestCase):
    """Testes de integração da interface gráfica (CalculadoraGUI) e eventos Tkinter."""

    @classmethod
    def setUpClass(cls):
        cls.root = tk.Tk()
        cls.root.withdraw()
        cls.app = CalculadoraGUI(cls.root)

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def setUp(self):
        self.app.limpar_tudo()

    def test_fluxo_porcentagem_display_duplo(self):
        """
        Validação obrigatória completa de ponta a ponta:
        Digitar 1000 - 10 % {ENTER} -> Visor: 900, Histórico: '1000 - 10% = 900'.
        """
        for c in ['1', '0', '0', '0']:
            self.app.inserir_digito(c)
        self.app.inserir_operador('-')
        for c in ['1', '0']:
            self.app.inserir_digito(c)
        self.app.inserir_porcentagem()

        self.assertEqual(self.app.visor_var.get(), "1000 - 10%")
        self.app.calcular_resultado()

        self.assertEqual(self.app.visor_var.get(), "900")
        self.assertEqual(self.app.historico_var.get(), "1000 - 10% = 900")

    def test_fluxo_raiz_negativa_ui(self):
        """Valida que raiz de negativo no visor exibe 'Entrada inválida' sem travar a interface."""
        self.app.definir_visor("-25")
        self.app.executar_raiz()
        self.assertEqual(self.app.visor_var.get(), "Entrada inválida")
        self.assertEqual(self.app.historico_var.get(), "√(-25)")

    def test_fluxo_divisao_zero_ui(self):
        """Valida que divisão por zero exibe 'Divisão por zero'."""
        self.app.definir_visor("50 ÷ 0")
        self.app.calcular_resultado()
        self.assertEqual(self.app.visor_var.get(), "Divisão por zero")
        self.assertEqual(self.app.historico_var.get(), "50 ÷ 0 =")

    def test_alternador_tema_slicer(self):
        """Valida a alternância em tempo real entre Modo Claro (Light) e Modo Escuro (Dark) e contraste de visor."""
        self.app.alternar_tema("light")
        self.assertEqual(self.app.tema_atual, "light")
        self.assertEqual(self.app.display_frame.cget("bg"), "#ffffff")
        self.assertEqual(self.app.visor_entry.cget("readonlybackground"), "#ffffff")
        self.assertEqual(self.app.visor_entry.cget("fg"), "#09090b")

        self.app.alternar_tema("dark")
        self.assertEqual(self.app.tema_atual, "dark")
        self.assertEqual(self.app.display_frame.cget("bg"), "#09090b")
        self.assertEqual(self.app.visor_entry.cget("readonlybackground"), "#09090b")
        self.assertEqual(self.app.visor_entry.cget("fg"), "#f4f4f5")

    def test_bloqueio_pontos_consecutivos_ui(self):
        """Valida que pressionamentos repetidos de '.' são ignorados."""
        self.app.inserir_digito("7")
        self.app.inserir_ponto()
        self.app.inserir_ponto()
        self.assertEqual(self.app.visor_var.get(), "7.")

    def test_quantidade_de_botoes_grade_6x4(self):
        """Valida se todas as 24 teclas estão presentes na grade."""
        self.assertEqual(len(self.app.botoes_widgets), 24)
        esperados = [
            'C', 'CE', '⌫', '÷',
            '√x', 'x²', '^', '%',
            '7', '8', '9', '×',
            '4', '5', '6', '-',
            '1', '2', '3', '+',
            '±', '0', '.', '='
        ]
        for rotulo in esperados:
            self.assertIn(rotulo, self.app.botoes_widgets)

    def test_atalhos_teclado_numpad_registrados(self):
        """Valida presença dos atalhos de teclado essenciais vinculados."""
        atalhos = ["<Return>", "<KP_Enter>", "<BackSpace>", "<Escape>", "<KP_Add>", "<KP_Subtract>"]
        for atalho in atalhos:
            bindings = self.root.bind(atalho)
            self.assertTrue(len(bindings) > 0, f"Atalho {atalho} não foi vinculado!")


if __name__ == "__main__":
    unittest.main()
