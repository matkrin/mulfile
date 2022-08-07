from __future__ import annotations
from typing import List, Union, TYPE_CHECKING
from collections.abc import Iterable
from struct import pack
import numpy as np

if TYPE_CHECKING:
    from .mul import Mul, MulImage


class Gwy:
    """Class for handeling the construction of bytes for a .gwy-file

    :param imgs: the Mul or MulImage instance that is converted to bytes
                 according to the GWY file format
    """

    def __init__(self, imgs: Union[Mul, MulImage]) -> None:
        self.imgs: Union[Mul, List[MulImage]]

        if isinstance(imgs, Iterable):
            self.imgs = imgs
        else:
            self.imgs = [imgs]

        self.gwycontent = self._make_gwy()

    def _make_si_unit(self, dimension: str) -> bytes:
        """Constructs GwySIUnit

        :param dimension: spacial dimension of the SI Unit (either xy or z)
        """

        si_name = (
            b"si_unit_" + bytes(dimension, "utf-8") + b"\0o" + b"GwySIUnit\0"
        )
        unit = b"unitstr\0s" + b"m\0"
        unit_size = pack("<i", len(unit))

        return si_name + unit_size + unit

    def _make_datafield(self, img: MulImage) -> bytes:
        """Constructs a GwyDatafield as defined by the .gwy file format

        :param img: the image for which the datafield bytes are created
        """

        datafield = b"".join(
            [
                b"xreal\0d" + pack("<d", float(img.xsize) * 1e-9),
                b"yreal\0d" + pack("<d", float(img.ysize) * 1e-9),
                b"xoff\0d" + pack("<d", 0),
                b"yoff\0d" + pack("<d", 0),
                b"xres\0i" + pack("<i", img.xres),
                b"yres\0i" + pack("<i", img.yres),
            ]
        )

        datafield += self._make_si_unit("xy")
        datafield += self._make_si_unit("z")

        data_arr = np.flip(img.img_data, axis=0).flatten() * 1e-9
        data_arr_size = len(data_arr)

        datafield += b"data\0D" + pack("<i", data_arr_size)
        datafield += data_arr.tobytes()

        datafield_size = pack("<i", len(datafield))

        return b"GwyDataField\0" + datafield_size + datafield

    def _make_meta(self, img: MulImage, channel_num: int) -> bytes:
        """Constructs a  GwyContainer containing the meta-data of an image

        :param img: the image for which the datafield bytes are created
        :param channel_num: the number of the channel in the GWY file
        """

        meta_name = bytes(f"/{channel_num}/meta\0o", "utf-8")
        meta_name += b"GwyContainer\0"

        meta_data = b"".join(
            [
                bytes(f"ID\0s{img.img_id}\0", "utf-8"),
                bytes(f"Bias\0s{img.bias * 1e-3:.5f} V\0", "utf-8"),
                bytes(f"Current\0s{img.current:.2f} nA\0", "utf-8"),
                bytes(f"Current factor\0s{img.currfac}\0", "utf-8"),
                bytes(
                    f"Scan Size\0s{img.xsize} nm, {img.ysize} nm\0", "utf-8"
                ),
                bytes(f"Resolution\0s{img.xres}, {img.yres}\0", "utf-8"),
                bytes(f"Datetime\0s{img.datetime}\0", "utf-8"),
                bytes(f"Gain\0s{img.gain}\0", "utf-8"),
                bytes(f"Mode\0s{img.mode}\0", "utf-8"),
                bytes(f"Postprocessing\0s{img.postpr}\0", "utf-8"),
                bytes(f"Scan Duration\0s{img.speed:.2f} s\0", "utf-8"),
                bytes(f"Line Time\0s{img.line_time:.2f} ms\0", "utf-8"),
                bytes(f"Tilt\0s{img.tilt} deg\0", "utf-8"),
                bytes(f"X-Offset\0s{img.xoffset:.2f} nm\0", "utf-8"),
                bytes(f"Y-Offset\0s{img.yoffset:.2f} nm\0", "utf-8"),
                bytes(f"Z-Scale\0s{img.zscale}\0", "utf-8"),
            ]
        )

        meta_data_size = pack("<i", len(meta_data))

        return meta_name + meta_data_size + meta_data

    def _make_data_container(self) -> bytes:
        """Constructs a top-level GwyContainer containing image data as
        GwyDataFields and image meta-data as nested GwyContainers
        """

        container = b""
        for channel_num, img in enumerate(self.imgs):
            channel_title = bytes(f"{img.img_id}\0", "utf-8")
            channel_key = bytes(f"/{channel_num}/data\0o", "utf-8")
            title_key = bytes(f"/{channel_num}/data/title\0s", "utf-8")

            container += (
                channel_key
                + self._make_datafield(img)
                + title_key
                + channel_title
                + self._make_meta(img, channel_num)
            )

        container_size = pack("<i", len(container))

        return b"GwyContainer\0" + container_size + container

    def _make_gwy(self) -> bytes:
        """Constructs the content of a .gwy-file as defined by the GWY file format
        """

        GWY_HEADER = b"GWYP"
        content = GWY_HEADER + self._make_data_container()
        return content

    def save_gwyfile(self, output_name: str) -> None:
        """Writes the content of a .gwy file into a file

        :param output_name: name of the .gwy file to create
        """

        with open(output_name, "wb") as f:
            f.write(self.gwycontent)
