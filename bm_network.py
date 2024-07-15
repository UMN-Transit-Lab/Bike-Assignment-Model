'''-------------------------------------------------------
*** Bicycle Routing and Assignment Model ***
    Copyright 2023 Alireza Khani
    Contact: akhani@umn.edu or akhani.phd@gmail.com
    Licensed under the GNU General Public License v3.0
-------------------------------------------------------
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    https://www.gnu.org/licenses/gpl-3.0.en.html
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-------------------------------------------------------'''

import random, time, math
import operator

zoneSet = {}
nodeSet = {}
linkSet = {}
demandSet = {}

################################################## Zone Class ##################################################
class Zone:
    'zones in the network'
    zoneCount = 0

    'functions'
    def __init__(self, _zoneId, _transcadId, _area):
        Zone.zoneCount = Zone.zoneCount + 1
        self.zoneId = _zoneId
        self.zoneTranscadId = _zoneId
        self.zoneArea = _area
        self.zoneNodes = []
        self.zoneProduction = {}
        self.zoneAttraction = {}
        self.forwardShortestPaths = {}
        self.forwardHyperPaths = {}
        self.forwardPathSets = {}
    def connectToNode(self, _nodeId):
        self.zoneNodes.append(_nodeId)
    def getArea(self):
        return self.zoneArea
    def getNodes(self):
        return self.zoneNodes
    def getRandomNode(self):
        from random import choice
        return choice(self.zoneNodes)
    def getMinBackwardLabelNode(self):
        tmpMinLabel = 999999
        for tmpNode in self.zoneNodes:
            if nodeSet[tmpNode].getBackwardLabel() < tmpMinLabel:
                tmpMinLabel = nodeSet[tmpNode].getBackwardLabel()
                tmpMinLabelNode = tmpNode
        if tmpMinLabel == 999999:
            from random import choice
            #print ('X')
            return choice(self.zoneNodes)
        else:
            return tmpMinLabelNode
    def getMinForwardLabelNode(self):
        tmpMinLabel = 999999
        for tmpNode in self.zoneNodes:
            if nodeSet[tmpNode].getForwardLabel() < tmpMinLabel:
                tmpMinLabel = nodeSet[tmpNode].getForwardLabel()
                tmpMinLabelNode = tmpNode
        if tmpMinLabel == 999999:
            from random import choice
            #print ('X')
            return choice(self.zoneNodes)
        else:
            return tmpMinLabelNode
    def resetDemand(self):
        self.zoneProduction = {}
        self.zoneAttraction = {}
    def addTripProduction(self, _toZone, _production):
        if _toZone in self.zoneProduction:
            self.zoneProduction[_toZone] = self.zoneProduction[_toZone] + float(_production)
            print ("trip production from", self.zoneID, "to", _toZone, "already added to the zone")
        else:
            self.zoneProduction[_toZone] = float(_production)
    def addTripAttraction(self, _fromZone, _attraction):
        if _fromZone in self.zoneAttraction:
            self.zoneAttraction[_fromZone] = self.zoneAttraction[_fromZone] + float(_attraction)
        else:
            self.zoneAttraction[_fromZone] = float(_attraction)
    def getTotalTripProduction(self):
        ## return sum(self.zoneProduction.itervalues()) ##2023: itervalues renamed to items in py3.4+
        return sum(self.zoneProduction.values())
    def getTotalTripAttraction(self):
        tmpAttraction = 0
        for i in self.zoneAttraction.keys():
            tmpAttraction = tmpAttraction + self.zoneAttraction[i]
        return tmpAttraction        
    def getTripProduction(self, _toZone):
        if _toZone not in self.zoneProduction.keys():
            return 0
        return self.zoneProduction[_toZone]
    def getTripAttraction(self, _fromZone):
        if _fromZone not in self.zoneAttraction.keys():
            return 0
        return self.zoneAttraction[_fromZone]
    ''' From this point is 2023 update to store paths''' 
#    def addForwardShortestPath(self, _destination, _shortestPath):
#        self.forwardShortestPaths[_destination] = _shortestPath
#    def addForwardHyperPath(self, _destination, _hyperpath):
#        self.forwardHyperpaths[_destination] = _hyperpath
    def addPathToTheForwardPathSets(self, _numberOfIterations, _destination, _path, _length, _time):
        if _destination in self.forwardPathSets:
            if str(_path[1]) in self.forwardPathSets[_destination]:
                self.forwardPathSets[_destination][str(_path[1])]['probability'] += 1.0/_numberOfIterations
            else:
                self.forwardPathSets[_destination][str(_path[1])] = {'probability': 1.0/_numberOfIterations, 'nodes': _path[0], 'links': _path[1], 'length': _length, 'time': _time}
        else:
            self.forwardPathSets[_destination] = {}
            self.forwardPathSets[_destination][str(_path[1])] = {'probability': 1.0/_numberOfIterations, 'nodes': _path[0], 'links': _path[1], 'length': _length, 'time': _time}
            #print (self.forwardPathSets)
            
        
        

################################################## Node Class ##################################################
class Node:
    'nodes in the network'
    nodeCount = 0
    minCostNode = ""

    'functions'
    def __init__(self, _nodeId, _name, _type, _lon, _lat):
        Node.nodeCount = Node.nodeCount + 1
        self.nodeId = _nodeId
        self.nodeName = _name
        self.nodeType = _type  ## this should represent the intersection type (major, minor, no, etc.)
        self.nodeLon = float(_lon)/1000000.0  ## (2*float(_lon)-900)
        self.nodeLat = float(_lat)/1000000.0   ## (900.0 - float(_lat))
        self.inLinks = []
        self.outLinks = []
        self.permanent = False
        self.nodeArrivalTime = []
        self.nodeArrivalCost = []
        self.nodePredecessor = []
        self.nodeForwardLink = ''
        self.nodeForwardLabel = 999999
        self.nodeDepartureTime = []
        self.nodeDepartureCost = []
        self.nodeSuccessor = []
        self.nodeBackwardLink = ''
        self.nodeBackwardLabel = 999999
        self.nodeProduction = {}
        self.nodeAttraction = {}
    def getCoordinates(self):
        return self.nodeLon, self.nodeLat
    def getDisplayAttributes(self):
        self.displayAttributes = self.nodeLon-10, self.nodeLat+10, self.nodeLon+10, self.nodeLat-10
        return self.displayAttributes

    def attachLink(self, _linkId, _direction):
        if _direction == "in":
            self.inLinks.append(_linkId)
        else:
            self.outLinks.append(_linkId)
    #def addTripProduction(self, _toNode, _production):
    #    self.nodeProduction[_toNode] = _production
    #def addTripAttraction(self, _fromNode, _attraction):
    #    self.nodeAttraction[_fromNode] = _attraction
    def getInboundLinks(self):
        return self.inLinks
    def getOutboundLinks(self):
        return self.outLinks
    #def getTripProduction(self, _toNode):
    #    return self.nodeProduction[_toNode]
    #def getTripAttraction(self, _fromNode):
    #    return self.nodeAttraction[_fromNode]
    def resetLabels(self):
        self.permanent = False
        self.nodeArrivalTime = []
        self.nodeArrivalCost = []
        self.nodePredecessor = []
        self.nodeForwardLink = []
        self.nodeForwardLabel = 999999
        self.nodeDepartureTime = []
        self.nodeDepartureCost = []
        self.nodeSuccessor = []
        self.nodeBackwardLink = []
        self.nodeBackwardLabel = 999999
    def setForwardLabel(self, _label, _time, _predecessor, _link):
        self.nodeArrivalTime = _time
        self.nodePredecessor = _predecessor
        self.nodeForwardLink = _link
        self.nodeForwardLabel = _label
    def setBackwardLabel(self, _label, _time, _successor, _link):
        self.nodeDepartureTime = _time
        self.nodeSuccessor = _successor
        self.nodeBackwardLink = _link
        self.nodeBackwardLabel = _label
    def getForwardLabel(self):
        return self.nodeForwardLabel
    def getBackwardLabel(self):
        return self.nodeBackwardLabel
    def getForwardTime(self):
        return self.nodeArrivalTime
    def getBackwardTime(self):
        return self.nodeDepartureTime
    def getPredecessor(self):
        return self.nodePredecessor
    def getSuccessor(self):
        return self.nodeSuccessor
    def getForwardLink(self):
        return self.nodeForwardLink
    def getBackwardLink(self):
        return self.nodeBackwardLink
    def printNode(self):
        print ("ID:",self.nodeId, " Name:",self.nodeName, " Type:",self.nodeType, " LON:",self.nodeLon, " LAT:",self.nodeLat, " Inbound:", self.inLinks, " Outbound:", self.outLinks)  
    def makePermanent(self):
        self.permanent = True
    def isPermanent(self):
        return self.permanent
    def isPredecessor(self, _nodeId):
        if _nodeId in self.nodePredecessor:
            return True
        return False
    def isSuccessor(self, _nodeId):
        if _nodeId in self.nodeSuccessor:
            return True
        return False
    def setForwardHyperLabel(self, _label, _time, _cost, _predecessor, _link):
        self.nodeArrivalTime.append(_time)
        self.nodeArrivalCost.append(_cost)
        self.nodePredecessor.append(_predecessor)
        self.nodeForwardLink.append(_link)
        self.nodeForwardLabel = _label
    def setBackwardHyperLabel(self, _label, _time, _cost, _successor, _link):
        self.nodeDepartureCost.append(_time)
        self.nodeDepartureCost.append(_cost)
        self.nodeSuccessor.append(_successor)
        self.nodeBackwardLink.append(_link)
        self.nodeBackwardLabel = _label
    def refineForwardHyperpath(self, _theta, _diffUtility):
        i = 0
        tmpLogSum = 0
        tmpRemovedLinks = []
        while i < len(self.nodeArrivalCost):
            #print self.nodeArrivalCost[i], self.nodeForwardLabel, _diffUtility
            if self.nodeArrivalCost[i] > self.nodeForwardLabel + _diffUtility:
                tmpRemovedLinks = tmpRemovedLinks + [self.nodeForwardLink[i]]
                del self.nodeArrivalTime[i]
                del self.nodeArrivalCost[i]
                del self.nodePredecessor[i]
                del self.nodeForwardLink[i]
            else:
                tmpLogSum = tmpLogSum + math.exp(-_theta*self.nodeArrivalCost[i])
                i = i + 1
        self.nodeForwardLabel = (-1/_theta)*math.log(tmpLogSum)
        return tmpRemovedLinks
        
    def refineBackwardHyperpath(self, _theta, _diffUtility):
        i = 0
        tmpLogSum = 0
        while i < len(self.nodeDepartureCost):
            #print self.nodeDepartureCost[i], self.nodeBackwardLabel, _diffUtility
            if self.nodeDepartureCost[i] > self.nodeBackwardLabel + _diffUtility:
                del self.nodeDepartureTime[i]
                del self.nodeDepartureCost[i]
                del self.nodeSuccessor[i]
                del self.nodeBackwardLink[i]
            else:
                tmpLogSum = tmpLogSum + math.exp(-_theta*self.nodeDepartureCost[i])
                i = i + 1
            self.nodeBackwardLabel = (-1/_theta)*math.log(tmpLogSum)
    def getMinForwardTime(self):
        if len(self.nodeArrivalTime)==0:
            return 999999
        return min(self.nodeArrivalTime)
    def getMinBackwardTime(self):
        if len(self.nodeDepartureTime)==0:
            return 999999
        return min(self.nodeDepartureTime)
    def getMinForwardCost(self):
        if len(self.nodeArrivalCost)==0:
            return 999999
        return min(self.nodeArrivalCost)
    def getMinBackwardCost(self):
        if len(self.nodeDepartureCost)==0:
            return 999999
        return min(self.nodeDepartureCost)
    def getForwardHypernode(self):
        return self.nodePredecessor
    def getBackwardHypernode(self):
        return self.nodeSuccessor
    def getForwardHyperlink(self):
        return self.nodeForwardLink
    def getBackwardHyperlink(self):
        return self.nodeBackwardLink
    def getForwardAlternative(self, _theta, _minProb):
        #print self.nodeId, self.nodePredecessor, self.nodeForwardLink
        tmpAltProb = []
        for i in range(len(self.nodePredecessor)):
            if i==0:
                tmpAltProb = tmpAltProb + [math.exp(-_theta*self.nodeArrivalCost[i])/math.exp(-_theta*self.nodeForwardLabel)]
            else:
                tmpAltProb = tmpAltProb + [tmpAltProb[i-i] + math.exp(-_theta*self.nodeArrivalCost[i])/math.exp(-_theta*self.nodeForwardLabel)]
        #if tmpAltProb[len(tmpAltProb)-1]<1: print tmpAltProb[len(tmpAltProb)-1]
        if len(tmpAltProb)==0: 
            #print ("*****************")
            return None
        tmpRand = random.uniform(0, tmpAltProb[len(tmpAltProb)-1])
        for i in range(len(self.nodePredecessor)):
            if tmpRand <= tmpAltProb[i]:
                return [self.nodePredecessor[i], self.nodeForwardLink[i]]
    def getBackwardAlternative(self, _theta, _minProb):
        #print self.nodeId, self.nodeSuccessor, self.nodeBackwardLink
        tmpAltProb = []
        for i in range(len(self.nodeSuccessor)):
            if i==0:
                tmpAltProb = tmpAltProb + [math.exp(-_theta*self.nodeDepartureCost[i])/math.exp(-_theta*self.nodeBackwardLabel)]
            else:
                tmpAltProb = tmpAltProb + [tmpAltProb[i-i] + math.exp(-_theta*self.nodeDepartureCost[i])/math.exp(-_theta*self.nodeBackwardLabel)]
        tmpRand = random.uniform(0, tmpAltProb[len(tmpAltProb)-1])
        for i in range(len(self.nodeSuccessor)):
            if tmpRand <= tmpAltProb[i]:
                return [self.nodeSuccessor[i], self.nodeBackwardLink[i]]
    def printForwardShortestpathLabels(self):
        print ("ID:",self.nodeId, "Inbound:", self.inLinks, " Outbound:", self.outLinks,
               "ArrivalTime:", self.nodeArrivalTime, "Predecessor:", self.nodePredecessor, 
               "ForwardLink:", self.nodeForwardLink, "ForwardLabel:", self.nodeForwardLabel)  

    def printForwardHyperpathLabels(self):
        print ("ID:",self.nodeId, "Inbound:", #self.inLinks, " Outbound:", self.outLinks,
               "ForwardLabel:", self.nodeForwardLabel)  

################################################## Link Class ##################################################
class Link:
    'links in the network'
    linkCount = 0

    'functions'
    def __init__(self, _token, _rev):
        self.linkId = _token[0]
        self.linkName = _token[1]
        self.linkFromNode = _token[2]
        self.linkToNode = _token[3]
        if _rev == 'reverse1':
            self.linkFromNode = _token[3]
            self.linkToNode = _token[2]
        if _rev == 'reverse2':
            self.linkId = _token[0] + '.1'
            self.linkFromNode = _token[3]
            self.linkToNode = _token[2]
        self.linkType = _token[4]
        self.linkDirection = float(_token[5])
        self.linkLength = float(_token[6])
        self.pathType = _token[7]
        self.surface = _token[8]
        self.speedLimit = float(_token[9])
        self.freeFlowTime = float(_token[10])
#        self.capacity = float(_token[9])
#        self.alpha = float(_token[10])
#        self.beta = float(_token[11])
        self.X1 = nodeSet[self.linkFromNode].getCoordinates()[0]
        self.Y1 = nodeSet[self.linkFromNode].getCoordinates()[1]
        self.X2 = nodeSet[self.linkToNode].getCoordinates()[0]
        self.Y2 = nodeSet[self.linkToNode].getCoordinates()[1]
        self.alreadyUsed = False
        self.flow = 0
        self.auxiliaryFlow = 0
        self.travelTime = self.freeFlowTime
        Link.linkCount = Link.linkCount + 1
    def calculateSpeedAndTime(self):
        self.speed = 9.24 ## constant obtained from regression modeling and fixing some variables 
        self.speed += 0.23*self.linkLength ## speed increase for longer links
        if self.pathType in ['Bike Lane', 'Multi-Use Path -']: ## assuming off-street, so adding full speed increase 
            self.speed += 0.94 
        elif self.pathType in ['Bike Route', 'Paved Shoulder']:  ## assuming semi-off-street, so adding half speed increase 
            self.speed += (0.94 / 2.0)
        else:  ##assuming on-street and deducting the full speed decrease
            self.speed -= 0.32
        ## calculate travel time and add the effect of signalized intersection:
        self.freeFlowTime = self.linkLength / self.speed * 60
        if nodeSet[self.linkToNode].nodeType == 3:
            self.freeFlowTime -= 1.0
        elif nodeSet[self.linkToNode].nodeType == 2:
            self.freeFlowTime -= 0.5
        self.travelTime = self.freeFlowTime
        
    def resetLabels(self):
        self.alreadyUsed = False
    def getFromNode(self):
        return self.linkFromNode
    def getToNode(self):
        return self.linkToNode
    def getLength(self):
        return self.linkLength
    def getCapacity(self):
        return self.capacity
    def getCost(self, _utility):
        tmpCost = self.linkLength*_utility[2]
        '''
        if self.linkType==1:
            tmpCost = tmpCost*_utility[3]
        elif self.linkType==2:
            tmpCost = tmpCost*_utility[4]
        elif self.linkType==2:
            tmpCost = tmpCost*_utility[5]
        '''
        return tmpCost
    def exclude(self):
        self.alreadyUsed = True
    def isExcluded(self):
        return self.alreadyUsed
    def printLink(self):
        print ("ID:",self.linkId, "\tName:",self.linkName, "From:",self.LinkFromNode, "To:",self.linkToNode, "\tLength:",self.linkLength, "\tType:",self.linkType)  
    
    def addFlow(self, _flow):
        self.flow = _flow
    def getFlow(self):
        return round(self.flow,3)
    def resetFlow(self):
        self.flow = 0
    def updateFlow(self, _msaIter):
        self.flow = (_msaIter-1.0)/_msaIter * self.flow + 1.0/_msaIter * self.auxiliaryFlow
    def addAuxiliaryFlow(self, _flow):
        self.auxiliaryFlow = self.auxiliaryFlow + _flow
    def getAuxiliaryFlow(self):
        return round(self.auxiliaryFlow,3)
    def resetAuxiliaryFlow(self):
        self.auxiliaryFlow = 0
    def updateTravelTime(self):
        self.travelTime = self.freeFlowTime * (1+self.alpha*(self.flow/self.capacity)**self.beta)
    def getTravelTime(self):
        return round(self.travelTime,3)
    def calculateLinkIntegral(self):
        tmpIntegral = 1.0/60 * (self.freeFlowTime*self.flow + 1.0/(self.beta+1.0)*self.alpha*(self.flow/self.capacity)**(self.beta+1.0))
        return tmpIntegral

    
################################################## Reading Input Data ##################################################
def readNodes(_networkName):
    ''' Reads nodes from a text (.dat) file and creates Node objects '''
    inFile = open(_networkName+"input_nodes.csv", "r")
    tmpIn = inFile.readline()
    while (1):
        tmpIn = inFile.readline()
        if tmpIn == "": break
        token = tmpIn.split(',')
        tmpNodeId = token[0]
        #nodeList.append(tmpNodeId)
        ''' Here it creates a Node object and adds it to the set NodeSet '''
        nodeSet[tmpNodeId] = Node(token[0],token[1],token[2],token[3],token[4])
    inFile.close()
    return len(nodeSet) #bm_network.Node.nodeCount

def readLinks(_networkName):
    ''' Reads links from a text (.dat) file and creates Link objects '''
    inFile = open(_networkName+"input_links.csv", "r")
    tmpIn = inFile.readline()
    while (1):
        tmpIn = inFile.readline()
        if tmpIn == "": break
        token = tmpIn.split(',')
        tmpLinkId = token[0]
        tmpDir = int(token[5])
        if(tmpDir==1):
            ''' Seems like TransCAD direction ID, ''forward'', create a forward link '''
            linkSet[tmpLinkId] = Link(token, '')
            tmpFromNode = token[2]
            tmpToNode = token[3]
            nodeSet[tmpFromNode].attachLink(tmpLinkId, "out")
            nodeSet[tmpToNode].attachLink(tmpLinkId, "in")
        elif(tmpDir==-1):
            ''' Seems like TransCAD direction ID, ''reverse'', create an opposite direction link  '''
            linkSet[tmpLinkId] = Link(token, 'reverse1')
            tmpFromNode = token[3]
            tmpToNode = token[2]
            nodeSet[tmpFromNode].attachLink(tmpLinkId, "out")
            nodeSet[tmpToNode].attachLink(tmpLinkId, "in")
        else:
            ''' Seems like TransCAD direction ID, ''bidirectional'', careate two links in forward and opposite direction  '''
            linkSet[tmpLinkId] = Link(token, '')
            tmpFromNode = token[2]
            tmpToNode = token[3]
            nodeSet[tmpFromNode].attachLink(tmpLinkId, "out")
            nodeSet[tmpToNode].attachLink(tmpLinkId, "in")
            #create the reverse link too
            linkSet[tmpLinkId+'.1'] = Link(token, 'reverse2')
            tmpFromNode = token[3]
            tmpToNode = token[2]
            nodeSet[tmpFromNode].attachLink(tmpLinkId+'.1', "out")
            nodeSet[tmpToNode].attachLink(tmpLinkId+'.1', "in")
    inFile.close()
    return len(linkSet) #Link.linkCount

def calculateLinkSpeeds():
    for tmpLinkId in linkSet.keys():
        linkSet[tmpLinkId].calculateSpeedAndTime()

def refineNodes():
    ''' Checks for nodes that are NOT CONNECTED to any links and removes them '''
    nodesToBeRemoved = []
    for tmpNode in nodeSet.keys():
        tmpInLinks = nodeSet[tmpNode].getInboundLinks()
        tmpOutLinks = nodeSet[tmpNode].getOutboundLinks()
        if tmpInLinks==[] and tmpOutLinks==[]:
            nodesToBeRemoved.append(tmpNode)
    for tmpNode in nodesToBeRemoved:
        del nodeSet[tmpNode]
    if len(nodesToBeRemoved) > 0:
        print (len(nodesToBeRemoved), 'nodes are NOT CONNECTED and removed')
    return len(nodeSet) #bm_network.Node.nodeCount

def readZones(_networkName):
    ''' Reads zones (connedtors?) from a text (.dat) file and creates Zone objects '''
    inFile = open(_networkName+"input_zones.csv", "r")
    tmpIn = inFile.readline()
    #i = 1
    while (1):
        tmpIn = inFile.readline()
        if tmpIn == "": break
        token = tmpIn.split(',')
        tmpZoneId = token[0]
        tmpNodeId = token[1]
        tmpTranscadId = token[2]
        tmpArea = float(token[3])
        ''' Here it creates a Zone object if it's not already in ZoneSet' '''
        if tmpZoneId not in zoneSet:#.keys():
            zoneSet[tmpZoneId] = Zone(tmpZoneId, tmpTranscadId, tmpArea)
        ''' Then it connects the Zone object to the given (accessible) nodes 
        Note that a zone may be connected to more than one node, and they appear in multiple rows of the input zone file '''
        if tmpNodeId in nodeSet:#.keys():
            zoneSet[tmpZoneId].connectToNode(tmpNodeId);
            #i = i+1
    inFile.close()
    return len(zoneSet) #bm_network.Zone.zoneCount, i

def refineZones():
    ''' Checks for zones that are NOT CONNECTED to any nodes and removes them '''
    zonesToBeRemoved = []
    for tmpZone in zoneSet.keys():
        tmpNodes = zoneSet[tmpZone].getNodes()
        if tmpNodes==[]:
            zonesToBeRemoved.append(tmpZone)
    for tmpZone in zonesToBeRemoved:
        del zoneSet[tmpZone]
    if len(zonesToBeRemoved) > 0:
        print (len(zonesToBeRemoved), 'zones are NOT CONNECTED and removed')
    return len(zoneSet) #bm_network.Zone.zoneCount

