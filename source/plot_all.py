#!/usr/bin/env python

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import signal
import sys, time
from mindwave import Headset, get_headset_dongles

gamefig = plt.figure()
gameplot = gamefig.add_subplot(1, 1, 1)
ANI = None
xs = [0]
ys = [0]
yAs = [0]
yMs = [0]
headsets = []
ball_location = [0, 0]


def show_state(i):
    global xs, ys, yAs, yMs
    xs.append(xs[-1] + 1)
    yAs.append(headsets[0].attention)
    yMs.append(headsets[0].meditation)
    ys.append(headsets[0].attention + headsets[0].meditation)
    xs = xs[-20:]
    ys = ys[-20:]
    yAs = yAs[-20:]
    yMs = yMs[-20:]
    gameplot.clear()
    gameplot.plot(xs, yAs, "r", label="attention")
    gameplot.plot(xs, yMs, "b", label="meditation")
    gameplot.plot(xs, ys, "g", label="sum")
    plt.xticks(rotation=45, ha="right")
    plt.subplots_adjust(bottom=0.30)
    plt.title("MINDBALL")
    plt.ylabel("Focus")
    plt.legend()
    return


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
    print(f"status: {headsets[0].status}")
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
            print(state)
        if state == "standby" or state is None:
            headsets[0].connect()

    print("now connected!")

    signal.signal(signal.SIGINT, signal.default_int_handler)
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
