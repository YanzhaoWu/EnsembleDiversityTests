from sklearn.base import BaseEstimator, TransformerMixin


class Combinator(BaseEstimator, TransformerMixin):
    """ Static A posteriori Combinator of predictions.

        Args:
            - scheme: String flag. Can be one of the following:
                - 'majority': Simple Hard Majority Voting
                - 'weights': Weighted Voting, with weights
                             passed by user in the weights
                             arg
                - 'accuracy': Weights are calculated according
                              to prediction accuracy over the
                              meta train set
                - 'optimal': The optimal weights are found, this
                             is done by optimizing over the classification
                             error
            - weights: list or numpy.array(not sure?) containing as many
                         weights as the models in the ensemble
        Returns:
            - The  ensemble Model. Needs to be fitted for the encoding part
    """

    def __init__(self, scheme='majority', weights=None):

        from sklearn.preprocessing import LabelEncoder, OneHotEncoder
        import numpy

        self.scheme = scheme
        self.weights = weights
        self.transformation = self.voting
        self.num_labels = 0
        self.num_models = 0
        self.lab = LabelEncoder()
        self.ohe = OneHotEncoder()

        if self.scheme == 'majority':
            # print "Hurray! Equality for all!"
            self.weights = None
        else:
            # print "Not so much Vox Populi, Vox Dei, huh?"
            if self.scheme == 'weights':
                if type(self.weights) in (numpy.array, numpy.ndarray):
                    pass  # It is from the optimization part
                else:
                    if not(self.weights):
                        print "Need weights for this scheme!"
                self.weights = weights
                weights_string = " %.2f |" * len(self.weights) % tuple(self.weights)
                # print "Using given weights: | %s" % weights_string
            else:
                # print "Will find the weights after fitting"
                pass

    def fit(self, X, y, weights=None):

        if y is None:
            raise ValueError('We need y labels to supervise-fit!')
        X_tr, y_tr = self.fit_encoders(X, y)
        if not(self.scheme in ['majority', 'weights']):
            self.find_weights(X, y, X_tr, y_tr)
            weights_string = " %.2f |" * len(self.weights) % tuple(self.weights)
            # print "Using found weights: | %s" % weights_string
        return self

    def transform(self, X):

        import numpy

        if type(X[0]) is numpy.array:
            N_samples = X[0].shape[0]
        else:
            N_samples = len(X[0])
        X = self.lab.transform(X)
        X = self.ohe.transform(X.reshape(-1, 1)).todense().reshape(N_samples, -1)
        prediction = self.transformation(X)
        prediction = self.lab.inverse_transform(prediction.argmax(axis=1))
        return prediction

    def predict(self, X):
        return self.transform(X)

    def score(self, X, y_true):

        from sklearn.metrics import accuracy_score

        y_pred = self.predict(X)
        return accuracy_score(y_true, y_pred, normalize=True)

    def fit_encoders(self, X, y):

        import numpy

        self.num_labels = len(set(y))
        N_samples = len(y)
        # print "N_smaples"
        # print N_samples
        if type(X) is numpy.array:
            y = y.reshape(-1, 1)
        else:
            y = numpy.array(y).reshape(-1, 1)
        # print y
        y = self.lab.fit_transform(y).reshape(-1, 1)
        # print 'label'
        # print y
        y = self.ohe.fit_transform(y).todense()
        # print 'ohe'
        # print y
        # print X
        # print len(X)
        # print len(X[0])
        X = self.lab.transform(X)
        # print 'Label'
        # print X
        # print X.shape
        # reshape(N_samples, N_samples*self.num_labels)
        X = self.ohe.transform(X.T.reshape(-1, 1)).todense().reshape(N_samples, -1)
        # print 'ohe'
        # print X.shape
        self.num_models = int(X.shape[1] / self.num_labels)
        return X, y

    def voting(self, X):

        import numpy

        predictions = numpy.zeros([X.shape[0], self.num_labels])
        if type(self.weights) in (numpy.array, numpy.ndarray):
            pass
        else:
            if not(self.weights):
                self.weights = [1 for i in xrange(self.num_models)]
        for i in xrange(X.shape[0]):
            # print X.shape
            # print X
            subarrays = numpy.split(X[i, :], self.num_models, axis=1)
            # print "subarrays"
            # print subarrays
            votes = numpy.zeros([1, self.num_labels])
            for model_index, subar in enumerate(subarrays):
                # print subar
                votes = numpy.vstack((votes, subar*self.weights[model_index]))
            # print votes
            pred_ = votes.sum(axis=0).argmax()
            pred_ = self.ohe.transform(pred_).todense()
            predictions[i, :] = pred_
        return predictions

    def find_weights(self, X, y, X_tr, y_tr):

        import numpy

        weights = [0 for i in xrange(self.num_models)]
        if self.scheme == 'accuracy':
            for i in xrange(X_tr.shape[0]):
                subarrays = numpy.split(X_tr[i, :], self.num_models, axis=1)
                for model_index, subar in enumerate(subarrays):
                    if (subar == y_tr[i, :]).all():
                        weights[model_index] += 1
            self.weights = weights
        if self.scheme == 'optimal':
            from scipy.optimize import minimize

            w = [1 for i in xrange(self.num_models)]
            bnds = tuple([(0, None) for i in xrange(self.num_models)])
            a = minimize(self.f, w, args=(Combinator, X, y), method='SLSQP', bounds=bnds)
            self.weights = list(a.x)
        return

    def f(self, w, Combinator, x, y):
        gg = Combinator(scheme='weights', weights=w)
        gg.fit(x, y)
        score = 1 - gg.score(x, y)
        # print 'Weights'
        # print w
        # print 'Score: ' + str(score)
        return score    


#  Example Usage
# def f(w, Combinator, x, y):
#     gg = Combinator(scheme='weights', weights=w)
#     gg.fit(x, y)
#     score = 1- gg.score(x, y)
#     #print 'Weights'
#     #print w
#     #print 'Score: ' + str(score)
#     return score    

# w = [1 for i in xrange(6)]
# bnds = tuple([(0, None) for i in xrange(6)])
# a = minimize(f, w,  args=(Combinator, predictions_meta, y_meta), method='SLSQP', bounds=bnds)



class SubSpaceEnsemble4_2(BaseEstimator, TransformerMixin):
    """ Best model base on the prediction of the k-nearest, according to each model, neighbor.
        Implementing fitting with random weight searching for better results."""

    def __init__(self, models, cv_scores, k=6, weights=[0.6, 0.2, 0.3, 6], N_rand=8, rand_split=0.6):

        if (not models) or (not cv_scores):
            raise AttributeError('Models expexts a dictonary of models \
              containg the predictions of y_true for each classifier.\
              cv_score expects a list len(models.keys()) with the\
              cross validation scores of each model')
        else:
            self.models = models
            self.cv_scores = cv_scores
            self.k = k
            self.ind2names = {}
            self.weights = weights
            self.N_rand = N_rand
            self.rand_split = rand_split
            for i, name in enumerate(models.keys()):
                self.ind2names[i] = name
            self.predictions = []
            self.true = []
            self.trees = []
            self.representations = []

    def fit(self, X_cv, y_true=None, weights=None):
        from sklearn.neighbors import BallTree
        from sklearn.metrics import accuracy_score
        import random
        import time

        if y_true is None:
            raise ValueError('we need y labels to supervise-fit!')
        else:
            t0 = time.time()
            predictions = []
            for name, model in self.models.iteritems():
                predictions.append(model.predict(X_cv))
                # print len(predictions[-1])
                transf = model.steps[0][1].transform(X_cv)
                if hasattr(transf, "toarray"):
                    # print 'Exei'
                    self.representations.append(transf.toarray())
                else:
                    self.representations.append(transf)
                self.trees.append(BallTree(self.representations[-1], leaf_size=20))
            self.predictions = predictions
            self.true = y_true
            N_rand1 = int(self.rand_split * self.N_rand)
            poss_w = []
            acc_ = []
            pred = []
            for i in xrange(N_rand1):
                tmp_w = [0.6, 0.2, 0.3, 6]
                tmp_w[0] = round(random.random(), 3)
                tmp_w[1] = round(1 - tmp_w[0], 3)
                tmp_w[2] = round(random.uniform(0.2, 0.8), 3)
                # tmp_w[3] = random.randint(1,10)
                poss_w.append(tmp_w)
                pred = self.find_weights(X_cv, tmp_w)
                acc = accuracy_score(self.true, pred)
                # print('Accuracy : {}'.format(acc))
                acc_.append(acc)
            print('First search took: %0.3f seconds') % (time.time() - t0)
            tmp_w = poss_w[acc_.index(max(acc_))]
            poss_w = []
            acc_ = []
            for i in xrange(self.N_rand  -N_rand1):
                tmp_w2 = tmp_w
                tmp_w2[0] = round(random.uniform(tmp_w[0] - 0.1, tmp_w[0] + 0.1), 3)
                tmp_w2[1] = round(1 - tmp_w2[0], 3)
                tmp_w2[2] = round(random.uniform(tmp_w[2] - 0.1, tmp_w[1] + 0.1), 3)
                poss_w.append(tmp_w2)
                pred = self.find_weights(X_cv, tmp_w2)
                acc = accuracy_score(self.true, pred)
                # print('Accuracy : {}'.format(acc))
                acc_.append(acc)
            self.weights = poss_w[acc_.index(max(acc_))]
            self.k = self.weights[3]
            print 'Accuracy obtained in CV-data: %0.3f' % (100 * acc_[acc_.index(max(acc_))])
            print self.weights
            print('Fit took: %0.3f seconds') % (time.time() - t0)
            # print self.expert_scores
            # print self.experts
            return self

    def find_weights(self, X_cv, w):

        y_pred = []
        # t0 = time.time()
        for x in X_cv:
            # print 'True: ' + y_real[i]
            y_pred.append(self.expert_fit_decision(x, w))
        # print('Predict took: %0.3f seconds') % (time.time()-t0)
        return y_pred

    def expert_fit_decision(self, x_sample, w):

        from sklearn.metrics import accuracy_score
        # from collections import Counter

        possible_experts = []
        sample_predictions = []
        acc = []
        possible_experts_sc = []
        for model_i in xrange(len(self.models.values())):
            # print 'Model: ' + self.ind2names[model_i]
            temp_trans = self.models[self.ind2names[model_i]].steps[0][1].transform([x_sample])
            if hasattr(temp_trans, 'toarray'):
                temp_trans = temp_trans.toarray()
            _, model_neig = self.trees[model_i].query(temp_trans, w[3])
            # print "Model neig"
            # print model_neig[0].tolist()[0]
            model_neig_pred = []
            neigh_true = []
            for model_n_i in model_neig[0].tolist():
                model_neig_pred.append(self.predictions[model_i][model_n_i])
                neigh_true.append(self.true[model_n_i])
            # print "True_neighbors"
            # print neigh_true
            # print "Predicted neighbors"
            # print model_neig_pred
            acc.append(accuracy_score(neigh_true, model_neig_pred, normalize=True))
            # print 'Neig Accc: % 0.2f' % acc[-1]
            predicted = self.models[self.ind2names[model_i]].predict([x_sample])[0]
            proba = max(self.models[self.ind2names[model_i]].predict_proba([x_sample])[0])
            # print 'Predicted Sample: %s with proba: %0.3f' % (predicted, 100*proba)
            if  acc[-1] > w[2]:
                possible_experts.append(model_i)
                possible_experts_sc.append(w[1]*acc[-1]+w[0]*proba)
                sample_predictions.append(predicted)
        if possible_experts:
            # print 'Possible experts:'
            # print [self.ind2names[poss] for poss in possible_experts]
            # print sample_predictions
            # print 'Selected: '
            # print 'Place of best expert: %d ' % possible_scores.index(max(possible_scores))
            # print 'Name:  ' + self.ind2names[possible_experts[possible_scores.index(max(possible_scores))]]
            # print 'PRediction index: '
            # print possible_scores.index(max(possible_scores))
            # print 'PRediction : '
            # print sample_predictions[possible_experts_sc.index(max(possible_experts_sc))]
            return sample_predictions[possible_experts_sc.index(max(possible_experts_sc))]
        else:
            # print 'Selected2 from base model: ' + self.ind2names[(self.acc.index(max(acc)))]
            # print self.models[self.ind2names[(self.acc.index(max(acc)))]].predict([x_sample])[0]
            return self.models[self.ind2names[(acc.index(max(acc)))]].predict([x_sample])[0]

    def predict(self, X):
        # import time

        # print "PRedict"
        # print X.shape
        y_pred = []
        # t0 = time.time()
        for i, x in enumerate(X):
            # print 'True: ' + y_real[i]
            y_pred.append(self.expert_decision(x))
        # print('Predict took: %0.3f seconds') % (time.time()-t0)
        return y_pred

    def score(self, X, y, sample_weight=None):

        from sklearn.metrics import accuracy_score
        return accuracy_score(y, self.predict(X), normalize=True)
        # return self.svc.score(self.transform_to_y(X), y, sample_weight)

    def expert_decision(self, x_sample):

        from sklearn.metrics import accuracy_score
        # from collections import Counter

        possible_experts = []
        sample_predictions = []
        acc = []
        possible_experts_sc = []
        for model_i in xrange(len(self.models.values())):
            # print 'Model: ' + self.ind2names[model_i]
            temp_trans = self.models[self.ind2names[model_i]].steps[0][1].transform([x_sample])
            if hasattr(temp_trans, 'toarray'):
                temp_trans = temp_trans.toarray()
            _, model_neig = self.trees[model_i].query(temp_trans, self.k)
            # print "Model neig"
            # print model_neig[0].tolist()[0]
            model_neig_pred = []
            neigh_true = []
            for model_n_i in model_neig[0].tolist():
                model_neig_pred.append(self.predictions[model_i][model_n_i])
                neigh_true.append(self.true[model_n_i])
            # print "True_neighbors"
            # print neigh_true
            # print "Predicted neighbors"
            # print model_neig_pred
            acc.append(accuracy_score(neigh_true, model_neig_pred, normalize=True))
            # print 'Neig Accc: % 0.2f' % acc[-1]
            predicted = self.models[self.ind2names[model_i]].predict([x_sample])[0]
            proba = max(self.models[self.ind2names[model_i]].predict_proba([x_sample])[0])
            # print 'Predicted Sample: %s with proba: %0.3f' % (predicted, 100*proba)
            if acc[-1] > self.weights[2]:
                possible_experts.append(model_i)
                possible_experts_sc.append(self.weights[1] * acc[-1] + self.weights[0] * proba)
                sample_predictions.append(predicted)
        if possible_experts:
            # print 'Possible experts:'
            # print [self.ind2names[poss] for poss in possible_experts]
            # print sample_predictions
            # print possible_experts_sc
            # print 'Selected: '
            # print 'Place of best expert: %d ' % possible_scores.index(max(possible_scores))
            # print 'Name:  ' + self.ind2names[possible_experts[possible_scores.index(max(possible_scores))]]
            # print 'PRediction index: '
            # print possible_scores.index(max(possible_scores))
            # print 'PRediction : '
            # print sample_predictions[possible_experts_sc.index(max(possible_experts_sc))]
            return sample_predictions[possible_experts_sc.index(max(possible_experts_sc))]
        else:
            # print 'Selected2 from base model: ' + self.ind2names[(acc.index(max(acc)))]
            # print self.models[self.ind2names[(acc.index(max(acc)))]].predict([x_sample])[0]
            return self.models[self.ind2names[(acc.index(max(acc)))]].predict([x_sample])[0]
