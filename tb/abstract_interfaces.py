"""
The module contains abstract interfaces of the classes.
The interfaces are aimed to be schemas for further classes implementations.
Following these schemas will ensure compatibility of the code with the entire project.
"""
from abc import ABCMeta, abstractmethod
from future.utils import with_metaclass
import numpy as np


class AbstractStructureDesigner(with_metaclass(ABCMeta, object)):
    """
    The class builds the atomic structure represented by a list of atoms
    and their neighbouring.
    """

    def __init__(self):

        self._nn_distance = None
        self._kd_tree = None

    def _get_neighbours(self, query):

        if isinstance(query, list) or isinstance(query, np.ndarray):
            ans = self._kd_tree.query(query,
                                      k=25,
                                      distance_upper_bound=self._nn_distance)
        elif isinstance(query, int):

            query = list(self.atom_list.items())[query][1]

            if self._kd_tree.data.shape[1] > 3:
                query = np.append(query, 0)

            ans = self._kd_tree.query(query,
                                      k=25,
                                      distance_upper_bound=self._nn_distance)
        elif isinstance(query, str):
            ans = self._kd_tree.query(self.atom_list[query],
                                      k=25,
                                      distance_upper_bound=self._nn_distance)
        else:
            raise TypeError('Wrong input type for query')

        return ans

    @abstractmethod
    def get_neighbours(self, query):
        pass

    @property
    @abstractmethod
    def atom_list(self):
        pass


class AbstractBasis(with_metaclass(ABCMeta, object)):
    """
    The class contains information about sets of quantum numbers and
    dimensionality of the Hilbert space.
    It is also equipped with the member functions translating quantum numbers
    into a raw index and vise versa.
    """

    @abstractmethod
    def qn2ind(self, qn):
        """
        The member function trasform a dictionary of quantum numbers into a matrix index

        :param qn:
        :type qn:

        :return ind:   index
        :rtype:        int
        """
        pass

    @abstractmethod
    def ind2qn(self, ind):
        """
        The member function trasform a dictionary of quantum numbers into a matrix index

        :param ind:    index
        :type ind:     int

        :return qn:
        :rtype:
        """
        pass

    @property
    @abstractmethod
    def orbitals_dict(self):
        pass
