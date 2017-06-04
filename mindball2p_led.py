#!/usr/bin/env python

import platform
import os, sys, time, math
from pymindwave import headset
import RPi.GPIO as gpio

LIGHTS = [12, 16, 7, 11, 13, 15, 18, 22]

def ON(light_num):
    gpio.output(light_num, True)
def OFF(light_num):
    gpio.output(light_num, False)

#blink three times, finish off
def blink_all():
    for light in LIGHTS:
        ON(light)
    time.sleep(0.5)
    for light in LIGHTS:
        OFF(light)
    time.sleep(0.5)
    for light in LIGHTS:
        ON(light)
    time.sleep(0.5)
    for light in LIGHTS:
        OFF(light)
    time.sleep(0.5)
    for light in LIGHTS:
        ON(light)
    time.sleep(0.5)
    for light in LIGHTS:
        OFF(light)

def set_light_state(game_state):
    if game_state[0] == 0 or game_state[1] == 0:
        blink_all()
    else:
        light_float = (game_state[0] * 2.0/5.0) - 0.5
        light_low = int(math.floor(light_float))
        light_high = int(math.ceil(light_float))
        for light in range(len(LIGHTS)):
            if light == light_high or light == light_low:
                ON(LIGHTS[light])
            else:
                OFF(LIGHTS[light])
        

def start_mindball(hs1, hs2):
    while True:
        a = raw_input("Press ENTER when both players are ready.")
        winner = mindball_loop(hs1, hs2)
        time.sleep(5)


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

def mindball_loop(hs1, hs2):
    winner = 0
    game_state = [10, 10]
    set_light_state(game_state)
    while not winner:
        #get player attention values
        time.sleep(1)
        att1 = hs1.get('attention')
        med1 = hs1.get('meditation')
        p1_strength = att1 + med1
        att2 = hs2.get('attention')
        med2 = hs2.get('meditation')
        p2_strength = att2 + med2

        #make sure we're getting data before continuing
        if p1_strength is 0 or p2_strength is 0:
            print "waiting for readings..."
            continue

        #compare attention values
        do_we_step_right = (p1_strength > p2_strength)

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
        if p1_strength < 10:
            pad = 3

        #report
        #print str(p1_strength) + (' '*pad) + show_state(game_state, p1_strength, p2_strength) + ' ' + str(p2_strength)
        os.system('clear')
        print show_state(game_state, p1_strength, p2_strength)
        set_light_state(game_state)

        #check for game over
        if game_state[0] > 19:
            print "Player 1 Wins!"
            winner = 1
        elif game_state[1] > 19:
            print "Player 2 Wins!"
            winner = 2

    return winner


if __name__ == "__main__":
    #connect headset #1
    hs1 = headset.Headset('/dev/ttyUSB0')
    hs2 = headset.Headset('/dev/ttyUSB1')

    # wait some time for parser to udpate state so we might be able
    # to reuse last opened connection.
    time.sleep(1)
    if hs1.get_state() == 'connected':
        hs1.disconnect()
    if hs2.get_state() == 'connected':
        hs2.disconnect()

    print "Player 1, connect your headset."
    state = 'x'
    while hs1.get_state() != 'connected':
        time.sleep(1)
        curr_state = hs1.get_state()
        if not curr_state == state:
            state = curr_state
            print state
        if (state == 'standby'):
            hs1.connect()
    print "Player 1 connected!"

    print "Player 2, connect your headset."
    while hs2.get_state() != 'connected':
        time.sleep(1)
        curr_state = hs2.get_state()
        if not curr_state == state:
            state = curr_state
            print state
        if (state == 'standby'):
            hs2.connect()
    print "Player 2 connected!"

    gpio.setmode(gpio.BOARD)
    for light in LIGHTS:
        gpio.setup(light, gpio.OUT)

    start_mindball(hs1, hs2)
    #mindball_loop(hs)

    print 'disconnecting...'
    hs1.disconnect()
    hs1.destroy()
    hs2.disconnect()
    hs2.destroy()
    print 'done'
    sys.exit(0)
    

    
