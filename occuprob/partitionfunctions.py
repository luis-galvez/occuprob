""" Routines to calculate partition functions. """

# MIT License

# Copyright (c) 2021-2022 Luis Gálvez

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from abc import ABC, abstractmethod

import numpy as np

from occuprob.utils import calc_beta
from occuprob.utils import calc_exponent
from occuprob.utils import calc_geometric_mean

# Planck's constant in eV/THz
H = 4.135667696e-3


class PartitionFunction(ABC):
    """
    An abstract class that represents a partition function.

    ...

    Methods
    -------
    calc_partition_function(temperature):
        Calculates the partition function in the given temperature range.
    """

    @abstractmethod
    def calc_part_func(self, temperature):
        """
        Abstract method to calculate the partition function in the given
        temperature range.

        Parameters
        ----------
        temperature : :obj:`numpy.ndarray`
            A 1D array of size M containing the temperature values in K.

        Returns
        -------
        partition_function: :obj:`numpy.ndarray`
            A 2D array of shape (N, M) contaning the calculated partition
            functions for each of the N isomers in the given temperature range.
        """

    @abstractmethod
    def calc_part_func_w(self, temperature):
        """
        Abstract method to calculate the derivative of the partition function
        with respect to Beta divided by the partition function (W) multiplied
        by Beta.

        Parameters
        ----------
        temperature : :obj:`numpy.ndarray`
            A 1D array of size M containing the temperature values in K.

        Returns
        -------
        part_func_w: :obj:`numpy.ndarray`
            A 2D array of shape (N, M) contaning the calculated derivatives
            of the partition function for each of the N isomers, in the given
            temperature range.
        """

    @abstractmethod
    def calc_part_func_v(self, temperature):
        """
        Abstract method to calculate the derivative of W with respect to Beta (V)
        multiplied by Beta squared.

        Parameters
        ----------
        temperature : :obj:`numpy.ndarray`
            A 1D array of size M containing the temperature values in K.

        Returns
        -------
        part_func_v: :obj:`numpy.ndarray`
            A 2D array of shape (N, M) contaning the calculated derivatives
            of W for each of the N isomers, in the given temperature range.
        """


class ElectronicPF(PartitionFunction):
    """
    Represents a canonical electronic partition function.

    ...
    potential_energy : :obj:`numpy.ndarray`
        A 1D array containing the energy values (in eV) of each of the N isomers.
    spin_multiplicity : :obj:`numpy.ndarray`
        A 1D array containing the spin multiplicity corresponding to each of
        the N isomers.

    Methods
    -------
    calc_partition_function(temperature):
        Calculates the canonical electronic partition function in the given
        temperature range.
    """

    def __init__(self, potential_energy, spin_multiplicity):
        self.potential_energy = potential_energy
        self.spin_multiplicity = spin_multiplicity

        self.relative_energy = potential_energy - np.amin(potential_energy)

    def calc_part_func(self, temperature):
        """
        Calculates the electronic canonical partition function in the given
        temperature range.

        Parameters
        ----------
        temperature : :obj:`numpy.ndarray`
            A 1D array of size M containing the temperature values in K.

        Returns
        -------
        partition_function: :obj:`numpy.ndarray`
            A 2D array of shape (N, M) contaning the calculated partition
            functions for each of the N isomers in the given temperature range.
        """
        exponent = calc_exponent(self.relative_energy, temperature)
        partition_function = np.exp(-exponent)
        partition_function *= self.spin_multiplicity[:, None]

        return partition_function

    def calc_part_func_w(self, temperature):
        """
        Method to calculate the derivative of the partition function
        with respect to Beta divided by the partition function (W).

        Parameters
        ----------
        temperature : :obj:`numpy.ndarray`
            A 1D array of size M containing the temperature values in K.

        Returns
        -------
        part_func_w: :obj:`numpy.ndarray`
            A 2D array of shape (N, M) contaning the calculated derivatives
            of the partition function for each of the N isomers, in the given
            temperature range.
        """
        beta = calc_beta(temperature)
        part_func_w = -np.multiply(beta, self.relative_energy[:, None],
                                   where=self.relative_energy[:, None] != 0.,
                                   out=np.zeros([self.relative_energy.size,
                                                 beta.size]))

        return part_func_w

    def calc_part_func_v(self, temperature):
        """
        Method to calculate the derivative of W with respect to Beta (V)
        multiplied by Beta squared.

        Parameters
        ----------
        temperature : :obj:`numpy.ndarray`
            A 1D array of size M containing the temperature values in K.

        Returns
        -------
        part_func_v: :obj:`numpy.ndarray`
            A 2D array of shape (N, M) contaning the calculated derivatives
            of W for each of the N isomers, in the given temperature range.
        """

        part_func_v = np.zeros_like(self.calc_part_func_w(temperature))

        return part_func_v


class RotationalPF(PartitionFunction):
    """
    Represents a canonical rotational  partition function in a high-temperature
    approximation.

    ...
    symmetry_order : :obj:`numpy.ndarray`
        A 1D array of size N containing the order of rotational subgroup of the
        point group symmetry of each isomer.
    moments : :obj:`numpy.ndarray`
        A 2D array of shape (N, 3) containing the principal moments of inertia
        of each isomer.

    Methods
    -------
    calc_partition_function(temperature):
        Calculates the rotational partition function in the given temperature
        range.
    """

    def __init__(self, symmetry_order, moments):
        self.symmetry_order = symmetry_order
        self.moments = np.where(moments > 0, moments, 1.)

    def calc_part_func(self, temperature):
        """
        Calculates the electronic canonical partition function in the given
        temperature range.

        Parameters
        ----------
        temperature : :obj:`numpy.ndarray`
            A 1D array of size M containing the temperature values in K.

        Returns
        -------
        partition_function: :obj:`numpy.ndarray`
            A 2D array of shape (N, M) contaning the calculated partition
            functions for each of the N isomers in the given temperature range.
        """
        moments_product = np.prod(self.moments, axis=1)[:, None]
        partition_function = moments_product * np.ones_like(temperature)
        partition_function /= self.symmetry_order[:, None]

        return partition_function

    def calc_part_func_w(self, temperature):
        """
        Method to calculate the derivative of the partition function
        with respect to Beta divided by the partition function (W).

        Parameters
        ----------
        temperature : :obj:`numpy.ndarray`
            A 1D array of size M containing the temperature values in K.

        Returns
        -------
        part_func_w: :obj:`numpy.ndarray`
            A 2D array of shape (N, M) contaning the calculated derivatives
            of the partition function for each of the N isomers, in the given
            temperature range.
        """
        part_func_w = -1.5 * np.ones([self.symmetry_order.size,
                                      temperature.size])

        return part_func_w

    def calc_part_func_v(self, temperature):
        """
        Method to calculate the derivative of W with respect to Beta (V)
        multiplied by Beta squared.

        Parameters
        ----------
        temperature : :obj:`numpy.ndarray`
            A 1D array of size M containing the temperature values in K.

        Returns
        -------
        part_func_v: :obj:`numpy.ndarray`
            A 2D array of shape (N, M) contaning the calculated derivatives
            of W for each of the N isomers, in the given temperature range.
        """
        part_func_v = -self.calc_part_func_w(temperature)

        return part_func_v


class ClassicalHarmonicPF(PartitionFunction):
    """
    Represents a canonical vibrational partition function in the classical
    harmonic approximation.

    ...
    frequencies : :obj:`numpy.ndarray`
        A 2D array of shape (N, D) containing the D frequency values (in THz) of
        each of the N isomers.

    Methods
    -------
    calc_partition_function(temperature):
        Calculates the vibrational partition function in the given
        temperature range.
    """

    def __init__(self, frequencies):
        self.frequencies = frequencies
        self.n_vib = frequencies.shape[1]  # Number of vibrational modes

    def calc_part_func(self, temperature):
        """
        Calculates the classical vibrational partition function in the given
        temperature range.

        Parameters
        ----------
        temperature : :obj:`numpy.ndarray`
            A 1D array of size M containing the temperature values in K.

        Returns
        -------
        partition_function: :obj:`numpy.ndarray`
            A 2D array of shape (N, M) contaning the calculated partition
            functions for each of the N isomers in the given temperature range.
        """

        frequencies_gmean = calc_geometric_mean(self.frequencies)

        partition_function = np.outer(np.power(frequencies_gmean, -self.n_vib),
                                      np.ones_like(temperature))

        return partition_function

    def calc_part_func_w(self, temperature):
        """
        Method to calculate the derivative of the partition function
        with respect to Beta divided by the partition function (W).

        Parameters
        ----------
        temperature : :obj:`numpy.ndarray`
            A 1D array of size M containing the temperature values in K.

        Returns
        -------
        part_func_w: :obj:`numpy.ndarray`
            A 2D array of shape (N, M) contaning the calculated derivatives
            of the partition function for each of the N isomers, in the given
            temperature range.
        """
        part_func_w = -self.n_vib * np.ones([self.frequencies.shape[0],
                                             temperature.size])

        return part_func_w

    def calc_part_func_v(self, temperature):
        """
        Method to calculate the derivative of W with respect to Beta (V)
        multiplied by Beta squared.

        Parameters
        ----------
        temperature : :obj:`numpy.ndarray`
            A 1D array of size M containing the temperature values in K.

        Returns
        -------
        part_func_v: :obj:`numpy.ndarray`
            A 2D array of shape (N, M) contaning the calculated derivatives
            of W for each of the N isomers, in the given temperature range.
        """
        part_func_v = -self.calc_part_func_w(temperature)

        return part_func_v


class QuantumHarmonicPF(PartitionFunction):
    """
    Represents a canonical vibrational partition function in the quantum
    harmonic approximation.

    ...
    frequencies : :obj:`numpy.ndarray`
        A 2D array of shape (N, D) containing the D frequency values (in THz) of
        each of the N isomers.

    Methods
    -------
    calc_partition_function(temperature):
        Calculates the vibrational partition function in the given
        temperature range.
    """

    def __init__(self, frequencies):
        self.frequencies = frequencies

    def calc_part_func(self, temperature):
        """
        Calculates the quantum vibrational partition function in the given
        temperature range.

        Parameters
        ----------
        temperature : :obj:`numpy.ndarray`
            A 1D array of size M containing the temperature values in K.

        Returns
        -------
        partition_function: :obj:`numpy.ndarray`
            A 2D array of shape (N, M) contaning the calculated partition
            functions for each of the N isomers in the given temperature range.
        """
        exponent = calc_exponent(0.5 * H * self.frequencies[:, :, None],
                                 temperature)
        partition_function = np.prod(0.5 / np.sinh(exponent), axis=1)

        return partition_function

    def calc_part_func_w(self, temperature):
        """
        Method to calculate the derivative of the partition function
        with respect to Beta divided by the partition function (W).

        Parameters
        ----------
        temperature : :obj:`numpy.ndarray`
            A 1D array of size M containing the temperature values in K.

        Returns
        -------
        part_func_w: :obj:`numpy.ndarray`
            A 2D array of shape (N, M) contaning the calculated derivatives
            of the partition function for each of the N isomers, in the given
            temperature range.
        """
        beta = calc_beta(temperature)
        exponent = calc_exponent(0.5 * H * self.frequencies[:, :, None],
                                 temperature)
        coth = 1. / np.tanh(exponent)

        aux_w = -0.5 * H * np.sum(self.frequencies[:, :, None] * coth, axis=1)
        part_func_w = np.multiply(beta**2, aux_w, where=temperature > 0,
                                  out=np.zeros_like(aux_w))

        return part_func_w

    def calc_part_func_v(self, temperature):
        """
        Method to calculate the derivative of W with respect to Beta (V)
        multiplied by Beta squared.

        Parameters
        ----------
        temperature : :obj:`numpy.ndarray`
            A 1D array of size M containing the temperature values in K.

        Returns
        -------
        part_func_v: :obj:`numpy.ndarray`
            A 2D array of shape (N, M) contaning the calculated derivatives
            of W for each of the N isomers, in the given temperature range.
        """
        beta = calc_beta(temperature)
        exponent = calc_exponent(0.5 * H * self.frequencies[:, :, None],
                                 temperature)
        csch = 0.5 / np.sinh(exponent)

        aux_v = np.sum((H * self.frequencies[:, :, None] * csch)**2, axis=1)
        part_func_v = np.multiply(beta**2, aux_v, where=temperature > 0,
                                  out=np.zeros_like(aux_v))

        return part_func_v
