import numpy as np
import random
import time
from read import readInput
from write import writeOutput
from host import GO

class MyPlayer:
    def __init__(self, N=5):
        self.type = "Minimax"
        self.N = N
        self.side = None
        self.forward_step = 6
        self.start_time = time.time()
        self.max_time = 8.5

    # maximize my winning chance during my action stage
    def maximize(self, alpha, beta, go, depth, passed = False):
        go.piece_type = self.side

        # if reached max depth or time is running out, judge difference between scores
        if depth >= self.forward_step or time.time() - self.start_time > self.max_time:
            v = self.heuristic(go, self.side)
            return v, None

        # get all possible placements
        possible_placements = []
        for i in range(self.N):
            for j in range(self.N):
                if go.valid_place_check(i, j, self.side, test_check = False):
                    possible_placements.append((i,j))

        random.shuffle(possible_placements)
        # add PASS as a choice of movement
        possible_placements.append("PASS")

        # calculate v for every move
        v = - np.inf
        move = None
        for action in possible_placements:
            # simulate the action
            if action == "PASS" and passed == True:
                if passed == True:
                    result = self.heuristic(go, self.side)
            elif action == "PASS" and passed == False:
                result, opponent_move = self.minimize(alpha, beta, go, depth + 1, True)
            else:
                (i, j) = action
                # attempe the move
                go.board[i][j] = self.side
                dead_pieces = go.remove_died_pieces(3 - self.side)

                # only make the move if it is not too dangerous
                ally_members = go.ally_dfs(i, j)
                liberty_pos = self.find_liberty_pos(ally_members, go)
                if len(liberty_pos) <= 1:
                    result = - np.inf
                else:
                    result, opponent_move = self.minimize(alpha, beta, go, depth + 1)
            
                # undo the attempted move
                go.board[i][j] = 0
                for dead_piece in dead_pieces:
                    go.board[dead_piece[0]][dead_piece[1]] = 3 - self.side

            # update my best move
            if result > v:
                v = result
                move = action
            
            # perform alpha-beta pruning
            if v >= beta:
                return v, move
            
            # update alpha
            if v > alpha:
                alpha = v

        return v, move


    # minimize my winning chance during opponent's action stage
    def minimize(self, alpha, beta, go, depth, passed = False):
        go.piece_type = 3 - self.side

        # if reached max depth or time is running out, judge difference between scores
        if depth >= self.forward_step or time.time() - self.start_time > self.max_time:
            v = self.heuristic(go, self.side)
            return v, None

        # get all possible placements
        possible_placements = []
        for i in range(self.N):
            for j in range(self.N):
                if go.valid_place_check(i, j, 3 - self.side, test_check = False):
                    possible_placements.append((i,j))
        
        if len(possible_placements) == 0:
            v = self.heuristic(go, self.side) - depth
            return v, None

        random.shuffle(possible_placements)
        # add PASS as a choice of movement
        possible_placements.append("PASS")


        # calculate v for every move
        v = np.inf
        move = None
        for action in possible_placements:
            # simulate the action
            if action == "PASS" and passed == True:
                if passed == True:
                    result = self.heuristic(go, self.side)
            elif action == "PASS" and passed == False:
                result, opponent_move = self.maximize(alpha, beta, go, depth + 1, True)
            else:
                (i, j) = action

                # attempe the move
                go.board[i][j] = 3 - self.side
                dead_pieces = go.remove_died_pieces(self.side)

                result, opponent_move = self.maximize(alpha, beta, go, depth + 1)

                # undo the attempted move
                go.board[i][j] = 0
                for dead_piece in dead_pieces:
                    go.board[dead_piece[0]][dead_piece[1]] = self.side

            # update opponent's best move
            if result < v:
                v = result
                move = action

            # perform alpha-beta pruning
            if v <= alpha:
                return v, move
            
            # update beta
            if v < beta:
                beta = v

        return v, move


    def get_input(self, go, piece_type):
        self.start_time = time.time()

        self.side = piece_type
        self.forward_step = 6

        # get all possible placements and positions of my stones
        possible_placements = []
        my_positions= []
        for i in range(self.N):
            for j in range(self.N):
                if go.board[i][j] == self.side:
                    my_positions.append((i, j)) 
                if go.valid_place_check(i, j, self.side, test_check = False):
                    possible_placements.append((i,j))
        
        if len(possible_placements) == 0:
            return "PASS"

        # opening move
        elif len(possible_placements) == 25:
            return (self.N // 2, self.N // 2)

        elif len(possible_placements) > 16:
            self.forward_step = 8

        elif len(possible_placements) < 8:
            self.forward_step = 4

        # make move that kill most opponents
        kills = 0
        move = None
        for action in possible_placements:
            (i, j) = action
            # attempe the move
            go.board[i][j] = self.side
            dead_pieces = go.remove_died_pieces(3 - self.side)
            
            if len(dead_pieces) > kills:
                kills = len(dead_pieces)
                move = action
            
            # undo the attempted move
            go.board[i][j] = 0
            for dead_piece in dead_pieces:
                go.board[dead_piece[0]][dead_piece[1]] = 3 - self.side
        if move != None:
            return move
        
        # make move that save most stones
        checked = []
        saved = 0
        move = None
        for (row, col) in my_positions:
            if (row, col) not in checked:
                # find the group
                ally_members = go.ally_dfs(row, col)

                # find liberties positions of the group have
                liberty_pos = self.find_liberty_pos(ally_members, go)

                # try saving if only 1 liberty left
                if len(liberty_pos) == 1:
                    action = liberty_pos[0]
                    if action in possible_placements:
                        (i, j) = action

                        # attempe the move
                        go.board[action[0]][action[1]] = self.side
                        dead_pieces = go.remove_died_pieces(3 - self.side)

                        # check if the move caused the group to have more than 1 liberty
                        new_ally_members = go.ally_dfs(row, col)
                        new_liberty_pos = self.find_liberty_pos(new_ally_members, go)
                        if len(new_liberty_pos) > 1:
                            # check if it is the largest group saved
                            if len(ally_members) > saved:
                                saved = len(new_ally_members) - 1
                                move = liberty_pos[0]

                        # undo the attempted move
                        go.board[i][j] = 0
                        for dead_piece in dead_pieces:
                            go.board[dead_piece[0]][dead_piece[1]] = 3 - self.side

                # consider all in the group as checked
                checked += ally_members
        if move != None:
            return move


        v, move = self.maximize(-np.inf, np.inf, go.copy_board(), 0)
        if move == None:
            return "PASS"
        return move


    # find liberty positions for a group
    def find_liberty_pos(self, group, go):
        liberty_pos = [] 
        for member in group:
            neighbors = go.detect_neighbor(member[0], member[1])
            for piece in neighbors:
                if go.board[piece[0]][piece[1]] == 0:
                    liberty_pos.append(piece[0])
        return liberty_pos


    # calculate stone number difference between black and white
    def find_stone_dif(self, go):
        black_count = 0
        white_count = 0
        for i in range(self.N):
            for j in range(self.N):
                if go.board[i][j] == 1:
                    if 0 < i < self.N - 1 and 0 < j < self.N - 1:
                        black_count += 1
                    else:
                        # give less weight for moves on the edge
                        black_count += 0.8
                elif go.board[i][j] == 1:
                    if 0 < i < self.N - 1 and 0 < j < self.N - 1:
                        white_count += 1
                    else:
                        # give less weight for moves on the edge
                        white_count += 0.8
        return black_count - white_count

    # calculate liberty difference between black and white
    def find_liberty_dif(self, go):
        liberty_b = set()
        liberty_w = set()

        for i in range(self.N):
            for j in range(self.N):
                if go.board[i][j] == 0:
                    continue
                
                neighbors = go.detect_neighbor(i, j)
                for neighbor in neighbors:
                    if go.board[neighbor[0]][neighbor[1]] == 0:
                        if go.board[i][j] == 1:
                            liberty_b.add(neighbor)
                        else:
                            liberty_w.add(neighbor)

        
        return len(liberty_b) - len(liberty_w)



    # calculate Euler number difference between black and white
    def find_euler_dif(self, go):
        q1_b, q3_b, qd_b = 0, 0, 0
        q1_w, q3_w, qd_w = 0, 0, 0
        padded_board = np.pad(np.array(go.board), [(1, 1), (1, 1)])
        for i in range(padded_board.shape[0] - 1):
            for j in range(padded_board.shape[1] - 1):
                window = padded_board[i : i + 2, j: j + 2]
                black_count = (window == 1).sum()
                white_count = (window == 2).sum()

                # count q1
                if black_count == 1:
                    q1_b += 1
                if white_count == 1:
                    q1_w += 1
                
                # count q3
                if black_count == 3:
                    q3_b += 1
                if white_count == 3:
                    q3_w += 1
                
                # count qd
                if black_count == 2:
                    if window[0, 0] == window[1, 1] or window[0, 1] == window[1, 0]:
                        qd_b += 1
                if white_count == 2:
                    if window[0, 0] == window[1, 1] or window[0, 1] == window[1, 0]:
                        qd_w += 1

        # E = (q1 - q3 + 2 * qd) / 4
        euler_b = (q1_b - q3_b + 2 * qd_b) / 4
        euler_w = (q1_w - q3_w + 2 * qd_w) / 4
        return euler_b - euler_w


    # calculate the heuristic value of the current board
    def heuristic(self, go, piece_type):
        stone_dif = self.find_stone_dif(go)
        liberty_dif = self.find_liberty_dif(go)
        euler_dif = self.find_euler_dif(go)

        v = liberty_dif + stone_dif - 4 * euler_dif
        if piece_type == 2:
            v = -v
        return v

if __name__ == "__main__":
    N = 5
    piece_type, previous_board, board = readInput(N)
    go = GO(N)
    go.set_board(piece_type, previous_board, board)

    player = MyPlayer()

    action = player.get_input(go, piece_type)

    writeOutput(action)