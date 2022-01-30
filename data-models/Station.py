
class Station:
    def __init__(self,name,peopleCount,imgfile="s1.jpeg"):
        self.peopleCount = peopleCount
        self.name = name
        self.next = []
        self.image = imgfile
    
    def getPeopleCount(self):
        return self.peopleCount

    def getName(self):
        return self.name

    def addNeighbours(self,neighbour):
        self.next.append(neighbour)
    
    def updatePeopleCount(self,newPeopleCount):
        self.peopleCount = max(0,newPeopleCount)


    def depart(self,departingPeople):
        self.updatePeopleCount(self.peopleCount-departingPeople)
    
    def __str__(self):
        return "name: "+self.name+" peopleCount:"+str(self.peopleCount)