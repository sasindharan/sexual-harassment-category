
from google.colab import drive
drive.mount('/content/drive')

"""**importing libraries**"""

!pip install numpy==1.20.3 pandas==1.2.4 tensorflow-cpu tensorflow-addons==0.13.0 streamlit==0.82.0 pickle-mixin==1.0.2 lime==0.2.0.1 scikit-multilearn nltk

!pip install scikit-multilearn

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from tqdm import tqdm

import re
import datetime as dt

from sklearn.feature_extraction.text import CountVectorizer # BOW=> Bag of Words
from sklearn.feature_extraction.text import TfidfVectorizer # TF-IDF=> Term-Frequency/ Inverse-Document Frequency
from sklearn.multiclass import OneVsRestClassifier # for Multi-label/class classification
from sklearn.linear_model import LogisticRegression # Linear Model, Simple, and powerful
from sklearn.linear_model import SGDClassifier # using Optimization to minimize loss

# metrics to assess the model performance
from sklearn.metrics import f1_score, precision_score, recall_score, hamming_loss
from sklearn.metrics import multilabel_confusion_matrix,classification_report, accuracy_score
from sklearn.metrics import roc_auc_score, roc_curve, auc
from sklearn.model_selection import RepeatedStratifiedKFold, GridSearchCV

# ML Algorithms for Multi-label Classification
from skmultilearn.adapt import mlknn
from skmultilearn.problem_transform import ClassifierChain
from skmultilearn.problem_transform import BinaryRelevance
from skmultilearn.problem_transform import LabelPowerset

import tensorflow as tf # deep learning library
import pickle # to save/load the model/variable

"""**loading the dataset for Machine Learning**"""

data_path = '../dataset/multilabel_classification'

train = pd.read_csv( 'new_train.csv')
test = pd.read_csv('new_test.csv')

train.head()

test.head()

train.shape

test.shape

# https://datascience.stackexchange.com/questions/67189/unable-to-save-the-tf-idf-vectorizer
def text_splitter(text):
    """
    this function split the text and return the list of splitted words
    """
    return text.split()


# create instance of TfidfVectorizer to get TF-IDF of text data
# https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html
# https://stackoverflow.com/questions/39303912/tfidfvectorizer-in-scikit-learn-valueerror-np-nan-is-an-invalid-document
tfidf = TfidfVectorizer(
                        min_df=0.00009,
                        max_features=5000, # use 5000 after tuning # even with 500 result is almost same and not overfitting even
                        smooth_idf=True,
                        norm="l2",
                        tokenizer = text_splitter, # used function instead of lambda
                        sublinear_tf=False,
                        ngram_range=(1,3)
                       )

tfidf_train = tfidf.fit_transform(train.Description.apply(lambda x: np.str_(x)))
tfidf_test = tfidf.transform(test.Description)
print("Train and Test shape : ",tfidf_train.shape, tfidf_test.shape)

# saving the tfidf for further use
with open('tfidf.pkl', 'wb') as tf:
    pickle.dump(tfidf, tf)

tfidf

# creating label for train and test dataset
train_label = train[['Commenting','Ogling','Groping']]
test_label = test[['Commenting','Ogling','Groping']]

train_label.head()

test_label.head()

set(np.where(test_label.iloc[0])[0]) # np.where returns the index of 1's

# Hamming loss/score metrics does by XOR between the actual and predicted labels and then average across the dataset.
# https://www.linkedin.com/pulse/hamming-score-multi-label-classification-chandra-sharat/

def hamming_score(y_true, y_pred):
    """
    this function returns hamming_score for multilabel classification
    """
    acc_list = [] # to store result of all the observation and later, find the mean on calculated values.

    # typecasting to np.array to implement other numerical operations like np.where.
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)

    for i in range(y_true.shape[0]): # for each value in y_true
        set_true = set(np.where(y_true[i])[0]) # getting the index location where value is 1
        set_pred = set(np.where(y_pred[i])[0]) # same as above

        temp_a = None # to save temporary result of one observation.

        if len(set_true)==0 and len(set_pred) ==0:
            # if both predicted and real target has no positive value means they are 100% correct.
            # doing this if condition to remove division by zero error in else condition.
            temp_a =1
        else:
            temp_a = len(set_true.intersection(set_pred))/float(len(set_true.union(set_pred)))
        acc_list.append(temp_a)
    return np.mean(acc_list)

def multilabel_classification_report(model, train_data, train_label, test_data, test_label,skmultilearn=False):
    """
    This function return classification report and their result
    return :
            returns complete description of best model fitted on given train data and their labels.

    Parameters:
        skmultilearn : default=False, make it True if you are using skmultilearn library.
    """
    result = {} # to be returned

    import pandas
    if pandas.core.frame.DataFrame == type(train_label):
        train_label = train_label.values
    if pandas.core.frame.DataFrame == type(test_label):
        test_label = test_label.values

    print("################ Modeling Report ###################")
    ################ TRAIN ERROR and ACCURACY ###################
    # prediction of test dataset using best LogisticRegression()
#     print(model)
    test_predicted = model.predict(test_data)
    train_predicted = model.predict(train_data)

    # skmultilearn library returns sparse predicted matrix, so change it into dense
    if skmultilearn == True:
        test_predicted = test_predicted.toarray()
        train_predicted = train_predicted.toarray()

#     print("accuracy")
    train_accuracy = accuracy_score(train_label, train_predicted)
    test_accuracy = accuracy_score(test_label, test_predicted)

    result['train_accuracy']=train_accuracy
    result['test_accuracy']=test_accuracy

#     print("f1-score")
    train_f1_score = f1_score(train_label, train_predicted, average='macro')
    test_f1_score = f1_score(test_label, test_predicted, average='macro')

    result['train_f1_score']=train_f1_score
    result['test_f1_score']=test_f1_score

#     print("recall score")
    train_recall_score = recall_score(train_label, train_predicted, average='macro')
    test_recall_score = recall_score(test_label, test_predicted, average='macro')

    result['train_recall']=train_recall_score
    result['test_recall']=test_recall_score

#     print("Hamming loss")
    train_hamming_loss = hamming_loss(train_label, train_predicted)
    test_hamming_loss = hamming_loss(test_label, test_predicted)
    result['train_hamming_loss'] = train_hamming_loss
    result['test_hamming_loss'] = test_hamming_loss

#     print("Hamming score")
    train_hamming_score = hamming_score(train_label, train_predicted)
    test_hamming_score = hamming_score(test_label, test_predicted)
    result['train_hamming_score'] = train_hamming_score
    result['test_hamming_score'] = test_hamming_score

#     print("Hamming score finalized")


    print("TRAIN Accuracy(exact match) : ",train_accuracy)
    print("TEST Accuracy(exact match) : ",test_accuracy)
    print("="*50)
    print("TRAIN f1-score(macro) : ",train_f1_score)
    print("TEST f1-score(macro) : ",test_f1_score)
    print("="*50)
    print("TRAIN hamming loss : ",train_hamming_loss)
    print("TEST hamming loss : ",test_hamming_loss)
    print("="*50)
    print("TRAIN hamming score : ", train_hamming_score)
    print("TEST hamming score : ", test_hamming_score)

    print("#"*50)
    print("Confusion MATRIX")
    print("TRAIN : ",multilabel_confusion_matrix(train_label, train_predicted))
    print("TEST : ", multilabel_confusion_matrix(test_label, test_predicted))
    print("multilabel confusion matrix")
    ###########################################################################

    ############### CLASSIFICATIO RESULT of both Train, and Test dataset ######
    train_cf_report = classification_report(train_label, train_predicted)
    test_cf_report = classification_report(test_label, test_predicted)

    print("Classification report of TRAIN : ")
    print(train_cf_report)
    print("Classification report of TEST : ")
    print(test_cf_report)
    #############################################################################################

    ################### ROC-AUC Score ###########################################################
    # getting train_score, and test_score
    test_prob = model.predict_proba(test_data)
    train_prob = model.predict_proba(train_data)

    # skmultilearn return sparse predicte matrix, so change it into dense
    if skmultilearn == True:
        test_prob = test_prob.toarray()
        train_prob = train_prob.toarray()

    # area under the curve
    train_auc = roc_auc_score(train_label, train_prob, average='macro')
    test_auc = roc_auc_score(test_label, test_prob, average='macro')

    result['train_auc']=train_auc
    result['test_auc']=test_auc
    print("#"*50)
    print("TRAIN AUC : ",train_auc)
    print("TEST AUC : ",test_auc)

#     ns_probs_train = [0 for _ in range(len(train_label))] # no skill probability for train
#     ns_probs_test = [0 for _ in range(len(test_label))] # no skill probability for test dataset


    ##########  TRAIN AUC  ###########

    # https://scikit-learn.org/stable/auto_examples/model_selection/plot_roc.html#plot-roc-curves-for-the-multilabel-problem

    n_classes = train_label.shape[1] # no.of classes
    print("no.of classes : ",n_classes)
    # Compute ROC Curve and ROC area for each class
    fpr_train, fpr_test = dict(), dict()
    tpr_train, tpr_test = dict(), dict()
    roc_auc_train, roc_auc_test = dict(), dict()

    for i in range(n_classes):
        fpr_train[i], tpr_train[i], _ = roc_curve(train_label[:,i], train_prob[:,i])
        fpr_test[i], tpr_test[i], _ = roc_curve(test_label[:,i], test_prob[:,i])
        roc_auc_train[i] = auc(fpr_train[i], tpr_train[i])
        roc_auc_test[i] = auc(fpr_test[i], tpr_test[i])

#     # No skill ROC Curve
#     ns_fpr, ns_tpr, _ = roc_curve(train_label[:,0], ns_probs_train)

    plt.figure(figsize=(10,7))
    for i in range(n_classes):
        plt.plot(fpr_train[i],tpr_train[i],label='TRAIN AUC(macro) class={} Score={}'.format(i,roc_auc_train[i]))
    plt.plot([0,1],[0,1], label='No skill',color='navy',lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title("TRAIN AUC scores per class of Logistic regression")
    plt.legend() # to show the label on plot
    plt.show() # force to show the plot

    plt.figure(figsize=(10,7))
    for i in range(n_classes):
        plt.plot(fpr_test[i],tpr_test[i],label='TEST AUC(macro) calss={} Score={}'.format(i,roc_auc_test[i]))
    plt.plot([0,1],[0,1], label='No skill',color='navy',lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title("TEST AUC scores per class of Logistic regression")
    plt.legend() # to show the label on plot
    plt.show() # force to show the plot

    result['model'] = model #
    return result

"""<h2 style="font-family:'Segoe UI';color:blue">Logistic Regression using OneVsRestClassifier</h2>

<h4 style="font-family:'Segoe UI';color:purple">class_weight='balanced', penalty='l2'</h4>
"""

def train_logistic_regression(train_data, train_label, penalty='l2', class_weight=None):
    """this function return fitted model on train data and given parameters."""
    # initialize LogisticRegression
    lr_model = LogisticRegression(
                            C=1.0,
                            solver='saga',
                            penalty= penalty,
                            class_weight=class_weight
                        )

    # initialize our OVR model for multi-label classification
    model = OneVsRestClassifier(
        lr_model
    )

    # fitting the best model
    print("[INFO] fitting the model...")
    model.fit(train_data, train_label)
    print("[INFO] model fitted.")

    return model # return fitted model

def lr_validation(train_data, train_label, test_data, test_label):
    """
    this function returns the result of all tuned Logistic Regression like:
    class_weights = [None,'balanced']
    penalties = ['l1','l2']
    """
    class_weights = [None,'balanced']
    penalties = ['l1','l2']

    results = []
    for cw in class_weights: # for each class weight
        for p in penalties: # for each penalty

            # train logistic regression model on train data
            model = train_logistic_regression(train_data,
                                              train_label,
                                              p, # penalty
                                              cw # class_weight
                                        )

            # get the classification report
            res = multilabel_classification_report(model,
                                                   train_data,
                                                   train_label,
                                                   test_data,
                                                   test_label
                                                  )
            results.append(res)

    return results

lr_results = lr_validation(tfidf_train, train_label, tfidf_test, test_label)

lr_results

final_lr_df = pd.DataFrame(lr_results)

final_lr_df

"""<h2 style="font-family:'Segoe UI';color:blue">RandomForest using OneVsRestClassifier</h2>"""

from sklearn.ensemble import RandomForestClassifier
from sklearn.multioutput import MultiOutputClassifier

# https://scikit-learn.org/stable/modules/multiclass.html#multioutputclassifier
# https://stackoverflow.com/questions/42819460/what-is-the-difference-between-onevsrestclassifier-and-multioutputclassifier-in
def complete_rf_training(train_data, train_label, test_data, test_label,n_estimators=100):
    """
    This function do hyper-parameter tuning for Random Forest for multi-label classification.
    We use sklearn's MultiOutputClassifier for Multi-label purpose.
    return :
            returns complete description of best Logistic Regression model fitted on given train data and their labels.
    """
    result = None

    rf = RandomForestClassifier(n_estimators=n_estimators)
    # initialize our OVR model for multi-label
    best_rf_model = OneVsRestClassifier(
        rf
    )

    # fitting the best model
    best_rf_model.fit(train_data, train_label)

    result = multilabel_classification_report(best_rf_model, train_data, train_label, test_data, test_label)

    return result

def rf_validation():
    """
    this function returns the result of all tuned Random Forest like:
    n_estimators = [10,20,50,100,150,250,300]
    """
    n_estimators = [10,20,50,100,150,250,300]

    results = []

    for e in n_estimators:
        res = complete_rf_training(
            tfidf_train,
            train_label.values,
            tfidf_test,
            test_label.values,
            n_estimators=e
        )
        results.append(res)

    return results

# Commented out IPython magic to ensure Python compatibility.
# %%time
# final_rf_result = rf_validation()

final_rf_df = pd.DataFrame(final_rf_result)

final_rf_df

"""<h2 style="font-family:'Segoe UI';color:blue">Using skmultilearn library</h2>

https://www.analyticsvidhya.com/blog/2017/08/introduction-to-multi-label-classification/

<h3 style="font-family:'Segoe UI';color:purple">1. Problem Transformation</h3>

<h3 style="font-family:'Segoe UI';color:#373">1.1 Binary Relevance</h3>
<img src="https://cdn.analyticsvidhya.com/wp-content/uploads/2017/08/25230613/Screen-Shot-2017-08-21-at-1.42.27-AM.png">
<img src="https://cdn.analyticsvidhya.com/wp-content/uploads/2017/08/25230630/Screen-Shot-2017-08-21-at-1.46.00-AM.png">
"""



from skmultilearn.problem_transform import BinaryRelevance
# BinaryRelevance create #classifiers corresponding to each label.

# we will use LogisticRegression to create classifier for each label
from sklearn.linear_model import LogisticRegression

# Classifier chain can be referred in analytics vidhya blog
from skmultilearn.problem_transform import ClassifierChain

"""<p style="color:#b00">Here as a base Model I used Logistic Regression. You can use any algorithm. Try and see the result</p>"""

binary_lr = LogisticRegression(
                            C=1.0,
                            solver='saga',
#                             penalty= 'penalty',
#                             class_weight=class_weight
                        )
# initialize our OVR model for multi-label
best_binary_lr_model = BinaryRelevance(
    binary_lr,
    require_dense=[False, True] # input should be Sparse and result should be dense
)

# fitting the best model
best_binary_lr_model.fit(tfidf_train, train_label)

y_pred = best_binary_lr_model.predict(tfidf_test)
y_pred.toarray()

def complete_binary_lr_training(train_data, train_label, test_data, test_label,penalty='l2',class_weight=None):
    """
    This function do hyper-parameter tuning for Logistic Regression.
    return :
            returns complete description of best Logistic Regression model fitted on given train data and their labels.
    """
    result = None # to be returned

    binary_lr = LogisticRegression(
                            C=1.0,
                            solver='saga',
                            penalty= penalty,
                            class_weight=class_weight
                        )
    # initialize our OVR model for multi-label
    best_binary_lr_model = BinaryRelevance(
        binary_lr,
        require_dense=[False, True] # input should be Sparse and result should be dense
    )

    # fitting the best model
    best_binary_lr_model.fit(train_data, train_label)

    result = multilabel_classification_report(best_binary_lr_model,
                                              train_data,
                                              train_label,
                                              test_data,
                                              test_label,
                                              True # we are using skmultilearn
                                             )

    return result

def binary_lr_validation(train_data, train_label, test_data, test_label):
    """
    this function returns the result of all tuned Logistic Regression like:
    class_weights = [None,'balanced']
    penalties = ['l1','l2']
    """
    class_weights = [None,'balanced']
    penalties = ['l1','l2']

    results = []
    for cw in class_weights:
        for p in penalties:
            res = complete_binary_lr_training(
                train_data,
                train_label,
                test_data,
                test_label,
                penalty=p,
                class_weight=cw
            )
            results.append(res)

    return results

# Commented out IPython magic to ensure Python compatibility.
# %%time
# final_binary_lr_result = binary_lr_validation(tfidf_train, train_label, tfidf_test, test_label)

final_binary_lr_df = pd.DataFrame(final_binary_lr_result)

final_binary_lr_df

"""<h3 style="font-family:'Segoe UI';color:purple">1.2 Classifier Chains</h3>
<img src="https://cdn.analyticsvidhya.com/wp-content/uploads/2017/08/25230735/Screen-Shot-2017-08-25-at-12.41.13-AM.png">
<img src="https://cdn.analyticsvidhya.com/wp-content/uploads/2017/08/25233225/Screen-Shot-2017-08-25-at-11.31.58-PM.png">

<p style="color:#b00">Here as a base Model I used Logistic Regression. You can use any algorithm. Try and see the result</p>
"""

def complete_cc_lr_training(train_data, train_label, test_data, test_label,penalty='l2',class_weight=None):
    """
    This function do hyper-parameter tuning for Logistic Regression.
    return :
            returns complete description of best Logistic Regression model fitted on given train data and their labels.
    """
    result = None # to be returned

    cc_lr = LogisticRegression(
                            C=1.0,
                            solver='saga',
                            penalty= penalty,
                            class_weight=class_weight
                        )
    # initialize our OVR model for multi-label
    best_cc_lr_model = ClassifierChain(
        cc_lr,
        require_dense=[False, True] # input should be Sparse and result should be dense
    )

    # fitting the best model
    best_cc_lr_model.fit(train_data, train_label)

    result = multilabel_classification_report(best_cc_lr_model, train_data, train_label, test_data, test_label, True)

    return result

def cc_lr_validation():
    """
    this function returns the result of all tuned Logistic Regression like:
    class_weights = [None,'balanced']
    penalties = ['l1','l2']
    """
    class_weights = [None,'balanced']
    penalties = ['l1','l2']

    results = []
    for cw in class_weights:
        for p in penalties:
            res = complete_cc_lr_training(
                tfidf_train,
                train_label.values,
                tfidf_test,
                test_label.values,
                penalty=p,
                class_weight=cw
            )
            results.append(res)

    return results

# Commented out IPython magic to ensure Python compatibility.
# %%time
# final_cc_lr_result = cc_lr_validation()

final_cc_lr_df = pd.DataFrame(final_cc_lr_result)

final_cc_lr_df



"""<h3 style="font-family:'Segoe UI';color:purple">ClassifierChain using BernoulliNB</h3>

<p style="color:#b00">Here as a base Model I used BernoulliNB. You can use any algorithm. Try and see the result</p>
"""

from sklearn.naive_bayes import BernoulliNB

def complete_cc_bernoulli_training(train_data, train_label, test_data, test_label, alpha=1):
    """
    This function do hyper-parameter tuning for Logistic Regression.
    return :
            returns complete description of best Logistic Regression model fitted on given train data and their labels.
    """
    result = None # to be returned

    cc_bernoulli = BernoulliNB(alpha=alpha)
    # initialize our OVR model for multi-label
    best_cc_bernoulli_model = BinaryRelevance(
        cc_bernoulli,
        require_dense=[False, True] # input should be Sparse and result should be dense
    )

    # fitting the best model
    best_cc_bernoulli_model.fit(train_data, train_label)

    result = multilabel_classification_report(best_cc_bernoulli_model,
                                              train_data,
                                              train_label,
                                              test_data,
                                              test_label,
                                              skmultilearn=True
                                             )
    return result

def cc_bernoulli_validation():
    """
    this function returns the result of Classifier chain using BernoulliNB:
    """
    alphas = [0.001,0.01,0.1,1,10,100]
    results = [] # results to store the result of different Bernoulli Naive Bayes
    for alpha in alphas:
        res = complete_cc_bernoulli_training(
                    tfidf_train,
                    train_label,
                    tfidf_test,
                    test_label,
                    alpha # value of
                )
        results.append(res)
    return results

# Commented out IPython magic to ensure Python compatibility.
# %%time
# final_cc_bernoulli_result = cc_bernoulli_validation()

# final_cc_bernoulli_result

final_cc_bernoulli_result

final_cc_bernoulli_df = pd.DataFrame(final_cc_bernoulli_result,
                                     #index=[0] # if there is only one row of value
                                    )

final_cc_bernoulli_df

"""<h3 style="font-family:'Segoe UI';color:purple">1.3 Label Powerset</h3>
<img src="https://cdn.analyticsvidhya.com/wp-content/uploads/2017/08/25230858/Screen-Shot-2017-08-25-at-12.46.30-AM.png">
<img src="https://cdn.analyticsvidhya.com/wp-content/uploads/2017/08/25230915/Screen-Shot-2017-08-25-at-12.46.37-AM.png">
"""

# using Label Powerset
from skmultilearn.problem_transform import LabelPowerset
from sklearn.linear_model import LogisticRegression

lp = LabelPowerset(LogisticRegression(), require_dense=[False, True])

lp.fit(tfidf_train, train_label)

lp.predict(tfidf_test).toarray()

accuracy_score(test_label, lp.predict(tfidf_test).toarray())

"""<p style="color:#b00">Here as a base Model I used Logistic Regression. You can use any algorithm. Try and see the result</p>"""

def complete_label_lr_training(train_data, train_label, test_data, test_label,penalty='l2',class_weight=None):
    """
    This function do hyper-parameter tuning for Logistic Regression.
    return :
            returns complete description of best Logistic Regression model fitted on given train data and their labels.
    """
    result = None # to be returned

    label_lr = LogisticRegression(
                            C=1.0,
                            solver='saga',
                            penalty= penalty,
                            class_weight=class_weight
                        )
    # initialize our LabelPowerset model for multi-label
    best_label_lr_model = LabelPowerset(
        label_lr,
        require_dense=[False, True] # input should be Sparse and result should be dense
    )

    # fitting the best model
    best_label_lr_model.fit(train_data, train_label)

    result = multilabel_classification_report(best_label_lr_model, train_data, train_label, test_data, test_label, skmultilearn=True)

    return result

def label_lr_validation():
    """
    this function returns the result of all tuned Logistic Regression using LabelPowerset like:
    class_weights = [None,'balanced']
    penalties = ['l1','l2']
    """
    class_weights = [None,'balanced']
    penalties = ['l1','l2']

    results = []
    for cw in class_weights:
        for p in penalties:
            res = complete_label_lr_training(
                tfidf_train,
                train_label.values,
                tfidf_test,
                test_label.values,
                penalty=p,
                class_weight=cw
            )
            results.append(res)

    return results

# Commented out IPython magic to ensure Python compatibility.
# %%time
# final_label_lr_result = label_lr_validation()

# final_label_lr_result

final_label_lr_df = pd.DataFrame(final_label_lr_result)

final_label_lr_df



"""<h2 style="font-family:'Segoe UI';color:blue">2 Adapted Algorithm </h2>
<h3 style="font-family:'Segoe UI';color:purple">2.1 MlkNN </h3>
"""

from skmultilearn.adapt import MLkNN # KNN is not good for low-latency system

kmodel = MLkNN(k=10)

tfidf_train.toarray()

train_label.values

kmodel.fit(tfidf_train.toarray(), train_label.values)

accuracy_score(test_label.values,(kmodel.predict(tfidf_test.toarray())).toarray())

def complete_mlknn_training(train_data, train_label, test_data, test_label,n_neighbors=10):
    """
    This function do hyper-parameter tuning for Logistic Regression.
    return :
            returns complete description of best Logistic Regression model fitted on given train data and their labels.
    """
    result = {} # to be returned


    # initialize our OVR model for multi-label
    best_mlknn_model = MLkNN(k=n_neighbors)

    # fitting the best model
    best_mlknn_model.fit(train_data, train_label)

    result = multilabel_classification_report(best_mlknn_model,
                                              train_data,
                                              train_label,
                                              test_data,
                                              test_label,
                                              skmultilearn=True
                                             )
    return result

def mlknn_validation():
    """
    this function returns the result of Classifier MLkNN:
    """
    results = []
    neighbors = [10,15,20,30,40,50]
    for n in neighbors:
        res = complete_mlknn_training(
                    tfidf_train.toarray(),
                    train_label,
                    tfidf_test.toarray(),
                    test_label,
                    n # no.of neighbors
                )
        results.append(res)
    return results

# Commented out IPython magic to ensure Python compatibility.
# %%time
# final_mlknn_result = mlknn_validation()

# final_mlknn_result

final_mlknn_df = pd.DataFrame(final_mlknn_result)

final_mlknn_df





"""<h1 style="font-family:'Segoe UI';color:blue">Deep Learning For Multi-label Classification</h1>

https://machinelearningmastery.com/multi-label-classification-with-deep-learning/
"""

!pip install lime

# Hamming loss/score metrics does by XOR between the actual and predicted labels and then average across the dataset.
# https://www.linkedin.com/pulse/hamming-score-multi-label-classification-chandra-sharat/

def hamming_score(y_true, y_pred):
    """
    this function returns hamming_score for multilabel classification
    """
    acc_list = []

    for i in range(y_true.shape[0]): # for each value in y_true
        set_true = set(np.where(y_true[i])[0])
        set_pred = set(np.where(y_pred[i])[0])

        temp_a = None

        if len(set_true)==0 and len(set_pred) ==0:
            temp_a =1
        else:
            temp_a = len(set_true.intersection(set_pred))/float(len(set_true.union(set_pred)))
        acc_list.append(temp_a)
    return np.mean(acc_list)


def deep_modeling_report(model, train_data, train_label, test_data, test_label, title="Deep Learning Model"):
    """
    This function show the report of Deep Learning Models.
    """
    result = {} # dictionary to store all the result of particular model
    print("################ Modeling Report ###################")
    ################ TRAIN ERROR and ACCURACY ###################
    # prediction of test dataset using deep learning models
    test_predicted = (model.predict(test_data)>0.5).astype("int32")
    train_predicted = (model.predict(train_data)>0.5).astype("int32")

    train_accuracy = accuracy_score(train_label, train_predicted)
    test_accuracy = accuracy_score(test_label, test_predicted)

    result['train_accuracy']=train_accuracy
    result['test_accuracy']=test_accuracy

    train_f1_score = f1_score(train_label, train_predicted, average='macro')
    test_f1_score = f1_score(test_label, test_predicted, average='macro')

    result['train_f1_score']=train_f1_score
    result['test_f1_score']=test_f1_score

    train_recall_score = recall_score(train_label, train_predicted, average='macro')
    test_recall_score = recall_score(test_label, test_predicted, average='macro')

    result['train_recall']=train_recall_score
    result['test_recall']=test_recall_score

    train_hamming_loss = hamming_loss(train_label, train_predicted)
    test_hamming_loss = hamming_loss(test_label, test_predicted)
    result['train_hamming_loss'] = train_hamming_loss
    result['test_hamming_loss'] = test_hamming_loss

    train_hamming_score = hamming_score(train_label, train_predicted)
    test_hamming_score = hamming_score(test_label, test_predicted)
    result['train_hamming_score'] = train_hamming_score
    result['test_hamming_score'] = test_hamming_score

    print("TRAIN Accuracy(exact match) : ",train_accuracy)
    print("TEST Accuracy(exact match) : ",test_accuracy)
    print("="*50)
    print("TRAIN f1-score(macro) : ",train_f1_score)
    print("TEST f1-score(macro) : ",test_f1_score)
    print("="*50)
    print("TRAIN hamming loss : ",train_hamming_loss)
    print("TEST hamming loss : ",test_hamming_loss)
    print("="*50)
    print("TRAIN hamming score : ", train_hamming_score)
    print("TEST hamming score : ", test_hamming_score)

    print("#"*50)
    print("Confusion MATRIX")
    print("TRAIN : ",multilabel_confusion_matrix(train_label, train_predicted))
    print("TEST : ", multilabel_confusion_matrix(test_label, test_predicted))
    ###########################################################################

    ############### CLASSIFICATIO RESULT of both Train, and Test dataset ######
    train_cf_report = classification_report(train_label, train_predicted)
    test_cf_report = classification_report(test_label, test_predicted)

    print("Classification report of TRAIN : ")
    print(train_cf_report)
    print("Classification report of TEST : ")
    print(test_cf_report)
    #############################################################################################

    ################### ROC-AUC Score ###########################################################
    # getting train_score, and test_score
    test_prob = model.predict(test_data)
    train_prob = model.predict(train_data)

    # area under the curve
    train_auc = roc_auc_score(train_label, train_prob, average='macro')
    test_auc = roc_auc_score(test_label, test_prob, average='macro')

    result['train_auc']=train_auc
    result['test_auc']=test_auc
    print("#"*50)
    print("TRAIN AUC : ",train_auc)
    print("TEST AUC : ",test_auc)

    ##########  TRAIN AUC  ###########

    # https://scikit-learn.org/stable/auto_examples/model_selection/plot_roc.html#plot-roc-curves-for-the-multilabel-problem

    n_classes = train_label.shape[1] # no.of classes

    # Compute ROC Curve and ROC area for each class
    fpr_train, fpr_test = dict(), dict()
    tpr_train, tpr_test = dict(), dict()
    roc_auc_train, roc_auc_test = dict(), dict()

    for i in range(n_classes):
        fpr_train[i], tpr_train[i], _ = roc_curve(train_label[:,i], train_prob[:,i])
        fpr_test[i], tpr_test[i], _ = roc_curve(test_label[:,i], test_prob[:,i])
        roc_auc_train[i] = auc(fpr_train[i], tpr_train[i])
        roc_auc_test[i] = auc(fpr_test[i], tpr_test[i])

    plt.figure(figsize=(10,7))
    for i in range(n_classes):
        plt.plot(fpr_train[i],tpr_train[i],label='TRAIN AUC(macro) class={} Score={}'.format(i,roc_auc_train[i]))
    plt.plot([0,1],[0,1], label='No skill',color='navy',lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title("TRAIN AUC scores per class of {}".format(title))
    plt.legend() # to show the label on plot
    plt.show() # force to show the plot

    plt.figure(figsize=(10,7))
    for i in range(n_classes):
        plt.plot(fpr_test[i],tpr_test[i],label='TEST AUC(macro) calss={} Score={}'.format(i,roc_auc_test[i]))
    plt.plot([0,1],[0,1], label='No skill',color='navy',lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title("TEST AUC scores per class of {}".format(title))
    plt.legend() # to show the label on plot
    plt.show() # force to show the plot

    result['model'] = title
    return result


from lime.lime_text import LimeTextExplainer
def deep_multi_label_explainer(model, input_text, labels, num_features=None, num_samples=None, bow=True):
    # labels - all outputs
    for label in labels:
        class_names = ['Non-{}'.format(label), label]

        def make_classifier_pipeline(label=label):
            label_index = labels.index(label)
            # pick the corresponding output node
            def lime_explainer_pipeline(texts):
                input_text = pd.Series(texts)# typecasting to series from raw text
                input_sequence = tokenizer.texts_to_sequences(input_text) #changing text into sequences
                padded_input_sequence = pad_sequences(input_sequence, maxlen=maxlen, padding='post') # padding the sequence
                predicted_prob = model.predict(padded_input_sequence)
                prob_true = predicted_prob[:, label_index]
                result = np.transpose(np.vstack(([1-prob_true, prob_true])))
                result  = result.reshape(-1, 2)
                #print(predicted_prob)
                #print(result)
                return result

            return lime_explainer_pipeline

       # make a classifier function for the required label
        classifier_fn = make_classifier_pipeline(label=label)

        # ignore this code
#         if num_samples is None:
#             num_samples = int(len(input_text.split(' ')) * 2.5)
#             num_samples = 1000 if num_samples > 1000 else num_samples
#         if num_features is None:
#             num_features = int(len(input_text.split(' ')) // 20)
#             num_features = 10 if num_features > 10 else num_features

        explainer = LimeTextExplainer(
                                        class_names=class_names, # class labels(negative, positive)
                                        kernel_width=25,
                                        bow=bow
        )
        exp = explainer.explain_instance(
            input_text, # explain instance on this particular query text
            classifier_fn, # pipeline
#             num_features=num_features,
#             num_samples=num_samples
         )

        exp.show_in_notebook(text=True, predict_proba=True)

data_path='../dataset/multilabel_classification'
data_path

save_model_path = '../model_save/multilabel_data'

# loading train,val, and test dataset
train = pd.read_csv( 'train.csv')
val = pd.read_csv('dev.csv')
test = pd.read_csv('test.csv')

# shape of the datasets
train.shape, val.shape, test.shape

train.columns = ['Description','Commenting','Ogling','Groping']
val.columns = ['Description','Commenting','Ogling','Groping']
test.columns = ['Description','Commenting','Ogling','Groping']

train.head()

train_label = train[['Commenting','Ogling','Groping']]
val_label = val[['Commenting','Ogling','Groping']]
test_label = test[['Commenting','Ogling','Groping']]

train_label.head()



"""**using pre-trained embedding from Word2Vec embeddings**"""

import tensorflow as tf

pip install tensorflow-addons

import tensorflow_addons as tfa

# tokenize the data that can be used by embeddings
from tensorflow.keras.preprocessing.text import Tokenizer

tokenizer = Tokenizer(num_words=10000) # used in the research paper
tokenizer.fit_on_texts(train.Description.apply(lambda x: np.str_(x)))

tokenizer.index_word[7000] # word corresponding to particular index

tokenizer.index_word[1] # index_word is dictionary of containing index as key and word as value

# changing tokens into sequences to train word embeddings
X_train = tokenizer.texts_to_sequences(train.Description)
X_val = tokenizer.texts_to_sequences(val.Description)
X_test = tokenizer.texts_to_sequences(test.Description)

len(tokenizer.word_index)

# vocabulary size
vocab_size = len(tokenizer.word_index)+1 # adding 1 because index 0 is reserved
vocab_size

print(train.Description.iloc[5])

# PROBLEM is: each sentence has variable no.of words.
# So, do padding.
from tensorflow.keras.preprocessing.sequence import pad_sequences

maxlen = 100

# It doesn't matter that you preprend or append the padding
X_train = pad_sequences(X_train, padding='post', maxlen=maxlen)
X_val = pad_sequences(X_val, padding='post', maxlen=maxlen)
X_test = pad_sequences(X_test, padding='post', maxlen=maxlen)

X_train[5]

# https://realpython.com/python-keras-text-classification/
def create_embedding_matrix(filepath, word_index, embed_dim):
    """
    This function creates and return the embedding matrix.
    """
    vocab_size = len(word_index)+1 # Adding 1 because of reserved 0 index
    # creating zeros matrix with shape (#vocab_size X embedding_dimension)
    embedding_matrix = np.zeros((vocab_size, embed_dim))

    # access the file given in filepath
    with open(filepath,'r', encoding='utf-8') as f:
        # for each line in the file
        for line in tqdm(f): # for each row in the file
            # get word and vector
            word, *vector = line.split() # *variable collects all args value, ** -> kwargs

            # if word is present in word_index
            if word in word_index:
                # try is used to by-pass error(if happen during converting vector values to float)
                try:
                    idx = word_index[word]
                    embedding_matrix[idx]=np.array(vector, dtype=np.float32)[:embed_dim]
                except:
                    pass
    return embedding_matrix

# embedding dimension, file path, and creating embedding matrix
embedding_dim = 300
# filepath = '../dataset/glove.6B.300d.txt' # uncomment to use 50d 60billion text corpus
filepath = '/content/drive/My Drive/glove.840B.300d.txt'
embedding_matrix = create_embedding_matrix(filepath, tokenizer.word_index, embedding_dim)
np.save('embedding_matrix_300d', embedding_matrix)

# shape of embedding matrix
embedding_matrix.shape

nonzero_elements = np.count_nonzero(np.count_nonzero(embedding_matrix, axis=1))
nonzero_elements / vocab_size

"""<p style="font-family:'Segoe UI';color:green"><b>It means 85% of our vocabulary is covered by pretrained model</p>

<h2 style="font-family:'Segoe UI';color:blue">CNN
"""

checkpoint_path_cnn_embedding = "best_cnn_embedding_recall.hdf5"
checkpoint_dir_cnn_embedding = os.path.dirname(checkpoint_path_cnn_embedding)



np.random.seed(42)

# n_inputs : number of neurons in the input layer of the model
# n_outputs : number of neurons in the output layer of the model
n_inputs, n_outputs = X_train.shape[1], train_label.shape[1]
n_inputs, n_outputs
# because of using Embeddings by ourself and training, n_inputs wouldn't be 50
# instead, it would be vocabulary size(vocab_size)

# https://stackoverflow.com/questions/65464463/importerror-cannot-import-name-keras-tensor-from-tensorflow-python-keras-eng
import tensorflow_addons as tfa

# callbacks to save Models
save_model_cnn_embedding = tf.keras.callbacks.ModelCheckpoint(
    filepath=checkpoint_path_cnn_embedding,
    monitor='val_recall',
    save_best_only=True,
    verbose=1,
    mode='max' # get maximum val_recall
)

# https://keras.io/layers/embeddings/
# Now, we will learn a new embedding space using Embedding layer
# which maps above encoded word representation into dense vector.
# input_dim = the size of the vocabulary
# output_dim = the size of the dense vector
# input_length = the length of the sequence

# clear all previous sessions
tf.keras.backend.clear_session()
embedding_dim = 300
def create_cnn_embedding_model():
    model = tf.keras.models.Sequential()
    model.add(tf.keras.layers.Embedding(input_dim=vocab_size,
                               output_dim=embedding_dim, # embedding_dim = 300
                               weights=[embedding_matrix],
                               input_length=maxlen,
                               trainable=True # We are using already trained weights, make it True to train this embedding
                              ))
    model.add(tf.keras.layers.Conv1D(100, 3, activation='relu',
                           kernel_initializer='he_normal'))
    model.add(tf.keras.layers.MaxPool1D(pool_size=2))
    model.add(tf.keras.layers.Dropout(0.5))
    model.add(tf.keras.layers.Conv1D(100, 4, activation='relu',
                           kernel_initializer='he_normal'))
    model.add(tf.keras.layers.MaxPool1D(pool_size=2))
    model.add(tf.keras.layers.Dropout(0.5))
    model.add(tf.keras.layers.Conv1D(100, 5, activation='relu',
                           kernel_initializer='he_normal'))
#     model.add(tf.keras.layers.Dropout(0.5))
    model.add(tf.keras.layers.GlobalMaxPool1D())
#     model.add(tf.keras.layers.Dropout(0.5))
    model.add(tf.keras.layers.Dense(10, activation='relu',kernel_initializer='he_normal'))
    model.add(tf.keras.layers.Dense(n_outputs, activation='sigmoid'))
    return model
cnn_embedding_model = create_cnn_embedding_model()

cnn_embedding_model.compile(optimizer='adam',
              loss='binary_crossentropy',
              metrics=['accuracy',
                       tf.keras.metrics.Precision(),
                       tf.keras.metrics.Recall(),
                       # hamming loss from tensorflow-addons
                       tfa.metrics.HammingLoss(mode='multilabel',threshold=0.5)
                      ])
cnn_embedding_model.summary()

cnn_embedding_history=cnn_embedding_model.fit(X_train, train_label.values,
              epochs=20,
              validation_data=(X_val, val_label.values),
              batch_size=128,
              verbose=2,
              callbacks=[save_model_cnn_embedding]
         )

# evaluate model on test dataset
cnn_embedding_model.evaluate(X_test, test_label.values)

# actually we used Hamming loss metrics from tensorflow-addons
# So, we will have to say the dependencies while loading the model that
# what is HammingLoss <-- Use exactly same case, case sensitive
dependencies = {
    'HammingLoss':tfa.metrics.HammingLoss(mode='multilabel',threshold=0.5)
}

best_cnn_embedding_model=tf.keras.models.load_model(checkpoint_path_cnn_embedding,custom_objects=dependencies)

# best_cnn_embedding_model.evaluate(X_test, test_label)

deep_modeling_report(best_cnn_embedding_model, X_train, train_label.values, X_test, test_label.values, 'best CNN1 TEST')

deep_modeling_report(best_cnn_embedding_model, X_train, train_label.values, X_val, val_label.values, 'best CNN1 Validation')



"""<h3 style="font-family:'Segoe UI';color:purple">CNN 2"""

checkpoint_path_cnn2_embedding = "best_cnn2_embedding_recall.hdf5"
checkpoint_dir_cnn2_embedding = os.path.dirname(checkpoint_path_cnn2_embedding)

# callbacks to save Models
save_model_cnn2_embedding = tf.keras.callbacks.ModelCheckpoint(
    filepath=checkpoint_path_cnn2_embedding,
    monitor='val_recall',
    save_best_only=True,
    verbose=1,
    mode='max' # get maximum val_recall
)

np.random.seed(42)

# n_inputs : number of neurons in the input layer of the model
# n_outputs : number of neurons in the output layer of the model
n_inputs, n_outputs = X_train.shape[1], train_label.shape[1]
n_inputs, n_outputs
# because of using Embeddings by ourself and training, n_inputs wouldn't be 50
# instead, it would be vocabulary size(vocab_size)

# https://stackoverflow.com/questions/65464463/importerror-cannot-import-name-keras-tensor-from-tensorflow-python-keras-eng
import tensorflow_addons as tfa

# https://keras.io/layers/embeddings/
# Now, we will learn a new embedding space using Embedding layer
# which maps above encoded word representation into dense vector.
# input_dim = the size of the vocabulary
# output_dim = the size of the dense vector
# input_length = the length of the sequence

# clear all previous sessions
tf.keras.backend.clear_session()
embedding_dim = 300
def create_cnn2_embedding_model():
    model = tf.keras.models.Sequential()
    model.add(tf.keras.layers.Embedding(input_dim=vocab_size,
                               output_dim=embedding_dim, # embedding_dim = 50
                               weights=[embedding_matrix],
                               input_length=maxlen,
                               trainable=False # We are using already trained weights, make it True to train this embedding
                              ))
    model.add(tf.keras.layers.Conv1D(64,
                                    5,
                                    activation='relu',
                                    kernel_initializer='he_uniform'
                                   ))
    model.add(tf.keras.layers.Dropout(0.5))
    model.add(tf.keras.layers.Conv1D(32,
                                     4,
                                     activation='relu',
                                     kernel_initializer='he_uniform'
                                    ))
#     model.add(tf.keras.layers.Flatten())
    model.add(tf.keras.layers.GlobalMaxPooling1D())
    model.add(tf.keras.layers.Dense(n_outputs, activation='sigmoid'))
    return model
cnn2_embedding_model = create_cnn2_embedding_model()

cnn2_embedding_model.compile(optimizer='adam',
              loss='binary_crossentropy',
              metrics=['accuracy',
                       tf.keras.metrics.Precision(),
                       tf.keras.metrics.Recall(),
                       tfa.metrics.HammingLoss(mode='multilabel',threshold=0.5)
                      ])
cnn2_embedding_model.summary()

# I did not use MaxPooling Because It's a bad idea :
# https://towardsdatascience.com/what-is-wrong-with-convolutional-neural-networks-75c2ba8fbd6f
# I did not use Dropout Because It's difficult to debug the NN, If you use Dropout:
# By Andrej Karipathy

X_train[1]

cnn2_embedding_history=cnn2_embedding_model.fit(X_train, train_label.values,
              epochs=20,
              validation_data=(X_val, val_label.values),
              batch_size=16,
              verbose=2,
              callbacks=[save_model_cnn2_embedding]
         )

cnn2_embedding_model.evaluate(X_test, test_label.values)

# actually we used Hamming loss metrics from tensorflow-addons
# So, we will have to say the dependencies while loading the model that
# what is HammingLoss <-- Use exactly same case, case sensitive
dependencies = {
    'HammingLoss':tfa.metrics.HammingLoss(mode='multilabel',threshold=0.5)
}

best_cnn2_embedding_model=tf.keras.models.load_model(checkpoint_path_cnn2_embedding, custom_objects=dependencies)

best_cnn2_embedding_model.evaluate(X_test, test_label.values)

deep_modeling_report(best_cnn2_embedding_model, X_train, train_label.values, X_val, val_label.values, 'best CNN2 Validation')

deep_modeling_report(best_cnn2_embedding_model, X_train, train_label.values, X_test, test_label.values, 'best CNN2 TEST')

"""<h4 style="font-family:'Segoe UI';color:purple">Interpret using LIME (Local Interpretability Model-agnostic Explanation</h4>"""

test_label.head()

list(test_label.columns)

labels=list(test_label.columns)
query = "When I was passing through local market a person commented on me and started following. after few minutes he came nearer to me and started ogling on me and he touched me also."

deep_multi_label_explainer(best_cnn2_embedding_model,query,labels)

query = "A person was staring on me."
deep_multi_label_explainer(best_cnn2_embedding_model, query, labels)



"""<h3 style="font-family:'Segoe UI';color:purple">CNN 3</h3>"""

checkpoint_path_cnn3_embedding = "../model_save/multi_data/best_cnn3_embedding_recall.hdf5"
checkpoint_dir_cnn3_embedding = os.path.dirname(checkpoint_path_cnn3_embedding)

np.random.seed(42)

# n_inputs : number of neurons in the input layer of the model
# n_outputs : number of neurons in the output layer of the model
n_inputs, n_outputs = X_train.shape[1], train_label.shape[1]
n_inputs, n_outputs
# because of using Embeddings by ourself and training, n_inputs wouldn't be 50
# instead, it would be vocabulary size(vocab_size)

# https://stackoverflow.com/questions/65464463/importerror-cannot-import-name-keras-tensor-from-tensorflow-python-keras-eng
import tensorflow_addons as tfa

# callbacks to save Models
save_model_cnn3_embedding = tf.keras.callbacks.ModelCheckpoint(
    filepath=checkpoint_path_cnn3_embedding,
    monitor='val_recall',
    save_best_only=True,
    verbose=1,
    mode='max' # get maximum val_recall
)

# https://keras.io/layers/embeddings/
# Now, we will learn a new embedding space using Embedding layer
# which maps above encoded word representation into dense vector.
# input_dim = the size of the vocabulary
# output_dim = the size of the dense vector
# input_length = the length of the sequence

# clear all previous sessions
tf.keras.backend.clear_session()
embedding_dim = 300
def create_cnn3_embedding_model():
    model = tf.keras.models.Sequential()
    model.add(tf.keras.layers.Embedding(input_dim=vocab_size,
                               output_dim=embedding_dim, # embedding_dim = 50
                               weights=[embedding_matrix],
                               input_length=maxlen,
                               trainable=False # We are using already trained weights, make it True to train this embedding
                              ))
    model.add(tf.keras.layers.Conv1D(64,
                                    5,
                                    activation='relu',
                                    kernel_initializer='he_uniform'
                                   ))
    model.add(tf.keras.layers.MaxPool1D(5, strides=1, padding='valid'))
    model.add(tf.keras.layers.Dropout(0.5))
    model.add(tf.keras.layers.Conv1D(64,
                                     4,
                                     activation='relu',
                                     kernel_initializer='he_uniform'
                                    ))
    model.add(tf.keras.layers.GlobalMaxPooling1D())
    model.add(tf.keras.layers.Dense(n_outputs, activation='sigmoid'))
    return model
cnn3_embedding_model = create_cnn3_embedding_model()

cnn3_embedding_model.compile(optimizer='adam',
              loss='binary_crossentropy',
              metrics=['accuracy',
                       tf.keras.metrics.Precision(),
                       tf.keras.metrics.Recall(),
                       tfa.metrics.HammingLoss(mode='multilabel',threshold=0.5)
                      ])
cnn3_embedding_model.summary()

cnn3_embedding_history=cnn3_embedding_model.fit(X_train, train_label.values,
              epochs=20,
              validation_data=(X_val, val_label.values),
              batch_size=16,
              verbose=2,
              callbacks=[save_model_cnn3_embedding]
         )

cnn3_embedding_model.evaluate(X_test, test_label.values)

best_cnn3_embedding_model=tf.keras.models.load_model(checkpoint_path_cnn3_embedding, custom_objects=dependencies)

best_cnn3_embedding_model.evaluate(X_test, test_label)

deep_modeling_report(best_cnn3_embedding_model, X_train, train_label.values, X_val, val_label.values, 'best CNN3 Validation')
deep_modeling_report(best_cnn3_embedding_model, X_train, train_label.values, X_test, test_label.values, 'best CNN3 TEST')

labels=list(test_label.columns)
query = "When I was passing through local market a person commented on me and started following. after few minutes he came nearer to me and started ogling on me and he touched me also."

deep_multi_label_explainer(best_cnn3_embedding_model,query,labels)

query = "A person was staring on me."
deep_multi_label_explainer(best_cnn3_embedding_model, query, labels)

"""<h2 style="font-family:'Segoe UI';color:purple">CNN 4 </h2>"""

checkpoint_path_cnn4_embedding = "../model_save/multi_data/best_cnn4_embedding_recall.hdf5"
checkpoint_dir_cnn4_embedding = os.path.dirname(checkpoint_path_cnn4_embedding)

np.random.seed(42)

# n_inputs : number of neurons in the input layer of the model
# n_outputs : number of neurons in the output layer of the model
n_inputs, n_outputs = X_train.shape[1], train_label.shape[1]
n_inputs, n_outputs
# because of using Embeddings by ourself and training, n_inputs wouldn't be 50
# instead, it would be vocabulary size(vocab_size)

# https://stackoverflow.com/questions/65464463/importerror-cannot-import-name-keras-tensor-from-tensorflow-python-keras-eng
import tensorflow_addons as tfa

# callbacks to save Models
save_model_cnn4_embedding = tf.keras.callbacks.ModelCheckpoint(
    filepath=checkpoint_path_cnn4_embedding,
    monitor='val_recall',
    save_best_only=True,
    verbose=1,
    mode='max' # get maximum val_recall
)

# https://keras.io/layers/embeddings/
# Now, we will learn a new embedding space using Embedding layer
# which maps above encoded word representation into dense vector.
# input_dim = the size of the vocabulary
# output_dim = the size of the dense vector
# input_length = the length of the sequence

# clear all previous sessions
tf.keras.backend.clear_session()
embedding_dim = 300
def create_cnn4_embedding_model():
    model = tf.keras.models.Sequential()
    model.add(tf.keras.layers.Embedding(input_dim=vocab_size,
                               output_dim=embedding_dim, # embedding_dim = 50
                               weights=[embedding_matrix],
                               input_length=maxlen,
                               trainable=True # We are using already trained weights, make it True to train this embedding
                              ))
    model.add(tf.keras.layers.Conv1D(32, 4, activation='relu',kernel_initializer='he_normal'))
    model.add(tf.keras.layers.MaxPool1D(pool_size=4, strides=2, padding='valid'))
    model.add(tf.keras.layers.Dropout(0.6))
    model.add(tf.keras.layers.Conv1D(16, 3, activation='relu',kernel_initializer='he_normal'))
    model.add(tf.keras.layers.GlobalMaxPool1D())
    model.add(tf.keras.layers.Dropout(0.5))
    model.add(tf.keras.layers.Dense(10, activation='relu'))
    model.add(tf.keras.layers.Dense(n_outputs, activation='sigmoid'))
    return model

cnn4_embedding_model = create_cnn4_embedding_model()

cnn4_embedding_model.compile(optimizer='adam',
              loss='binary_crossentropy',
              metrics=['accuracy',
                       tf.keras.metrics.Precision(),
                       tf.keras.metrics.Recall(),
                       tfa.metrics.HammingLoss(mode='multilabel',threshold=0.5)
                      ])
cnn4_embedding_model.summary()

cnn4_embedding_history=cnn4_embedding_model.fit(X_train, train_label.values,
              epochs=20,
              validation_data=(X_val, val_label.values),
              batch_size=16,
              verbose=2,
              callbacks=[save_model_cnn4_embedding]
         )

cnn4_embedding_model.evaluate(X_test, test_label.values)

best_cnn4_embedding_model=tf.keras.models.load_model(checkpoint_path_cnn4_embedding, custom_objects=dependencies)

best_cnn4_embedding_model.evaluate(X_test, test_label)

deep_modeling_report(best_cnn4_embedding_model, X_train, train_label.values, X_val, val_label.values, 'best cnn4 Validation')
deep_modeling_report(best_cnn4_embedding_model, X_train, train_label.values, X_test, test_label.values, 'best cnn4 TEST')

labels=list(test_label.columns)
query = "When I was passing through local market a person commented on me and started following. after few minutes he came nearer to me and started staring on me and he touched me also."

deep_multi_label_explainer(best_cnn4_embedding_model,query,labels)

query = "A person was staring on me."
deep_multi_label_explainer(best_cnn4_embedding_model, query, labels)





"""<h3 style="font-family:'Segoe UI';color:purple">Understanding the CNN model and their architecture, wieghts, etc.</h3>

https://www.kdnuggets.com/2018/07/text-classification-lstm-cnn-pre-trained-word-vectors.html
"""

# list layers in the model
best_cnn3_embedding_model.layers

# getting the weights of first convolutional layers
conv1d1 = best_cnn3_embedding_model.layers[1].get_weights()[0]

conv1d1.shape # shape of the kernel,
# (kernel_size, embedding_dim, no.of_kernels)

best_cnn3_embedding_model.layers[1].get_config() # configuration of the particular layer

kernel0 = conv1d1[:,:,0]
kernel0

import seaborn as sns

plt.figure(figsize=(14,4))
sns.heatmap(kernel0,cmap='gray') # heatmap of one kernel in first Conv1D

# getting embeddings of words
embedding = best_cnn3_embedding_model.layers[0].get_weights()[0]

embedding.shape

len(tokenizer.word_index)

tokenizer.word_index['abusively']

titles = ['boy','girl','man','woman','women','abusively','encounter','talk','surrounded']

def plot_embeddings(titles, tokenizer, embedding):
    """
    This function plot the embeddings of given list according to tokenizer and embedding
    """
    for t in titles:
        # getting vector of particular title
        vec = embedding[tokenizer.word_index[t], :].reshape(1,-1)
        plt.figure(figsize=(20,1))
        sns.heatmap(vec,
                    #cmap='gray'
                   )#plotting vector
        plt.title(t) # showing title t
        plt.show() # force to show. otherwise you will get only last plot
    return None

plot_embeddings(titles, tokenizer, embedding)





"""<h1 style="font-family:'Segoe UI';color:blue">RNN-LSTM</h1>"""

checkpoint_path_lstm1_embedding = "../model_save/comment_data/best_lstm1_embedding_recall.hdf5"
checkpoint_dir_lstm1_embedding = os.path.dirname(checkpoint_path_lstm1_embedding)

# n_inputs : number of neurons in the input layer of the model
# n_outputs : number of neurons in the output layer of the model
n_inputs, n_outputs = X_train.shape[1], train_label.shape[1]
n_inputs, n_outputs
# because of using Embeddings by ourself and training, n_inputs wouldn't be 50
# instead, it would be vocabulary size(vocab_size)

# callbacks to save Models
save_model_lstm1_embedding = tf.keras.callbacks.ModelCheckpoint(
    filepath=checkpoint_path_lstm1_embedding,
    monitor='val_recall',
    save_best_only=True,
    verbose=1,
    mode='max' # get maximum val_recall
)

# https://keras.io/layers/embeddings/
# Now, we will learn a new embedding space using Embedding layer
# which maps above encoded word representation into dense vector.
# input_dim = the size of the vocabulary
# output_dim = the size of the dense vector
# input_length = the length of the sequence

# clear all previous sessions
tf.keras.backend.clear_session()
embedding_dim = 300
def create_lstm1_embedding_model():
    model = tf.keras.models.Sequential()
    model.add(tf.keras.layers.Embedding(input_dim=vocab_size,
                               output_dim=embedding_dim, # embedding_dim = 50
                               weights=[embedding_matrix],
                               input_length=maxlen,
                               trainable=True # We are using already trained weights, make it True to train this embedding
                              ))
    model.add(tf.keras.layers.LSTM(100, return_sequences=True))
    model.add(tf.keras.layers.LSTM(100))
    model.add(tf.keras.layers.Dense(10, activation='relu', kernel_initializer='he_uniform'))
    model.add(tf.keras.layers.Dense(n_outputs, activation='sigmoid'))
    return model

lstm1_embedding_model = create_lstm1_embedding_model()

lstm1_embedding_model.compile(optimizer='adam',
              loss='binary_crossentropy',
              metrics=['accuracy',
                       tf.keras.metrics.Precision(),
                       tf.keras.metrics.Recall(),
                       tfa.metrics.HammingLoss(mode='multilabel',threshold=0.5),
#                        hamming_score
                      ])
lstm1_embedding_model.summary()

lstm1_embedding_history=lstm1_embedding_model.fit(X_train, train_label.values,
              epochs=40,
              validation_data=(X_val, val_label.values),
              batch_size=128, # larger the batch size, model quality reduce : https://arxiv.org/abs/1609.04836
              verbose=2,
              callbacks=[save_model_lstm1_embedding]
         )

# evaluate model on test dataset
lstm1_embedding_model.evaluate(X_test, test_label.values)

best_lstm1_embedding_model=tf.keras.models.load_model(checkpoint_path_lstm1_embedding, custom_objects=dependencies)

best_lstm1_embedding_model.evaluate(X_test, test_label)

deep_modeling_report(best_lstm1_embedding_model, X_train, train_label.values, X_val, val_label.values, 'best lstm11 validation')

deep_modeling_report(best_lstm1_embedding_model, X_train, train_label.values, X_test, test_label.values, 'best lstm11 test')

labels=list(test_label.columns)
query = "When I was passing through local market a person commented on me and started following. after few minutes he came nearer to me and started ogling on me and he touched me also."

deep_multi_label_explainer(best_lstm1_embedding_model,query,labels)

query = "A person was staring on me."
deep_multi_label_explainer(best_lstm1_embedding_model, query, labels)



"""**bold text**<h2 style="font-family:'Segoe UI';color:purple">CNN-LSTM</h2>"""

checkpoint_path_cnn_lstm_embedding = "../model_save/multi_data/best_cnn_lstm_embedding_recall.hdf5"
checkpoint_dir_cnn_lstm_embedding = os.path.dirname(checkpoint_path_cnn_lstm_embedding)



np.random.seed(42)

# n_inputs : number of neurons in the input layer of the model
# n_outputs : number of neurons in the output layer of the model
n_inputs, n_outputs = X_train.shape[1], train_label.shape[1]
n_inputs, n_outputs
# because of using Embeddings by ourself and training, n_inputs wouldn't be 50
# instead, it would be vocabulary size(vocab_size)

# https://stackoverflow.com/questions/65464463/importerror-cannot-import-name-keras-tensor-from-tensorflow-python-keras-eng
import tensorflow_addons as tfa

# callbacks to save Models
save_model_cnn_lstm_embedding = tf.keras.callbacks.ModelCheckpoint(
    filepath=checkpoint_path_cnn_lstm_embedding,
    monitor='val_recall',
    save_best_only=True,
    verbose=1,
    mode='max' # get maximum val_recall
)

# https://keras.io/layers/embeddings/
# Now, we will learn a new embedding space using Embedding layer
# which maps above encoded word representation into dense vector.
# input_dim = the size of the vocabulary
# output_dim = the size of the dense vector
# input_length = the length of the sequence

# clear all previous sessions
tf.keras.backend.clear_session()
embedding_dim = 300
def create_cnn_lstm_embedding_model():
    model = tf.keras.models.Sequential()
    model.add(tf.keras.layers.Embedding(input_dim=vocab_size,
                               output_dim=embedding_dim, # embedding_dim = 50
                               weights=[embedding_matrix],
                               input_length=maxlen,
                               trainable=True # We are using already trained weights, make it True to train this embedding
                              ))
    model.add(tf.keras.layers.Conv1D(100, 3, activation='relu',
                           kernel_initializer='he_normal'))
    model.add(tf.keras.layers.MaxPool1D(pool_size=2))
    model.add(tf.keras.layers.Dropout(0.5))
    model.add(tf.keras.layers.Conv1D(100, 4, activation='relu',
                           kernel_initializer='he_normal'))
    model.add(tf.keras.layers.MaxPool1D(pool_size=2))
    model.add(tf.keras.layers.Dropout(0.5))
    model.add(tf.keras.layers.Conv1D(100, 5, activation='relu',
                           kernel_initializer='he_normal'))
    model.add(tf.keras.layers.MaxPool1D(pool_size=2))
    model.add(tf.keras.layers.Dropout(0.5))
    model.add(tf.keras.layers.LSTM(100
                         ))
    model.add(tf.keras.layers.Dense(n_outputs, activation='sigmoid'))
    return model
cnn_lstm_embedding_model = create_cnn_lstm_embedding_model()

cnn_lstm_embedding_model.compile(optimizer='adam',
              loss='binary_crossentropy',
              metrics=['accuracy',
                       tf.keras.metrics.Precision(),
                       tf.keras.metrics.Recall(),
                       tfa.metrics.HammingLoss(mode='multilabel',threshold=0.5),
                      ])
cnn_lstm_embedding_model.summary()

X_train[1] # an example of training dataset

cnn_lstm_embedding_history=cnn_lstm_embedding_model.fit(X_train, train_label.values,
              epochs=20,
              validation_data=(X_val, val_label.values),
              batch_size=128, # larger the batch size, model quality reduce : https://arxiv.org/abs/1609.04836
              verbose=2,
              callbacks=[save_model_cnn_lstm_embedding]
            )

best_cnn_lstm_embedding_model = tf.keras.models.load_model(checkpoint_path_cnn_lstm_embedding, custom_objects=dependencies)

best_cnn_lstm_embedding_model.evaluate(X_test, test_label)

deep_modeling_report(best_cnn_lstm_embedding_model, X_train, train_label.values, X_val, val_label.values, 'best cnn_lstm1 validation')

deep_modeling_report(best_cnn_lstm_embedding_model, X_train, train_label.values, X_test, test_label.values, 'best cnn_lstm1 test')

"""

```
# This is formatted as code
```

<h4 style="font-family:'Segoe UI';color:purple">Interpret using LIME</h4>"""

labelslabels=list(test_label.columns)
query = "When I was passing through local market a person commented on me and started following. after few minutes he came nearer to me and started ogling on me and he touched me also."

deep_multi_label_explainer(best_cnn_lstm_embedding_model, query, labels)

query = "A person was looking at me."
deep_multi_label_explainer(best_cnn_lstm_embedding_model, query, labels)
