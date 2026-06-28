# 🚀 Guia de Execução Rápida

## Opção 1: Via Terminal (Recomendado para Lote)

### Processamento de uma imagem específica

```bash
cd src
python main.py --imagem ../imagens/GrayAndMagenta.png --metodo both --config ../config/params.json
```

### Processamento de todas as imagens

```bash
cd src
python main.py --metodo both --config ../config/params.json
```

### Usando configurações diferentes

**Sensível (detecta mais bordas):**

```bash
python main.py --metodo both --config ../config/params_sensivel.json
```

**Robusta (menos falsos positivos):**

```bash
python main.py --metodo both --config ../config/params_robusta.json
```

---

## Opção 2: Via Jupyter Notebook (Recomendado para Análise)

```bash
# Instalar Jupyter (se não tiver)
pip install jupyter

# Executar notebook
jupyter notebook demo.ipynb
```

Ou abra `demo.ipynb` direto no VS Code com a extensão **Jupyter**.

---

## Opção 3: Importar como Módulo Python

```python
import sys
sys.path.insert(0, 'src')

from canny_classic import CannyClassic
from canny_modificado import CannyModificado
from utils import read_image, save_image

# Carrega imagem
image = read_image('imagens/GrayAndMagenta.png')

# Canny Clássico
canny_classic = CannyClassic(sigma=1.0, low_threshold=100, high_threshold=200)
edges_classic = canny_classic.detect(image)

# Canny Modificado
canny_mod = CannyModificado(num_gabor_orientations=8, num_gabor_frequencies=3)
edges_mod = canny_mod.detect(image)

# Salva resultados
save_image(edges_classic, 'resultados/classic.png')
save_image(edges_mod, 'resultados/modificado.png')
```

---

## Configurações de Parâmetros

Os arquivos JSON em `config/` controlam os limiares e filtros:

| Parâmetro            | Descrição                           | Intervalo Típico |
| -------------------- | ----------------------------------- | ---------------- |
| `sigma`              | Desvio padrão do desfoque Gaussiano | 0.5 - 2.0        |
| `kernel_size`        | Tamanho do kernel (deve ser ímpar)  | 3, 5, 7          |
| `low_threshold`      | Limiar baixo para histerese         | 30 - 150         |
| `high_threshold`     | Limiar alto para histerese          | 80 - 250         |
| `gabor_orientations` | Número de orientações de Gabor      | 4 - 16           |
| `gabor_frequencies`  | Número de frequências de Gabor      | 2 - 5            |

**Dica:** Para imagens com muito detalhe, aumente `low_threshold` e `high_threshold`.

---

## Estrutura de Saída

Após execução, verifique a pasta `resultados/`:

```
resultados/
├── GrayAndMagenta_canny_classic.png      # Resultado Canny tradicional
├── GrayAndMagenta_canny_modificado.png   # Resultado Canny modificado
└── GrayAndMagenta_comparacao.png         # Comparação lado a lado
```

---

## Troubleshooting

### ❌ Erro: "ModuleNotFoundError"

```bash
pip install -r requirements.txt
```

### ❌ Erro: "No module named 'cv2'"

```bash
pip install opencv-python
```

### ❌ Executar lentamente?

- Reduzir `gabor_orientations` (ex: 6 ao invés de 8)
- Aumentar `kernel_size` do desfoque (menos detalhes)
- Testar com imagens menores primeiro

---

## 📊 Esperado nos Resultados

| Imagem                 | Diferença Esperada                                   |
| ---------------------- | ---------------------------------------------------- |
| **GrayAndMagenta.png** | Modificado detecta borda magenta; Clássico a perde   |
| **Zebra.jpg**          | Similar (contraste em cinza); Gabor detecta texturas |
| **FCBarcelona.png**    | Modificado preserva cores sólidas                    |
| **PlacaMercosul.webp** | Ambos bons; Modificado com menos ruído               |
