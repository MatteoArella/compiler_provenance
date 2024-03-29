if __name__ == '__main__':
    from compiler_provenance.common.hyperparameter import EstimatorSelectionHelper
    from compiler_provenance.common.preprocessing import AbstractedAsmTransformer
    from joblib import load, dump
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.pipeline import Pipeline
    from sklearn.svm import SVC
    from sklearn.naive_bayes import MultinomialNB
    from datetime import date
    import os

    train = load('compiler_provenance/compiler/train.joblib')
    test = load('compiler_provenance/compiler/test.joblib')

    X_train, y_train = train['instructions'], train['target']
    X_test, y_test = test['instructions'], test['target']

    random_state=25

    asmTransformer = AbstractedAsmTransformer()

    pipelines = {
        'SVMClassifier': {   'pipeline': Pipeline([
                                        ('asm_preproc', asmTransformer),
                                        ('tfidf', TfidfVectorizer(analyzer='word', use_idf=True)),
                                        ('clf', SVC(gamma='scale', probability=True))
                                    ]),
                            'hyperparams': {
                                'tfidf__ngram_range': [(1,2), (1,3), (1,4), (1,5),
                                                    (2,2), (3,3), (4,4), (5,5)],
                                'clf__kernel': ['linear', 'poly', 'rbf'],
                                'clf__C': [0.01, 0.1, 1, 10, 100],
                            },
        },
        'MultinomialNVClassifier': { 'pipeline': Pipeline([
                                        ('asm_preproc', asmTransformer),
                                        ('tfidf', TfidfVectorizer(analyzer='word', use_idf=True)),
                                        ('clf', MultinomialNB())
                                    ]),
                                    'hyperparams': {
                                        'tfidf__ngram_range': [(1,2), (1,3), (1,4), (1,5),
                                                                (2,2), (3,3), (4,4), (5,5)],
                                    }
        }
    }

    dirpath = date.today().strftime('compiler_provenance/compiler/%d-%m-%Y')

    estimator = EstimatorSelectionHelper(pipelines)
    estimator.fit(X_train, y_train, cv=5, n_jobs=-1, iid=False, verbose=10)
    summary = estimator.score_summary()
    print(summary)

    if not os.path.exists(dirpath):
        os.makedirs(dirpath)

    estimator.dump(dirpath)
    dump(summary, '%s/summary.joblib' % (dirpath), compress=('gzip', 6))
