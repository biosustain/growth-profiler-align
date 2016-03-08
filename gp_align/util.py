import numpy as np


def list_of_well_names(n_rows, n_columns, orientation="top_left"):
    """Returns a list of well names in left-to-right reading direction
    Orientation is given as the corner where A1 is located."""
    rows = ["A", "B", "C", "D", "E", "F", "G", "H"]
    columns = list(range(1, 13))
    rows = rows[:n_rows]
    columns = columns[:n_columns]

    if orientation == "top_left":
        out = [row+str(col) for row in rows for col in columns]

    elif orientation == "top_right":
        rows = list(reversed(rows))
        out = [row+str(col) for col in columns for row in rows]

    elif orientation == "bottom_right":
        rows = list(reversed(rows))
        columns = list(reversed(columns))
        out = [row+str(col) for row in rows for col in columns]

    elif orientation == "bottom_left":
        columns = list(reversed(columns))
        out = [row+str(col) for col in columns for row in rows]

    else:
        raise ValueError("Valid orientations are ['top_left', 'top_right', 'bottom_right', 'bottom_left']")

    return out


def split_image_in_n(image, n_height=3, n_width=2):
    """Evenly cuts an image into bits. The returned order is column-wise left-to-right"""
    height, width = image.shape
    output = []
    for j in range(n_width):
        for i in range(n_height):
            output.append(
                np.array(image[
                    i*height//n_height:(i+1)*height//n_height,
                    j*width//n_width:(j+1)*width//n_width
                ]) # Take "slices" out of the image
            )
    return output