"""
Implementação do Canny Modificado com Bancos de Filtros de Gabor e Di Zenzo.

Pipeline Vetorial:
1. Processamento de imagem colorida (não converte para cinza)
2. Cálculo de derivadas parciais por canal RGB
3. Construção da matriz de estrutura de Di Zenzo
4. Extração de autovalores e autovetores
5. Aplicação de banco de filtros de Gabor
6. Fusão de informações no domínio das derivadas
7. Supressão de Não-Máximos (NMS) e Histerese
"""

import numpy as np
try:
    from .utils import apply_gaussian_blur, non_maximum_suppression, hysteresis_thresholding
except ImportError:
    from utils import apply_gaussian_blur, non_maximum_suppression, hysteresis_thresholding


class GaborFilterBank:
    """Banco de Filtros de Gabor com múltiplas orientações e frequências."""
    
    def __init__(self, num_orientations=8, num_frequencies=3, 
                 sigma=3.0, lambda_base=5.0):
        """
        Inicializa o banco de filtros de Gabor.
        
        Args:
            num_orientations (int): Número de orientações (0-180°)
            num_frequencies (int): Número de frequências espaciais
            sigma (float): Desvio padrão do envelope Gaussiano
            lambda_base (float): Comprimento de onda base
        """
        self.num_orientations = num_orientations
        self.num_frequencies = num_frequencies
        self.sigma = sigma
        self.lambda_base = lambda_base
        self.filters = self._generate_filters()
    
    def _generate_filters(self):
        """Gera os kernels de Gabor."""
        filters = []
        size = int(2 * np.ceil(3 * self.sigma) + 1)
        center = size // 2
        
        for orientation_idx in range(self.num_orientations):
            theta = (orientation_idx / self.num_orientations) * np.pi
            
            for freq_idx in range(self.num_frequencies):
                lambda_val = self.lambda_base * (1.5 ** freq_idx)
                
                kernel = np.zeros((size, size), dtype=np.float32)
                
                for y in range(size):
                    for x in range(size):
                        dx = x - center
                        dy = y - center
                        
                        # Rotação para orientação
                        x_theta = dx * np.cos(theta) + dy * np.sin(theta)
                        y_theta = -dx * np.sin(theta) + dy * np.cos(theta)
                        
                        # Componente Gaussiana
                        gaussian = np.exp(-(x_theta**2 + y_theta**2) / (2 * self.sigma**2))
                        
                        # Componente senoidal (onda plana complexa)
                        sinusoid = np.cos(2 * np.pi * x_theta / lambda_val)
                        
                        kernel[y, x] = gaussian * sinusoid
                
                # Normaliza
                kernel = kernel / (np.sum(np.abs(kernel)) + 1e-10)
                filters.append(kernel)
        
        return filters
    
    def apply(self, channel):
        """
        Aplica banco de filtros a um canal de imagem.
        
        Args:
            channel (np.ndarray): Canal de imagem (H x W)
            
        Returns:
            np.ndarray: Respostas dos filtros (num_filters x H x W)
        """
        H, W = channel.shape
        responses = []
        
        for kernel in self.filters:
            h, w = kernel.shape
            response = np.zeros_like(channel, dtype=np.float32)
            
            pad_y, pad_x = h // 2, w // 2
            
            for y in range(pad_y, H - pad_y):
                for x in range(pad_x, W - pad_x):
                    patch = channel[y-pad_y:y+pad_y+1, x-pad_x:x+pad_x+1].astype(np.float32)
                    response[y, x] = np.sum(patch * kernel)
            
            responses.append(response)
        
        return np.array(responses)


class DiZenzoOperator:
    """Processamento vetorial de Di Zenzo para imagens coloridas."""
    
    @staticmethod
    def compute_structure_matrix(image_rgb, sigma=1.5):
        """
        Computa matriz de estrutura de Di Zenzo.
        
        Args:
            image_rgb (np.ndarray): Imagem RGB (H x W x 3)
            sigma (float): Desvio padrão para suavização
            
        Returns:
            tuple: (eigenvalues, eigenvectors) da matriz em cada pixel
        """
        H, W, _ = image_rgb.shape
        
        # Suaviza cada canal
        channels_smooth = []
        for c in range(3):
            smooth = apply_gaussian_blur(image_rgb[:, :, c].astype(np.float32), 
                                         sigma=sigma)
            channels_smooth.append(smooth)
        
        # Computa derivadas parciais por canal
        derivatives = []
        for smooth_channel in channels_smooth:
            # Gradiente em x (diferenças finitas)
            gx = np.zeros_like(smooth_channel)
            gx[:, :-1] = np.diff(smooth_channel, axis=1)
            
            # Gradiente em y
            gy = np.zeros_like(smooth_channel)
            gy[:-1, :] = np.diff(smooth_channel, axis=0)
            
            derivatives.append((gx, gy))
        
        # Constrói tensor de estrutura (matriz de covariância dos gradientes)
        eigenvalues = np.zeros((H, W, 2), dtype=np.float32)
        eigenvectors = np.zeros((H, W, 2, 2), dtype=np.float32)
        
        for y in range(H):
            for x in range(W):
                # Matriz de covariância 2x2 (gradiente vetorial)
                J = np.zeros((2, 2), dtype=np.float32)
                
                for c in range(3):
                    gx, gy = derivatives[c]
                    # Acumula contribuição de cada canal
                    J[0, 0] += gx[y, x]**2
                    J[0, 1] += gx[y, x] * gy[y, x]
                    J[1, 1] += gy[y, x]**2
                
                J[1, 0] = J[0, 1]  # Simetria
                
                # Autovalores e autovetores
                try:
                    evals, evecs = np.linalg.eigh(J)
                    eigenvalues[y, x] = evals
                    eigenvectors[y, x] = evecs
                except:
                    pass
        
        return eigenvalues, eigenvectors


class CannyModificado:
    """Detector de bordas Canny Modificado (Vetorial com Gabor-Di Zenzo)."""
    
    def __init__(self, sigma_blur=1.0, num_gabor_orientations=8,
                 num_gabor_frequencies=3, low_threshold=100, 
                 high_threshold=200):
        """
        Inicializa o detector Canny Modificado.
        
        Args:
            sigma_blur (float): Desvio padrão do desfoque inicial
            num_gabor_orientations (int): Orientações dos filtros de Gabor
            num_gabor_frequencies (int): Frequências dos filtros de Gabor
            low_threshold (float): Limiar baixo para histerese
            high_threshold (float): Limiar alto para histerese
        """
        self.sigma_blur = sigma_blur
        self.low_threshold = low_threshold
        self.high_threshold = high_threshold
        
        self.gabor_bank = GaborFilterBank(
            num_orientations=num_gabor_orientations,
            num_frequencies=num_gabor_frequencies,
            sigma=3.0,
            lambda_base=5.0
        )
        self.di_zenzo = DiZenzoOperator()
    
    def detect(self, image_rgb):
        """
        Executa o pipeline completo de detecção com processamento vetorial.
        
        Args:
            image_rgb (np.ndarray): Imagem em RGB (H x W x 3), uint8
            
        Returns:
            np.ndarray: Imagem binária de bordas (H x W), uint8
        """
        image_rgb = image_rgb.astype(np.float32)
        
        # Passo 1: Processamento vetorial Di Zenzo
        print("  [Canny Modificado] Computando matriz de estrutura (Di Zenzo)...")
        eigenvalues, eigenvectors = self.di_zenzo.compute_structure_matrix(
            image_rgb, sigma=self.sigma_blur
        )
        
        # Passo 2: Extrai magnitude do maior autovalor (contraste cromático)
        magnitude_di_zenzo = eigenvalues[:, :, 1]  # Maior autovalor
        
        # Passo 3: Aplica Banco de Filtros de Gabor por canal
        print("  [Canny Modificado] Aplicando Banco de Filtros de Gabor...")
        gabor_responses = []
        for c in range(3):
            responses = self.gabor_bank.apply(image_rgb[:, :, c])
            gabor_responses.append(responses)
        
        # Passo 4: Fusão de informações (máxima energia Gabor + Di Zenzo)
        print("  [Canny Modificado] Fusão de informações Gabor-Di Zenzo...")
        
        H, W = image_rgb.shape[:2]
        gabor_magnitude = np.zeros((H, W), dtype=np.float32)
        gabor_direction = np.zeros((H, W), dtype=np.float32)
        
        for y in range(H):
            for x in range(W):
                # Coleta respostas de todos os filtros
                all_responses = []
                for c in range(3):
                    all_responses.extend(gabor_responses[c][:, y, x])
                
                # Energia máxima
                gabor_magnitude[y, x] = np.max(np.abs(all_responses)) if all_responses else 0
                
                # Estima direção a partir de Di Zenzo
                if eigenvalues[y, x, 1] > 0:
                    gabor_direction[y, x] = np.arctan2(eigenvectors[y, x, 1, 1],
                                                        eigenvectors[y, x, 1, 0])
        
        # Passo 5: Fusão: combina Di Zenzo com Gabor
        magnitude_fused = (magnitude_di_zenzo + gabor_magnitude) / 2.0
        magnitude_fused = (magnitude_fused / magnitude_fused.max()) * 255 if magnitude_fused.max() > 0 else magnitude_fused
        
        # Passo 6: NMS
        print("  [Canny Modificado] Aplicando NMS...")
        nms_result = non_maximum_suppression(magnitude_fused, gabor_direction)
        
        # Passo 7: Histerese
        print(f"  [Canny Modificado] Aplicando Histerese (T_low={self.low_threshold}, T_high={self.high_threshold})...")
        edges = hysteresis_thresholding(nms_result, self.low_threshold, self.high_threshold)
        
        return edges
