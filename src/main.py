"""
Script principal para execução dos algoritmos de detecção de bordas.
Suporta CLI e processamento em lote.
"""

import argparse
import json
import os
from pathlib import Path
import numpy as np

from utils import read_image, save_image
from canny_classic import CannyClassic
from canny_modificado import CannyModificado


def load_config(config_path):
    """Carrega configurações de um arquivo JSON."""
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def run_detection(image_path, method='both', config=None, output_dir='resultados'):
    """
    Executa detecção de bordas em uma imagem.
    
    Args:
        image_path (str): Caminho da imagem
        method (str): 'classic', 'modificado', ou 'both'
        config (dict): Configurações (limiares, etc.)
        output_dir (str): Diretório de saída
    """
    if config is None:
        config = {
            'sigma': 1.0,
            'kernel_size': 5,
            'low_threshold': 100,
            'high_threshold': 200,
            'gabor_orientations': 8,
            'gabor_frequencies': 3
        }
    
    # Lê a imagem
    print(f"\n📷 Processando: {image_path}")
    image = read_image(image_path)
    print(f"   Dimensões: {image.shape}")
    
    # Extrai nome base
    base_name = Path(image_path).stem
    
    # Canny Clássico
    if method in ['classic', 'both']:
        print(f"\n🔍 Executando Canny Clássico...")
        canny_classic = CannyClassic(
            sigma=config.get('sigma', 1.0),
            kernel_size=config.get('kernel_size', 5),
            low_threshold=config.get('low_threshold', 100),
            high_threshold=config.get('high_threshold', 200)
        )
        edges_classic = canny_classic.detect(image)
        
        output_path = os.path.join(output_dir, f"{base_name}_canny_classic.png")
        save_image(edges_classic, output_path)
    
    # Canny Modificado
    if method in ['modificado', 'both']:
        print(f"\n🔍 Executando Canny Modificado (Gabor-Di Zenzo)...")
        canny_mod = CannyModificado(
            sigma_blur=config.get('sigma', 1.0),
            num_gabor_orientations=config.get('gabor_orientations', 8),
            num_gabor_frequencies=config.get('gabor_frequencies', 3),
            low_threshold=config.get('low_threshold', 100),
            high_threshold=config.get('high_threshold', 200)
        )
        edges_mod = canny_mod.detect(image)
        
        output_path = os.path.join(output_dir, f"{base_name}_canny_modificado.png")
        save_image(edges_mod, output_path)
        
        # Gera comparação lado a lado
        if method == 'both':
            print(f"\n📊 Gerando comparação...")
            save_comparison(edges_classic, edges_mod, base_name, output_dir)


def save_comparison(edges_classic, edges_mod, base_name, output_dir):
    """Salva comparação lado a lado dos dois métodos."""
    H, W = edges_classic.shape
    
    # Cria imagem de comparação
    comparison = np.zeros((H, W * 2 + 10), dtype=np.uint8)
    comparison[:, :W] = edges_classic
    comparison[:, W+10:] = edges_mod
    
    output_path = os.path.join(output_dir, f"{base_name}_comparacao.png")
    save_image(comparison, output_path)


def main():
    parser = argparse.ArgumentParser(
        description='Detecção de Bordas: Canny vs. Canny-Modificado (Gabor-Di Zenzo)'
    )
    
    parser.add_argument('--imagem', type=str, help='Caminho da imagem')
    parser.add_argument('--diretorio', type=str, default='imagens',
                        help='Diretório com imagens para processamento em lote')
    parser.add_argument('--metodo', type=str, default='both',
                        choices=['classic', 'modificado', 'both'],
                        help='Método: classic, modificado, ou both')
    parser.add_argument('--config', type=str, default='config/params.json',
                        help='Arquivo de configuração JSON')
    parser.add_argument('--output', type=str, default='resultados',
                        help='Diretório de saída')
    
    args = parser.parse_args()
    
    # Carrega configuração
    config = None
    if os.path.exists(args.config):
        config = load_config(args.config)
        print(f"✓ Configuração carregada de: {args.config}")
    
    # Cria diretório de saída
    os.makedirs(args.output, exist_ok=True)
    
    # Processamento
    if args.imagem:
        # Imagem única
        if os.path.exists(args.imagem):
            run_detection(args.imagem, method=args.metodo, 
                         config=config, output_dir=args.output)
        else:
            print(f"❌ Imagem não encontrada: {args.imagem}")
    else:
        # Processamento em lote
        if os.path.isdir(args.diretorio):
            print(f"📁 Processando imagens de: {args.diretorio}")
            
            # Extensões suportadas
            extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.webp'}
            images = [f for f in os.listdir(args.diretorio)
                     if os.path.splitext(f)[1].lower() in extensions]
            
            if not images:
                print(f"❌ Nenhuma imagem encontrada em: {args.diretorio}")
                return
            
            print(f"   Encontradas {len(images)} imagens")
            
            for img_file in images:
                img_path = os.path.join(args.diretorio, img_file)
                run_detection(img_path, method=args.metodo,
                             config=config, output_dir=args.output)
        else:
            print(f"❌ Diretório não encontrado: {args.diretorio}")


if __name__ == '__main__':
    main()
