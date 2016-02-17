#!/usr/bin/env python

import os, sys, argparse
import gzip
import model

# TODO: dump some info

# Parse command line arguments
parser = argparse.ArgumentParser(description="Test scikit-learn model accuracy.")
parser.add_argument('model_file', metavar='model_file', type=str)
parser.add_argument('data_file', metavar='test_data', type=str)
parser.add_argument('target', metavar='predicted_category', type=str)
args = parser.parse_args()

fh = gzip.open(args.data_file, 'rb', 'UTF-8')
line = fh.readline().rstrip("\n")
feature_names =  line.split("\t")

# Read the data
test_X = []
test_Y = []
while True:
	line = fh.readline().rstrip("\n")
	if not line:
		break
	feat_values = line.split("\t")
	
	feat_row = dict()
	for i in range(len(feature_names)):
		if feature_names[i] == args.target:
			test_Y.append(feat_values[i])
		elif "new" not in feature_names[i]:
			feat_row.update({feature_names[i]:feat_values[i]})

	test_X.append(feat_row)

# Load model (TODO: and print some info)
m = model.Model()
m.load(args.model_file, True)
#m.print_params()

# predict classes and compare results
predicted = m.predict(test_X)
correct = 0
for i in range(len(predicted)):
	if (predicted[i] == test_Y[i]):
		correct += 1
	print "predicted: %s\tcorrect: %s" % (predicted[i], test_Y[i])

print "\nAccuracy: %s" % (correct/len(predicted))
