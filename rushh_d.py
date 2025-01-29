# Pedro Rasinhas nemc 103541
# Gonçalo Silva nmec 103668

from tree_search import *

VEHICLES_STR = "ABCDEFGHIJKLMNOPQRSTUVXYZ"


class RushHour(SearchDomain):
    def __init__(self, board, width):
        self.width = width
        self.board = [
            list(board[i : i + self.width]) for i in range(0, len(board), self.width)
        ]

    def actions(self, state):
        state = [
            list(state[i : i + self.width]) for i in range(0, len(state), self.width)
        ]

        action_lst = []
        visited_cars = set()
        for r in range(self.width):
            for c in range(self.width):
                if VEHICLES_STR.__contains__(state[r][c]):
                    car_id = state[r][c]
                    if car_id not in visited_cars:
                        vertical = False
                        visited_cars.add(car_id)
                        car_len = 2

                        if r + 1 < self.width and state[r + 1][c] == car_id:
                            vertical = True
                            if r + 2 < self.width and state[r + 2][c] == car_id:
                                car_len = 3

                            if r - 1 >= 0 and state[r - 1][c] == "o":
                                action_lst.append(
                                    {"id": car_id, "direction": "w", "len": car_len}
                                )

                            if (
                                r + car_len < self.width
                                and state[r + car_len][c] == "o"
                            ):
                                action_lst.append(
                                    {"id": car_id, "direction": "s", "len": car_len}
                                )

                        if (
                            not vertical
                            and c + 1 < self.width
                            and state[r][c + 1] == car_id
                        ):
                            if c + 2 < self.width and state[r][c + 2] == car_id:
                                car_len = 3

                            if c - 1 >= 0 and state[r][c - 1] == "o":
                                action_lst.append(
                                    {"id": car_id, "direction": "a", "len": car_len}
                                )

                            if (
                                c + car_len < self.width
                                and state[r][c + car_len] == "o"
                            ):
                                action_lst.append(
                                    {"id": car_id, "direction": "d", "len": car_len}
                                )

        return action_lst

    def result(self, state, action):
        new_board = [
            list(state[i : i + self.width]) for i in range(0, len(state), self.width)
        ]
        car_id = action["id"]
        direction = action["direction"]
        car_len = action["len"]
        found = False
        for r in range(self.width):
            for c in range(self.width):
                if new_board[r][c] == car_id:
                    if direction == "w":
                        new_board[r - 1][c] = car_id
                        new_board[r + car_len - 1][c] = "o"
                        found = True

                    elif direction == "s":
                        new_board[r][c] = "o"
                        new_board[r + car_len][c] = car_id
                        found = True

                    elif direction == "a":
                        new_board[r][c - 1] = car_id
                        new_board[r][c + car_len - 1] = "o"
                        found = True

                    elif direction == "d":
                        new_board[r][c] = "o"
                        new_board[r][c + car_len] = car_id
                        found = True

                if found:
                    break
            if found:
                break
        new_b = ""
        for l in new_board:
            for c in l:
                new_b += c
        return new_b

    def heuristic(self, state, goal):
        board = [
            list(state[i : i + self.width]) for i in range(0, len(state), self.width)
        ]
        car_block_num = 0

        for r in range(self.width):
            for c in range(self.width):
                if board[r][c] == "A":
                    distance = self.width - 1 - c
                    for i in range(c + 1, self.width):
                        if board[r][i] != "o":
                            car_block_num += 1
                    return distance + car_block_num

    def satisfies(self, state):
        state = [
            list(state[i : i + self.width]) for i in range(0, len(state), self.width)
        ]

        if (
            state[round((self.width - 1) / 2)][self.width - 2] == "A"
            and state[round((self.width - 1) / 2)][self.width - 1] == "A"
        ):
            return True
        return False

    def __str__(self):
        return "\n".join([" ".join(row) for row in self.board])
