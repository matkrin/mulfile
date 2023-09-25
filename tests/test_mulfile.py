from pathlib import Path
import pytest

import mulfile as mul
from mulfile.mul import Mul

test_filepath = Path(__file__).parent / "test_files"

TEST_MUL_FILE = test_filepath / "test_mul.mul"
TEST_MUL_TO_GWY_FILE = test_filepath / "test_mul.gwy"

TEST_FLM_FILE = test_filepath / "test_flm.flm"
TEST_FLM_TO_GWY_FILE = test_filepath / "test_flm.gwy"

TEST_MUL_SINGLE = test_filepath / "test_single_image.mul"
TEST_MUL_TO_GWY_SINGLE = test_filepath / "test_single_image.gwy"


def test_mul_load():
    test_mul = mul.load(TEST_MUL_FILE)
    assert isinstance(test_mul, Mul)
    assert len(test_mul) == 4
    assert test_mul[0].tilt == 0
    assert test_mul[1].gain == 955
    assert test_mul[2].xres == 512
    assert test_mul[2].img_data.shape == (512, 512)


def test_mul_save_gwy(tmp_path):
    test_mul = mul.load(TEST_MUL_FILE)
    output_name = tmp_path / "mul_output.gwy"
    test_mul.save_gwy(output_name)

    output_cont = output_name.read_bytes()
    test_gwy_cont = TEST_MUL_TO_GWY_FILE.read_bytes()
    assert output_cont == test_gwy_cont


def test_flm_load():
    test_flm = mul.load(TEST_FLM_FILE)
    assert isinstance(test_flm, Mul)
    assert len(test_flm) == 5
    assert test_flm[2].img_data.shape == (512, 512)
    assert test_flm[3].gain == 1095
    assert test_flm[4].tilt == 51
    assert test_flm[4].zscale == 50


def test_flm_save_gwy(tmp_path):
    test_flm = mul.load(TEST_FLM_FILE)
    output_name = tmp_path / "flm_output.gwy"
    test_flm.save_gwy(output_name)

    output_cont = output_name.read_bytes()
    test_gwy_cont = TEST_FLM_TO_GWY_FILE.read_bytes()
    assert output_cont == test_gwy_cont


def test_mul_load_single():
    test_mul_single = mul.load(TEST_MUL_SINGLE)
    assert isinstance(test_mul_single, Mul)
    assert test_mul_single[0].tilt == 349
    assert test_mul_single[0].gain == 10000
    assert test_mul_single[0].xres == 512
    assert test_mul_single[0].img_data.shape == (512, 512)


def test_mul_save_gwy_single(tmp_path):
    test_mul = mul.load(TEST_MUL_SINGLE)
    output_name = tmp_path / "mul_single_output.gwy"
    test_mul.save_gwy(output_name)

    output_cont = output_name.read_bytes()
    test_gwy_cont = TEST_MUL_TO_GWY_SINGLE.read_bytes()
    assert output_cont == test_gwy_cont
