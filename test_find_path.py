# -*- coding: utf-8 -*-
from collections import deque
from math import fabs

class Game():
    def __init__(self):
        self.board_size = 20
        self.head_x = 5
        self.head_y = 8
        self.food_x = 10
        self.food_y = 17
        self.cells = []
        self.snakeCells = [[self.head_x, self.head_y], [self.head_x-1, self.head_y], [self.head_x-2, self.head_y]]
        
    def in_snake_body(self, cell):
        return cell in self.snakeCells[1:len(self.snakeCells)]

    def over_board(self, x, y):
        return y > (self.board_size - 1) or x > (self.board_size - 1) or x < 0 or y < 0
    
    # compute the distance of each grid to food
    def compute_dis(self):
        dis_arr = []
        for i in range(self.board_size):
            tmp = []
            for j in range(self.board_size):
                tmp.append(fabs(i-self.food_x) + fabs(j-self.food_y))
            dis_arr.append(tmp)
        return dis_arr

    
    def is_cell_safe(self, cell):
        return not self.in_snake_body(cell) and not self.over_board(cell[0], cell[1])
    

    # According to http://stackoverflow.com/questions/8379785/how-does-a-breadth-first-search-work-when-looking-for-shortest-path
    # BFS can only be used to find shortest path in a graph if:

    # There are no loops
    # All edges have same weight or no weight.
    # So We can use simple BFS and record a previous arr
    #
    def have_path(self):
        print "Food:", self.food_x, self.food_y
        self.path = []
        dis_cur = self.board_size * 2 + 1
        dis_arr = self.compute_dis()
        # find food using bfs
        self.previous = [[[-1, -1] for j in range(self.board_size)] for i in range(self.board_size)]
        self.visited = [[False for j in range(self.board_size)] for i in range(self.board_size)]
        not_visited = lambda cell: not self.visited[cell[0]][cell[1]]
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
            self.visited[cell_x][cell_y] = True
            #print cell_x, cell_y
            nearby = [[cell_x + 1,cell_y],
                     [cell_x - 1, cell_y],
                     [cell_x, cell_y + 1],
                     [cell_x, cell_y - 1]]

            nearby = filter(cell_safe, nearby)
            #print "nearby:", nearby
            nearby = filter(not_visited, nearby)
            #print "nearby:", nearby
            #min_cell = None
            for cell in nearby:
                x, y = cell
                self.previous[x][y] = [cell_x, cell_y]
                if x == self.food_x and y == self.food_y:
                    found = True
                    return found
                self.visited[x][y] = True
                queue.append(cell)
                
                #if dis_arr[x][y] < dis_cur:
                #    min_cell = cell
                #    dis_cur = dis_arr[x][y]
            #if min_cell:
            #    self.path.append(min_cell)
                
                    
            #print "len queue:",len(queue), "queue:", queue
            #print "visited:", visited
        return found
    
    def find_path(self):
        path = []
        print "head:", self.head_x, self.head_y
        cell = [self.food_x, self.food_y]
        previous = self.previous
        while cell != [self.head_x, self.head_y]:
            path.append(cell)
            print "coord :", cell,
            cell = previous[cell[0]][cell[1]]
            print "previous:", cell
            if cell == [-1, -1]:
                break
        return path
        

    def paint_path(self):
        print self.path
        for i in range(20):
            for j in range(20):
                if i == self.food_x and j == self.food_y:
                    print "@",
                elif [i,j] in self.path:
                    print "#",
            print
    
    def paint_visited(self):
        for i in range(20):
            for j in range(20):
                if i == self.food_x and j == self.food_y:
                    print "@",
                elif self.visited[i][j]:
                    print "#",
            print

if __name__ == "__main__":
    game = Game()
    print game.have_path()
    print game.find_path()
    #game.paint_visited()
    #game.paint_path()
    
    
