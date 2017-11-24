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
import multiprocessing
from os.path import join, dirname, basename, splitext

import numpy as np
from pandas import DataFrame, Timedelta
from skimage.color import rgb2grey
from skimage.feature import canny
from skimage.io import imread
from six import iteritems
from tqdm import tqdm

from gp_align.align import align_plates
from gp_align.parse_time import fix_date, convert_to_datetime
from gp_align.util import well_names, cut_image

LOGGER = logging.getLogger(__name__)
DATA_DIR = join(dirname(__file__), "data")
CANNY_SIGMA = 1.0
PLATES = {
    1: ["tray1", "tray2", "tray3", "tray4", "tray5", "tray6"],
    2: ["tray7", "tray8", "tray9", "tray10", "tray11", "tray12"]
}


def analyze_run(images, scanner=1, plate_type=1, orientation="top-right",
                plates=None, unit="h", num_proc=1):
    """
    Analyse a list of images from the Growth Profiler.

    Parameters
    ----------
    plate_type :
        The type of plates used
    plates : optional
        Specify which plates will be analysed e.g. [1, 2, 3] for the three left
        plates. Default (None) is to analyze all plates.
    unit : {'D', 'h', 'm'}, optional
        The unit of time. Any valid numpy datetime unit but usefully either
        D, h, or m.
    num_proc : int, optional
        Number of processes to use for the calculations.
    """
    unit = Timedelta(1, unit=unit)
    if plates is not None:
        raise NotImplementedError(
            "Selection of specific plates or trays is not possible yet.")
    config = configure_run(scanner, plate_type, orientation)

    data = dict()
    LOGGER.info("%d images in the series.", len(images))
    pool = multiprocessing.Pool(processes=num_proc)
    LOGGER.debug("Submitting tasks...")
    result_iter = pool.imap_unordered(analyze_image,
                                      [(i, config) for i in images])
    pool.close()
    with tqdm(total=len(images)) as pbar:
        for res in result_iter:
            if "error" in res:
                LOGGER.error("Image '%s' produced the following error: %s.",
                             res["filename"], res["error"])
            else:
                for plate, row in iteritems(res):
                    data.setdefault(plate, list()).append(row)
            pbar.update()
    pool.join()

    for plate, plate_data in iteritems(data):
        LOGGER.debug("Plate '%s' has %d rows and %d columns.",
                     plate, len(plate_data), len(plate_data[0]))

    output = dict()
    columns = config["well_names"]
    columns.insert(0, "time")
    for plate, plate_data in iteritems(data):
        plate_df = DataFrame(plate_data)
        assert len(plate_df.columns) == len(columns), "{:d} != {:d}".format(
            len(plate_df.columns), len(columns))
        plate_df.sort_values("time", inplace=True)
        plate_df["time"] -= plate_df["time"].iat[0]
        plate_df["time"] /= unit
        plate_df.set_index("time", inplace=True)
        output[plate] = plate_df.loc[:, columns[1:]]  # order columns
    return output


def configure_run(scanner, plate_type, orientation):
    config = dict()
    config["plate_names"] = PLATES[scanner]

    with io.open(join(DATA_DIR, "plate_specs.json"), encoding=None) as file_h:
        plate_specs = json.load(file_h)
    rows, columns = plate_specs["rows_and_columns"][str(plate_type)]
    config["rows"] = rows
    config["columns"] = columns
    LOGGER.debug("Plate type %d has %d rows and %d columns.", plate_type,
                 rows, columns)

    calibration_name_left = "calibration_type_{:d}_left".format(plate_type)
    config["left_image"] = detect_edges(join(
        DATA_DIR, calibration_name_left + ".png"))

    calibration_name_right = "calibration_type_{:d}_right".format(plate_type)
    config["right_image"] = detect_edges(join(
        DATA_DIR, calibration_name_right + ".png"))

    config["well_names"] = well_names(rows, columns, orientation)
    config["plate_size"] = plate_specs["plate_size"]
    config["left_positions"] = plate_specs[
        "plate_positions"][calibration_name_left]
    config["right_positions"] = plate_specs[
        "plate_positions"][calibration_name_right]
    return config


def detect_edges(filename):
    """Return a normalized gray scale image."""
    LOGGER.debug(filename)
    image = rgb2grey(imread(filename))  # rgb2gray can be a noop
    image = image / image.max()
    return canny(image, sigma=CANNY_SIGMA)


def analyze_image(args):
    """Analyze all wells from all trays in one image."""
    filename, config = args
    LOGGER.debug(filename)
    rows = config["rows"]
    columns = config["columns"]
    well_names = config["well_names"]

    try:
        image = rgb2grey(imread(filename))
    except OSError as err:
        return {"error": str(err), "filename": filename}

    plate_images = cut_image(image)

    data = dict()
    time = convert_to_datetime(
        fix_date(splitext(basename(filename))[0]))

    for i, (plate_name, plate_image) in enumerate(
            zip(config["plate_names"], plate_images)):
        plate = data[plate_name] = dict()
        plate["time"] = time
        if i // 3 == 0:
            calibration_plate = config["left_image"]
            positions = config["left_positions"]
        else:
            calibration_plate = config["right_image"]
            positions = config["right_positions"]

        try:
            edge_image = canny(plate_image, CANNY_SIGMA)
            offset = align_plates(edge_image, calibration_plate)

            # Add the offset to get the well centers in the analyte plate
            well_centers = generate_well_centers(
                np.array(positions) + offset, config["plate_size"], rows,
                columns)
            assert len(well_centers) == rows * columns

            plate_image /= (1 - plate_image)

            well_intensities = [find_well_intensity(plate_image, center)
                                for center in well_centers]

            for well, intensity in zip(well_names, well_intensities):
                plate[well] = intensity
        except (AttributeError, IndexError) as err:
            return {"error": str(err), "filename": filename}

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
