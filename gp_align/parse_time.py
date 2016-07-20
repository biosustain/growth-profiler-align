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

"""Parse datetimes from image filenames."""

from __future__ import absolute_import

import os
from datetime import datetime


def fix_date(timestamp):
    """
    Try to correct an erroneous image filename.

    Fix a datetime string where leading zeros of day and month have been
    omitted. It can NOT however be used to explain why anyone would do this in
    the first place.

    Notes
    -----
    Ambiguous dates will be fixed to the date that comes FIRST in a year, e.g.,
    112 will be Feb 11 not Dec 1.
    """
    ds, ts = timestamp[:-6], timestamp[-6:]
    d = datetime.strptime(ds, "%d%m%Y")
    return "%0.2d%0.2d%0.4d" % (d.day, d.month, d.year) + ts


def convert_to_datetime(string):
    return datetime.strptime(string, "%d%m%Y%H%M%S")


def sort_filenames(image_list):
    date_dict = {image_name: convert_to_datetime(
        fix_date(os.path.split(image_name)[-1].split(".")[0]))
        for image_name in image_list
    }
    sorted_image_list = sorted(image_list, key=date_dict.get)
    time_list = [
        round((date_dict[name] - date_dict[sorted_image_list[0]]).total_seconds() / 60) for name in sorted_image_list
    ]
    return time_list, sorted_image_list
