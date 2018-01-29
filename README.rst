==============================
Growth Profiler Image Analyzer
==============================

This package contains functions for analysing the raw image outputs of
the growth profiler.

Installation
------------

Installing Python
~~~~~~~~~~~~~~~~~

Skip this if you already have a working installation of Python. To use
this package you need to have Python. Using the operating system's
built-in Python interpreter is not recommended. The easiest way to
obtain Python is from https://www.continuum.io/downloads - Select the
relevant OS and download the Python 3.X installer (Python 2.7 will also
work for now, but Python 3 is recommended). - Run the installer and
follow the instructions. - Open a terminal (windows: search for 'command
prompt'/'cmd.exe', OSX/Linux: search for 'terminal') in your operating
system and type ``python -V``. This should print the version of Python,
and contain the word 'Anaconda'

Installing the Growth Profiler Image Analyzer (``gpalign``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Installation is as easy as running the following line of code in your
terminal (Anaconda or other Python environment).

.. code-block:: console

    $ pip install https://github.com/biosustain/growth-profiler-align/archive/master.zip

This will install all necessary requirements as well as the ``gpalign``
command line program.

Usage
-----

You can find useful information in the help of the ``gpalign`` program and
its subcommands.

.. code-block:: console

    $ gpalign -h
    $ gpalign analyze -h
    $ gpalign convert -h

Analyzing the Images
~~~~~~~~~~~~~~~~~~~~

-  Navigate to the directory where you want the output files to be
   placed. Make sure this is a location where you have permission to
   create files, e.g., a subdirectory of Documents.
-  Figure out which plate type was used for the run and use the number
   in the subsequent commands:

   -  Black 96 well (``<plate type>=1``)
   -  White 96 well (``<plate type>=2``)
   -  White 24 well (``<plate type>=3``)

-  To analyse the plates run the following code filling in the parameters:

   .. code-block:: console

       $ gpalign analyze --scanner <1 or 2> --plate_type <plate type> --out <base path> "<terminal pattern for images>"

-  To analyse the plates in scanner 2, for example, run

   .. code-block:: console

       $ gpalign analyze --scanner 2 --plate_type 2 --out Profiles/scanner_2 "Images/Scanner 2/*.Png"

-  The output files will have ``_trayX.G.tsv`` appended to the output path.
   For the above example: ``Profiles/scanner_2_tray1.G.tsv`` and so on.
   The below table shows how the trays are organised in the scanners.
-  **N.B.:** You should place your plates such that A1 is in the upper
   right corner. Otherwise you should add the argument
   ``--orientation bottom-left`` to the above commands.
-  You can choose to analyse individual plates only by specifying the
  ``--trays`` parameter one or more times:

   .. code-block:: console

       $ gpalign analyze --scanner 2 --plate_type 2 --trays 7,10 --out Profiles/scanner_2 "Images/Scanner 2/*.Png"

Tray Layouts
~~~~~~~~~~~~

+-------------+-----+
| Scanner 1         |
+=============+=====+
| 1           | 4   |
+-------------+-----+
| 2           | 5   |
+-------------+-----+
| 3           | 6   |
+-------------+-----+

+-------------+------+
| Scanner 2          |
+=============+======+
| 7           | 10   |
+-------------+------+
| 8           | 11   |
+-------------+------+
| 9           | 12   |
+-------------+------+

Converting the G-values to OD
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Obtain a set of calibration parameters (A, B, C) from Kristian
-  Run ``gpalign convert A B C "<terminal pattern>"``
