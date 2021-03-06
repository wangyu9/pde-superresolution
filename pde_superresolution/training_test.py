# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Sanity tests for training a model."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import json
import tempfile

from absl import flags
from absl.testing import parameterized
from absl.testing import absltest  # pylint: disable=g-bad-import-order
import numpy as np
import pandas as pd
import tensorflow as tf

from pde_superresolution import training  # pylint: disable=g-bad-import-order


FLAGS = flags.FLAGS

NUM_X_POINTS = 256


class TrainingTest(parameterized.TestCase):

  def setUp(self):
    self.tmpdir = tempfile.mkdtemp(dir=FLAGS.test_tmpdir)

  extra_testcases = []
  for equation in ['burgers', 'kdv', 'ks']:
    for conservative in [True, False]:
      for num_time_steps in [0, 1]:
        extra_testcases.append({
            'equation': equation,
            'conservative': conservative,
            'num_time_steps': num_time_steps,
        })

  @parameterized.parameters(
      dict(equation='burgers', polynomial_accuracy_order=0),
      dict(equation='ks', coefficient_grid_min_size=9),
      dict(equation='ks', polynomial_accuracy_order=0),
      dict(equation='burgers', conservative=True, numerical_flux=True),
      dict(equation='ks', conservative=True, numerical_flux=True),
      dict(equation='kdv', conservative=True, numerical_flux=True),
      dict(equation='burgers', noise_probability=0.5, noise_amplitude=0.1),
      dict(equation='burgers', noise_probability=0.5, noise_amplitude=0.1,
           noise_type='filtered'),
      dict(equation='burgers', kernel_size=5, nonlinearity='relu6'),
      dict(equation='burgers', resample_factor=64),
      dict(equation='burgers', polynomial_accuracy_order=1, num_layers=0),
      *extra_testcases)
  def test_training_loop(self, **hparam_values):
    with tf.Graph().as_default():
      snapshots = np.random.RandomState(0).randn(100, NUM_X_POINTS)
      hparams = training.create_hparams(
          learning_rates=[1e-3],
          learning_stops=[20],
          eval_interval=10,
          equation_kwargs=json.dumps({'num_points': NUM_X_POINTS}),
          **hparam_values)
      results = training.training_loop(snapshots, self.tmpdir, hparams)
      self.assertIsInstance(results, pd.DataFrame)
      self.assertEqual(results.shape[0], 2)


if __name__ == '__main__':
  absltest.main()
