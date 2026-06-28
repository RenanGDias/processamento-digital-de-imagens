"""
Implementação do Algoritmo de Canny Clássico (Escalar).

Pipeline:
1. Conversão RGB -> Escala de Cinza
2. Desfoque Gaussiano
3. Cálculo de Gradientes (Sobel)
4. Supressão de Não-Máximos (NMS)
5. Histerese com dois limiares
"""

import numpy as np
try:
    from .utils import (
        rgb_to_gray, apply_gaussian_blur, compute_sobel_gradients,
        non_maximum_suppression, hysteresis_thresholding
    )
except ImportError:
    from utils import (
        rgb_to_gray, apply_gaussian_blur, compute_sobel_gradients,
        non_maximum_suppression, hysteresis_thresholding
    )


class CannyClassic:
    """Detector de bordas Canny tradicional (escalar)."""
    
    def __init__(self, sigma=1.0, kernel_size=5, 
                 low_threshold=100, high_threshold=200):
        """
        Inicializa o detector Canny.
        
        Args:
            sigma (float): Desvio padrão do desfoque Gaussiano
            kernel_size (int): Tamanho do kernel (deve ser ímpar)
            low_threshold (float): Limiar baixo para histerese
            high_threshold (float): Limiar alto para histerese
        """
        self.sigma = sigma
        self.kernel_size = kernel_size
        self.low_threshold = low_threshold
        self.high_threshold = high_threshold
    
    def detect(self, image_rgb):
        """
        Executa o pipeline completo de detecção de bordas.
        
        Args:
            image_rgb (np.ndarray): Imagem em RGB (H x W x 3), uint8
            
        Returns:
            np.ndarray: Imagem binária de bordas (H x W), uint8
        """
        # Passo 1: Conversão para escala de cinza
        print("  [Canny Classic] Convertendo RGB → Cinza...")
        gray = rgb_to_gray(image_rgb)
        
        # Passo 2: Desfoque Gaussiano
        print(f"  [Canny Classic] Aplicando desfoque Gaussiano (σ={self.sigma})...")
        blurred = apply_gaussian_blur(gray, kernel_size=self.kernel_size, 
                                      sigma=self.sigma)
        
        # Passo 3: Cálculo de gradientes
        print("  [Canny Classic] Calculando gradientes (Sobel)...")
        magnitude, direction = compute_sobel_gradients(blurred)
        
        # Normaliza magnitude
        magnitude = (magnitude / magnitude.max()) * 255 if magnitude.max() > 0 else magnitude
        
        # Passo 4: NMS
        print("  [Canny Classic] Aplicando NMS...")
        nms_result = non_maximum_suppression(magnitude, direction)
        
        # Passo 5: Histerese
        print(f"  [Canny Classic] Aplicando Histerese (T_low={self.low_threshold}, T_high={self.high_threshold})...")
        edges = hysteresis_thresholding(nms_result, self.low_threshold, self.high_threshold)
        
        return edges
