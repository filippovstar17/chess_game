import pygame as pg
from game_config import *


class Piece(pg.sprite.Sprite):
    """Класс, описывающий шахматную фигуру."""
    def __init__(self, cell_size: int, color: str, field_name: str, file_posfix: str):
        """Конструктор инициализации."""
        super().__init__()
        picture = pg.image.load(PIECE_PATH + color + file_posfix).convert_alpha()
        self.image = pg.transform.scale(picture, (cell_size, cell_size))
        self.rect = self.image.get_rect()
        self._color = color
        self.field_name = field_name
        self.__sound = pg.mixer.Sound(MOVE_SOUND)

    def move_to_cell(self, cell):
        """Перемещает фигуру в ячейку."""
        if self.field_name != cell.field_name:
            self.field_name = cell.field_name
            self.__sound.play()
        self.rect = cell.rect.copy()


class King(Piece):
    """Класс наследник фигуры, описывающий Короля."""
    def __init__(self, cell_size: int, color: str, field: str):
        """Конструктор инициализации."""
        super().__init__(cell_size, color, field, 'K.png')


class Queen(Piece):
    """Класс наследник фигуры, описывающий Королеву."""
    def __init__(self, cell_size: int, color: str, field: str):
        """Конструктор инициализации."""
        super().__init__(cell_size, color, field, 'Q.png')


class Rook(Piece):
    """Класс наследник фигуры, описывающий Ладью."""
    def __init__(self, cell_size: int, color: str, field: str):
        """Конструктор инициализации."""
        super().__init__(cell_size, color, field, 'R.png')


class Bishop(Piece):
    """Класс наследник фигуры, описывающий Слона."""
    def __init__(self, cell_size: int, color: str, field: str):
        """Конструктор инициализации."""
        super().__init__(cell_size, color, field, 'B.png')


class Knight(Piece):
    """Класс наследник фигуры, описывающий Коня."""
    def __init__(self, cell_size: int, color: str, field: str):
        """Конструктор инициализации."""
        super().__init__(cell_size, color, field, 'N.png')


class Pawn(Piece):
    """Класс наследник фигуры, описывающий Пешку."""
    def __init__(self, cell_size: int, color: str, field: str):
        """Конструктор инициализации."""
        super().__init__(cell_size, color, field, 'P.png')
