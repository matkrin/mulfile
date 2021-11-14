from typing import Callable, Union
from . import mul


def load(file: str) -> Union[mul.Mul, mul.MulImage]:
    """ """    
    return mul.read_mul(file)
