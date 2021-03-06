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

from grove.utils.utility_programs import ControlledProgramBuilder

STANDARD_GATE_NAMES = list(STANDARD_GATES.keys())
X_GATE = np.array([[0, 1], [1, 0]])


def amplification_circuit(algorithm, oracle, qubits, num_iter):
    """
    Returns a program that does ``num_iter`` rounds of amplification, given a measurement-less
    algorithm, an oracle, and a list of qubits to operate on.

    :param Program algorithm: A program representing a measurement-less algorithm run on qubits.
    :param Program oracle: An oracle maps any basis vector ``|psi>`` to either ``+|psi>`` or
    ``-|psi>`` depending on whether ``|psi>`` is in the desirable subspace or the undesirable
    subspace.
    :param Sequence qubits: the qubits to operate on
    :param int num_iter: number of iterations of amplifications to run
    :return: The amplified algorithm.
    :rtype: Program
    """
    if num_iter <= 0:
        raise ValueError("num_iter must be greater than zero")

    prog = pq.Program()

    uniform_superimposer = pq.Program().inst([H(qubit) for qubit in qubits])
    prog += uniform_superimposer

    for _ in range(num_iter):
        prog += oracle + algorithm.dagger() + diffusion_program(qubits) + algorithm
    return prog


def diffusion_program(qubits):
    """Constructs the diffusion operator used in Grover's Algorithm, acted on both sides by an
     a Hadamard gate on each qubit. Note that this means that the matrix representation of this
     operator is diag(1, -1, ..., -1).

    See C. Lavor, L.R.U. Manssur, and R. Portugal (2003) `Grover's Algorithm: Quantum Database
    Search`_ for more information.

    .. _`Grover's Algorithm: Quantum Database Search`: https://arxiv.org/abs/quant-ph/0301079

    :param qubits: A list of ints corresponding to the qubits to operate on.
                   The operator operates on bistrings of the form
                   |qubits[0], ..., qubits[-1]>.
    """
    diffusion_program = pq.Program()

    if len(qubits) == 1:
        diffusion_program.inst(Z(qubits[0]))
    else:
        diffusion_program.inst([X(q) for q in qubits])
        diffusion_program.inst(H(qubits[-1]))
        diffusion_program.inst(RZ(-np.pi)(qubits[0]))
        diffusion_program += (ControlledProgramBuilder()
                              .with_controls(qubits[:-1])
                              .with_target(qubits[-1])
                              .with_operation(X_GATE)
                              .with_gate_name("NOT").build())
        diffusion_program.inst(RZ(-np.pi)(qubits[0]))
        diffusion_program.inst(H(qubits[-1]))
        diffusion_program.inst([X(q) for q in qubits])
    return diffusion_program
