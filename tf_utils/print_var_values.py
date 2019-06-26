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
    parser.add_argument("--variables", type=str, default="",
                        help="Which values to print.")
    args = parser.parse_args()

    reader = tf.contrib.framework.load_checkpoint(args.checkpoint)
    for name in args.variables.split(","):
        if reader.has_tensor(name):
            print("{}\t{}".format(name, reader.get_tensor(name)))
        else:
            #TODO
            pass


if __name__ == "__main__":
    main()
