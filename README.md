# EnsembleDiversityTests
***
## Simple python implementations of Diversity Measures for Classifiers
***
Measures mainly from 
- [**Combining Pattern Classifiers: Methods and Algorithms**, *Ludmila Kuncheva, 2004*](http://www.ccas.ru/voron/download/books/machlearn/kuncheva04combining.pdf)
- Conditional Accuracy Table as in [**Combining Information Extraction Systems Using Voting 
and Stacked Generalization**, *Sigletos et al, 2005*](http://www.jmlr.org/papers/volume6/sigletos05a/sigletos05a.pdf)

## Python dependencies

(May need sudo rights for the following installations)

1. Install _pip_ 
```sh
apt-get install python-pip 
```
2. Install  needed python modules trhough _pip_

```sh
$ pip install -r requirements.txt
```

That’s it.

## Example python usage

(Running the following in python):

```python
from EnsembleDiversityTests import DiversityTests

pred_a = ['male', 'female', 'male']
pred_b = ['female', 'female', 'female']
pred_c = ['male','male','male']
names = ['a', 'b', 'c']
truth = ['female', 'male', 'female']
predictions_test= [pred_a,pred_b,pred_c]
test_class = DiversityTests(predictions_test, names, truth)
test_class.print_report()
```
Will produce:
```python
---------------------------------------------------------------
Diversity Tests Report
---------------------------------------------------------------

Measures Details
===============================================================
Correlation: For +-1 perfect aggrement/disagreement
Q-statistic: Q=0  => Independent. For q>0 predictors find the the same results
Cohen's k: k->0  => High Disagreement => High Diversity
Kohovi-Wolpert Variance -> Inf => High Diversity
Conditional Accuracy Table: Conditional Probability that the row system predicts correctly, given
                            that the column system also predicts correctly
===============================================================
---------------------------------------------------------------

Measures Results
---------------------------------------------------------------

['get_KWVariance', 'get_avg_pairwise', 'get_conditional_acc_table']
#####  Kohovi-Wolpert Variance:  0.222  #####
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

#### Pairwise Average Metrics: #####
Avg. Cor: 0.000
Avg. Q-statistic: nan
Avg. Cohen's k: 0.000
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

###Conditional Accuracy Table###
     a    b    c
a 1.00 0.00 0.00
b  nan 1.00 0.00
c  nan 0.00 1.00
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

```

#### Args for DiversityTests:
- @predictions: list of lists. Each sublist contains the predictions
                      of a classifier
- @names: list of strings. Each string is the name of the classifier.
- @true: list of labels. Each label is the truth label



### Questions/Errors
Bougiatiotis Konstantinos, NCSR ‘DEMOKRITOS’
E-mail: bogas.ko@gmail.com
