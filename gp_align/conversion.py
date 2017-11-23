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

"""Convert values in data frames."""

from __future__ import absolute_import

import logging

from numpy import exp, log

LOGGER = logging.getLogger(__name__)


def convert_run(df, *params):
    """
    Transform the G values in a given data frame.

    Parameters
    ----------
    df : pandas.DataFrame
        A data frame with a 'time' column and G values.
    params : float
        Three parameters for the exponential function. (In principle
        extensible to other functions and parameters.)

    Returns
    -------
    pandas.DataFrame
        The transformed data frame with OD values.

    """
    wells = [col for col in df.columns if col.lower() != "time"]
    df.loc[:, wells] = df.loc[:, wells].apply(g2od, raw=True, args=params)
    return df


def g2od(vector, a, b, c):
    return exp((vector - c) / a) - b


def od2g(vector, a, b, c):
    return a * log(vector + b) + c
