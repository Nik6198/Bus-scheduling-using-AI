class Bus:
    def __init__(self,route,capacity,currStation):
        self.route = route
        self.capacity = capacity
        self.currentCount = 0
        self.currStation = currStation

    def getCapacity(self):
        return self.capacity

    def getCurrentCount(self):
        return self.currentCount

    def arrive(self,people):
        self.currentCount += people     

    #def __str__(self):
    #    return str(self.__class__) + ": " + str(self.__dict__)
    def __str__(self):
        return "route: "+str(self.route)+" currentCount:"+str(self.currentCount)+" currStation:"+self.route.route[self.currStation]
