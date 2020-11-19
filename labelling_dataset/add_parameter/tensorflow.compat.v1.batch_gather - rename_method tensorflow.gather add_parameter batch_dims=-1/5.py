# coding=utf-8
# Copyright 2020 The Google Research Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Truncated Rejection Sampling distribution."""

from __future__ import absolute_import
import functools
import tensorflow.compat.v1 as tf
import tensorflow_probability as tfp
from eim.models import base
tfd = tfp.distributions


class AbstractRejectionSampling(base.ProbabilisticModel):
  """Truncated Rejection Sampling distribution."""
  def sample(self, num_samples=1):


    accept_indices = get_first_nonzero_index(accept_samples)  # sample_shape
    samples = tf.batch_gather(proposal_samples, accept_indices)
    return tf.squeeze(samples, axis=1)  # Squeeze the selected dim
