# 📋 Estrutura e Componentes do Projeto

## Arquitetura Geral

```
processamento-digital-de-imagens/
│
├── src/                              # Código-fonte principal
│   ├── __init__.py                  # Pacote Python
│   ├── main.py                      # Script principal (CLI + lote)
│   ├── utils.py                     # Funções auxiliares (NMS, Histerese, I/O)
│   ├── canny_classic.py             # Implementação Canny Clássico (Escalar)
│   └── canny_modificado.py          # Implementação Canny Modificado (Gabor-Di Zenzo)
│
├── config/                           # Configurações (JSON)
│   ├── params.json                  # Configuração padrão
│   ├── params_sensivel.json         # Detecção mais agressiva
│   └── params_robusta.json          # Detecção mais conservadora
│
├── imagens/                          # Dataset de entrada
│   ├── GrayAndMagenta.png           # Teste primário (bordas cromáticas)
│   ├── Bear.jpg
│   ├── FCBarcelona.png
│   ├── PlacaMercosul.webp
│   ├── VintageCar.jpg
│   └── Zebra.jpg
│
├── resultados/                       # Saída dos algoritmos
│   ├── [image]_canny_classic.png
│   ├── [image]_canny_modificado.png
│   └── [image]_comparacao.png
│
├── demo.ipynb                        # Notebook Jupyter interativo
├── requirements.txt                  # Dependências Python
├── .gitignore                        # Git ignore
├── README.md                         # Documentação completa
├── QUICKSTART.md                     # Este arquivo
├── ARCHITECTURE.md                   # Detalhes técnicos
└── Relatorio_PDI.pdf                # Relatório completo (quando pronto)
```

---

## Componentes Principais

### 1️⃣ `src/utils.py` - Funções Auxiliares

**Funções principais:**

- `read_image()` - Carrega imagem (RGB, 8-bit)
- `save_image()` - Salva resultado como PNG
- `rgb_to_gray()` - Conversão linear RGB → Cinza
- `apply_gaussian_blur()` - Desfoque Gaussiano (NumPy)
- `compute_sobel_gradients()` - Operador Sobel (implementado)
- `non_maximum_suppression()` - NMS para afinar bordas
- `hysteresis_thresholding()` - Ligação de bordas com 2 limiares

---

### 2️⃣ `src/canny_classic.py` - Canny Tradicional

**Pipeline:**

```
RGB Image
    ↓
Convert to Gray (0.299R + 0.587G + 0.114B)
    ↓
Gaussian Blur (σ = 1.0)
    ↓
Sobel Gradients (Magnitude + Direction)
    ↓
Non-Maximum Suppression (afina bordas)
    ↓
Hysteresis Thresholding (T_low=100, T_high=200)
    ↓
Binary Edge Map (uint8)
```

**Classe: `CannyClassic`**

```python
detector = CannyClassic(sigma=1.0, kernel_size=5,
                       low_threshold=100, high_threshold=200)
edges = detector.detect(image_rgb)
```

**Problema:** Perde bordas cromáticas (ex: vermelho ↔ azul em cinza)

---

### 3️⃣ `src/canny_modificado.py` - Canny Modificado (Gabor-Di Zenzo)

#### Componente A: `GaborFilterBank`

Gera banco de filtros de Gabor com múltiplas orientações e frequências:

```
num_orientations × num_frequencies filtros
```

Cada filtro: envelope Gaussiano × onda senoidal rotacionada

**Parâmetros:**

- `num_orientations` (padrão: 8) - 0° a 180°
- `num_frequencies` (padrão: 3) - Múltiplas escalas
- `sigma` - Tamanho do envelope
- `lambda_base` - Comprimento de onda base

#### Componente B: `DiZenzoOperator`

Processamento vetorial de imagens coloridas:

```
Canal R, G, B
    ↓
Compute ∇R, ∇G, ∇B (gradientes)
    ↓
Structure Tensor (2×2 matrix de covariância)
    ↓
Eigenvalues & Eigenvectors
    ↓
Max eigenvalue → Magnitude
    ↓
Eigenvector → Direction
```

Preserva **contraste puramente cromático** (sem precisa de conversão para cinza)

#### Componente C: `CannyModificado`

**Pipeline Completo:**

```
RGB Image (preserva cor)
    ├─→ Di Zenzo Operator
    │    └─→ Magnitude (contraste cromático)
    │
    ├─→ Gabor Filter Bank (por canal)
    │    └─→ Energy responses
    │
    └─→ Fusion
         ├─→ max(Di Zenzo, Gabor)
         ├─→ NMS
         ├─→ Hysteresis
         └─→ Binary Edge Map
```

**Classe: `CannyModificado`**

```python
detector = CannyModificado(
    sigma_blur=1.0,
    num_gabor_orientations=8,
    num_gabor_frequencies=3,
    low_threshold=100, high_threshold=200
)
edges = detector.detect(image_rgb)
```

**Vantagem:** Detecta bordas invisíveis no Canny clássico

---

### 4️⃣ `src/main.py` - Interface CLI e Lote

**Modos de execução:**

1. **Imagem única:**

   ```bash
   python main.py --imagem imagens/GrayAndMagenta.png --metodo both
   ```

2. **Processamento em lote:**

   ```bash
   python main.py --diretorio imagens --metodo both
   ```

3. **Configurações customizadas:**
   ```bash
   python main.py --config config/params_sensivel.json
   ```

**Argumentos:**

- `--imagem` - Caminho da imagem única
- `--diretorio` - Pasta com múltiplas imagens
- `--metodo` - `classic`, `modificado`, ou `both`
- `--config` - Arquivo de configuração JSON
- `--output` - Pasta de saída

---

## Fluxo de Dados

```
                    INPUT
                      ↓
            ┌─────────┴─────────┐
            ↓                   ↓
    [CannyClassic]   [CannyModificado]
            ↓                   ↓
        Grayscale         Color Vectors
            ↓                   ↓
        Sobel Gradient    Gabor + Di Zenzo
            ↓                   ↓
            NMS ←─────────────→ NMS
            ↓                   ↓
        Hysteresis ←──────→ Hysteresis
            ↓                   ↓
        Binary Edges ←────→ Binary Edges
            ↓                   ↓
            └─────────┬─────────┘
                      ↓
              COMPARISON & SAVE
                      ↓
                    OUTPUT
                  (PNG files)
```

---

## Configurações Predefinidas

### `params.json` (Padrão)

- Equilibrado para a maioria das imagens
- Bom para detecção geral

### `params_sensivel.json` (Agressivo)

- Detecta mais bordas (inclusive fracas)
- Mais falsos positivos
- Ideal para imagens de baixo contraste

### `params_robusta.json` (Conservador)

- Menos bordas (apenas as fortes)
- Menos ruído
- Ideal para imagens com muito ruído

---

## Restrições de Implementação

✅ **Implementado do zero (NumPy only):**

- Convolução (Sobel, Gaussiano, Gabor)
- NMS
- Hysteresis
- Di Zenzo (álgebra linear)

❌ **NÃO utilizados:**

- `cv2.Canny`
- `cv2.filter2D`
- `cv2.getGaborKernel`
- OpenCV image processing (apenas I/O)
- SciPy convolve

---

## Complexidade Computacional

| Operação             | Complexidade | Tempo (1920×1080) |
| -------------------- | ------------ | ----------------- |
| Gaussian Blur        | O(H×W×K²)    | ~50ms             |
| Sobel Gradients      | O(H×W)       | ~30ms             |
| NMS                  | O(H×W)       | ~20ms             |
| Hysteresis           | O(H×W)       | ~40ms             |
| Gabor Bank           | O(H×W×F×K²)  | ~500ms            |
| Di Zenzo             | O(H×W)       | ~100ms            |
| **Total Clássico**   | -            | **~140ms**        |
| **Total Modificado** | -            | **~650ms**        |

---

## Próximas Melhorias

- [ ] Otimização com Cython/NumPy vectorization
- [ ] GPU suporte (CuPy/PyTorch)
- [ ] Detecção automática de limiares (Otsu)
- [ ] Filtros anisotrópicos adaptativos
- [ ] Interface gráfica (tkinter/PyQt)
