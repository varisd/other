#!/usr/bin/env python3
"""Replace the names of the variables in a TF model checkpoint with new ones.

Replace the names of variables matching ``in_regex'' with value
of ``out_regex''.
Drop the variables that match ``the remove regex'' (before renaming).
"""

import argparse
import os
import re

import numpy as np
import tensorflow as tf


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=str,
                        help="Processed model checkpoint")
    parser.add_argument("--in_regex", type=str,
                        help="Input substitution regex")
    parser.add_argument("--out_regex", type=str,
                        help="Output substitution regex")  
    parser.add_argument("--remove_regex", type=str,
                        help="Regex for removal")
    parser.add_argument("--output_path", type=str,
                        help="Path to output the renamed checkpoint to.")
    parser.add_argument("--dry_run", type=bool, default=False,
                        help="Only show the variable name changes.")
    parser.add_argument("--add_global_step", type=bool, default=False,
                        help="Add global_step to the checkpoint.")
    args = parser.parse_args()

    sub_re = None
    if args.in_regex and args.out_regex:
        sub_re = re.compile(args.in_regex)

    rm_re = None
    if args.remove_regex is not None:
        rm_re = re.compile(args.remove_regex)

    var_list = tf.contrib.framework.list_variables(args.checkpoint)
    with tf.Session() as sess:
        for (var_name, shape) in var_list:
            var = tf.contrib.framework.load_variable(args.checkpoint, var_name)

            if rm_re is not None and rm_re.match(var_name) is not None:
                if args.dry_run:
                    print("{}\t=>\t<REMOVED>".format(var_name))
                continue

            new_name = var_name
            if sub_re is not None:
                new_name = sub_re.sub(args.out_regex, var_name)
                if args.dry_run:
                    print("{}\t=>\t{}".format(var_name, new_name))
            var = tf.Variable(var, name=new_name)

        if args.add_global_step:
            gstep = tf.train.get_or_create_global_step()

        if not args.dry_run:
            # Save the variables
            saver = tf.train.Saver()
            sess.run(tf.global_variables_initializer())
            saver.save(sess, args.output_path)


if __name__ == "__main__":
    main()
