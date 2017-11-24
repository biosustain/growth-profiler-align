# -*- coding: utf-8 -*-

# Copyright 2017 Novo Nordisk Foundation Center for Biosustainability,
# Technical University of Denmark.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Align and compare plate images."""

from __future__ import absolute_import

import numpy as np


RADIUS = 20


def align_plates(plate_image, calibration_plate):
    """
    Compute a translation between plate image and calibration image.

    Both images should be converted to edges.

    Returns
    -------
    numpy.array
        A vector (x, y) that describes the translation from the calibration
        plate to the analyzed plate.
    """
    r = int(RADIUS)
    best_offset = (0, 0)
    best_value = 0
    for i in np.arange(-r, r + 1):
        for j in np.arange(-r, r + 1):
            value = compare_images(plate_image, calibration_plate, i, j)
            if value > best_value:
                best_value = value
                best_offset = (i, j)
    # TODO: Validate that the images are properly aligned (`best_value`).
    return np.array(best_offset)


def compare_images(image1, image2, x, y):
    """
    Find the overlap of white pixels between two images with offset.

    Returns
    -------
    int
        The number of pixels where both images are True/white/on when they are
        overlapped with the given offset (x, y).
    """
    shape1 = image1.shape
    shape2 = image2.shape
    image1_slice = image1[
        max(0, x): min(shape1[0], shape2[0] + x),
        max(0, y): min(shape1[1], shape2[1] + y)
    ]
    image2_slice = image2[
        max(0, -x): min(shape2[0], shape1[0] - x),
        max(0, -y): min(shape2[1], shape1[1] - y)
    ]
    assert image1_slice.shape == image2_slice.shape

    overlap = (image1_slice & image2_slice).sum()
    return overlap
