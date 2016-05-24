#!/usr/bin/env python2
import sys
from random import randrange, choice
from math import fabs
from collections import deque

from PyQt4 import QtGui, QtCore


class Game(QtGui.QWidget):
    def __init__(self):
        super(Game, self).__init__()
        self.auto = True
        self.board_size = 20
        self.size = 300
        self.grid_size = self.size / self.board_size
        self.speed = 100
        self.set_directions = ("UP", "DOWN", "LEFT", "RIGHT")
        self.initUI()

    def initUI(self):
        self.newGame()
        self.setFixedSize(self.size, self.size)
        self.show()

    def paintEvent(self, event):
        self.setWindowTitle('score:'+ str(self.score))
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawFood(qp)
        self.drawSnake(qp)
        if self.isOver:
            self.gameOver(event, qp)
        qp.end()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()

        if self.auto:
            return

        if not self.isOver:
            if e.key() == QtCore.Qt.Key_Up and self.lastKeyPress != 'UP' and self.lastKeyPress != 'DOWN':
                self.set_direction("UP")
                self.lastKeyPress = 'UP'
            elif e.key() == QtCore.Qt.Key_Down and self.lastKeyPress != 'DOWN' and self.lastKeyPress != 'UP':
                self.set_direction("DOWN")
                self.lastKeyPress = 'DOWN'
            elif e.key() == QtCore.Qt.Key_Left and self.lastKeyPress != 'LEFT' and self.lastKeyPress != 'RIGHT':
                self.set_direction("LEFT")
                self.lastKeyPress = 'LEFT'
            elif e.key() == QtCore.Qt.Key_Right and self.lastKeyPress != 'RIGHT' and self.lastKeyPress != 'LEFT':
                self.set_direction("RIGHT")
                self.lastKeyPress = 'RIGHT'
        elif e.key() == QtCore.Qt.Key_Space:
            self.newGame()

    def newGame(self):
        self.score = 0
        self.head_x = 0
        self.head_y = 0
        self.cells = []
        self.lastKeyPress = 'RIGHT'
        self.timer = QtCore.QBasicTimer()
        self.snakeCells = [[self.head_x, self.head_y], [self.head_x-1, self.head_y], [self.head_x-2, self.head_y]]
        self.food_x = 0
        self.food_y = 0
        self.path = []
        self.isOver = False
        self.FoodPlaced = False
        self.placeFood()
        self.start()
        
    def real_xy(self, x, y):
        return x * self.grid_size, y * self.grid_size


    def start(self):
        self.timer.start(self.speed, self)
        self.update()

    def set_direction(self, dir):
        if (dir == "DOWN" and self.checkStatus(self.head_x, self.head_y+1)):
            self.head_y += 1
            self.repaint()
            self.snakeCells.insert(0 ,[self.head_x, self.head_y])
        elif (dir == "UP" and self.checkStatus(self.head_x, self.head_y-1)):
            self.head_y -= 1
            self.repaint()
            self.snakeCells.insert(0 ,[self.head_x, self.head_y])
        elif (dir == "RIGHT" and self.checkStatus(self.head_x+1, self.head_y)):
            self.head_x += 1
            self.repaint()
            self.snakeCells.insert(0 ,[self.head_x, self.head_y])
        elif (dir == "LEFT" and self.checkStatus(self.head_x-1, self.head_y)):
            self.head_x -= 1
            self.repaint()
            self.snakeCells.insert(0 ,[self.head_x, self.head_y])

    def gameOver(self, event, qp):
        qp.setPen(QtGui.QColor(0, 34, 3))
        if self.score < 573:
            qp.drawText(event.rect(), QtCore.Qt.AlignCenter, "GAME OVER")
            qp.drawText(80, 170, "press space to play again")
        else:
            qp.drawText(event.rect(), QtCore.Qt.AlignCenter, "You Win!")
        self.timer.stop()
        self.update()

    def in_snake_body(self, cell):
        return cell in self.snakeCells[1:len(self.snakeCells)]

    def over_board(self, x, y):
        return y > (self.board_size - 1) or x > (self.board_size - 1) or x < 0 or y < 0

    def checkStatus(self, x, y):
        if self.over_board(x, y):
            self.isOver = True
            return False
        elif self.in_snake_body(self.snakeCells[0]):
            self.isOver = True
            return False
        elif self.head_y == self.food_y and self.head_x == self.food_x:
            self.FoodPlaced = False
            self.placeFood()
            self.score += 1
            return True
        elif self.score >= 573:
            self.isOver = True
            return False

        self.snakeCells.pop()

        return True

    # places the food when no food on the board
    def placeFood(self):
        if self.FoodPlaced == False:
            self.food_x = randrange(self.board_size)
            self.food_y = randrange(self.board_size)
            # for debug
            print("food:" , self.food_x, self.food_y)
            if not [self.food_x, self.food_y] in self.snakeCells:
                self.FoodPlaced = True

    def drawFood(self, qp):
        qp.setBrush(QtGui.QColor("green"))
        real_x, real_y = self.real_xy(self.food_x, self.food_y)
        qp.drawRect(real_x, real_y, self.grid_size, self.grid_size)


    # draws snake cells
    def drawSnake(self, qp):
        qp.setPen(QtCore.Qt.NoPen)
        qp.setBrush(QtGui.QColor("red"))
        real_x, real_y = self.real_xy(self.head_x, self.head_y)
        qp.drawRect(real_x, real_y, self.grid_size, self.grid_size)
        qp.setBrush(QtGui.QColor("black"))
        for i in self.snakeCells[1:]:
            real_x, real_y = self.real_xy(i[0], i[1])
            qp.drawRect(real_x, real_y, self.grid_size, self.grid_size)

    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():
            if self.auto:
                dis = self.compute_dis()
                new_coord = None
                dir = self.lastKeyPress
                if self.FoodPlaced and len(self.path) == 0:
                    if self.have_path():
                        self.find_path()
                    print self.path
                    if len(self.path) > 0:
                        new_coord = self.path.pop()
                        dir = self.coordinate_to_dir(self.snakeCells[0], new_coord)
                        if dir is None:
                            new_coord = self.find_nearby_path(dis)
                            if new_coord is None:
                                self.isOver = True
                        else:
                            dir = self.coordinate_to_dir(self.snakeCells[0], new_coord)
                else:
                    new_coord = self.find_nearby_path(dis)
                    if new_coord is None:
                        self.isOver = True
                    else:
                        dir = self.coordinate_to_dir(self.snakeCells[0], new_coord)
                
                print("food: ", self.food_x, self.food_y, "old: ", self.snakeCells[0], "new: ", new_coord, "distance: ", dis[self.head_x][self.head_y], dir)
                self.lastKeyPress = dir
                self.set_direction(dir)
            else:
                self.set_direction(self.lastKeyPress)
            self.repaint()
        else:
            QtGui.QFrame.timerEvent(self, event)

    def have_path(self):
        dis_cur = self.board_size * 2 + 1
        dis_arr = self.compute_dis()
        self.previous = [[[-1, -1] for j in range(self.board_size)] for i in range(self.board_size)]
        visited = [[False for j in range(self.board_size)] for i in range(self.board_size)]
        not_visited = lambda cell: not visited[cell[0]][cell[1]]
        cell_safe = lambda cell: not self.in_snake_body(cell) and not self.over_board(cell[0], cell[1])
        # using queue, can do popleft
        queue = deque()
        queue.append([self.head_x, self.head_y])
        found = False
        while(len(queue) > 0):
            cell_p = queue.popleft()
            cell_x, cell_y = cell_p
            if cell_x == self.food_x and cell_y == self.food_y:
                found = True
                return found
            visited[cell_x][cell_y] = True
            nearby = [[cell_x + 1,cell_y],
                     [cell_x - 1, cell_y],
                     [cell_x, cell_y + 1],
                     [cell_x, cell_y - 1]]

            nearby = filter(cell_safe, nearby)

            nearby = filter(not_visited, nearby)
            for cell in nearby:
                x, y = cell
                self.previous[x][y] = [cell_x, cell_y]
                if x == self.food_x and y == self.food_y:
                    found = True
                    self.path.append([self.food_x, self.food_y])
                    return found
                visited[x][y] = True
                queue.append(cell)
        return found
            
    def find_path(self):
        self.path = []
        cell = [self.food_x, self.food_y]
        previous = self.previous
        while cell != [self.head_x, self.head_y]:
            self.path.append(cell)
            cell = previous[cell[0]][cell[1]]
            if cell == [-1, -1]:
                return

    # 
    def find_nearby_path(self, distances):
        cells = [[self.head_x + 1,self.head_y],
                 [self.head_x - 1, self.head_y],
                 [self.head_x, self.head_y + 1],
                 [self.head_x, self.head_y - 1]]

        f = lambda cell: not self.in_snake_body(cell) and not self.over_board(cell[0], cell[1])
        cells = filter(f, cells)

        if  cells == []:
            return None

        min_path = self.board_size
        min_cell = choice(cells)

       
        for cell in cells:
            dis = distances[cell[0]][cell[1]]
            if  dis <= min_path:
                min_path = dis
                min_cell = cell
        return  min_cell


    # compute the distance of each grid to food
    def compute_dis(self):
        dis_arr = []
        for i in range(self.board_size):
            tmp = []
            for j in range(self.board_size):
                tmp.append(fabs(i-self.food_x) + fabs(j-self.food_y))
            dis_arr.append(tmp)
        return dis_arr

    # dir of old to new coordinate
    def coordinate_to_dir(self, c1, c2):
        if c1[0] == c2[0]:
            if c1[1] == c2[1] + 1:
                return "UP"
            elif c1[1] == c2[1] - 1:
                return "DOWN"
        elif c1[1] == c2[1]:
            if c1[0] == c2[0] + 1:
                return "LEFT"
            elif c1[0] == c2[0] - 1:
                return "RIGHT"
        return None


def main():
    app = QtGui.QApplication(sys.argv)
    game = Game()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
