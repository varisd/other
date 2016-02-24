from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import RidgeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import Perceptron
from sklearn.feature_extraction import DictVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn import tree
import cPickle
#import baseline
import sys, gzip

class Model:

    model = None
    feat_vectorizer = None
    label_encoder = None

    def __init__(self, model_type=None, model_params="", sparse_vectorizer=True):
        if (model_type == None):
            self.model = None
            self.feat_vectorizer = None
            label_encoder = None
            return

        #if (model_type == "baseline"):
        #    self.model = baseline.Baseline()
        if (model_type == "svm"):
            self.model = eval("SVC(" + model_params + ")")
            #self.model = SVC(kernel="linear")
        elif (model_type == "knn"):
            self.model = eval("KNeighborsClassifier(" + model_params + ")")
            #self.model = KNeighborsClassifier(n_neighbors=3)
        elif (model_type == "ridge_classifier"):
            self.model = eval("RidgeClassifier(" + model_params + ")")
        elif (model_type == "naive_bayes"):
            self.model = MultinomialNB()
        elif (model_type == "decision_trees"):
            self.model = DecisionTreeClassifier(random_state=0)
        elif (model_type == "log_regression"):
            self.model = eval("LogisticRegression(" + model_params + ")")
        elif (model_type == "perceptron"):
            self.model = eval("Perceptron(" + model_params + ")")
        elif (model_type == "extra_trees"):
            self.model = eval("ExtraTreesClassifier(" + model_params + ")")
        elif (model_type == "random_forest"):
            self.model = eval("RandomForestClassifier(" + model_params + ")")
        else:
            print >> sys.stderr, "Model of type " + model_type + " is not supported."

        self.feat_vectorizer = DictVectorizer(sparse=sparse_vectorizer)
        self.label_encoder = LabelEncoder()
    
    def fit(self, X, y):
        X = self.feat_vectorizer.fit_transform(X)
        y = self.label_encoder.fit_transform(y)
        self.model.fit(X, y)

    def predict(self, x):
        x = self.feat_vectorizer.transform(x)
        return self.label_encoder.inverse_transform(self.model.predict(x)).tolist()
    
    def predict_proba(self, x):
        x = self.feat_vectorizer.transform(x)
        return self.model.predict_proba(x)

    def predict_loss(self, X):
        if self.model.__class__.__name__ == "Perceptron":
            X = self.feat_vectorizer.transform(X)
            return -self.model.decision_function(X)
        probs = self.predict_proba(X)
        return probs[:,0]

    def score(self, X, y):
        X = self.feat_vectorizer.transform(X)
        y = self.label_encoder.transform(y)
        return self.model.score(X, y)

    def save(self, file_path, compress=False):
        if compress:
            f = gzip.open(file_path, "wb")
        else:
            f = open(file_path, "w")
        cPickle.dump((self.model, self.feat_vectorizer, self.label_encoder), f, protocol=cPickle.HIGHEST_PROTOCOL)
        f.close()

    def load(self, file_path, compress=False):
        if compress:
            f = gzip.open(file_path, "rb")
        else:
            f = open(file_path, "r")
        (self.model, self.feat_vectorizer, self.label_encoder) = cPickle.load(f)
        f.close()
       
    def get_classes(self):
        return self.label_encoder.inverse_transform(self.model.classes_)
 
    def print_params(self, file_path):
        f = open(file_path, "w")
        if (self.model.__class__.__name__ == "DecisionTreeClassifier"):
            f = tree.export_graphviz(self.model, out_file=f)
        f.close()

