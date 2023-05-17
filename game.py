from random import randint

class BoardException(Exception): 
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"

class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"

class BoardWrongShipException(BoardException):
    pass

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'Dot({self.x}, {self.y})'

class Ship:

    def __init__(self, length, start_dot_ship, orientation):
        self.length = length
        self.start_dot_ship = start_dot_ship
        self.orientation = orientation
        self.health = length
    @property
    def dots(self):
        ship_dots = []
        for i in range(self.length):
            cur_x = self.start_dot_ship.x
            cur_y = self.start_dot_ship.y
            if self.orientation == 0:
                cur_x += i
            elif self.orientation == 1:
                cur_y += i
            ship_dots.append(Dot(cur_x, cur_y))
        return ship_dots

    def shooten(self,shot):
        return shot in self.dots

class Board:

    def __init__(self, hid=False, size=6):
        self.hid = hid
        self.size = size
        self.lost_ships = 0
        self.field = [["0"] * size for _ in range(size)]
        self.busy = []
        self.ships = []

    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"
        if self.hid:
            res = res.replace("■", "O")
        return res

    def out(self,d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not self.out(cur) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = '.'
                    self.busy.append(cur)

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def shot(self,d):
        if self.out(d):
            raise BoardOutException()
        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if ship.shooten(d):
                ship.health -= 1
                self.field[d.x][d.y] = 'X'
                if ship.health == 0:
                    self.contour(ship,verb=True)
                    self.lost_ships += 1
                    print(f'Вы уничтожили {ship.length}-палубный корабль')
                    return False
                else:
                    print('Корабль ранен')
                    return False
            self.field[d.x][d.y] = '.'
            print('Вы промазали')
            return False

    def begin(self):
        self.busy = []

class Player:

    def __init__(self, board, enemy_board):
        self.board = board
        self.enemy_board = enemy_board

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy_board.shot(target)
                return repeat
            except BoardException as e:
                print(e)

class AI(Player):

    def ask(self):
        d = Dot(randint(0,5), randint(0, 5))
        print(f"Ход компьютера: {d.x+1} {d.y+1}")
        return d

class User(Player):

    def ask(self):
        while True:
            cords = input('Введите свой ход (2 числа от 1 до 6): ').split()
            if len(cords) != 2:
                print('Введите 2 числа')
                continue
            x, y = cords
            if not (x.isdigit()) or not (y.isdigit()):
                print('Введите числа!')
                continue
            x, y = int(x), int(y)
            return Dot(x-1, y-1)

class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def try_board(self):
        lens = [3,2,2,1,1,1,1]
        board = Board(size = self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(l, Dot(randint(0,self.size),randint(0,self.size)), randint(0,1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def welcome(self):
        print('Игра "Морской бой"')
        print('Чтобы сделать ход введите 2 числа через пробел')
        print('Первое число - номер строки')
        print('Второе число - номер столбца')
        print()

    def loop(self):
        num = 0
        while True:
            print()
            print("Доска игрока:")
            print(self.us.board)
            print()
            print("Доска компьютера:")
            print(self.ai.board)
            print()
            if num % 2 == 0:
                print("Ходит игрок!")
                repeat = self.us.move()
            else:
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.lost_ships == 7:
                print()
                print("Игрок выиграл!")
                break

            if self.us.board.lost_ships == 7:
                print()
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.welcome()
        self.loop()

g = Game()
g.start()





















