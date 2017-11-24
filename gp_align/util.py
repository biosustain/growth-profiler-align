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

"""Provide useful helper functions."""

from __future__ import absolute_import, division

from string import ascii_uppercase

import numpy as np


def well_names(num_rows, num_columns, orientation="top-right"):
    """
    Return well names in left-to-right reading direction.

    Orientation is given as the corner where A1 is located.
    """
    rows = ascii_uppercase[:num_rows]
    columns = list(range(1, num_columns + 1))

    if orientation == "top-left":
        names = ["{}{:d}".format(row, col)
                 for row in rows for col in columns]
    elif orientation == "top-right":
        names = ["{}{:d}".format(row, col)
                 for col in columns for row in reversed(rows)]
    elif orientation == "bottom-left":
        names = ["{}{:d}".format(row, col)
                 for col in reversed(columns) for row in rows]
    elif orientation == "bottom-right":
        names = ["{}{:d}".format(row, col)
                 for row in reversed(rows) for col in reversed(columns)]
    else:
        raise ValueError(
            "'{}' is an invalid orientation.".format(orientation))

    return names


def cut_image(image, n_height=3, n_width=2):
    """
    Evenly cut an image into bits.

    The returned order is column-wise left-to-right."""
    height, width = image.shape
    output = list()
    # TODO: Use `numpy.array.strides`, for example,
    # https://stackoverflow.com/a/30110497
    for j in range(n_width):
        for i in range(n_height):
            output.append(
                np.array(image[
                    i * height // n_height: (i + 1) * height // n_height,
                    j * width // n_width: (j + 1) * width // n_width
                ])  # Take "slices" out of the image
            )
    return output
