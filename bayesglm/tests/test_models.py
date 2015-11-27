import numpy as np
import numpy.testing as nptest
from scipy.special import logit, expit
import pandas as pd
import unittest

from ..models import load_model_template, bayesglm
from .. import family

BETA = np.array([15, 5])
NUM_ROWS = 2000
ITERATIONS = 200


def make_matrix_data(num_rows, beta, noise_sd=1, binary=False):
    np.random.seed(seed=0)
    x = np.random.normal(size=(num_rows,len(beta)))
    y = np.dot(x, beta) + np.random.normal(size=num_rows, scale=noise_sd)
    if binary:
        y = np.random.binomial(n=1, p=expit(y))
    return x, y


def make_data_frame_data(num_rows, beta, noise_sd=1, binary=False):
    x, y = make_matrix_data(num_rows, beta, noise_sd=noise_sd, binary=binary)
    df = pd.DataFrame(x, columns = ["x1", "x2"])
    df['y'] = y
    return df


class Tests(unittest.TestCase):

    def test_load_model_template(self):
        self.assertTrue(type(load_model_template()) == str)

    def test_bayesglm_gaussian(self):
        # tests both data frame and matrix form
        x, y = make_matrix_data(num_rows=NUM_ROWS, beta=BETA)
        result_matrix = bayesglm(x, y, family=family.gaussian(), iterations=ITERATIONS, seed=0)
        beta_samples = result_matrix.extract()['beta']
        beta_means = beta_samples.mean(axis=0)
        nptest.assert_allclose(beta_means, np.array(BETA), atol=.1)

        #check that data frame result is same as matrix result
        df = make_data_frame_data(num_rows=NUM_ROWS, beta=BETA)
        result_data_frame = bayesglm("y ~ 0 + x1 + x2", df, family=family.gaussian(), iterations=ITERATIONS, seed=0)
        nptest.assert_allclose(result_matrix.extract(permuted=False), result_data_frame.extract(permuted=False))


    def test_bayesglm_logistic(self):
        df = make_data_frame_data(num_rows=NUM_ROWS, beta=BETA, binary=True)
        result = bayesglm("y ~ x1 + x2", df, family=family.bernoulli(), iterations=ITERATIONS, seed=0)
        beta_samples = result.extract()['beta']
        beta_means = beta_samples.mean(axis=0)
        true_betas = np.hstack([[0], BETA])
        nptest.assert_allclose(beta_means, true_betas, atol=1) # "0" is true parameter for constant
