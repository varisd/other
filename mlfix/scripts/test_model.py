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
targets = args.target.split('|')

# Read the data
test_X = []
test_Y = []
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

	test_X.append(feat_row)
	test_Y.append(target_row)

# Load model (TODO: and print some info)
m = model.Model()
m.load(args.model_file, True)
#m.print_params()

# predict classes and compare results
correct = 0
for i in range(len(test_Y)):
	predicted = m.predict_proba(test_X)
	res = [sorted(zip(m.get_classes(), s), key=(lambda x: x[1]), reverse=True) for s in predicted]
	for res_line in res:
		print res_line
	print m.predict(test_X[0])
	break
	predicted = zip(m.get_classes(), predicted[0])
	predicted = sorted(predicted, key=(lambda x: x[1]), reverse=True)
	pred_list = []
	test_list = []
	print '##'.join([';'.join([str(key) + ':' + str(item) for key, item in pred[0].iteritems()]) + '#' + str(pred[1]) for pred in predicted])
	for key, value in predicted[0][0].iteritems():
		pred_list.append(value)
		test_list.append(test_Y[i][key])
	p = ';'.join(pred_list)
	t = ';'.join(test_list)
	if (p == t):
		correct += 1
	print "predicted: %s\tcorrect: %s" % (p, t)

acc = float(correct)/len(test_Y)

print "\nAccuracy: %f" % (acc)
