"""
The task is to simulate an M/M/k system with a single queue. 
Complete the skeleton code and produce results for three experiments.
The study is mainly to show various results of a queue against its ro parameter. 
ro is defined as the ratio of arrival rate vs service rate. 
For the sake of comparison, while plotting results from simulation, also produce the analytical results. 
"""

import heapq
import random
import matplotlib.pyplot as plt

# Parameters
class Params:
    def __init__(self, lambd, mu, k):        
        self.lambd = lambd 
        self.mu = mu
        self.k = k

# States and statistical counters        
class States:
    def __init__(self):
        
        # States
        self.aqueue = []
        self.dqueue = []
        self.server_state = 0
        self.current_queue_member = 0
        self.prev_time = 0
        self.cout = 0
        
        # Statistics
        self.util = 0.0         
        self.avgQdelay = 0.0
        self.avgQlength = 0.0
        self.served = 0

    def update(self, sim, event):
        if event.eventType == 'DEPARTURE':
            if len(self.aqueue) > 0:
                self.served += 1
                self.dqueue.append(event.eventTime)
                service_arrival = self.aqueue.pop(0)
                service_departure = self.dqueue.pop(0)
                self.avgQdelay += service_departure - service_arrival
                print('Delay is ', service_departure - service_arrival, self.cout)
                self.cout += 1
        elif event.eventType == 'ARRIVAL':
            #we are always appending the arrivals
            self.aqueue.append(event.eventTime)
        self.avgQlength += self.current_queue_member * (event.eventTime - self.prev_time)
        self.util += self.server_state * (event.eventTime - self.prev_time)
        self.prev_time = event.eventTime

    def finish(self, sim):
        self.avgQdelay = self.avgQdelay/self.served
        self.avgQlength = self.avgQlength/sim.now()
        self.util = self.util/(sim.now() * sim.params.k)
        
    def printResults(self, sim):
        # DO NOT CHANGE THESE LINES
        print ('MMk Results: lambda = %lf, mu = %lf, k = %d' %(sim.params.lambd, sim.params.mu, sim.params.k))
        print ('MMk Total customer served: %d' %(self.served))
        print ('MMk Average queue length: %lf' %(self.avgQlength))
        print ('MMk Average customer delay in queue: %lf' %(self.avgQdelay))
        print ('MMk Time-average server utility: %lf' %(self.util))
        
    def getResults(self, sim):
        return (self. avgQlength, self.avgQdelay, self.util)
   
class Event:
    def __init__(self, sim):
        self.eventType = None
        self.sim = sim
        self.eventTime = None
        
    def process(self, sim):
        raise Exception('Unimplemented process method for the event!')
    
    def __repr__(self):
        return self.eventType

class StartEvent(Event):
    def __init__(self, eventTime, sim):
        self.eventTime = eventTime
        self.eventType = 'START'
        self.sim = sim
        
    def process(self, sim):
        self.sim.states.server_state += 1
        sim.scheduleEvent(ArrivalEvent(sim.now(), sim))
        sim.scheduleEvent(DepartureEvent(sim.now() + random.expovariate(sim.params.mu), sim))

class ExitEvent(Event):
    def __init__(self, eventTime, sim):
        self.eventTime = eventTime
        self.eventType = 'EXIT'
        self.sim = sim
    
    def process(self, sim):
        self.sim.states.server_state = 0

                                
class ArrivalEvent(Event):        
    def __init__(self, eventTime, sim):
        self.eventTime = eventTime
        self.eventType = 'ARRIVAL'
        self.sim = sim

    def process(self, sim):
        if self.sim.states.served == sim.count:
            sim.scheduleEvent(ExitEvent(sim.now(), sim))
        else:
            sim.scheduleEvent(ArrivalEvent(sim.now() + random.expovariate(sim.params.lambd), sim))
            if self.sim.states.server_state < self.sim.params.k:
                self.sim.states.server_state += 1
                sim.scheduleEvent(DepartureEvent(sim.now() + random.expovariate(sim.params.mu), sim))
                #print('Served People ', self.sim.states.served)
            else:
                self.sim.states.current_queue_member += 1


class DepartureEvent(Event):
    def __init__(self, eventTime, sim):
        self.eventTime = eventTime
        self.eventType = 'DEPARTURE'
        self.sim = sim

    def process(self, sim):
        #print('Served People ', self.sim.states.served)
        if self.sim.states.served == sim.count:
            sim.scheduleEvent(ExitEvent(sim.now(), sim))
        else:
            if self.sim.states.current_queue_member > 0:
                self.sim.states.current_queue_member -= 1
                sim.scheduleEvent(DepartureEvent(sim.now() + random.expovariate(sim.params.mu), sim))
            else:
                self.sim.states.server_state -= 1


class Simulator:
    def __init__(self, seed, count):
        self.eventQ = []
        self.simclock = 0   
        self.seed = seed
        self.params = None
        self.states = None
        self.count = count
        self.isExit = 'NOTEXIT'
        
    def initialize(self):
        self.simclock = 0        
        self.scheduleEvent(StartEvent(0, self))
        #self.scheduleEvent(ExitEvent(self.duration, self))
        
    def configure(self, params, states):
        self.params = params
        self.states = states
            
    def now(self):
        return self.simclock
        
    def scheduleEvent(self, event):
        heapq.heappush(self.eventQ, (event.eventTime, event))        
    
    def run(self):
        random.seed(self.seed)        
        self.initialize()
        
        while (1):
            while len(self.eventQ) > 0:
                time, event = heapq.heappop(self.eventQ)
                if event.eventType == 'EXIT':
                    self.isExit = 'EXIT'
                    break
                self.states.update(self, event)
                print (event.eventTime, 'Event', event)
                self.simclock = event.eventTime #Updating Simulation Clock
                event.process(self)
            if self.isExit == 'EXIT':
                break
            elif len(self.eventQ) == 0:
                self.scheduleEvent(ArrivalEvent(self.now() + random.expovariate(self.params.lambd), self))
            #self.arrival_count += 1
        self.states.finish(self)
    
    def printResults(self):
        self.states.printResults(self)
        
    def getResults(self):
        return self.states.getResults(self)
        

def experiment1():
    seed = 101
    sim = Simulator(seed,100)
    sim.configure(Params(5.0/60, 8.0/60, 1), States())
    sim.run()
    sim.printResults()


def experiment2():
    seed = 110
    mu = 1000.0 / 60
    ratios = [u / 10.0 for u in range(1, 11)]

    avglength = []
    avgdelay = []
    util = []
    
    for ro in ratios:
        sim = Simulator(seed,100)
        sim.configure(Params(mu * ro, mu, 1), States())    
        sim.run()
        sim.printResults()
        length, delay, utl = sim.getResults()
        avglength.append(length)
        avgdelay.append(delay)
        util.append(utl)

    plt.figure(1)
    plt.subplot(311)
    plt.plot(ratios, avglength)
    plt.xlabel('Ratio (ro)')
    plt.ylabel('Avg Q length')    

    
    plt.subplot(312)
    plt.plot(ratios, avgdelay)
    plt.xlabel('Ratio (ro)')
    plt.ylabel('Avg Q delay (sec)')    

    plt.subplot(313)
    plt.plot(ratios, util)
    plt.xlabel('Ratio (ro)')
    plt.ylabel('Util')    
    
    plt.show()			




def experiment3():
	# Similar to experiment2 but for different values of k; 1, 2, 3, 4
    seed = 110
    mu = 1000.0 / 60
    ratios = [u / 10.0 for u in range(1, 11)]
    ks = [1,2,3,4]
    avglength = []
    avgdelay = []
    util = []
    for i in range(0,4):
        avglength.append([])
        avgdelay.append([])
        util.append([])
    for k in ks:
        for ro in ratios:
            sim = Simulator(seed, 10)
            sim.configure(Params(mu * ro, mu, k), States())
            sim.run()
            sim.printResults()
            lengths, delays, utls = sim.getResults()
            avglength[k-1].append(lengths)
            avgdelay[k-1].append(delays)
            util[k-1].append(utls)

    plt.figure(1)
    for k in ks:
        plt.subplot(311)
        plt.plot(ratios, avglength[k-1])
        plt.xlabel('Ratio (ro)')
        plt.ylabel('Avg Q length')
    for k in ks:
        plt.subplot(312)
        plt.plot(ratios, avgdelay[k-1])
        plt.xlabel('Ratio (ro)')
        plt.ylabel('Avg Q delay (sec)')
    for k in ks:
        plt.subplot(313)
        plt.plot(ratios, util[k-1])
        plt.xlabel('Ratio (ro)')
        plt.ylabel('Util')

    plt.show()



def main():
    #experiment1()
    #experiment2()
    experiment3()

          
if __name__ == "__main__":
    main()