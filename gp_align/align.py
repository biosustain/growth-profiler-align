from __future__ import division, absolute_import, print_function

import numpy as np


RADIUS = 20


def align_plates(plate_image, calibration_plate):
    """Both images should be converted to edges
    Returns a vector (x, y) that describes the translation from the calibration plate to the analyte plate"""
    r = int(RADIUS)
    best_offset = (0, 0)
    best_value = 0
    for i in np.linspace(-r, r, 2*r+1).astype(int):
        for j in np.linspace(-r, r, 2*r+1).astype(int):
            value = compare_images(plate_image, calibration_plate, i, j)
            if value > best_value:
                best_value = value
                best_offset = (i, j)
    # TODO: Some check for best_value to validate that the images are properly aligned

    return np.array(best_offset)


def compare_images(image1, image2, x, y):
    """Returns the number of pixels where both images are True/white/on when they are overlapped
    with the given offset (x, y)"""
    shape1 = image1.shape
    shape2 = image2.shape
    image1_slice = image1[
        max(0, x): min(shape1[0], shape2[0]+x),
        max(0, y): min(shape1[1], shape2[1]+y)
    ]
    image2_slice = image2[
        max(0, -x): min(shape2[0], shape1[0]-x),
        max(0, -y): min(shape2[1], shape1[1]-y)
    ]
    assert image1_slice.shape == image2_slice.shape

    overlap = (image1_slice & image2_slice).sum()
    return overlap