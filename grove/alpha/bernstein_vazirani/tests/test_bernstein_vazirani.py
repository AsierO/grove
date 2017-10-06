import numpy as np
import pyquil.api as api
import pyquil.quil as pq
import pytest
from pyquil.gates import X

from grove.alpha.bernstein_vazirani.bernstein_vazirani import bernstein_vazirani, oracle_function


@pytest.mark.skip(reason="Must add support for Forest connections in testing")
class TestOracleFunction(object):
    def test_one_qubit(self):
        vec_a = np.array([1])
        b = 0
        for x in range(2 ** len(vec_a)):
            _oracle_test_helper(vec_a, b, x)

    def test_two_qubits(self):
        vec_a = np.array([1, 0])
        b = 1
        for x in range(2 ** len(vec_a)):
            _oracle_test_helper(vec_a, b, x)

    def test_three_qubits(self):
        vec_a = np.array([0, 0, 0])
        b = 0
        for x in range(2 ** len(vec_a)):
            _oracle_test_helper(vec_a, b, x)

    def test_four_qubits(self):
        vec_a = np.array([1, 1, 1, 1])
        b = 1
        for x in range(2 ** len(vec_a)):
            _oracle_test_helper(vec_a, b, x)


@pytest.mark.skip(reason="Must add support for Forest connections in testing")
class TestBernsteinVazirani(object):
    def test_one_qubit_all_zeros(self):
        _bv_test_helper(np.array([0]), 0)

    def test_two_qubit_all_ones(self):
        _bv_test_helper(np.array([1, 1]), 1)

    def test_four_qubit_symmetric(self):
        _bv_test_helper(np.array([1, 0, 0, 1]), 1)

    def test_five_qubits_asymmetric(self):
        _bv_test_helper(np.array([0, 0, 1, 0, 1]), 0)


def _bv_test_helper(vec_a, b, trials=1):
    qubits = range(len(vec_a))
    ancilla = len(vec_a)
    oracle = oracle_function(vec_a, b, qubits, ancilla)
    bv_program = bernstein_vazirani(oracle, qubits, ancilla)
    cxn = api.SyncConnection()
    results = cxn.run_and_measure(bv_program, qubits, trials)
    for result in results:
        bv_a = result[::-1]
        assert bv_a == list(vec_a)


def _oracle_test_helper(vec_a, b, x, trials=1):
    qubits = range(len(vec_a))
    ancilla = len(vec_a)

    cxn = api.SyncConnection()
    bitstring = np.binary_repr(x, len(qubits))
    p = pq.Program()

    for i in range(len(bitstring)):
        if bitstring[-1 - i] == '1':
            p.inst(X(i))

    oracle = oracle_function(vec_a, b, qubits, ancilla)
    p += oracle
    results = cxn.run_and_measure(p, [ancilla], trials)
    a_dot_x = np.binary_repr(int(''.join(list(map(str, vec_a))), 2) & x).count("1")
    expected = (a_dot_x + b) % 2
    for result in results:
        y = result[0]
        assert y == expected


# if __name__ == "__main__":
#     import pyquil.api as api
#
#     # ask user to input the value for a
#     bitstring = input("Give a bitstring representation for the vector a: ")
#     while not (all([num in ('0', '1') for num in bitstring])):
#         print("The bitstring must be a string of ones and zeros.")
#         bitstring = input(
#             "Give a bitstring representation for the vector a: ")
#     vec_a = np.array(list(map(int, bitstring)))
#
#     # ask user to input the value for b
#     b = int(input("Give a single bit for b: "))
#     while b not in {0, 1}:
#         print("b must be either 0 or 1")
#         b = int(input("Give a single bit for b: "))
#
#     qvm = api.SyncConnection()
#     qubits = range(len(vec_a))
#     ancilla = len(vec_a)
#
#     oracle = oracle_function(vec_a, b, qubits, ancilla)
#
#     a, b, bv_program = run_bernstein_vazirani(qvm, oracle, qubits, ancilla)
#     bitstring_a = "".join(list(map(str, a)))
#     print("-----------------------------------")
#     print("The bitstring a is given by: ", bitstring)
#     print("b is given by: ", b)
#     print("-----------------------------------")
#     if input("Show Program? (y/n): ") == 'y':
#         print("----------Quantum Programs Used----------")
#         print("Program to find a given by: ")
#         print(bv_program)
#         print("Program to find b given by: ")
#         print(oracle)
