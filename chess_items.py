from pieces import *
import pyperclip as clip
import board_data

pg.init()  # инициализация pygame
fnt_num = pg.font.SysFont(FNT_PATH, FNT_SIZE)  # шрифт


class Chessboard:
    """Основной класс шахмат."""

    def __init__(self, parent_surface: pg.Surface, cell_qty: int = CELL_QTY, cell_size: int = CELL_SIZE):
        """Конструктор, инициализирует атрибуты."""
        self.__screen = parent_surface  # экран - родительская поверхность
        self.__table = board_data.board  # начальная расстановка фигур
        self.__qty = cell_qty  # кол-во ячеек в строке (столбце) квадратного поля
        self.__size = cell_size  # размер ячейки
        self.__pieces_types = PIECES_TYPES  # раскодирующий словарь шахматной нотации Форсайта — Эдвардса (FEN)
        self.__all_cells = pg.sprite.Group()  # группа ячеек
        self.__all_white_pieces = pg.sprite.Group()  # группа белых шахматных фигур
        self.__all_black_pieces = pg.sprite.Group()  # группа черных шахматных фигур
        self.__all_areas = pg.sprite.Group()  # группа областей при клике ПКМ
        self.__pressed_cell = None  # кликнутая ячейка
        self.__picked_piece = None  # выбранная фигура
        self.__dragged_piece = None  # перетаскиваемая фигура
        self.__func_keys = [pg.K_LCTRL, pg.K_v, pg.K_RETURN, pg.K_BACKSPACE]  # список используемых кнопок клавиатуры
        self.__hotkey = {pg.K_LCTRL: False, pg.K_v: False}  # словарь активности сочетания клавиш (ctrl+v)
        self.__turn = True  # переменная, отвечающая за ход игрока (True - ход белых фигур, False - ход черных фигур)
        self.__prepare_music()  # запуск фоновой музыки
        self.__prepare_screen()  # загрузка заднего фона
        self.__draw_playboard()  # отрисовываем игровую доску
        self.__setup_board()
        self.__grand_update()

    def __prepare_music(self):
        """Запускает фоновую музыку."""
        pg.mixer.music.load(BACKGROUND_MUSIC)
        pg.mixer.music.play(-1)
        pg.mixer.music.set_volume(0.1)

    def __prepare_screen(self):
        """Загружает картинку заднего фона."""
        back_img = pg.image.load(IMG_PATH + WIN_BG_IMG)
        back_img = pg.transform.scale(back_img, (self.__screen.get_width(), self.__screen.get_height()))
        self.__screen.blit(back_img, (0, 0))

    def __draw_playboard(self):
        """Отрисовывает игровую доску."""
        total_width = self.__qty * self.__size
        num_fields = self.__create_num_fields()
        self.__all_cells = self.__create_all_cells()
        num_fields_depth = num_fields[0].get_width()
        playboard_view = pg.Surface((
            2 * num_fields_depth + total_width,
            2 * num_fields_depth + total_width
        ), pg.SRCALPHA).convert_alpha()

        back_img = pg.image.load(IMG_PATH + BOARD_BG_IMG)
        back_img = pg.transform.scale(back_img, (
            playboard_view.get_width(),
            playboard_view.get_height()
        ))
        playboard_view.blit(back_img, back_img.get_rect())

        playboard_view.blit(num_fields[0], (0, num_fields_depth))
        playboard_view.blit(num_fields[0], (num_fields_depth + total_width, num_fields_depth))
        playboard_view.blit(num_fields[1], (num_fields_depth, 0))
        playboard_view.blit(num_fields[1], (num_fields_depth, num_fields_depth + total_width))

        playboard_rect = playboard_view.get_rect()
        playboard_rect.x += (self.__screen.get_width() - playboard_rect.width) // 2
        playboard_rect.y += (self.__screen.get_height() - playboard_rect.height) // 4
        self.__screen.blit(playboard_view, playboard_rect)
        cells_offset = (
            playboard_rect.x + num_fields_depth,
            playboard_rect.y + num_fields_depth
        )
        self.__apply_offset_for_cells(cells_offset)
        self.__draw_input_box(playboard_rect)

    def __draw_input_box(self, board_rect: pg.Rect):
        """Отрисовывает, поле ввода схемы шахматных фигур в нотации FEN."""
        self.__inputbox = Inputbox(board_rect)
        self.__all_cells.add(self.__inputbox)

    def __create_num_fields(self):
        """Создаёт и возвращает поверхности с буквами и цифрами вдоль шахматной доски."""
        n_lines = pg.Surface((self.__qty * self.__size, self.__size // 3), pg.SRCALPHA).convert_alpha()  # letters
        n_rows = pg.Surface((self.__size // 3, self.__qty * self.__size), pg.SRCALPHA).convert_alpha()  # numbers
        for i in range(0, self.__qty):
            letter = fnt_num.render(LTRS[i], 1, WHITE)
            number = fnt_num.render(str(self.__qty - i), 1, WHITE)
            n_lines.blit(letter, (
                i * self.__size + (self.__size - letter.get_rect().width) // 2,  # X
                (n_lines.get_height() - letter.get_rect().height) // 2  # Y
            )
                         )
            n_rows.blit(number, (
                (n_rows.get_width() - letter.get_rect().width) // 2,  # X
                i * self.__size + (self.__size - number.get_rect().height) // 2  # Y
            )
                        )
        return n_rows, n_lines

    def __create_all_cells(self):
        """Создаёт и возвращает группу ячеек в которых будут располагаться шахматные фигуры."""
        group = pg.sprite.Group()
        is_even_qty = (CELL_QTY % 2 == 0)
        cell_color_index = 1 if is_even_qty else 0
        for y in range(self.__qty):
            for x in range(self.__qty):
                cell = Cell(
                    cell_color_index,
                    self.__size,
                    (x, y),
                    LTRS[x] + str(self.__qty - y)
                )
                group.add(cell)
                cell_color_index ^= True  # бинарное XOR
            cell_color_index = cell_color_index ^ True if is_even_qty else cell_color_index
        return group

    def __apply_offset_for_cells(self, offset):
        """Применяет смещение для каждой ячейки поля."""
        for cell in self.__all_cells:
            cell.rect.x += offset[0]
            cell.rect.y += offset[1]

    def __setup_board(self):
        """Расставляет фигуры по местам согласно изначально заданной схеме и добавляет их в группы спрайтов."""
        for j, row in enumerate(self.__table):
            for i, field_value in enumerate(row):
                if field_value != 0:
                    piece = self.__create_piece(field_value, (j, i))
                    if field_value[0].islower():
                        self.__all_black_pieces.add(piece)
                    else:
                        self.__all_white_pieces.add(piece)
        # TODO: optimize
        for piece in self.__all_black_pieces:
            for cell in self.__all_cells:
                if piece.field_name == cell.field_name:
                    piece.rect = cell.rect.copy()
        for piece in self.__all_white_pieces:
            for cell in self.__all_cells:
                if piece.field_name == cell.field_name:
                    piece.rect = cell.rect.copy()

    def __create_piece(self, piece_symbol: str, table_coord: tuple):
        """Создаёт и возвращает объекты классов фигур."""
        field_name = self.__to_field_name(table_coord)
        piece_tuple = self.__pieces_types[piece_symbol]
        classname = globals()[piece_tuple[0]]
        return classname(self.__size, piece_tuple[1], field_name)

    def __to_field_name(self, table_coord: tuple):
        """Возвращает имя ячейки по координатам таблицы."""
        return LTRS[table_coord[1]] + str(self.__qty - table_coord[0])

    def __get_cell(self, position: tuple):
        """Возвращает ячейку по координатам мыши."""
        for cell in self.__all_cells:
            if cell.rect.collidepoint(position):  # проверка попадания точки в прямоугольник
                return cell
        return None

    def __get_piece_on_cell(self, cell):
        """Возвращает шахматную фигуру, находящуюся в ячейке cell."""
        # TODO: optimize
        for piece in self.__all_black_pieces:
            if piece.field_name == cell.field_name:
                return piece
        for piece in self.__all_white_pieces:
            if piece.field_name == cell.field_name:
                return piece
        return None

    def drag(self, position: tuple):
        """Отображает перетаскиваемую фигуру на курсоре в пределах поля"""
        if self.__dragged_piece is not None:
            # TODO: calculate automatically
            if 393 < position[0] < 973 and 75 < position[1] < 652:  # пределы поля
                self.__dragged_piece.rect.center = position
                self.__grand_update()

    def btn_down(self, button_type: int, position: tuple):
        """Срабатывает при нажатии кнопок мыши."""
        self.__pressed_cell = self.__get_cell(position)
        if (self.__pressed_cell is not None) and self.__pressed_cell.field_name != 'inputbox':
            self.__inputbox.deactivate()
            self.__dragged_piece = self.__get_piece_on_cell(self.__pressed_cell)
        elif (self.__pressed_cell is not None) and self.__pressed_cell.field_name == 'inputbox':
            self.__pressed_cell = None
            self.__inputbox.activate()
        else:
            self.__inputbox.deactivate()

    def btn_up(self, button_type: int, position: tuple):
        """Срабатывает при отпускании кнопок мыши."""
        released_cell = self.__get_cell(position)
        # простой клик по шахматной доске
        if released_cell is None:
            released_cell = self.__pressed_cell
        if (released_cell is not None) and (released_cell == self.__pressed_cell):
            if button_type == 3:  # ПКМ
                self.__mark_cell(released_cell)
            if button_type == 1:  # ЛКМ
                self.__pick_cell(released_cell)
        # перетаскивание фигуры
        if self.__dragged_piece is not None:
            self.__dragged_piece.move_to_cell(released_cell)
            # удаляем фигуру при поедании
            colls = pg.sprite.groupcollide(self.__all_white_pieces, self.__all_black_pieces, not self.__turn,
                                           self.__turn)
            if self.__dragged_piece.field_name != self.__pressed_cell.field_name:
                self.__turn ^= True  # меняем ход
            self.__dragged_piece = None
        self.__grand_update()

    def __check_paste(self):
        """Проверяет на нажатие сочетания клавиш ctrl+v."""
        if self.__hotkey[pg.K_LCTRL] and self.__hotkey[pg.K_v]:
            self.__inputbox.put_char(clip.paste())
            return True
        else:
            return False

    def key_down(self, event):
        """Обрабатывает нажатие клавиш на клавиатуре."""
        run = True
        if event.key == pg.K_ESCAPE:
            return not run  # выход
        if self.__inputbox.active and event.key in self.__func_keys:
            if event.key == pg.K_LCTRL:
                self.__hotkey[pg.K_LCTRL] = True
                self.__check_paste()
            if event.key == pg.K_v:
                self.__hotkey[pg.K_v] = True
                if not self.__check_paste():
                    self.__inputbox.put_char(event.unicode)
            if event.key == pg.K_RETURN:
                self.__update_board_with_fen()
            if event.key == pg.K_BACKSPACE:
                self.__inputbox.pop_char()
        elif self.__inputbox.active:
            self.__inputbox.put_char(event.unicode)
        self.__grand_update()
        return run

    def key_up(self, event):
        """Обрабатывает отпускание клавиш на клавиатуре."""
        if event.key == pg.K_LCTRL:
            self.__hotkey[pg.K_LCTRL] = False
        if event.key == pg.K_v:
            self.__hotkey[pg.K_v] = False

    def __update_board_with_fen(self):
        """Обновляет расстановку шахматных фигур по нотации FEN."""
        empty_cells = 0
        piece_map = self.__inputbox.text.split('/')
        for r in range(len(self.__table)):
            index = 0
            for i in range(len(self.__table[r])):
                if empty_cells == 0:
                    try:
                        empty_cells = int(piece_map[r][index])
                        self.__table[r][i] = 0
                        empty_cells -= 1
                    except ValueError:
                        self.__table[r][i] = piece_map[r][index]
                    index += 1
                else:
                    self.__table[r][i] = 0
                    empty_cells -= 1
        self.__all_black_pieces.empty()
        self.__all_white_pieces.empty()
        self.__setup_board()
        self.__grand_update()

    def __mark_cell(self, cell):
        """Отмечает ячейку зеленым кружком, при нажатии ПКМ."""
        if not cell.mark:
            mark = Area(cell)
            self.__all_areas.add(mark)
        else:
            for area in self.__all_areas:
                if area.field_name == cell.field_name:
                    area.kill()
                    break
        cell.mark ^= True

    def __pick_cell(self, cell):
        """Срабатывает при нажатии ЛКМ, активирует ячейку, либо перемещает фигуру если ячейка уже активна."""
        self.__unmark_all_cells()
        if self.__picked_piece is None:
            piece = self.__get_piece_on_cell(cell)
            if piece is not None:
                pick = Area(cell, False)
                self.__all_areas.add(pick)
                self.__picked_piece = piece
        else:
            first_picked_piece_field_name = self.__picked_piece.field_name
            self.__picked_piece.move_to_cell(cell)
            # удаляем фигуру при поедании
            colls = pg.sprite.groupcollide(self.__all_white_pieces, self.__all_black_pieces, not self.__turn,
                                           self.__turn)
            if first_picked_piece_field_name != cell.field_name:  # если ход сделан, а не отменён
                self.__turn ^= True  # меняем ход
            self.__picked_piece = None

    def __unmark_all_cells(self):
        """Удаляет все отметки на ячейках."""
        self.__all_areas.empty()
        for cell in self.__all_cells:
            cell.mark = False

    def __grand_update(self):
        """Перерисовывает все спрайты, обновляет экран."""
        self.__all_cells.draw(self.__screen)
        self.__all_areas.draw(self.__screen)
        self.__all_black_pieces.draw(self.__screen)
        self.__all_white_pieces.draw(self.__screen)
        pg.display.update()


class Inputbox(pg.sprite.Sprite):
    """Класс, описывающий поле ввода для нотации FEN."""
    def __init__(self, board_rect: pg.Rect):
        """Конструкор инициализации."""
        super().__init__()
        x, y = board_rect.x, board_rect.y
        width, height = board_rect.width, board_rect.height
        self.field_name = 'inputbox'
        self.text = ''
        self.active = False
        self.image = pg.Surface((width, INPUT_SIZE), pg.SRCALPHA).convert_alpha()
        self.image.fill(BLACK)
        pg.draw.rect(self.image, WHITE, (0, 0, width, INPUT_SIZE), 2)
        self.rect = pg.Rect(x, 2 * y + height, width, INPUT_SIZE)

    def activate(self):
        """Активирует поле ввода."""
        self.active = True
        pg.draw.rect(self.image, INPUT_FONT_COLOR, (0, 0, self.rect.width, self.rect.height), 2)

    def deactivate(self):
        """Деактивирует поле ввода."""
        self.active = False
        pg.draw.rect(self.image, WHITE, (0, 0, self.rect.width, self.rect.height), 2)

    def put_char(self, char: str):
        """Вставляет символ."""
        self.text += char
        self.__update_text()

    def pop_char(self):
        """Удаляет символ."""
        self.text = self.text[:-1]
        self.__update_text()

    def __update_text(self):
        """Обновляет текст."""
        self.image.fill(BLACK)
        pg.draw.rect(self.image, INPUT_FONT_COLOR, (0, 0, self.rect.width, self.rect.height), 2)
        fen_text = fnt_num.render(self.text, 1, INPUT_FONT_COLOR)
        self.image.blit(fen_text, (9, 9))


class Cell(pg.sprite.Sprite):
    """Класс, описывающий ячейки игрового поля."""
    def __init__(self, color_index: int, size: int, coords: tuple, name: str):
        """Конструктор инициализации."""
        super().__init__()
        x, y = coords
        self.color = color_index
        self.field_name = name
        self.image = pg.image.load(IMG_PATH + COLORS[color_index])
        self.image = pg.transform.scale(self.image, (size, size))
        self.rect = pg.Rect(x * size, y * size, size, size)
        self.mark = False


class Area(pg.sprite.Sprite):
    """Класс, описывающий отметку ячеек."""
    def __init__(self, cell: Cell, type_of_area: bool = True):
        """Конструктор инициализации."""
        super().__init__()
        coords = (cell.rect.x, cell.rect.y)
        area_size = (cell.rect.width, cell.rect.height)
        if type_of_area:
            # отмечает ячейку зеленым кружком при нажатии ПКМ
            picture = pg.image.load(IMG_PATH + 'mark.png').convert_alpha()
            self.image = pg.transform.scale(picture, area_size)
        else:
            # выбирает ячейку с фигурой при нажатии ЛКМ
            self.image = pg.Surface(area_size).convert_alpha()
            self.image.fill(ACTIVE_CELL_COLOR)
        self.rect = pg.Rect(coords, area_size)
        self.field_name = cell.field_name
