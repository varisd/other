#!/usr/bin/env python
# -*- coding: utf-8 -*-

# TODO: speed up the Search Phase (is it possible?)

# TODO: separate training, analysis (so we don't have to train everytime)
#   -> save/load scheme/cluster

# TODO: implement more statistical methods for clustering, similarity computing, tec.

# TODO: improve info/debug messages?

from __future__ import print_function
from time import gmtime, strftime
import string, codecs, argparse, sys, gzip, copy, math


class Scheme:
    """ParaMor Scheme data structure representation"""

    # stems - set
    # suffixes - set

    def __init__(self, stem, suff):
        self.stems = set([stem])
        self.suffixes = set([suff])

    def __repr__(self):
        return str.join(".",sorted(self.suffixes))

    def __hash__(self):
        return hash(self.__repr__())

    def add_stem(self, stem):
        self.stems.add(stem)

    def add_suffix(self, suff, stem_dict):
        """Add suffix to the set and remove all invalid stems """
        self.suffixes.add(suff)
        for s in self.stems.copy():
            if not suff in stem_dict[s]:
                self.stems.remove(s)

    def num_of_stems(self):
        return len(self.stems)

    def num_of_suffixes(self):
        return len(self.suffixes)

    def num_of_valid_stems(self, suff, stem_dict):
        """Return number of stems, that form a valid wordform with the 'suff'"""
        k = 0
        for s in self.stems:
            if suff in stem_dict[s]:
                k += 1
        return k

    def get_stem_suff(self):
        """Return set of stem-suffix pairs covered by a scheme"""
        result = set()
        for stem in self.stems:
            for suff in self.suffixes:
                # we want to indicate the morpheme boundary
                result.add(stem + "." + suff)
        return result

    def to_string(self):
        """We use this string as a unique identifier of a scheme"""
        return self.__repr__()

    def size(self):
        """Size of a scheme (for clustering cutoff)"""
        return len(self.stems) * len(self.suffixes)
                

class Cluster(Scheme):
        """Object to represent ParaMor's clusters"""
        
        # active ... false, if the cluster is merged into other
        # schemes - set of Scheme
        # suffixes - set
        # stems - set ... stems shared by all the suffixes
        # words - set ... stem-suffix pairs of cluster
        # large_count 
            # ... if > 0, we can merge with small scheme
            # ... small scheme's initial cluster has value -1
            # ... large scheme's initial cluster has value 1

        def __init__(self, scheme):
            self.schemes = set([scheme])
            # since we modify the clusters set during merges, we use a shallow copy
            self.suffixes = set(scheme.suffixes)
            self.stems = set(scheme.stems)
            self.words = scheme.get_stem_suff()
            if scheme.size() > threshold:
                self.large_counter = 1
            else:
                self.large_counter = -1
            self.active = 1

        def num_of_schemes(self):
            return len(self.schemes)

        def find_common_prefix(self):
            """Returns the longest prefix common to all of the cluster's suffixes"""
            # find common prefix
            prfx = None
            for suff in self.suffixes:
                if prfx == None: prfx = suff

                # handle null suffix
                suff = suff.replace("Ø".decode('UTF-8'), "")

                new_prfx = str()
                if len(suff) < len(prfx): suff,prfx = prfx,suff
                for i in range(len(prfx)):
                    if suff[i] == prfx[i]: new_prfx += prfx[i]
                prfx = new_prfx
            return prfx
                
        def strip_common_prefix(self):
            """Returns list of suffixes, after their longest common prefix is stripped"""
            prfx = self.find_common_prefix()
            result = list()
            for suff in self.suffixes:
                
                result.append(suff[len(prfx):])
            return result

        def similarity(self, cluster):
            """Compute cosine similarity score between clusters"""
            a = self.words
            b = cluster.words
            return len(a.intersection(b)) / math.sqrt(len(a)*len(b))

        def can_merge(self, cluster):
            # cannot merge two small (-1, -1) schemes, or a small scheme with cluster without enough large schemes (-1,0 or 0,-1)
            if self.large_counter + cluster.large_counter < 0:
                return False

            # check if the clusters share some stems
            if len(self.stems.intersection(cluster.stems)) == 0:
                return False

            return True

        def merge(self, cluster):
            """Merge clusters and deactivate the 'cluster'"""
            self.schemes = self.schemes.union(cluster.schemes)
            self.suffixes = self.suffixes.union(cluster.suffixes)
            self.words = self.words.union(cluster.words)
            self.stems = self.stems.intersection(cluster.stems)
            self.large_counter += cluster.large_counter

            # deactivate the merged cluster
            cluster.active = 0

def search_path(scheme):
    # return self, if we cannot find suitable parent
    result = scheme

    # we sort the keys from the ones that eliminate the least of the shceme's stems to the ones that eliminate the most
    suffixes = bottom_schemes.keys()
    suffixes = sorted(suffixes, key=lambda x: scheme.num_of_valid_stems(x,stems), reverse=True)

    # find a candidate suffix, which we can add to the scheme
    for suff in suffixes:
        new_stem_count = scheme.num_of_valid_stems(suff, stems)

        if suff in scheme.suffixes: continue
        # check, if the 1st criterion was met
        if new_stem_count / float(scheme.num_of_stems()) < ratio:
            break # since the suffixes are sorted, we can break
        # check, if the 2nd criterion was met
        if new_stem_count <= scheme.num_of_suffixes()+1:
            break # same here

        parent = copy.deepcopy(scheme)
        parent.add_suffix(suff, stems)

        # check, if the scheme was already visited via another path
        if parent.to_string() in visited: continue

        # now we can do the recursion
        visited.add(parent.to_string())
        result = search_path(parent)
        break

    return result

def log_msg(msg):
    """Write msg with a timestamp to std err"""
    msg = "  " + msg
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + msg, file=sys.stderr)

### Main Program ###

# Free parameters
ratio = 0.25
threshold = 37

parser = argparse.ArgumentParser(description="Implementaiton of ParaMor unsupervised morphological analyzer")
parser.add_argument('train', metavar='training_data', type=str)
parser.add_argument('test', metavar='testing_data', type=str)
parser.add_argument('scheme', metavar='output_schemes_file', type=str)
parser.add_argument('output', metavar='output_file', type=str)
args = parser.parse_args()

# schemes containing single suffix
bottom_schemes = dict()
# dictionary of stems seen in training data (each entry contains a set of possible suffixes)
stems = dict()


## Bottom Schemes (single suffixes only) ##
log_msg("Creating initial bottom schemes (single suffix)")

f = gzip.open(args.train, 'rb', 'UTF-8')
while True:
    line = f.readline()
    if not line:
        break

    line = line.rstrip("\n")
    words = line.split(" ")
    for w in words:
        w = w.decode('UTF-8')
        w = w.lower()
        for c in string.punctuation:
            w = w.rstrip(c)
        if w == "": continue

        for i in range(1,len(w)+1):
            # update stem dictionary
            stem = w[0:i]
            suff = w[i:len(w)+1]
            if suff == "": suff = "Ø".decode('UTF-8')   # null suffix
            if stems.has_key(stem):
                stems[stem].add(suff)
            else:
                stems[stem] = set([suff])
                        
            # update schemes
            if bottom_schemes.has_key(suff):
                bottom_schemes[suff].add_stem(stem)
            else:
                bottom_schemes[suff] = Scheme(stem, suff)

f.close()

log_msg(str(len(bottom_schemes.keys())) + " bottom schemes created")

## Search For Initial Schemes  ##
log_msg("Creating initial schemes (going through the search space)")

# we put the initial schemes generated by the search in their own clusters
clusters = list() 

# sort the schemes so we start from the ones, that have the most stems associated with them
keys = bottom_schemes.keys()
keys = sorted(keys, key=lambda x: bottom_schemes[x].num_of_stems(), reverse=True)

# indicate, which schemes we already explored during search
visited = set()

for key in keys:
    # cut off the loop if the number of stems is too low
    if bottom_schemes[key].num_of_stems() <= 2: break
    sch = search_path(bottom_schemes[key])
    if sch.num_of_suffixes() > 1:
        # from now on we will work with Cluster classes
        clusters.append(Cluster(sch))

log_msg(str(len(clusters)) + " initial schemes created")

## Clustering ##
log_msg("Scheme clustering start")

# stores cluster similarities
similarities = dict() 
# initialize
for i in range(len(clusters)):
    for j in range(i+1, len(clusters)):
        key = str(i) + "." + str(j)
        similarities[key] = clusters[i].similarity(clusters[j])

# do the merging
while True:
    end_clustering = 1

    keys = similarities.keys()
    keys = sorted(keys, key=lambda x: similarities[x], reverse=True)
    for key in keys:
        i,j = key.split(".")
        i = int(i)
        j = int(j)
        if not clusters[i].can_merge(clusters[j]): continue
        if not clusters[i].active or not clusters[j].active: continue

        end_clustering = 0

        # merge clusters
        clusters[i].merge(clusters[j])

        # update similarities
        for k in range(0, i):
            if not clusters[k].active: continue
            new_key = str(k) + "." + str(i)
            similarities[new_key] = clusters[i].similarity(clusters[k])
        for k in range(i+1, len(clusters)):
            if not clusters[k].active: continue
            new_key = str(i) + "." + str(k)
            similarities[new_key] = clusters[i].similarity(clusters[k])

        # throw away unnecessary keys
        for k in range(0, j):
            if not clusters[k].active: continue
            new_key = str(k) + "." + str(j)
            del similarities[new_key]

        for k in range(j+1, len(clusters)):
            if not clusters[k].active: continue
            new_key = str(j) + "." + str(k)
            del similarities[new_key]

        break
    #}

    if end_clustering: break
#}

log_msg("Clustering end. Number of scheme-clusters: " + str(len(clusters)))

## Cluster Filtering ##
log_msg("Filtering out clusters")

old_clusters = list(clusters)
clusters = list()

for i in range(len(old_clusters)):
    # remove inactive clusters
    if not old_clusters[i].active:
        continue
    # remove unclustered schemes under the size threshold
    if old_clusters[i].large_counter == -1 and old_clusters[i].num_of_schemes() == 1:
        continue  

    clusters.append(old_clusters[i])

del old_clusters
        
log_msg("Filtering end. Scheme-clusters left: " + str(len(clusters)))

## Morpheme Boundary Based Entropy Filtering  ##
log_msg("Entropy-based filtering start")

# note: since a whole lot of clusters have been filtered out in the previous step, we can afford to be little less time efficient here

# for each scheme-cluster, we try to adjust the "morpheme boundary", by stripping some of the common prefix - if the entropy of the signature increases, we throw it out
for cluster in clusters:
    prfx = cluster.find_common_prefix()
    if len(prfx) == 0: continue

    suffixes = cluster.strip_common_prefix()
    new_suffixes = set()

    # we simplify the entropy computation to counting, in how many different characters on the morpheme boundary the stems can end
    last_chars = set()
    for stem in cluster.stems:
        last_chars.add(stem[-1])
    entropy = len(last_chars)

    # now we move the m.b. and check if the entropy increases
    for i in range(1,len(prfx)+1):
        last_chars = None
        for base_suff in suffixes:
            suff = prfx[i:] + base_suff
            chars = set()
            
            # we check all the observed stems for a newly created suffix
            if not suff in bottom_schemes: break
            for stem in bottom_schemes[suff].stems:
                chars.add(stem[-1])

            if last_chars == None: last_chars = chars

            last_chars = last_chars.intersection(chars)
            # if the intersection is still empty we move on
            if len(last_chars) == 0: break
        #}

        # should we deactivate the cluster
        if (len(last_chars) > entropy):
            cluster.active = 0
    #}
#}

# throw away inactive clusters
old_clusters = list(clusters)
clusters = list()

for i in range(len(old_clusters)):
    if not old_clusters[i].active: continue
    clusters.append(old_clusters[i])

del old_clusters

log_msg("Filtering end. Final Number of scheme-clusters: " + str(len(clusters)))

log_msg("Saving schemes to " + args.scheme)
f = gzip.open(args.scheme, 'wb')
for cluster in clusters:
    f.write(cluster.to_string().encode('UTF-8'))
    f.write("\n".encode('UTF-8'))
f.close()


## Morphological Analysis ##
log_msg("Morphological Analysis start.")

test_vocab = set()

# first we collect all the words from the testing data
f = gzip.open(args.test, 'rb', 'UTF-8')
while True:
    line = f.readline()
    if not line:
        break

    line = line.rstrip("\n")
    words = line.split(" ")
    for w in words:
        w = w.decode('UTF-8')
        w = w.lower()
        for c in string.punctuation:
            w = w.rstrip(c)
        if w == "": continue
        test_vocab.add(w)

f.close()

# now do the actual analysis
f = gzip.open(args.test, 'rb', 'UTF-8')
f_out = gzip.open(args.output, 'wb')
while True:
    line = f.readline()
    if not line:
        break

    line = line.rstrip("\n")
    words = line.split(" ")
    for w in words:
        w = w.decode('UTF-8')
        w = w.lower()
        for c in string.punctuation:
            w = w.rstrip(c)
        if w == "": continue
        
        found = 0   # flag to indicate, if we found any analysis

        # we check each scheme-cluster to segment a word
        for cluster in clusters:
            for suff in cluster.suffixes:
                if w[0:len(w)-len(suff)] + suff != w: continue

                stem = w[0:len(w)-len(suff)]
                for suff2 in cluster.suffixes:
                    if suff == suff2: continue
                    w2 = stem + suff2
                    # check training and testing data vocabulary
                    if (w2 in test_vocab) or (stems.has_key(stem) and suff2 in (stems[stem])):
                        found = 1
                        f_out.write("%s.%s { %s }\n" % (stem.encode('UTF-8'), suff.encode('UTF-8'), cluster.to_string().encode('UTF-8')))

        # no complex analysis found
        if not found: f_out.write("%s\n" % (w.encode('UTF-8')))
         
f_out.close()
f.close()
