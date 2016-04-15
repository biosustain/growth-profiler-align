from __future__ import division, absolute_import, print_function

import sys
from gp_align.cli import parser

arguments = sys.argv[1:]

# if not os.path.isdir(arguments[0]):
#     raise ValueError("First argument must be the name of a directory containing the growth profiler images")
#
# image_dir = arguments[0]
#
# contents = os.listdir(image_dir)
#
# images = [f for f in contents if f.lower().endswith(".png")]
#
# panel = gp_align.analyse.analyse_run([os.path.join(image_dir, name) for name in images])
#
# import sys

from gp_align.cli import parser


def main():
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    sys.exit(main())

