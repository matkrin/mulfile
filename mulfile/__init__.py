from typing import Union
from pathlib import Path
from . import mul


def load(file: Union[str, Path]) -> Union[mul.Mul, mul.MulImage]:
    """Parses a mul-file (.mul) or a flm-file (.flm)

    :param file: the .mul or .flm file to be parsed

    """
    return mul.read_mul(file)
