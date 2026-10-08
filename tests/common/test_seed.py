import random
import numpy as np
from backend.common.seed import set_global_seed


def test_seed_reproducibility():
    """Verify set_global_seed produces identical random draws across calls."""
    set_global_seed(42)
    py_draw1 = [random.random() for _ in range(5)]
    np_draw1 = np.random.rand(5).tolist()

    set_global_seed(42)
    py_draw2 = [random.random() for _ in range(5)]
    np_draw2 = np.random.rand(5).tolist()

    assert py_draw1 == py_draw2, "Python random draw failed reproducibility"
    assert np_draw1 == np_draw2, "NumPy random draw failed reproducibility"


def test_different_seeds_produce_different_draws():
    """Verify different seeds produce distinct outputs."""
    set_global_seed(42)
    draw1 = np.random.rand(5).tolist()

    set_global_seed(999)
    draw2 = np.random.rand(5).tolist()

    assert draw1 != draw2, "Different seeds produced identical draws"
