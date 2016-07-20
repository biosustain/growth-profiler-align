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

"""Analyze growth profiler images."""

from __future__ import absolute_import

import io
import json
import logging
from os.path import join, dirname

import numpy as np
from pandas import DataFrame
from skimage.color import rgb2gray
from skimage.feature import canny
from skimage.io import imread
from six import iteritems

import gp_align
from gp_align.align import align_plates
from gp_align.util import well_names, cut_image

LOGGER = logging.getLogger(__name__)
DATA_DIR = join(dirname(__file__), "data")
CANNY_SIGMA = 1.0
PLATES = {
    1: ["tray1", "tray2", "tray3", "tray4", "tray5", "tray6"],
    2: ["tray7", "tray8", "tray9", "tray10", "tray11", "tray12"]
}


def analyze_run(image_list, scanner=1, plate_type=1, orientation="top-right",
                plates=None):
    """
    Analyse a list of images from the Growth Profiler.

    Parameters:
    plate_type: The type of plates used
    parse_dates: Whether to sort the images by time. The image_names must of format '%d%m%Y%H%M%S'
    orientation: The orientation of the plates in the machine. The corner where A1 is located.
    plates: Specify which plates will be analysed e.g. [1, 2, 3] for the three left plates.
        Default (None) is to analyze all plates.
    """
    if plates is not None:
        raise NotImplementedError(
            "Selection of specific plates or trays is not possible yet.")

    config = dict()
    config["plate_names"] = PLATES[scanner]

    with io.open(join(DATA_DIR, "plate_specs.json"), encoding=None) as file_h:
        plate_specs = json.load(file_h)
    rows, columns = plate_specs["rows_and_columns"][str(plate_type)]
    config["rows"] = rows
    config["columns"] = columns
    LOGGER.debug("Plate type %d has %d rows and %d columns.", plate_type,
                 rows, columns)

    time_list, sorted_image_list = gp_align.parse_time.sort_filenames(image_list)

    data = {}

    calibration_name_left = join(
        DATA_DIR, "calibration_type_{:d}_left.png".format(plate_type))
    config["left_image"] = calibrate_image(calibration_name_left)

    calibration_name_right = join(
        DATA_DIR, "calibration_type_{:d}_right.png".format(plate_type))
    config["right_image"] = calibrate_image(calibration_name_right)

    config["well_names"] = well_names(rows, columns, orientation)

    config["plate_size"] = plate_specs["plate_size"]
    config["left_positions"] = plate_specs[
        "plate_positions"][calibration_name_left]
    config["right_positions"] = plate_specs[
        "plate_positions"][calibration_name_right]

    analyze_image.config = config

    for image_name in sorted_image_list:
        pass

    # Format the data
    output = {}
    for plate, plate_data in iteritems(data):
        wells = well_names(rows, columns, orientation="top-left")
        plate_df = DataFrame(plate_data)
        assert len(plate_df.columns) == len(wells)
        plate_df = plate_df[wells]

        for col in plate_df:
            assert len(plate_df[col]) == len(time_list)
        plate_df.index = time_list
        output[plate] = plate_df

    return output


def calibrate_image(filename, convert=True):
    """Return a normalized gray scale image."""
    image = imread(filename)
    image /= image.max()
    return canny(image, sigma=CANNY_SIGMA)


def analyze_image(filename):
    """Analyze all wells from all trays in one image."""
    config = analyze_image.config
    rows = config["rows"]
    columns = config["columns"]
    well_names = config["well_names"]

    image = rgb2gray(imread(filename))

    plate_images = cut_image(image)

    data = dict()

    for i, (plate_name, plate_image) in enumerate(
            zip(config["plate_names"], plate_images)):
        if i // 3 == 0:
            calibration_plate = config["left_image"]
            positions = config["left_positions"]
        else:
            calibration_plate = config["right_image"]
            positions = config["right_positions"]

        edge_image = canny(plate_image, CANNY_SIGMA)
        offset = align_plates(edge_image, calibration_plate)

        # Add the offset to get the well centers in the analyte plate
        well_centers = generate_well_centers(
            np.array(positions) + offset, analyze_image.plate_size, rows,
            columns)
        assert len(well_centers) == rows * columns

        plate_image /= (1 - plate_image)

        well_intensities = [find_well_intensity(plate_image, center)
                            for center in well_centers]

        for well_name, intensity in zip(well_names, well_intensities):
            data.setdefault(plate_name, {}).setdefault(well_name, []).append(
                intensity)
    for plate_name in data:
        data[plate_name] = DataFrame(data[plate_name])
    return data


def generate_well_centers(position, size, rows, columns):
    """Returns coordinates given an origin, a plate size, and its dimensions."""
    xs = (np.arange(0, size[0], size[0] / (columns * 2)) + position[0])[1::2]
    ys = (np.arange(0, size[1], size[1] / (rows * 2)) + position[1])[1::2]
    return np.array([(int(round(x)), int(round(y))) for x in xs for y in ys])


def find_well_intensity(image, center, radius=4, n_mean=10):
    """Find the mean of the *n_mean* darkest pixels within *radius*."""
    im_slice = image[(center[0] - radius):(center[0] + radius + 1),
                     (center[1] - radius):(center[1] + radius + 1)].flatten()
    im_slice.sort()
    darkest = np.percentile(im_slice[:n_mean], 50)
    return darkest

