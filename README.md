Explanation Video Link : https://drive.google.com/file/d/1cJDusAj5dqFtXTv9_0iBA2U1DYv_xdwH/view?usp=drive_link

Data Overview: Refer: https://github.com/swkarlekar/safecity All of the data is in 2 folders. Folder 1(Binary Classification): commenting_data: train test validation groping_data: train test validation ogling_data: train test validation Folder 2(Multi-label classification): train test validation

Types of Machine Learning Problem

Single-Label Classification The data for single-label classification is given in two columns, with the first column being the description of the incident and the second column being 1 if the category of sexual harassment is present and 0 if it is not.

Examples from Groping Binary Classification Dataset:

Description Category Was walking along crowded street, holding mums hand, when an elderly man groped butt, I turned to look at him and he looked away, and did it again after a while.I was 12 yrs old then. 1 This incident took place in the evening.I was in the metro when two guys started staring. 0 Catcalls and passing comments were two of the ghastly things the Delhi police at the International Airport put me and my friend through. It is appalling that the protectors and law enforcers at the airport can make someone so uncomfortable. 0 10% of each dataset was randomly selected and held out for the test set. From the remaining training data, 10% was randomly selected and set aside for the development set.

Category % Positive Commenting 39.3% Ogling 21.4% Groping 30.1% For each category, there are 7201 training samples, 990 development samples, and 1701 test samples.

Multi-Label Classification The data for multi-label classification is given in four columns, with the first column being the description of the incident and the second, third, and fourth column being 1 if the category of sexual harassment is present and 0 if it is not.

Examples from Multi-Label Classification Dataset:

Description Commenting Ogling/Facial Expressions/Staring Touching/Groping Was walking along crowded street, holding mums hand, when an elderly man groped butt, I turned to look at h7m and he looked away, and did it again after a while.I was 12 yrs old then. 0 0 1 This incident took place in the evening.I was in the metro when two guys started staring. 0 1 0 Catcalls and passing comments were two of the ghastly things the Delhi police at the International Airport put me and my friend through. It is appalling that the protectors and law enforcers at the airport can make someone so uncomfortable. 1 1 0 10% of the dataset was randomly selected and held out for the test set. From the remaining training data, 10% was randomly selected and set aside for the development set.

Commenting Ogling Groping Examples in Dataset 1 1 1 351 1 1 0 819 1 0 1 459 0 1 1 201 1 0 0 2256 0 0 1 1966 0 1 0 743 0 0 0 3097 There are 7201 training samples, 990 development samples, and 1701 test samples.

Technical aspect I solved this problem using both Machine Learning and Deep Learning Algorithms

Machine Learning: Binary Classification: Encoding: For text encoding, I use TF-IDF(Term-Frequency Inverse-Document Frequency). ML Algorithms: Logistic Regression SVM(linear, 'rbf','ploy') Naive Bayes(Guassian, Multinomial, Binomial) Decision Tree Classifier Random Forest GBDT(Gradient Boosting Decision Tree) Didn't use KNN because of latency problem. Best Performance Algorithm: Logistic Regression Won the Game. Performance Metrics: Precision Recall. AUC (Area Under Curve) Library: scikit-learn Multilabel Classification: Agorithms: BinaryRelevance OneVsRestClassifier(with LogitsticRegression, etc.) ClassifierChain LabelPowerset Library used: skmultilearn Performance Metrics: Precision Recall : Hamming score Hamming loss: It is not interpretable for each label because it calculates loss for all the labels. Exact math(accuracy) was used in Research Paper, But the exact match is not the right metric to judge how the model is performing on each label. I used Precision score and Recall score for each label. Deep Learning: In Deep Learning, the only difference between Binary and Multi-label Classification is the last layer of the Neural Network. Encoding: Used Embedding Layer to train our own embedding Used Word2Vec pre-trained encoding for each word(50d, and 300d) DL Algorithms: CNN: Used Conv1D, 1D convolution is used to preserve sequential relationships to some extent. RNN: Recurrent Neural Network, we used LSTM(Long Short Term Memory). CNN-RNN: Combination of Conv1D and RNN Miscellaneous Details: Used Adam Optimizer. Used ReLU activation function as hidden activation function. Saved Best Model according to best validation recall. Used Dropout to overcome overfitting problem.
