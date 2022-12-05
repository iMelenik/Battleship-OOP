import random
from random import randint, choice


class Ship:
    def __init__(self, length, tp=1, x=None, y=None):
        """length - длина корабля (число палуб: целое значение: 1, 2, 3 или 4);
        tp - ориентация корабля (1 - горизонтальная; 2 - вертикальная).
        x, y - координаты начала расположения корабля (целые числа);"""
        self._length = length
        self._tp = tp
        self._x = x
        self._y = y
        self._is_move = True  # может ли корабль двигаться
        self._cells = [1] * self._length  # 1 - клетки корабля "на плаву", 2 - подбита

    def __setattr__(self, key, value):
        if key == '_length':
            if value not in (1, 2, 3, 4):
                raise ValueError(f"Длина корабля может быть от 1-й до 4-х ячеек")
        elif key == '_tp':
            if value not in (1, 2):
                raise ValueError(f"Ориентация корабля может быть: 1 - горизонтальная; 2 - вертикальная)")
        elif key in ('_x', '_y'):
            if value:
                if type(value) != int or value < 0:
                    raise ValueError(f"Координата {key} не может быть меньше 0")
        return object.__setattr__(self, key, value)

    def set_start_coords(self, x, y):
        self._x = x
        self._y = y

    def get_start_coords(self):
        return self._x, self._y

    def get_end_coords(self):
        return (self._x + self._length - 1, self._y) if self._tp == 1 else (self._x, self._y + self._length - 1)

    def move(self, go):
        """Движение корабля вперед или назад"""
        if self._is_move:
            x, y = self.get_start_coords()
            if self._tp == 1:  # двигаемся по X
                self.set_start_coords(x + 1 * go, y)
            elif self._tp == 2:  # двигаемся по Y
                self.set_start_coords(x, y + 1 * go)

    def is_collide(self, ship):
        """Проверка на столкновение с другим кораблем ship (столкновением считается,
        если другой корабль или пересекается с текущим или просто соприкасается,
         в том числе и по диагонали); метод возвращает True, если столкновение есть"""
        x11, y11 = self.get_start_coords()
        x12, y12 = self.get_end_coords()
        points1 = set((x, y) for x in range(x11 - 1, x12 + 2)
                      for y in range(y11 - 1, y12 + 2))
        if ship.get_start_coords() != (None, None):  # если заданы координаты
            x21, y21 = ship.get_start_coords()
            x22, y22 = ship.get_end_coords()
            points2 = set((x, y) for x in range(x21, x22 + 1)
                          for y in range(y21, y22 + 1))
            if points1 & points2:
                return True
        return False

    def is_out_pole(self, size):
        """Проверка на выход корабля за пределы игрового поля (size - размер игрового поля);
        возвращается булево значение True, если корабль вышел из игрового поля"""
        x1, y1 = self.get_start_coords()
        x2, y2 = self.get_end_coords()
        if 0 <= x1 < size and 0 <= y1 < size and 0 <= x2 < size and 0 <= y2 < size:
            return False
        return True

    def is_alive(self):
        return any(map(lambda x: x == 1, self._cells))

    def area(self):
        """Возвращает set из tuple координат, занимаемых кораблем"""
        width = self._length if self._tp == 1 else 1
        height = self._length if self._tp == 2 else 1
        area = {(x, y) for x in range(self._x, self._x + width) for y in range(self._y, self._y + height)}
        return area

    def get_shot(self, coords):
        """Принимает глобальные координаты, регистрирует попадание по кораблю"""
        self._is_move = False
        tp = 0 if self._tp == 1 else 1
        pos = abs(self.get_start_coords()[tp] - coords[tp])
        self._cells[pos] = 2
        if not self.is_alive():
            print("Потоплен")

    def __getitem__(self, indx):
        return self._cells[indx]

    def __setitem__(self, indx, value):
        if value not in (1, 2):
            raise ValueError("Возможные значения: 1 - клетка корабля 'на плаву', 2 - подбита")
        self._cells[indx] = value


class GamePole:
    def __init__(self, size=10):
        self._size = size
        self._ships = []
        self._pole = [[0 for _ in range(self._size)] for _ in range(self._size)]

    def init(self):
        """Создаем поле и корабли: однопалубных - 4; двухпалубных - 3;
        трехпалубных - 2; четырехпалубный - 1 со случайной ориентацией"""
        self._ships = [Ship(4, randint(1, 2))] + \
                      [Ship(3, randint(1, 2)) for _ in range(2)] + \
                      [Ship(2, randint(1, 2)) for _ in range(3)] + \
                      [Ship(1, randint(1, 2)) for _ in range(4)]

        """Расстановка на игровом поле со случайными координатами так,
        чтобы корабли не пересекались между собой, в т.ч. по диагонали"""
        planted = 0
        while planted < len(self._ships):
            curr_ship = self._ships[planted]
            curr_ship.set_start_coords(randint(0, self._size - 1), randint(0, self._size - 1))
            if self.__is_invalid_ship_state(curr_ship):
                pass
            else:
                self.__set_values(curr_ship)
                planted += 1

    def __is_invalid_ship_state(self, curr_ship):
        """True если корабль выходит за поле или пересекается с другими кораблями"""
        return curr_ship.is_out_pole(self._size) or \
               any(curr_ship.is_collide(i) for i in self._ships if i != curr_ship)

    def __set_values(self, curr_ship):
        x1, y1 = curr_ship.get_start_coords()
        x2, y2 = curr_ship.get_end_coords()

        i = 0
        for y in range(y1, y2 + 1):
            for x in range(x1, x2 + 1):
                self._pole[y][x] = curr_ship[i]
                i += 1

    def get_ships(self):
        return self._ships

    def move_ships(self):
        """Перемещает каждый корабль из коллекции _ships на одну клетку
        (случайным образом вперед или назад) в направлении ориентации корабля;
        если перемещение в выбранную сторону невозможно (другой корабль или
        пределы игрового поля), то попытаться переместиться в противоположную сторону,
        иначе (если перемещения невозможны), оставаться на месте"""
        for curr_ship in self._ships:
            x01, y01 = curr_ship.get_start_coords()  # первоначальные координаты начала
            x02, y02 = curr_ship.get_end_coords()  # первоначальные координаты конца
            go = choice([-1, 1])
            try:
                curr_ship.move(go)
            except ValueError:
                continue
            else:
                if self.__is_invalid_ship_state(curr_ship):
                    curr_ship.move(-go)
                else:
                    self._pole[y01][x01] = 0
                    self._pole[y02][x02] = 0
                    self.__set_values(curr_ship)

    def show(self):
        for line in self._pole:
            for i in line:
                print('x' if i == 0 or i == 1 else '*', end=' ')
            print()

    def get_pole(self):
        return tuple(tuple(i for i in line) for line in self._pole)


class SeaBattle:
    """Битва с компьютером"""
    SIZE_GAME_POLE = 10
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self):
        self.player_pole = GamePole(self.SIZE_GAME_POLE)
        self.player_pole.init()
        self.computer_pole = GamePole(self.SIZE_GAME_POLE)
        self.computer_pole.init()
        self.play()

    def __player_turn(self):
        print("Поле врага:")
        self.computer_pole.show()
        print("Ваш ход. Введите координаты (столбец строка) от 0 до 9:")
        shoot_coords = self.__shoot_coord_validaror(input())
        self.shoot('player', shoot_coords, self.computer_pole)

    def __shoot_coord_validaror(self, coords: str):
        try:
            coords = tuple(map(int, coords.split()))
        except ValueError:
            raise ValueError("Введено не целочисленное значение.")
        for coord in coords:
            if not 0 <= coord < self.SIZE_GAME_POLE:
                raise ValueError("Значение вне пределов поля.")
        return coords

    def __computer_turn(self):
        aviable_coords = [(x, y) for x in range(self.SIZE_GAME_POLE) for y in range(self.SIZE_GAME_POLE)]
        coords = choice(aviable_coords)
        aviable_coords.remove(coords)
        self.shoot('computer', coords, self.player_pole)

    @staticmethod
    def shoot(player, coords, pole):
        for ship in pole.get_ships():
            if coords in ship.area():
                if player == 'player':
                    print("Есть попадание!")
                ship.get_shot(coords)
                break

    def play(self):
        while True:
            self.__player_turn()
            if self.__pole_destroyed(self.computer_pole):
                print("Вы победили!")
                break
            self.computer_pole.move_ships()

            self.__computer_turn()
            if self.__pole_destroyed(self.player_pole):
                print("Вы проиграли.")
                break
            self.player_pole.move_ships()

    @staticmethod
    def __pole_destroyed(pole):
        return not any(ship.is_alive() for ship in pole.get_ships())


SeaBattle()
