import os
import random


def set_global_seed(seed: int = 42) -> None:
    """
    Sets global deterministic seeds across standard python random, numpy, and environment.
    Ensures complete execution reproducibility for research pipelines.
    
    Args:
        seed (int): The integer seed to apply globally.
    """
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    
    try:
        import numpy as np
        np.random.seed(seed)
    except ImportError:
        pass

    try:
        import torch
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except ImportError:
        pass
