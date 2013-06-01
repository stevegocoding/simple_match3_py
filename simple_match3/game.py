__author__ = 'magkbdev'

import component
from utils import State


class BoardComponent(component.Component):
    """
    Contains and manages all the cells in this board
    """

    def __init__(self):
        self._cells_list = []


class CellComponent(component.Component):

    def __init__(self, board, cell_x, cell_y, type):
        self._board = board
        self._cell_x = cell_x
        self._cell_y = cell_y
        self._type = type


class PieceComponent(component.Component):

    """
    The piece represents all the objects that is located in the board and
    respecting the coordinate system defined by the board and cells. Also
    they can be eliminated when there is a match-3.
    """

    def __init__(self, cell, type):
        self._owner_cell = cell
        self._type = type
        self._state = State()


class BoardRenderComponent(component.Component):
    pass


class PieceRenderComponent(component.Component):

    def __init__(self):
        pass


