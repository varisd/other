#!/usr/bin/env python

import os, sys, argparse
import gzip
import model

# Parse command line arguments
parser = argparse.ArgumentParser(description="Train a Scikit-Learn classification model.")
parser.add_argument('train', metavar='training_data', type=str)
parser.add_argument('target', metavar='predicted_category', type=str)
parser.add_argument('model_type', metavar='model_type', type=str)
parser.add_argument('model_params', metavar='model_parameters', type=str)
parser.add_argument('output', metavar='output_file', type=str)
args = parser.parse_args()

fh = gzip.open(args.train, 'rb', 'UTF-8')
line = fh.readline().rstrip("\n")
feature_names =  line.split("\t")
targets = args.target.split('|')
model_type = args.model_type

# some models doesn't support sparse matrices
dense_models = ["extra_trees", "random_forest"]
sparse = True
if model_type in dense_models:
	sparse = False

# Read the data
train_X = []
train_Y = []
while True:
	line = fh.readline().rstrip("\n")
	if not line:
		break
	feat_values = line.split("\t")
	
	feat_row = dict()
	target_row = dict()
	for i in range(len(feature_names)):
		if feature_names[i] in targets:
			target_row.update({feature_names[i]:feat_values[i]})
		elif "new" not in feature_names[i]:
			feat_row.update({feature_names[i]:feat_values[i]})

	train_X.append(feat_row)
	train_Y.append(target_row)


# Train and save model
m = model.Model(model_type, args.model_params, sparse)
m.fit(train_X, train_Y)
m.save(args.output, True)
