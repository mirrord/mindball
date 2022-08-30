#!/usr/bin/env python

import platform
import os, sys, time
from mindwave import Headset


def start_mindball(hs1):
    dif = 100
    while True:
        print("difficulty: " + str(dif))
        a = input("Press ENTER when you are ready.")
        winner = mindball_loop(hs1, dif)
        time.sleep(5)
        if winner == 1:
            dif+=10
        else:
            dif-=10

def show_state(game_state, p1_strength, p2_strength):
    left_side = '='*game_state[0]
    right_side = '='*game_state[1]
    game_line = left_side + 'o' + right_side
    p1_top = False
    p2_top = False

    #walk down the screen, starting at line 20
    screen_state = ""
    for j in range(20):
        i = (20-j)*10
        if p1_top:
            screen_state += "||"
        elif p1_strength > i:
            p1_top = True
            screen_state += "__"
        elif p1_strength+10 > i:
            screen_state += str(p1_strength)
        else:
            screen_state += "  "
            
        if j==10:
            screen_state += (" "*4) + game_line + (" "*4)
        else:
            screen_state += (" "*30)

        if p2_top:
            screen_state += "||"
        elif p2_strength > i:
            p2_top = True
            screen_state += "__"
        elif p2_strength+10 > i:
            screen_state += str(p2_strength)
        else:
            screen_state += "  "
        screen_state += "\n"

    return screen_state

def mindball_loop(hs1, difficulty):
    winner = 0
    game_state = [10, 10]
    while not winner:
        #get player attention values
        time.sleep(1)
        att1 = hs1.attention
        med1 = hs1.meditation
        p1_strength = att1 + med1

        #make sure we're getting data before continuing
        if p1_strength == 0:
            print("waiting for readings...")
            continue

        #compare attention values
        do_we_step_right = (p1_strength > difficulty)

        #generate state step, add state step to current game state
        if do_we_step_right:
            game_state[0]+=1
            game_state[1]-=1
        else:
            game_state[1]+=1
            game_state[0]-=1

        pad = 1
        if p1_strength < 100:
            pad = 2

        #report
        #print str(p1_strength) + (' '*pad) + show_state(game_state, p1_strength, 100) + ' ' + str(difficulty)
        #os.system('clear')
        print(show_state(game_state, p1_strength, 100))

        #check for game over
        if game_state[0] > 20:
            print("Player 1 Wins!")
            winner = 1
        elif game_state[1] > 20:
            print("Player 2 Wins!")
            winner = 2

    return winner


if __name__ == "__main__":
    #connect headset #1
    hs = Headset('/dev/ttyUSB1')

    # wait some time for parser to udpate state so we might be able
    # to reuse last opened connection.
    time.sleep(1)
    print(f"status: {hs.status}")
    if hs.status == 'connected':
        hs.disconnect()
        time.sleep(1)

    print("connecting...")
    hs.connect()
    state = 'x'
    while hs.status != 'connected':
        time.sleep(5)
        curr_state = hs.status
        if not curr_state == state:
            state = curr_state
            print(state)
        if state == 'standby' or state == None:
            print("connecting...")
            hs.connect()

    print('now connected!')

    start_mindball(hs)
    #mindball_loop(hs)

    print('disconnecting...')
    hs.disconnect()
    hs.destroy()
    print('done')
    sys.exit(0)
    

    
