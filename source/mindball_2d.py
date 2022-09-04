#!/usr/bin/env python

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import signal
import sys, time
from mindwave import Headset, get_headset_dongles


gamefig = plt.figure()
gameplot = gamefig.add_subplot(1, 1, 1)
ANI = None
headsets = []
ball_location = [330, 190]
BACKGROUND = plt.imread("field.jpg")
INTERVAL = 30
BALL_RADIUS = 10
pause = False

GOALS = [
    [[25, 125], [110, 270]],
    [[530, 630], [110, 270]],
]


def check_win():
    if (
        ball_location[0] > GOALS[0][0][0]
        and ball_location[0] < GOALS[0][0][1]
        and ball_location[1] > GOALS[0][1][0]
        and ball_location[1] < GOALS[0][1][1]
    ):
        return 2
    if (
        ball_location[0] > GOALS[1][0][0]
        and ball_location[0] < GOALS[1][0][1]
        and ball_location[1] > GOALS[1][1][0]
        and ball_location[1] < GOALS[1][1][1]
    ):
        return 1
    return 0


def show_state(i):
    global pause
    global ball_location
    if not pause:
        winner = check_win()
        if winner:
            pause = True
            print(f"Player {winner} wins!")

        p1a = headsets[0].attention
        p1m = headsets[0].meditation
        gameplot.clear()

        plt.xticks(rotation=45, ha="right")
        plt.subplots_adjust(bottom=0.30)
        plt.title("MINDBALL")

        ball_location[0] += int((p1a - 50) / 50 * INTERVAL)
        ball_location[1] += int((p1m - 50) / 100 * INTERVAL)

        ball_location = [
            min(max(ball_location[0], 10), 650),
            min(max(ball_location[1], 10), 390),
        ]

        gameplot.add_patch(plt.Circle(ball_location, BALL_RADIUS, color="blue"))
        gameplot.imshow(BACKGROUND)


def onClick(event):
    global ball_location
    global pause
    ball_location = [330, 190]
    pause = False
    pass


if __name__ == "__main__":
    # connect headset #1
    ports = get_headset_dongles()
    if not ports:
        print(
            "ERROR: Could not find MindWave RF adapter. Please make sure your adapter is plugged in and a red or blue light is on."
        )
    headsets.append(Headset(ports[0]))

    # wait some time for parser to udpate state so we might be able
    # to reuse last opened connection.
    time.sleep(1)
    if headsets[0].status == "connected":
        headsets[0].disconnect()
        time.sleep(1)

    print("connecting...")
    headsets[0].connect()
    state = "x"
    while headsets[0].status != "connected":
        time.sleep(5)
        curr_state = headsets[0].status
        if not curr_state == state:
            state = curr_state
        if state == "standby" or state is None:
            headsets[0].connect()

    print("now connected!")

    signal.signal(signal.SIGINT, signal.default_int_handler)
    gamefig.canvas.mpl_connect("button_press_event", onClick)
    try:
        ANI = animation.FuncAnimation(
            gamefig,
            show_state,
            interval=500,
        )
        plt.show()
    except KeyboardInterrupt:
        pass

    print("\ndisconnecting...")
    headsets[0].disconnect()
    print("done")
    sys.exit(0)
