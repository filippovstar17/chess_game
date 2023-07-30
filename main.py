from chess_items import *


pg.display.set_caption("Шахматы")  # имя окна
clock = pg.time.Clock()  # создание таймера для отслеживания кол-ва кадров в секунду (FPS)
infoObject = pg.display.Info()  # получение информации об экране
screen = pg.display.set_mode((infoObject.current_w, infoObject.current_h))  # создание родительского экрана с размерами
screen.fill(BACKGROUND)  # заполнение заднего фона цветом

chessboard = Chessboard(screen, 8, 80)  # создание объекта класса Chessboard

run = True  # переменная, отвечающая за выполнение основного цикла событий
while run:
    """Основной цикл событий."""
    clock.tick(FPS)
    for event in pg.event.get():
        # если нажали на крестик
        if event.type == pg.QUIT:
            pg.quit()
            run = False
        # если нажата клавиша(-и) мыши
        if event.type == pg.MOUSEBUTTONDOWN:
            chessboard.btn_down(event.button, event.pos)
        # если отпущена клавиша(-и) мыши
        if event.type == pg.MOUSEBUTTONUP:
            chessboard.btn_up(event.button, event.pos)
        # если передвигаем мышь
        if event.type == pg.MOUSEMOTION:
            chessboard.drag(event.pos)
        # если нажата клавиша(-и) на клавиатуре
        if event.type == pg.KEYDOWN:
            run = chessboard.key_down(event)  # если нажата клавиша ESC, закрываем игру
        # если отпущена клавиша(-и) на клавиатуре
        if event.type == pg.KEYUP:
            chessboard.key_up(event)