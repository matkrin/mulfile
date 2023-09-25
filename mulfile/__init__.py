from typing import Union
from pathlib import Path
from . import mul


def load(file: Union[str, Path]) -> mul.Mul:
    """Parses a mul-file (.mul) or a flm-file (.flm)

    Args:
        file: The .mul or .flm file to be parsed

    Returns:
        An instance of Mul if more than one image was found in the file
        or an instance of Mul if the file contains one image

    """

    return mul.read_mul(file)
