# 🧮 Calculadora Pro com Interface Gráfica em Python

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![GUI](https://img.shields.io/badge/GUI-Tkinter-1f2937?style=for-the-badge)](https://docs.python.org/3/library/tkinter.html)
[![Plataforma](https://img.shields.io/badge/Plataforma-Windows%20%7C%20Linux%20%7C%20macOS-blue?style=for-the-badge)](https://www.python.org/)
[![Licença](https://img.shields.io/badge/Licen%C3%A7a-MIT-green.svg?style=for-the-badge)](LICENSE)

Aplicação desktop profissional de uma calculadora completa desenvolvida em **Python** utilizando a biblioteca nativa **Tkinter**. Possui arquitetura modular orientada a objetos desacoplando a lógica matemática (`MotorCalculadora`) da camada de apresentação visual (`CalculadoraGUI`), com alternador de temas Claro/Escuro em tempo real, display duplo integrado, feedback sonoro e teclas realistas em 3D.

---

## 📖 Descrição da Solução

A calculadora foi desenvolvida com foco em segurança computacional, rigor matemático e ergonomia de uso:

* **Arquitetura Modular:** Separação estrita entre o núcleo de cálculo e a interface visual. O motor de cálculo pode ser executado e testado independentemente da janela gráfica.
* **Segurança por AST (Abstract Syntax Tree):** Parser matemático construído sobre a árvore sintática do Python, garantindo que apenas operações aritméticas puras sejam avaliadas e impedindo qualquer execução de código arbitrário.
* **Display Duplo:** Linha superior dedicada ao histórico da expressão em andamento com o resultado (ex: `1000 - 10% = 900`) e linha principal em destaque tipográfico para o valor atual.
* **Alternador de Temas em Tempo Real (Slicer):** Controle deslizante estilizado permitindo alternar instantaneamente entre o **Modo Claro (☀️)** e o **Modo Escuro (🌙)** com alto contraste e harmonia de cores.
* **Teclas Realistas em 3D:** Efeito de relevo físico tátil (`raised`/`sunken`) reproduzindo a experiência de um teclado mecânico de mesa.
* **Feedback Auditivo:** Emissão de tom sonoro suave e não obstrusivo ao acionar as teclas (executado em thread paralela para manter a fluidez de 60 FPS da interface).

---

## 📊 Tabela de Operações Matemáticas Suportadas

| Operação | Símbolo Visual | Atalho Teclado | Exemplo Prático | Comportamento e Regra |
| :--- | :---: | :---: | :--- | :--- |
| **Adição** | `+` | `+` / `Numpad +` | `15 + 27 = 42` | Soma de inteiros e decimais com encadeamento de múltiplos operandos. |
| **Subtração** | `-` | `-` / `Numpad -` | `50 - 18 = 32` | Subtrações sucessivas com suporte a resultados negativos. |
| **Multiplicação** | `×` | `*` / `Numpad *` | `6 × 7 = 42` | Multiplicação de alta precisão. |
| **Divisão** | `÷` | `/` / `Numpad /` | `84 ÷ 2 = 42` | Divisão com tratamento defensivo contra divisores nulos. |
| **Porcentagem** | `%` | `%` (`Shift+5`) | `1000 - 10% = 900` | Suporte a desconto (`-`), acréscimo (`+`), produto (`×`), razão (`÷`) e valor avulso (`50% = 0.5`). |
| **Exponenciação** | `^` | `^` (`Shift+6`) | `2 ^ 3 = 8` | Potenciação com base e expoente customizáveis ($x^y$). |
| **Quadrado** | `x²` | `q` / `Q` | `sqr(5) = 25` | Elevação direta do número atual ao quadrado ($x^2$). |
| **Raiz Quadrada** | `√x` | `r` / `R` | `√(16) = 4` | Cálculo imediato da raiz quadrada com validação de domínio real. |
| **Inversão de Sinal** | `±` | — | `42` ➔ `-42` | Alterna o operando atual entre positivo e negativo. |

---

## 🛡️ Regras de Validação Matemática e Blindagem

1. **Prevenção Ativa de Divisão por Zero:**  
   Tentativas de divisão por zero (ex: `10 ÷ 0`) são interceptadas antes da propagação de erro, exibindo `"Divisão por zero"` no visor principal e preservando o estado da calculadora sem travamento.

2. **Raiz Quadrada de Números Negativos:**  
   Ao tentar calcular a raiz quadrada de um número estritamente negativo (ex: `√(-16)`), o sistema exibe `"Entrada inválida"` e mantém o histórico `√(-16)`, protegendo o domínio dos números reais.

3. **Tratamento de Casas Decimais e Precisão Numérica:**  
   * **Limitação de Casas Decimais:** Resultados são arredondados em 10 casas decimais para prevenir imperfeições inerentes à representação binária de ponto flutuante (IEEE 754), como `0.1 + 0.2 = 0.3` (evitando `0.30000000000000004`).
   * **Supressão de Zeros Redundantes:** Números inteiros resultantes de cálculos de float são normalizados (ex: `5.0` é formatado esteticamente como `5`).

4. **Bloqueio de Pontos Decimais Repetidos:**  
   A lógica de entrada inspeciona o termo numérico ativo. Caso o número em digitação já contenha um ponto decimal, pressionamentos adicionais da tecla `.` são sumariamente descartados (ex: `5..` permanece `5.`, `5.25.` permanece `5.25`).

5. **Cálculo Avançado de Porcentagem:**  
   O motor normaliza expressões percentuais respeitando a convenção de calculadoras comerciais:
   $$\text{Base} \pm \text{Pct}\% \implies \text{Base} \pm \left(\text{Base} \times \frac{\text{Pct}}{100}\right)$$
   $$\text{Exemplo: } 1000 - 10\% \implies 1000 - (1000 \times 0.10) = 900$$

---

## ⌨️ Atalhos do Teclado Físico

A interface é 100% navegável pelo teclado alfanumérico e teclado numérico dedicado (*Numpad*):

| Tecla / Combinação | Função Associada |
| :--- | :--- |
| `0` a `9` ou `Numpad 0-9` | Inserção dos dígitos numéricos |
| `.` ou `,` ou `Numpad .` | Inserção do ponto decimal |
| `+` ou `Numpad +` | Operador de Adição |
| `-` ou `Numpad -` | Operador de Subtração |
| `*` ou `Numpad *` | Operador de Multiplicação |
| `/` ou `Numpad /` | Operador de Divisão |
| `^` | Operador de Exponenciação ($x^y$) |
| `%` (`Shift + 5`) | Operador de Porcentagem |
| `r` ou `R` | Raiz Quadrada do valor atual ($\sqrt{x}$) |
| `q` ou `Q` | Quadrado do valor atual ($x^2$) |
| `Enter` ou `Numpad Enter` ou `=` | Calcular resultado final |
| `Backspace` | Apagar último caractere inserido (⌫) |
| `Delete` | Limpar visor atual (`CE`) |
| `Escape` | Limpar visor e histórico (`C`) |

---

## 🚀 Guia de Execução

### Pré-requisitos
* Python 3.8 ou superior instalado. O pacote `tkinter` já vem incluído por padrão nas distribuições oficiais de Windows e macOS.

### 1. Execução Direta
No terminal, execute o script principal:

```bash
python calculadora.py
```

### 2. Execução da Suíte de Testes Automatizados
Para rodar a bateria de testes unitários e de integração com cobertura total:

```bash
python -m unittest test_calculadora.py -v
```

### 3. Como Gerar um Executável Standalone (.exe)
É possível empacotar a aplicação em um único arquivo executável para Windows sem exigir que o usuário final tenha o Python instalado, utilizando o **PyInstaller**:

1. Instale o PyInstaller via pip:
   ```bash
   pip install pyinstaller
   ```

2. Gere o executável com as opções de arquivo único e sem janela de terminal:
   ```bash
   pyinstaller --onefile --noconsole --name="Calculadora" calculadora.py
   ```

   * **`--onefile`:** Empacota todo o interpretador Python, bibliotecas e assets em um único arquivo binário (`Calculadora.exe`).
   * **`--noconsole`:** Oculta a tela preta do prompt de comando, iniciando diretamente a janela gráfica.
   * **`--name="Calculadora"`:** Define o nome do executável final gerado dentro da pasta `dist/`.

O executável estará pronto para distribuição na pasta `dist/Calculadora.exe`.

---

## 📜 Licença

Distribuído sob a **Licença MIT**. Veja o arquivo abaixo para mais detalhes:

```text
MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
