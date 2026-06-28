"""
Funções auxiliares para processamento de imagens e detecção de bordas.
Implementa: NMS (Non-Maximum Suppression), Histerese, I/O de imagens.
"""

import numpy as np
from PIL import Image
import os


def read_image(image_path):
    """
    Lê uma imagem e retorna como array numpy (RGB, 8-bit).
    
    Args:
        image_path (str): Caminho da imagem
        
    Returns:
        np.ndarray: Imagem em RGB com dtype uint8
    """
    img = Image.open(image_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    return np.array(img)


def save_image(image_array, output_path):
    """
    Salva um array numpy como imagem PNG.
    
    Args:
        image_array (np.ndarray): Array com valores 0-255
        output_path (str): Caminho de saída
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Normaliza para 0-255 se necessário
    if image_array.dtype != np.uint8:
        if image_array.max() <= 1.0:
            image_array = (image_array * 255).astype(np.uint8)
        else:
            image_array = np.clip(image_array, 0, 255).astype(np.uint8)
    
    img = Image.fromarray(image_array)
    img.save(output_path)
    print(f"✓ Imagem salva: {output_path}")


def rgb_to_gray(image_rgb):
    """
    Converte imagem RGB para escala de cinza usando coeficientes lineares.
    Fórmula: Gray = 0.299*R + 0.587*G + 0.114*B
    
    Args:
        image_rgb (np.ndarray): Imagem em RGB (H x W x 3)
        
    Returns:
        np.ndarray: Imagem em escala de cinza (H x W)
    """
    coefficients = np.array([0.299, 0.587, 0.114])
    gray = np.dot(image_rgb.astype(np.float32), coefficients)
    return gray


def normalize_image(image):
    """
    Normaliza imagem para range [0, 1].
    
    Args:
        image (np.ndarray): Imagem de entrada
        
    Returns:
        np.ndarray: Imagem normalizada
    """
    img_min = image.min()
    img_max = image.max()
    if img_max == img_min:
        return np.zeros_like(image)
    return (image - img_min) / (img_max - img_min)


def non_maximum_suppression(magnitude, direction):
    """
    Supressão de Não-Máximos (NMS): mantém apenas máximos locais na direção do gradiente.
    Reduz a espessura das bordas para 1 pixel.
    
    Args:
        magnitude (np.ndarray): Magnitude do gradiente (H x W)
        direction (np.ndarray): Direção do gradiente em radianos (H x W)
        
    Returns:
        np.ndarray: Magnitude após NMS
    """
    H, W = magnitude.shape
    nms = np.zeros_like(magnitude)
    
    # Normaliza direção para [0, 180] graus
    direction_deg = np.degrees(direction) % 180
    
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            angle = direction_deg[y, x]
            mag = magnitude[y, x]
            
            # Define vizinhos baseado na direção do gradiente
            if (angle >= 0 and angle < 22.5) or (angle >= 157.5 and angle <= 180):
                # Horizontal
                q, r = magnitude[y, x + 1], magnitude[y, x - 1]
            elif angle >= 22.5 and angle < 67.5:
                # Diagonal /
                q, r = magnitude[y - 1, x + 1], magnitude[y + 1, x - 1]
            elif angle >= 67.5 and angle < 112.5:
                # Vertical
                q, r = magnitude[y + 1, x], magnitude[y - 1, x]
            else:  # 112.5 <= angle < 157.5
                # Diagonal \
                q, r = magnitude[y - 1, x - 1], magnitude[y + 1, x + 1]
            
            if mag >= q and mag >= r:
                nms[y, x] = mag
    
    return nms


def hysteresis_thresholding(magnitude, low_threshold, high_threshold):
    """
    Histerese com dois limiares: bordas fortes e fracas.
    Bordas fracas conectadas a bordas fortes são mantidas.
    
    Args:
        magnitude (np.ndarray): Magnitude do gradiente (H x W)
        low_threshold (float): Limiar baixo
        high_threshold (float): Limiar alto
        
    Returns:
        np.ndarray: Imagem binária com bordas finais
    """
    H, W = magnitude.shape
    edges = np.zeros((H, W), dtype=np.uint8)
    
    # Bordas fortes
    strong = (magnitude >= high_threshold).astype(np.uint8)
    # Bordas fracas
    weak = ((magnitude >= low_threshold) & (magnitude < high_threshold)).astype(np.uint8)
    
    edges[strong == 1] = 255
    edges[weak == 1] = 75  # Marca provisoriamente
    
    # Conecta bordas fracas a bordas fortes (tracking)
    changed = True
    while changed:
        changed = False
        for y in range(1, H - 1):
            for x in range(1, W - 1):
                if edges[y, x] == 75:
                    # Verifica vizinhança 3x3 para bordas fortes
                    if np.any(edges[y-1:y+2, x-1:x+2] == 255):
                        edges[y, x] = 255
                        changed = True
                    else:
                        edges[y, x] = 0
    
    return edges


def compute_sobel_gradients(image):
    """
    Calcula gradientes usando operador de Sobel.
    
    Args:
        image (np.ndarray): Imagem em escala de cinza (H x W)
        
    Returns:
        tuple: (magnitude, direction) onde direction está em radianos
    """
    # Kernels de Sobel
    Gx = np.array([[-1, 0, 1],
                   [-2, 0, 2],
                   [-1, 0, 1]], dtype=np.float32)
    
    Gy = np.array([[-1, -2, -1],
                   [0, 0, 0],
                   [1, 2, 1]], dtype=np.float32)
    
    H, W = image.shape
    gx = np.zeros_like(image, dtype=np.float32)
    gy = np.zeros_like(image, dtype=np.float32)
    
    # Convolução manual
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            patch = image[y-1:y+2, x-1:x+2].astype(np.float32)
            gx[y, x] = np.sum(patch * Gx)
            gy[y, x] = np.sum(patch * Gy)
    
    magnitude = np.sqrt(gx**2 + gy**2)
    direction = np.arctan2(gy, gx)
    
    return magnitude, direction


def apply_gaussian_blur(image, kernel_size=5, sigma=1.0):
    """
    Aplica desfoque Gaussiano.
    
    Args:
        image (np.ndarray): Imagem de entrada
        kernel_size (int): Tamanho do kernel (deve ser ímpar)
        sigma (float): Desvio padrão da Gaussiana
        
    Returns:
        np.ndarray: Imagem desfocada
    """
    if kernel_size % 2 == 0:
        kernel_size += 1
    
    # Cria kernel Gaussiano
    ax = np.arange(-kernel_size // 2 + 1., kernel_size // 2 + 1.)
    xx, yy = np.meshgrid(ax, ax)
    kernel = np.exp(-(xx**2 + yy**2) / (2.0 * sigma**2))
    kernel /= kernel.sum()
    
    H, W = image.shape
    h, w = kernel.shape
    blurred = np.zeros_like(image, dtype=np.float32)
    
    pad_y, pad_x = h // 2, w // 2
    
    for y in range(pad_y, H - pad_y):
        for x in range(pad_x, W - pad_x):
            patch = image[y-pad_y:y+pad_y+1, x-pad_x:x+pad_x+1].astype(np.float32)
            blurred[y, x] = np.sum(patch * kernel)
    
    return blurred
