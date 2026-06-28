"""
Módulo de detecção de bordas: Canny Clássico vs. Canny Modificado (Gabor-Di Zenzo)
"""

from .canny_classic import CannyClassic
from .canny_modificado import CannyModificado, GaborFilterBank, DiZenzoOperator
from .utils import read_image, save_image, rgb_to_gray

__version__ = "1.0.0"
__all__ = [
    'CannyClassic',
    'CannyModificado',
    'GaborFilterBank',
    'DiZenzoOperator',
    'read_image',
    'save_image',
    'rgb_to_gray'
]
