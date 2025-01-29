# Pedro Rasinhas    nmec    103541
# Gonçalo Silva     nmec    103668

from math import sqrt
import getpass
import asyncio
import json
import os
import sys
from time import perf_counter

# Next 4 lines are not needed for AI agents, please remove them from your code!
import websockets
from rushh_d import *


def new_state_calc(state, dim, act):
    statex = [list(state[i : i + dim]) for i in range(0, len(state), dim)]
    new_state = statex

    car_id = act["id"]
    direction = act["direction"]
    car_len = act["len"]
    found = False
    for r in range(dim):
        for c in range(dim):
            if new_state[r][c] == car_id:
                # UP
                if direction == "w":
                    if r - car_len >= 0:
                        new_state[r - 1][c] = car_id
                        new_state[r + car_len - 1][c] = "o"
                        found = True

                # DOWN
                elif direction == "s":
                    if r + car_len < dim:
                        new_state[r + car_len][c] = car_id
                        new_state[r][c] = "o"
                        found = True

                # LEFT
                elif direction == "a":
                    new_state[r][c - 1] = car_id
                    new_state[r][c + car_len - 1] = "o"
                    found = True

                # RIGHT
                elif direction == "d":
                    if c + car_len < dim:
                        new_state[r][c] = "o"
                        new_state[r][c + car_len] = car_id
                        found = True

            if found:
                break
            else:
                continue
        if found:
            break
        else:
            continue
    new_b = ""
    for l in new_state:
        for c in l:
            new_b += c
    return new_b, found


def act_key_convert(action_list, board, dim, cursor, selected):
    state = [list(board[i : i + dim]) for i in range(0, len(board), dim)]
    act = action_list.pop(0)
    act_keys = []

    car_coords = [
        [j, i] for i in range(dim) for j in range(dim) if state[i][j] == act["id"]
    ]
    car_coords.sort(
        key=lambda x: sqrt((x[0] - cursor[0]) ** 2 + (x[1] - cursor[1]) ** 2)
    )
    car_c = car_coords[0]  # car_coords[0] is the closest to the cursor

    if selected != "":
        if selected != act["id"]:
            act_keys.append(" ")
            selected = ""

    if car_c[0] > cursor[0]:
        [act_keys.append("d") for i in range(car_c[0] - cursor[0])]

    elif car_c[0] < cursor[0]:
        [act_keys.append("a") for i in range(cursor[0] - car_c[0])]

    if car_c[1] > cursor[1]:
        [act_keys.append("s") for i in range(car_c[1] - cursor[1])]

    elif car_c[1] < cursor[1]:
        [act_keys.append("w") for i in range(cursor[1] - car_c[1])]

    if selected == "":
        act_keys.append(" ")
    act_keys.append(act["direction"])
    return act_keys


async def agent_loop(server_address="localhost:8000", agent_name="student"):
    async with websockets.connect(
        f"ws://{server_address}/player", ping_interval=None
    ) as websocket:
        # Receive information about static game properties
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))

        action_list = []
        key_list = []  # para cada action
        crazy_car = False
        ib = ""
        flag_nl = False
        nit = 0
        i = 0
        flag_happened = True
        while True:
            try:
                state = json.loads(
                    await websocket.recv()
                )  # receive game update, this must be called timely or your game will get out of sync with the server

                if (
                    ib != state.get("grid").split(" ")[1] and flag_nl
                ) or not flag_happened:
                    crazy_car = True
                    print("crazy car happened :", i, "\n")
                    i += 1
                    flag_nl = False

                if crazy_car:
                    action_list = []
                    key_list = []

                if action_list == [] and key_list == []:
                    if not flag_nl:
                        flag_nl = True
                        ib = state.get("grid").split(" ")[1]
                        crazy_car = False

                    initial_board = state.get("grid").split(" ")[1]
                    rh_domain = RushHour(
                        initial_board, state.get("dimensions")[0]
                    )  # its a square
                    p = SearchProblem(
                        rh_domain, initial_board
                    )  # -> take only the board str
                    t = SearchTree(p)
                    start_time = perf_counter()
                    action_list = t.search()
                    end_time = perf_counter()
                    tts = end_time - start_time

                    if tts > 0.1:
                        nit = round(tts * 10)
                        [await websocket.recv() for _ in range(nit)]

                elif len(action_list) > 0 and (len(key_list) == 0):
                    act = action_list[0]
                    key_lst = act_key_convert(
                        action_list,
                        state.get("grid").split(" ")[1],
                        state.get("dimensions")[0],
                        state.get("cursor"),
                        state.get("selected"),
                    )
                    key_list = key_lst

                if len(key_list) > 0:

                    key = key_list.pop(0)
                    await websocket.send(json.dumps({"cmd": "key", "key": key}))
                    if key_list == [] and key != "-":
                        ib, flag_happened = new_state_calc(
                            state.get("grid").split(" ")[1],
                            state.get("dimensions")[0],
                            act,
                        )

            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return


# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='arrumador' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))
