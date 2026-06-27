# Detecção de Bordas: Canny Clássico vs. Modificado (Gabor-Di Zenzo)

Este repositório contém a implementação e a análise comparativa de algoritmos de detecção de bordas, desenvolvido como Trabalho Prático para a disciplina de **Introdução ao Processamento Digital de Imagens (2026.1)**, ministrada pelo Prof. Leonardo no Centro de Informática (CI) da UFPB.

## 📖 Sobre o Projeto

O objetivo principal deste trabalho é implementar e comparar o algoritmo clássico de Canny com uma versão modificada, que integra **Bancos de Filtros de Gabor** e a **abordagem vetorial de Di Zenzo** para o processamento de imagens coloridas.

O Canny tradicional converte imagens RGB para tons de cinza, o que frequentemente resulta na perda de informações cruciais sobre bordas cromáticas. A abordagem modificada soluciona esse problema processando a imagem de forma vetorial e fundindo as informações de cor no domínio das derivadas, preservando bordas que seriam invisíveis na versão tradicional.

### ⚠️ Restrições de Implementação

Todo o pipeline crítico de detecção foi implementado **"do zero"**, utilizando apenas a biblioteca NumPy para álgebra de matrizes. Funções prontas de bibliotecas externas de processamento de imagens (como `cv2.Canny`, `cv2.filter2D` ou `cv2.getGaborKernel`) **não** foram utilizadas.

---

## ⚙️ Metodologias Implementadas

* **Canny Tradicional (Escalar):** * Conversão linear da imagem RGB para tons de cinza.
* Cálculo de gradientes espaciais (ex: Operador de Sobel).
* Supressão de Não-Máximos (NMS) e Histerese.


* **Canny Modificado (Vetorial / Gabor-Di Zenzo):**
* Uso de Bancos de Filtros de Gabor para capturar transições de frequência e direção.
* Processamento vetorial baseado em Di Zenzo para preservar contrastes puramente cromáticos.
* Fusão de informações no domínio das derivadas.
* Supressão de Não-Máximos (NMS) e Histerese garantindo linhas finais com exatamente 1 pixel de largura.



---

## 🖼️ Imagens de Teste e Validação

O algoritmo foi testado e validado utilizando o seguinte conjunto de imagens, focando em diferentes desafios de detecção de bordas (textura, cor, contraste):

| Arquivo | Descrição / Foco da Análise |
| --- | --- |
| `GrayAndMagenta.png` | **Principal base de comparação:** Avalia a perda de bordas cromáticas no Canny padrão vs. a preservação no modelo modificado. |
| `Bear.jpg` | Análise de detecção em texturas complexas (pelagem) e iluminação natural. |
| `FCBarcelona.png` | Teste de detecção de bordas em transições de cores sólidas e geometrias bem definidas. |
| `PlacaMercosul.webp` | Avaliação de leitura de bordas de caracteres e alto contraste. |
| `VintageCar.jpg` | Reflexos, detalhes finos e variações de iluminação em superfícies metálicas. |
| `Zebra.jpg` | Teste clássico de alta frequência espacial e transições de preto e branco. |

---

## 📂 Estrutura do Repositório

```text
├── src/                      # Código-fonte principal do projeto
│   ├── canny_classic.py      # Implementação do Canny tradicional
│   ├── canny_modificado.py   # Implementação da abordagem Gabor-Di Zenzo
│   └── utils.py              # Funções auxiliares (NMS, Histerese, leitura/escrita)
├── config/                   # Arquivos JSON com configurações de parâmetros (T_high, T_low)
├── imagens/                  # Dataset fornecido para os testes
├── resultados/               # Imagens geradas pelas execuções dos algoritmos (comparativos e zoom digital)
├── Relatorio_PDI.pdf         # Relatório completo com fundamentação, discussão e justificativas
└── README.md                 # Descrição do projeto

```

---

## 🚀 Como Executar

### Pré-requisitos

Certifique-se de ter o Python 3.x instalado, juntamente com as bibliotecas necessárias para manipulação de matrizes e leitura de arquivos de imagem (como `numpy` e `Pillow`/`opencv-python` restrito apenas a I/O):

```bash
pip install -r requirements.txt

```

### Execução

Para rodar a detecção em uma imagem específica utilizando as configurações predefinidas (limiares `Thigh` e `Tlow`), execute:

```bash
# Exemplo de uso fictício da linha de comando
python src/main.py --imagem imagens/GrayAndMagenta.png --metodo modificado --config config/params.json

```

*(Substitua pelas instruções exatas de inicialização do seu código)*

---

## 👥 Equipe

* **[Renan]** - [Matrícula]
* **[João Vitor Sampaio Costa]** - 20230089776
* **[André]** - [Matrícula]
