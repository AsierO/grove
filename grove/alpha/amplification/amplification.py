##############################################################################
# Copyright 2016-2017 Rigetti Computing
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
##############################################################################

"""Module for amplitude amplification, for use in algorithms such as Grover's algorithm.

 See G. Brassard, P. Hoyer, M. Mosca (2000) `Quantum Amplitude Amplification and Estimation
 <https://arxiv.org/abs/quant-ph/0005055 arXiv:quant-ph/0005055>`_ for more information.
"""

import numpy as np

import pyquil.quil as pq
from pyquil.gates import H, X, Z, RZ, STANDARD_GATES

from grove.alpha.utility_programs import n_qubit_control
from grove.alpha.utility_programs import is_valid_qubits

STANDARD_GATE_NAMES = list(STANDARD_GATES.keys())


def amplify(algorithm, oracle, qubits, num_iter):
    """
    Returns a program that does n rounds of amplification, given a measurement-less algorithm,
    an oracle, and a list of qubits to operate on.

    :param Program algorithm: A program representing a measurement-less algorithm run on qubits.
    :param Program oracle: An oracle maps any basis vector to either |0> or |1>.
    :param Sequence qubits: the qubits to operate on
    :param int num_iter: number of iterations of amplifications to run
    :return: The amplified algorithm.
    :rtype: Program
    """
    if not isinstance(algorithm, pq.Program):
        raise ValueError("algorithm must be a valid Program instance")
    if not isinstance(oracle, pq.Program):
        raise ValueError("oracle must be a valid Program instance")
    if num_iter <= 0:
        raise ValueError("num_iter must be greater than zero")
    if not is_valid_qubits(qubits) or len(qubits) <= 0:
        raise ValueError("The list of qubits to apply the diffusion operator to must be non-empty")

    prog = pq.Program()

    uniform_superimposer = pq.Program().inst(list(map(H, qubits)))
    prog += uniform_superimposer

    for _ in range(num_iter):
        prog += oracle + algorithm.dagger() + diffusion_operator(qubits) + algorithm
    return prog


def diffusion_operator(qubits):
    """Constructs the diffusion operator in the Hadamard basis on qubits,
    assuming they are ordered from most significant qubit to least significant qubit.

    This is the diagonal operator given by (1, -1, -1, ..., -1).

    See C. Lavor, L.R.U. Manssur, and R. Portugal (2003) `Grover's Algorithm: Quantum Database
    Search<https://arxiv.org/abs/quant-ph/0301079>`_ for more information.

    :param qubits: A list of ints corresponding to the qubits to operate on.
                   The operator operates on bistrings of the form
                   |qubits[0], ..., qubits[-1]>.
    """

    if not is_valid_qubits(qubits) or len(qubits) == 0:
        raise ValueError("qubits must be a non-empty Sequence of qubits.")

    p = pq.Program()

    if len(qubits) == 1:
        p.inst(Z(qubits[0]))
    else:
        p.inst(list(map(X, qubits)))
        p.inst(H(qubits[-1]))
        p.inst(RZ(-np.pi)(qubits[0]))
        p += n_qubit_control(qubits[:-1], qubits[-1], np.array([[0, 1], [1, 0]]), "NOT")
        p.inst(RZ(-np.pi)(qubits[0]))
        p.inst(H(qubits[-1]))
        p.inst(list(map(X, qubits)))
    return p
