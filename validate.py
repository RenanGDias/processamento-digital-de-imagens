#!/usr/bin/env python3
"""
Script de validação do projeto.
Verifica se todos os arquivos e dependências estão corretos.
"""

import os
import sys
import json
from pathlib import Path

print("=" * 80)
print("🔍 VALIDAÇÃO DO PROJETO - Detecção de Bordas")
print("=" * 80)

# Diretório base
base_dir = Path(__file__).parent

# Checklist
checks = {
    "Estrutura de Diretórios": [
        ("src/", "Diretório de código-fonte"),
        ("config/", "Diretório de configurações"),
        ("imagens/", "Diretório de imagens de entrada"),
        ("resultados/", "Diretório de resultados"),
    ],
    "Arquivos de Código": [
        ("src/__init__.py", "Pacote Python"),
        ("src/utils.py", "Funções auxiliares"),
        ("src/canny_classic.py", "Canny clássico"),
        ("src/canny_modificado.py", "Canny modificado (Gabor-Di Zenzo)"),
        ("src/main.py", "Interface CLI"),
    ],
    "Arquivos de Configuração": [
        ("config/params.json", "Parâmetros padrão"),
        ("config/params_sensivel.json", "Parâmetros sensíveis"),
        ("config/params_robusta.json", "Parâmetros robustos"),
    ],
    "Documentação": [
        ("README.md", "Documentação principal"),
        ("QUICKSTART.md", "Guia rápido"),
        ("ARCHITECTURE.md", "Detalhes técnicos"),
        ("requirements.txt", "Dependências"),
        (".gitignore", "Git ignore"),
    ],
    "Notebooks": [
        ("demo.ipynb", "Notebook Jupyter"),
    ],
}

results = {}
all_ok = True

for category, files in checks.items():
    print(f"\n📋 {category}")
    print("-" * 80)
    results[category] = []
    
    for file_path, description in files:
        full_path = base_dir / file_path
        exists = full_path.exists()
        status = "✓" if exists else "✗"
        
        if not exists:
            all_ok = False
        
        results[category].append({
            "file": file_path,
            "description": description,
            "exists": exists,
            "status": status
        })
        
        print(f"  {status} {file_path:<35} {description}")

# Verificar dependências
print(f"\n📦 Dependências Python")
print("-" * 80)

dependencies = [
    ("numpy", "Álgebra linear"),
    ("PIL", "Leitura/escrita de imagens"),
    ("cv2", "Processamento de imagens (I/O)"),
    ("matplotlib", "Visualização"),
]

dep_ok = True
for pkg, desc in dependencies:
    try:
        __import__(pkg)
        print(f"  ✓ {pkg:<15} {desc}")
    except ImportError:
        print(f"  ✗ {pkg:<15} {desc} [FALTANDO]")
        dep_ok = False
        all_ok = False

# Validar JSONs
print(f"\n📄 Validação de Configurações JSON")
print("-" * 80)

json_files = [
    "config/params.json",
    "config/params_sensivel.json",
    "config/params_robusta.json",
]

required_keys = {
    "sigma", "kernel_size", "low_threshold", "high_threshold",
    "gabor_orientations", "gabor_frequencies"
}

for json_file in json_files:
    path = base_dir / json_file
    if path.exists():
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            
            missing = required_keys - set(data.keys())
            if missing:
                print(f"  ✗ {json_file:<35} Faltam chaves: {missing}")
                all_ok = False
            else:
                print(f"  ✓ {json_file:<35} Válido")
        except json.JSONDecodeError as e:
            print(f"  ✗ {json_file:<35} JSON inválido: {e}")
            all_ok = False
    else:
        print(f"  ✗ {json_file:<35} Arquivo não encontrado")
        all_ok = False

# Verificar imagens
print(f"\n🖼️  Imagens de Entrada")
print("-" * 80)

imagens_dir = base_dir / "imagens"
if imagens_dir.exists():
    images = list(imagens_dir.glob("*.[pP][nN][gG]")) + \
             list(imagens_dir.glob("*.[jJ][pP][gG]")) + \
             list(imagens_dir.glob("*.[jJ][pP][eE][gG]")) + \
             list(imagens_dir.glob("*.[wW][eE][bB][pP]"))
    
    if images:
        print(f"  ✓ {len(images)} imagens encontradas:")
        for img in sorted(images)[:5]:
            print(f"      • {img.name}")
        if len(images) > 5:
            print(f"      • ... e {len(images) - 5} mais")
    else:
        print(f"  ⚠ Nenhuma imagem encontrada em imagens/")
        print(f"    (Adicione imagens para testar o projeto)")
else:
    print(f"  ✗ Diretório 'imagens/' não existe")
    all_ok = False

# Resumo Final
print(f"\n{'=' * 80}")
if all_ok and dep_ok:
    print("✅ VALIDAÇÃO COMPLETA: Tudo OK!")
    print("\nPróximos passos:")
    print("  1. Adicione imagens em imagens/")
    print("  2. Execute: cd src && python main.py --metodo both")
    print("  3. Ou abra: jupyter notebook demo.ipynb")
    sys.exit(0)
else:
    print("⚠️  VALIDAÇÃO COM AVISOS")
    if not dep_ok:
        print("\n❌ Dependências faltando. Execute:")
        print("   pip install -r requirements.txt")
    if not all_ok:
        print("\n❌ Alguns arquivos estão faltando!")
    sys.exit(1)
