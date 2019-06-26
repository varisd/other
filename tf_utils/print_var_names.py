#!/usr/bin/env python3
"""Print the names of the variables present within a TF model checkpoint.

Prints out TAB separated name and shape of each model variable
"""

import argparse
import os
import re

import numpy as np
import tensorflow as tf


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=str,
                        help="Processed model checkpoint.")
    args = parser.parse_args()

    var_list = tf.contrib.framework.list_variables(args.checkpoint)
    var_values, var_dtypes = {}, {}
    # TODO: print also var_dtypes?
    for (name, shape) in var_list:
        print("{}\t{}".format(name, shape))


if __name__ == "__main__":
    main()
