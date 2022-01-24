"""
Unit and regression test for the occuprob package.
"""
import pytest

import numpy as np

from occuprob.superpositions import ClassicalHarmonicSA, QuantumHarmonicSA


def test_classical_harmonic():
    """Tests the asymptotic behaviour of the occupation probability for a
    ficticious landscape with two minima. The occupation probability is
    calculated using the corresponding canonical partition funcion under
    the classical harmonic superposition approximation"""

    energy = np.array([0.0, 0.1])
    frequencies = np.array([[1.0, 1.0, 1.0], [2.0, 1.0, 1.0]])
    symmetry = np.array([3.0, 1.0])
    temperature = np.array([0.0, np.inf])
    landscape = ClassicalHarmonicSA(energy, frequencies, symmetry)

    expected_probability = np.array([[1.0, 0.4], [0.0, 0.6]])
    calculated_probability = landscape.calc_probability(temperature)

    print(calculated_probability)

    assert pytest.approx(calculated_probability) == expected_probability


def test_quantum_harmonic():
    """Tests the asymptotic behaviour of the occupation probability for a
    ficticious landscape with two minima. The occupation probability is
    calculated using the corresponding canonical partition funcion under
    a quantum harmonic superposition approximation"""

    energy = np.array([0.0, 0.1])
    frequencies = np.array([[1.0, 1.0], [3.0, 1.0]])
    symmetry = np.array([1.0, 1.0])
    multiplicity = np.array([1.0, 1.0])
    temperature = np.array([0.0, np.inf])
    landscape = QuantumHarmonicSA(energy, frequencies, symmetry, multiplicity)

    expected_probability = np.array([[1.0, 0.75], [0.0, 0.25]])
    calculated_probability = landscape.calc_probability(temperature)

    assert pytest.approx(calculated_probability) == expected_probability
