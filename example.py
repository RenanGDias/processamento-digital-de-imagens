#!/usr/bin/env python3
"""
Exemplo rápido de uso do projeto.
Detecta bordas com ambos os métodos e salva resultados.
"""

import os
import sys

# Muda para o diretório src
os.chdir(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, '.')

from utils import read_image, save_image
from canny_classic import CannyClassic
from canny_modificado import CannyModificado
import json

def main():
    """Executa exemplo rápido."""
    
    # Configuração
    print("🚀 Exemplo Rápido - Detecção de Bordas")
    print("=" * 70)
    
    # Carrega configuração
    with open('../config/params.json', 'r') as f:
        config = json.load(f)
    
    # Teste com a primeira imagem disponível
    image_dir = '../imagens'
    images = [f for f in os.listdir(image_dir) 
              if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    
    if not images:
        print("❌ Nenhuma imagem encontrada em imagens/")
        return
    
    test_image = os.path.join(image_dir, images[0])
    print(f"\n📷 Testando com: {images[0]}")
    
    # Carrega imagem
    image = read_image(test_image)
    print(f"✓ Dimensões: {image.shape}")
    
    # Canny Clássico
    print("\n⏳ Executando Canny Clássico...")
    canny_classic = CannyClassic(
        sigma=config['sigma'],
        kernel_size=config['kernel_size'],
        low_threshold=config['low_threshold'],
        high_threshold=config['high_threshold']
    )
    edges_classic = canny_classic.detect(image)
    print("✓ Canny Clássico concluído")
    
    # Canny Modificado
    print("\n⏳ Executando Canny Modificado...")
    canny_mod = CannyModificado(
        sigma_blur=config['sigma'],
        num_gabor_orientations=config['gabor_orientations'],
        num_gabor_frequencies=config['gabor_frequencies'],
        low_threshold=config['low_threshold'],
        high_threshold=config['high_threshold']
    )
    edges_mod = canny_mod.detect(image)
    print("✓ Canny Modificado concluído")
    
    # Salva resultados
    os.makedirs('../resultados', exist_ok=True)
    base_name = images[0].split('.')[0]
    
    path_classic = f'../resultados/{base_name}_canny_classic.png'
    path_mod = f'../resultados/{base_name}_canny_modificado.png'
    
    save_image(edges_classic, path_classic)
    save_image(edges_mod, path_mod)
    
    # Estatísticas
    import numpy as np
    n_edges_classic = (edges_classic > 128).sum()
    n_edges_mod = (edges_mod > 128).sum()
    
    print(f"\n📊 Resultados:")
    print(f"  Pixels de borda (Clássico): {n_edges_classic}")
    print(f"  Pixels de borda (Modificado): {n_edges_mod}")
    print(f"  Diferença: {abs(n_edges_classic - n_edges_mod)}")
    
    print(f"\n✅ Sucesso! Verifique 'resultados/' para os arquivos gerados.")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
