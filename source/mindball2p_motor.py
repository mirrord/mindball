#!/usr/bin/env python

import platform
import RPi.GPIO as GPIO
import os, sys, time
from pymindwave import headset

#set up the appropriate pins
GPIO.setmode(GPIO.BOARD)

enable_pin = 12
coil_A_1_pin = 7
coil_A_2_pin = 11
coil_B_1_pin = 16
coil_B_2_pin = 18

#TODO: make sure these pins match up
goal1_pin = 13
goal2_pin = 15

GPIO.setup(enable_pin, GPIO.OUT)
GPIO.setup(coil_A_1_pin, GPIO.OUT)
GPIO.setup(coil_A_2_pin, GPIO.OUT)
GPIO.setup(coil_B_1_pin, GPIO.OUT)
GPIO.setup(coil_B_2_pin, GPIO.OUT)

GPIO.setup(goal1_pin, GPIO.IN)
GPIO.setup(goal1_pin, GPIO.IN)

def setStep(w1, w2, w3, w4):
    GPIO.output(coil_A_1_pin, w1)
    GPIO.output(coil_A_2_pin, w2)
    GPIO.output(coil_B_1_pin, w3)
    GPIO.output(coil_B_2_pin, w4)

def motor_to_p1(speed):
    delay = 0.005
    for i in range(0, int(speed/10)):
        setStep(1, 0, 1, 0)
        time.sleep(delay)
        setStep(0, 1, 1, 0)
        time.sleep(delay)
        setStep(0, 1, 0, 1)
        time.sleep(delay)
        setStep(1, 0, 0, 1)
        time.sleep(delay)

def motor_to_p2(speed):
    delay = 0.005
    for i in range(0, int(speed/10)):
        setStep(1, 0, 0, 1)
        time.sleep(delay)
        setStep(0, 1, 0, 1)
        time.sleep(delay)
        setStep(0, 1, 1, 0)
        time.sleep(delay)
        setStep(1, 0, 1, 0)
        time.sleep(delay)

def poll_p1_goal():
    return

def poll_p1_goal():
    return

def center_motor():
    while not poll_p1_goal():
        motor_to_p1(1)

    step_count = 0
    while not poll_p2_goal():
        motor_to_p2(1)
        step_count+=1

    steps_to_center = step_count/2
    for step in range(steps_to_center):
        motor_to_p1()

    return steps_to_center

def wait_for_button():
    while not (poll_p1_goal() and poll_p2_goal()):
        #ideally light an LED or something...
        pass

def start_mindball(hs1, hs2):
    steps_to_win = center_motor()
    while True:
        a = wait_for_button()
        winner = mindball_loop(hs1, hs2, steps_to_win)
        time.sleep(5)

def show_state(game_state, p1_strength, p2_strength):
    if p1_strength > p2_strength:
        motor_to_p1(p1_strength - p2_strength)
    if p2_strength > p1_strength:
        motor_to_p2(p2_strength - p1_strength)

def mindball_loop(hs1, hs2, to_win):
    reset = False
    winner = 0
    game_state = [to_win, to_win]
    while not winner:
        #get player attention values
        time.sleep(1) #TODO: do I need this?
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

        #report
        #print str(p1_strength) + (' '*pad) + show_state(game_state, p1_strength, p2_strength) + ' ' + str(p2_strength)
        #os.system('clear')
        show_state(game_state, p1_strength, p2_strength)

        #check the hall effect sensors
        p1_goal = poll_p1_goal()
        p2_goal = poll_p2_goal()
        if p1_goal and p2_goal:
            reset = True

        #check for game over
        if game_state[0] > 2*to_win or p2_goal:
            print "Player 1 Wins!"
            winner = 1
        elif game_state[1] > 2*to_win or p1_goal:
            print "Player 2 Wins!"
            winner = 2
        elif RESET:
            RESET = False
            winner = 3

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

    start_mindball(hs1, hs2)
    #mindball_loop(hs)

    print 'disconnecting...'
    hs1.disconnect()
    hs1.destroy()
    hs2.disconnect()
    hs2.destroy()
    print 'done'
    sys.exit(0)
    

    
