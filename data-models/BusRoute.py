class BusRoute:
    def __init__(self,id,route):
        self.id = id
        self.route = route
        self.score = 1
        self.maxCount = 5

    def __str__(self):
        return "id:"+self.id+" score: "+str(self.score)+" route:"+str(self.route)
  
    def calculateCostOfRoute(self,nameToStationMap):
        cost = 0
        maxPoplulatedStation = None
        maxPoplulation = -1

        for station in self.route:
            currStation = nameToStationMap[station]

            cost += currStation.getPeopleCount()

            if maxPoplulation < currStation.getPeopleCount():
                maxPoplulation = currStation.getPeopleCount()
                maxPoplulatedStation = currStation

        return [cost,maxPoplulatedStation]
