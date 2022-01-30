import random
import requests
from imageai.Detection import ObjectDetection
import os
import argparse
from data-models.Station import Station
from data-models.Bus import Bus
from data-models.BusRoute import BusRoute
import tensorflow as tf
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

class Schedule:
    def __init__(self):
        self.detector = ObjectDetection()
        self.nameToStationMap = {}
        self.busRoutes = []
        self.buses = {}
        self.parser = argparse.ArgumentParser()
    
    def initialiseModel(self):
        execution_path = os.getcwd()
        self.detector.setModelTypeAsRetinaNet()
        self.detector.setModelPath( os.path.join(execution_path , "count-detection-model\resnet50_coco_best_v2.0.1.h5"))
        self.detector.loadModel()
        self.parser.add_argument("-r","-send request",default=False,type=bool)
        self.parser.add_argument("-n","-no of iterations",default=15,type=int)
        self.parser.add_argument("-d","-debug",default=False,type=bool)
        self.parser.add_argument("-x","-aggregrate percentage",default=50,type=int)
        self.args = args = vars(self.parser.parse_args())

    def println(self,out):
        if self.args['d'] :
            print(out)

    def setUp(self,fileName):
        with open(fileName) as file:
            
            line = file.readline()

            #skipping comments
            while line[0] is '#':
                line = file.readline()

            noOfStations = int(line)
            
            for i in range(noOfStations):
                line = file.readline()
                name,peopleCount = line.split()
                #read image
                filename = 's1.jpeg'
                if(peopleCount[0]=='#'):
                    img_path = peopleCount[1:]
                    filename = img_path
                    execution_path = os.getcwd()
                    custom_objects = self.detector.CustomObjects(person=True, car=False)
                    detections = self.detector.detectCustomObjectsFromImage(input_image=os.path.join(execution_path , img_path ), output_image_path=os.path.join(execution_path , img_path+"_new.png"), custom_objects=custom_objects, minimum_percentage_probability=45)
                    self.println("Getting head counts for station "+name+" "+str(len(detections)))
                    peopleCount = len(detections)

                station = Station(name,int(peopleCount),img_path)
                self.nameToStationMap[name] = station
            line = file.readline()
            
            noOfRoutes = int(line)

            for i in range(noOfRoutes):
                line = file.readline()
                id,route = line.split()
                route = route. split(',')
                busRoute = BusRoute(id,route)
                self.busRoutes.append(busRoute)
    
    def schedule(self):
        for i in range(self.args['n']):

            congestedStation = None
            congestRoute = None
            maxCost = -999999
            
          
            
            #bus state
            for key in self.buses.keys():
                self.println(key+" "+str(self.buses[key]))
                temp_dict = {}
                for b in range(len(self.buses[key])):
                    print("\n\nCurrent buses on path are ::"+str(self.buses[key][b]))

                    #bus moves ahead
                    if( random.random() > .5):
                        
                        
                        #people get on bus
                        currStation = self.nameToStationMap[self.buses[key][b].route.route[self.buses[key][b].currStation]]
                        totalPeople = currStation.peopleCount
                        peopleArriving = random.randint(0,max(1,min(currStation.peopleCount,self.buses[key][b].capacity-self.buses[key][b].currentCount))) 
                        print("People entering bus "+str(self.buses[key][b])+" are : "+str(peopleArriving))
                        currStation.updatePeopleCount((currStation.peopleCount-peopleArriving))
                        self.nameToStationMap[self.buses[key][b].route.route[self.buses[key][b].currStation]] =currStation

                        self.println("Bus moved ahead")
                        temp = self.buses[key][b]
                        temp.currStation += 1
                        if temp.currStation == len(temp.route.route):
                            temp_dict[b]=b
                            continue
                        temp.currentCount += peopleArriving
                        self.buses[key][b] = temp 

                        #update rank
                        
                        if totalPeople <= 0:
                            totalPeople = 1
                        rank = peopleArriving/totalPeople
                        busRoute = self.buses[key][b].route
                        busRoute.score += rank
                        self.buses[key][b].route = busRoute
                temp = self.buses[key]
                for k in temp_dict.keys():
                    temp.remove(temp[k])
                self.buses[key] = temp

            #station state
            for s in self.nameToStationMap.keys():
                if(random.random() > 0.8 ):
                    newPeople = random.randint(0,10)
                    temp = self.nameToStationMap[s]
                    self.println("new people "+str(newPeople)+"arrived at "+str(temp))
                    temp.peopleCount += newPeople
                    self.nameToStationMap[s] = temp
                self.println("Station state:"+str(self.nameToStationMap[s]))


            if(i%2 != 0):
                continue        
            
            for busRoute in self.busRoutes:
                self.println("Printing routes")
                self.println(str(busRoute))
                self.println("Cost of route")
                cost,station=busRoute.calculateCostOfRoute(self.nameToStationMap)
                self.println(str(cost)+" "+station.getName())
                
                #cal curr busRoute penatly
                noOfBusesOnRoad = 0
                if self.buses.get(busRoute.id) != None:
                    noOfBusesOnRoad =len(self.buses.get(busRoute.id))
                currBusPenalty = 0.05*noOfBusesOnRoad
                avgcost = cost / (30*len(busRoute.route))
                self.println(str(avgcost)+" "+station.getName())

                if avgcost - currBusPenalty  > maxCost:
                    maxCost = avgcost - currBusPenalty
                    congestRoute = busRoute
                    congestedStation = station
            
            
            
            capacity = 40
            data = {
                "number" : congestRoute.id,
                "name" : congestRoute.route[0]+" to "+congestRoute.route[len(congestRoute.route)-1],
                "to" : congestRoute.route[len(congestRoute.route)-1],
                "from" : congestRoute.route[0], 
                "congestion" : cost,
                "max" : station.getName(),
                "imgsrc":station.image
            }
            API_ENDPOINT = "http://172.52.84.22:3001/api/upload/fetchRelease"
            if self.args['r']:
                r = requests.post(url = API_ENDPOINT, data = data) 
                print(r)
            bus = Bus(congestRoute,capacity,0)
            print("Sending new bus "+str(bus))
            if self.buses.get(congestRoute.id) == None:
                self.buses[congestRoute.id] = [bus]
            else:
                temp = self.buses[congestRoute.id]
                temp.append(bus)
                self.buses[congestRoute.id] = temp
               


            print("Congested station "+str(congestedStation))



main = Schedule()
main.initialiseModel()
main.setUp("input")
main.schedule()

# score = rank + curr no of buses + peoplenentering + cost