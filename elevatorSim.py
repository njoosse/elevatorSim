# -*- coding: utf-8 -*-
"""
Created on Sat Jan 27 13:35:09 2018

@author: njoos
"""

import math
import random
import threading
import time

floors = 10
numberOfRequests = 100

oddsOfKeypress = 20 #1/value 
# 20 -> 5% chance, 4 -> 25% chance

requests = []
order = []
for x in range(numberOfRequests):
    fromFloor = random.randint(1, floors)
    toFloor = random.randint(1, floors)
    while toFloor == fromFloor:
        toFloor = random.randint(1, floors)
    requests.append((fromFloor, toFloor))

keypresses = 0
while keypresses < numberOfRequests:
    val = random.randint(1, oddsOfKeypress)
    if val == 1:
        keypresses += 1
    order.append(val)
    
print len(order)

keypadTime = 1.0
elevTime = 0.5
pending = 0

simTime = 0 

passengerResolutionTimes = []
queue = []

def keypad():
    global pending
    if len(requests) == 0:
        return
    elif order.pop(0) == 1:
        req = requests.pop(0)
        queue.append(Passenger(req[0], req[1]))
        pending += 1
            
requester = threading.Thread(target = keypad, args = ())
requester.daemon = True
requester.start()

def incrementSimTime(additionalTime):
    global simTime
    oldTime = simTime
    simTime += additionalTime
    #print oldTime, simTime
    keypresses = int(simTime/keypadTime) - int(oldTime/keypadTime)
    for k in range(keypresses):
        keypad()
        #print 'pressed'

def openDoors(numberOfPassengersMoving):
    global simTime
    simTime += elevTime*numberOfPassengersMoving/2

class Passenger():
    def getDir(self):
        if self.startFloor > self.endFloor:
            return 'down'
        else:
            return 'up'
    def __init__(self, s, d):
        self.startFloor = s
        self.endFloor = d
        self.startTime = simTime
        self.direction = self.getDir()

class Elevator():
    def __init__(self):
        self.direction = 'up'
        self.currentFloor = 1
        self.destinationFloor = 0
        self.passengers = []
        self.maxPassengers = 1000
        self.minFloor = 0
        self.maxFloor = floors
        self.stopFloors = []

elevA = Elevator()
ongoing = True
simStartTime = time.clock()
onBoard = {}
elev = elevA
while len(requests) + pending > 0:
    remainingSpots = elev.maxPassengers-len(elev.passengers)
#    print elev.currentFloor
    if len(queue) > 0 and len(elev.passengers) == 0:
        elev.destinationFloor = queue[0].startFloor
        incrementSimTime(elevTime*abs(elev.destinationFloor - elev.currentFloor))
        elev.currentFloor = elev.destinationFloor  
    elif elev.currentFloor in elev.stopFloors:
        elev.stopFloors.remove(elev.currentFloor)
        disembarking = filter(lambda p: p.endFloor == elev.currentFloor, elev.passengers)
        disembarkingCount = len(disembarking)
        
        for p in disembarking:
            elev.passengers.remove(p)
            passengerResolutionTimes.append(simTime - p.startTime)
            pending -= 1
        if len(elev.passengers) == 0:
            # can set a new direction based on the current floor
            applicableRequests = filter(lambda r: r.startFloor == elev.currentFloor, queue)
            if len(applicableRequests) > 0:
                elev.direction = applicableRequests[0].direction
                newPassengers = filter(lambda p: p.startFloor == elev.currentFloor\
                                       and p.direction == elev.direction, queue)\
                                       [:remainingSpots]
                for x in range(len(newPassengers)):
                    elev.passengers.append(newPassengers[x])
                    queue.remove(newPassengers[x])
                    if newPassengers[x].endFloor not in elev.stopFloors:
                        elev.stopFloors.append(newPassengers[x].endFloor)
                    
                openDoors(len(newPassengers))
            elif len(queue) > 0:
                elev.destinationFloor = queue[0].startFloor
                incrementSimTime(elevTime*abs(elev.destinationFloor - elev.currentFloor))
                elev.currentFloor = elev.destinationFloor
            else:
                incrementSimTime(elevTime)
        openDoors(disembarkingCount)
    if elev.currentFloor == elev.destinationFloor and len(queue) > 0:
        if len(elev.passengers) == 0:
            embarking = filter(lambda p: p.startFloor == elev.currentFloor and p.direction == queue[0].direction, queue)[:remainingSpots]
        else:
            embarking = filter(lambda p: p.startFloor == elev.currentFloor and p.direction == elev.direction, queue)[:remainingSpots]
        for p in embarking:
            elev.passengers.append(p)
            if p.endFloor not in elev.stopFloors:
                elev.stopFloors.append(p.endFloor)
            queue.remove(p)
        if len(elev.passengers) > 0:
            elev.destinationFloor = elev.passengers[0].endFloor
        else:
            elev.destinationFloor = queue[0].startFloor
        if elev.destinationFloor > elev.currentFloor:
            elev.direction = 'up'
        else:
            elev.direction = 'down'
        incrementSimTime(elevTime*len(embarking)/2)
    else:
        if elev.direction == 'up' and elev.currentFloor < elev.maxFloor:
            elev.currentFloor += 1
        elif elev.direction == 'down' and elev.currentFloor > elev.minFloor:
            elev.currentFloor -= 1
        incrementSimTime(elevTime)
    
print 'Total Resolution Time: {} seconds'.format(simTime)
print 'Average Resolution Time: {} seconds'.format(sum(passengerResolutionTimes)/len(passengerResolutionTimes))
print 'Shortest Resolution Time: {} seconds'.format(min(passengerResolutionTimes))
print 'Longest Resolution Time: {} seconds'.format(max(passengerResolutionTimes))