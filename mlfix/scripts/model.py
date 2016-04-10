from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import RidgeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import Perceptron
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction import FeatureHasher
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_selection import SelectKBest
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn import tree
from sklearn.externals import joblib
#import baseline
import sys, gzip

def saveModel(model, file_path):
    joblib.dump(model, file_path, compress = 3)

def loadModel(file_path):
    return joblib.load(file_path)

class Model:

    model = None
    pipeline = None
    label_encoder = None

    def __init__(self, model_type=None, \
                    model_params="", \
                    sparse_vectorizer=True, \
                    n_comps=10):
        if (model_type == None):
            self.model = None
            self.pipeline = None
            self.lable_encoder = None
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

        #self.feat_vectorizer = DictVectorizer(sparse=sparse_vectorizer)
        feat_vectorizer = FeatureHasher()
        scaler = StandardScaler(with_mean=False)
        combined_features = FeatureUnion([('truncatedSVD', TruncatedSVD(n_components=10))])
        self.pipeline = Pipeline([('vectorizer', feat_vectorizer), ('features', combined_features), ('scaler', scaler), ('model', self.model)])
        self.label_encoder = LabelEncoder()
    
    def fit(self, X, Y):
        Xtr = [self.transform_features(i) for i in X]
        Y = self.label_encoder.fit_transform(Y)
        self.pipeline.fit(Xtr, Y)

    def predict(self, X):
        if not isinstance(X, list):
            raise ValueError(X)
        Xtr = [self.transform_features(i) for i in X]
        return self.label_encoder.inverse_transform(self.pipeline.predict(Xtr))
    
    def predict_proba(self, X):
        if not isinstance(X, list):
            raise ValueError(X)
        Xtr = [self.transform_features(i) for i in X]
        return self.pipeline.predict_proba(Xtr)

    def score(self, X, Y):
        Xtr = [self.transform_features(i) for i in X]
        Y = self.label_encoder.transform(Y)
        return self.pipeline.score(Xtr, Y)

    def get_classes(self):
        return self.label_encoder.inverse_transform(self.model.classes_)
 
    def print_params(self, file_path):
        f = open(file_path, "w")
        if (self.model.__class__.__name__ == "DecisionTreeClassifier"):
            f = tree.export_graphviz(self.model, out_file=f)
        f.close()

    def transform_features(self, features):
        """ Transform features with string values into new sets of features. """
        transformed = dict()
        if isinstance(features, unicode):
            raise ValueError(features)
        for name, value in features.iteritems():
            if isinstance(value, basestring):
                name = "%s_%s" % (name,value)
                value = 1.
            transformed[name] = float(value)
        return transformed

