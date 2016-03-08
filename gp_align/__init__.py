from __future__ import absolute_import

import json
import os
from gp_align import util
from gp_align import align
from gp_align import analyse
from gp_align import parse_time

with open(os.path.join(os.path.dirname(__file__), "data/plate_specs.json")) as infile:
    plate_specs = json.load(infile)


