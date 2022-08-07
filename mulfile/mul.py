from __future__ import annotations
from typing import List, Union
import os
from pathlib import Path
from datetime import datetime
from struct import unpack
from dataclasses import dataclass
from collections import UserList
import numpy as np

from .gwyddion import Gwy


@dataclass
class MulImage:
    """Class for a single STM-image and its metadata in a mulfile

    Attributes:
        filepath: Path of the .mul or .flm file
        img_num: Number of the image in the file (starting at 1)
        img_id: Filename without extension with underscore and img_num
        size:
        xres: Resolution in x-direction (in pixels)
        yres: Resolution in y-direction (in pixels)
        zres:
        datetime: Datetime of image acquisition (YYYY-MM-DD hh:mm:ss)
        xsize: Size of the image in x-direction (in nm)
        ysize: Size of the image in y-direction (in nm)
        xoffset: Offset of the image in x-direction from 0 (in nm)
        yoffset: Offset of the image in y-direction from 0 (in nm)
        zscale: ADC range (in V)
        tilt: Rotation of x-scan-direction (in degree)
        speed: Image acquisition time (in seconds)
        line_time: Time for one scan line (in milliseconds)
        bias: Bias Voltage (in mV)
        current: Tunneling Current Setpoint (in nA)
        sample: Sample name as prompted when saving the image
        title: Title name as prompted when saving the image
        postpr:
        postd1:
        mode: Scan Mode
        currfac: Current factor (either 1 or 5)
        num_pointscans: Number of pointscans during image acquisition
        unitnr:
        version:
        gain: Gain of PI
        img_data: Data of the image as 2D numpy array, ordered according to
            scanning sequence (in nm)

    """

    filepath: Union[str, Path]
    img_num: int
    img_id: str
    size: int
    xres: int
    yres: int
    zres: int
    datetime: datetime
    xsize: int
    ysize: int
    xoffset: int
    yoffset: int
    zscale: int
    tilt: int
    speed: float
    line_time: float
    bias: float
    current: float
    sample: str
    title: str
    postpr: int
    postd1: int
    mode: int
    currfac: int
    num_pointscans: int
    unitnr: int
    version: int
    gain: int
    img_data: np.ndarray

    def __add__(self, other: MulImage) -> Mul:
        """Defines the addition operator for MulImage-instances

        :param other: the MulImage that is added
        """

        return Mul([self, other])

    def save_gwy(self, output_name: str) -> None:
        """Saves a MulImage-instance as a GWY file

        :param output_name: name of the .gwy file to create
        """

        gwy = Gwy(self)
        gwy.save_gwyfile(output_name)


class Mul(UserList):
    """Class for an entire mulfile, list-like sequence of MulImage STM-images

    :param data: the data the Mul-instance contains
    """

    def __init__(self, data: List[MulImage]) -> None:
        super().__init__(self)
        self.data = data

    def save_gwy(self, output_name: str) -> None:
        """Saves a Mul-instance as a GWY file

        :param output_name: name of the .gwy file to create
        """

        gwy = Gwy(self)
        gwy.save_gwyfile(output_name)


def read_mul(filepath: Union[str, Path]) -> Union[Mul, MulImage]:
    """Parses a mul-file (.mul) or a flm-file (.flm)

    :param filepath: absolute or relative path to the .mul or .flm file
    """

    basename = os.path.basename(filepath)
    filename, fileext = os.path.splitext(basename)
    if fileext not in [".mul", ".flm"]:
        raise ValueError("Filetype not supported. Select a .mul or .flm file")

    MUL_BLOCK = 128
    filesize = os.path.getsize(filepath)
    data = []

    with open(filepath, "rb") as f:
        nr = unpack("h", f.read(2))[0]
        adr = unpack("i", f.read(4))[0]
        f.seek(0)

        block_counter = 0

        if adr == 3:
            f.seek(MUL_BLOCK * adr)
            block_counter += adr

        while block_counter * MUL_BLOCK < filesize:
            img_num, size = unpack("hh", f.read(4))
            xres, yres, zres = unpack("hhh", f.read(6))
            year, month, day = unpack("hhh", f.read(6))
            hour, minute, second = unpack("hhh", f.read(6))

            xsize = unpack("h", f.read(2))[0] * 0.1  # in nm
            ysize = unpack("h", f.read(2))[0] * 0.1  # in nm
            xoffset = unpack("h", f.read(2))[0] * 0.1  # in nm
            yoffset = unpack("h", f.read(2))[0] * 0.1  # in nm
            zscale, tilt = unpack("hh", f.read(4))  # in V, deg

            speed, bias, current = unpack("hhh", f.read(6))

            sample = "".join([chr(i) for i in f.read(21)])
            title = "".join([chr(i) for i in f.read(21)])

            postpr, postd1, mode, currfac = unpack("hhhh", f.read(8))
            num_pointscans, unitnr, version = unpack("hhh", f.read(6))

            spare_48, spare_49, spare_50 = unpack("hhh", f.read(6))
            spare_51, spare_52, spare_53 = unpack("hhh", f.read(6))
            spare_54, spare_55, spare_56 = unpack("hhh", f.read(6))
            spare_57, spare_58, spare_59 = unpack("hhh", f.read(6))
            gain, spare_61, spare_62, spare_63 = unpack("hhhh", f.read(8))

            img_data = np.frombuffer(f.read(xres * yres * 2), dtype=np.int16)
            img_data = img_data.astype("float64")
            img_data *= -0.1 / 1.36 * zscale / 2000  # in nm
            img_data = img_data.reshape((xres, yres))

            if num_pointscans > 0:
                for _ in range(0, num_pointscans):
                    ps_size, ps_type, ps_time4scan = unpack("hhh", f.read(6))
                    ps_minv, ps_maxv = unpack("hh", f.read(4))
                    ps_xpos, ps_ypos = unpack("hh", f.read(4))
                    ps_dz, ps_delay = unpack("hh", f.read(4))
                    ps_version, ps_indendelay = unpack("hh", f.read(4))
                    ps_xposend, ps_yposend = unpack("hh", f.read(4))
                    ps_vt_fw, ps_it_fw = unpack("hh", f.read(4))
                    ps_vt_bw, ps_it_bw = unpack("hh", f.read(4))
                    ps_lscan = unpack("h", f.read(2))[0]

                    f.read(MUL_BLOCK - 18 * 2)  # spare
                    ps_data = np.frombuffer(
                        f.read(ps_size * 2), dtype=np.int16
                    )

            block_counter += size

            speed *= 0.01  # in s
            line_time = speed / yres * 1000  # in ms
            bias = -bias / 3.2768  # in mV
            current *= currfac * 0.01  # in nA

            data.append(
                MulImage(
                    filepath,
                    img_num,
                    filename + "_" + str(img_num),
                    size,
                    xres,
                    yres,
                    zres,
                    datetime(year, month, day, hour, minute, second),
                    xsize,
                    ysize,
                    xoffset,
                    yoffset,
                    zscale,
                    tilt,
                    speed,
                    line_time,
                    bias,
                    current,
                    sample,
                    title,
                    postpr,
                    postd1,
                    mode,
                    currfac,
                    num_pointscans,
                    unitnr,
                    version,
                    gain,
                    img_data,
                )
            )

    if len(data) == 1:
        return data[0]

    return Mul(data)
