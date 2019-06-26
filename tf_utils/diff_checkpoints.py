#!/usr/bin/env python3
"""Take two checkpoints and print the mean difference of their
variables and its difference.

Print results for the selected variables.
"""

import argparse
import os
import re
import sys

import numpy as np
import tensorflow as tf


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoints", type=str,
                        help="Processed model checkpoint.")
    parser.add_argument("--variables", type=str, default="",
                        help="Which values to print.")
    args = parser.parse_args()

    ckpts = args.checkpoints.split(","):
    if len(ckpts) != 2:
        raise ValueError("You must provide exactly two checkpoints.")

    reader1 = tf.contrib.framework.load_checkpoint(ckpts[0])
    reader2 = tf.contrib.framework.load_checkpoint(ckpts[1])
    for name in args.variables.split(","):
        if reader1.has_tensor(name) and reader2.has_tensor(name):
            val = reader1.get_tensor(name) - reader2.get_tensor(name)
            val = np.abs(val)
            print("{}\t{}\t{}".format(name, np.mean(val), np.var(val)))
        else:
            print("Tensor '{}' is missing from one of the provided "
                  "checkpoints.".format(name), file=sys.stderr)


if __name__ == "__main__":
    main()
