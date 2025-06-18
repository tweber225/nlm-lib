from typing import ClassVar

import numpy as np

from dirigo.sw_interfaces.display import TransferFunction




class NegativeExponential(TransferFunction):
    """
    Standard power-law (linear->display) transfer.
    gamma < 1 boosts mid-tones; gamma > 1 darkens.
    """
    alpha: float = 2.0

    slug:  ClassVar[str] = "negative_exponential"
    label: ClassVar[str] = "Negative exponential"

    def _f(self, x: np.ndarray) -> np.ndarray:
        return np.exp(-self.alpha * x)