#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kerin Grewal
lt1_problem2
Python 3
"""



"""DIRECTIONS
Call Simulate() to test results
Make sure the program is in the same directory as lt1pr1.py
"""
from queue import Queue
from lt1pr1 import RandVar


class event:
    def __init__(self, arrivalT, serviceT, serviceStart):
        self.arrivalT = arrivalT
        self.serviceT = serviceT
        self.serviceStart = serviceStart
        
        self.serviceEnd = self.serviceStart+self.serviceT
        self.response = self.serviceEnd - self.arrivalT


def getStats(tasks, lamb):
    
    simTime = tasks[-1].serviceEnd
    
    responseTime = [e.response for e in tasks]
    avg_wait = sum(responseTime)/len(tasks)
    
    service_time = [e.serviceT for e in tasks]
    avg_service = sum(service_time)/len(tasks)
    
    q = lamb*(avg_wait+avg_service)
    w = lamb*avg_wait
    
    Utilization = sum(service_time)/simTime
    print("Results:")
    print("")
    print("Simulation time: ", simTime)
    print("Average wait (Tw): ", avg_wait)
    print("Average service (Ts): ", avg_service)
    print("Average time in system(Tq): ", avg_wait+avg_service)
    print()
    print("Items waiting: ", w)
    print("Items in the system: ", q)
    print("")
    print("Utilization: ", Utilization)
    print("")
    
    
class MM1():
    def simulator(lamb, Ts, finish):
        #set time to zero 
        
        t = 0;
        
        schedule = Queue()
        
        completed = []
        
        while t<finish:
            
            serviceT = RandVar.exp(1/Ts)[1]
            
            #queue is empty, start service right away
            if schedule.empty():
                arrivalT = RandVar.exp(lamb)[1]
                
                serviceStart = arrivalT
                
            #queue is not empty, create a new birth    
            else:
                arrivalT += RandVar.exp(lamb)[1]
            
                completed.append(schedule.get())
                if(arrivalT > completed[-1].serviceEnd):
                    serviceStart = arrivalT
                else:
                    serviceStart = completed[-1].serviceEnd
            
            #Update time
            t = arrivalT    
            
            #Add new event to the queue
            schedule.put(event(arrivalT, serviceT, serviceStart))
            
        getStats(completed, lamb)
        return t
    
def Simulate():
    
    finish = 1000
    lamb = 5.0
    Ts = 0.15
    print("Part A:")
    MM1.simulator(lamb, Ts, finish)
    
    finish = 1000
    lamb = 6.0
    Ts = 0.15
    print("Part D:")
    MM1.simulator(lamb, Ts, finish)
    
    finish = 1000
    lamb = 6.0
    Ts = 0.20
    print("Part E:")
    MM1.simulator(lamb, Ts, finish)
    