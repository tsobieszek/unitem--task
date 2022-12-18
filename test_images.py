from math import sqrt

from numpy.linalg import norm
from typing import TYPE_CHECKING

import PIL
import numpy as np
import pytest
from numpy.testing import assert_array_equal

import images
from images import Image, PngImageSaver
from source import Source, DataSource


@pytest.mark.parametrize("image, factor",
                         (
                                 (np.array([[[255, 0, 0], [0, 255, 0]], [[0, 0, 255], [0, 0, 0]]],
                                           dtype=np.uint8), 4),
                                 (Source((20, 20, 3)).get_data(), 3),
                                 (Source((600, 400, 3)).get_data(), 2)
                         ))
def test_resizing_up_and_down_again_gives_a_similar_image(image, factor):
    # when
    blown_up = images.resize(4)(image)
    shrunk_back = images.resize(1 / 4)(blown_up)
    # then
    assert blown_up.shape[:-1] == tuple(map(lambda x: x * 4, image.shape))[:-1]
    assert blown_up.shape[-1] == image.shape[-1]
    assert shrunk_back.shape == image.shape
    assert norm((image - shrunk_back) / 256) < sqrt(image.size)


# TODO
def ignored_test_median_filter():
    assert True


def check_if_Source_satisfies_DataSource_protocol() -> None:
    # runs only in mypy and similar tools
    if TYPE_CHECKING:
        source: DataSource[Image] = Source((1, 1, 1))
        source  # added to silence unused variable warning of pyflakes


@pytest.mark.parametrize("image",
                         (
                                 np.array([[[255, 0, 0], [0, 255, 0]], [[0, 0, 255], [0, 0, 0]]],
                                          dtype=np.uint8),
                         ))
def test_saving_of_images(tmp_path, image):
    # given
    saver = PngImageSaver()

    # when
    file = tmp_path / f'file.{saver.extension()}'
    saver.save(file, image)
    loaded_image = np.array(PIL.Image.open(file).convert('RGB'))

    # then
    assert file.is_file()
    assert_array_equal(image, loaded_image)
