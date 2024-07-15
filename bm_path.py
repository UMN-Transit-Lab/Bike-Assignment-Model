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
import heapq
import bm_network
################################################## Path Algorithm Class ##################################################
class PathAlgorithm:
    utilityParameters = []

    def __init__(self):
        self.travelTime = 0
        self.travelCost = 0
        self.pathSet = {}
    def getMinForwardLabelNode(self):
        minLabel = 999999
        for node in bm_network.nodeSet:
            bm_network.nodeSet[node].getForwardLabel()
    def readUtilityParameters(self, _filePath):
        inFile = open(_filePath+"input_routeChoice.dat", "r")
        self.utilityParameters = []
        tmpIn = inFile.readline()
        while (1):
            tmpIn = inFile.readline()
            if tmpIn == "": break
            self.utilityParameters = self.utilityParameters + [float(tmpIn.split()[0])]
        inFile.close()
        return self.utilityParameters
        
################################################## Shortest Paths ##################################################
    def findForwardShortestPath(self, _origin, _skim):
        for node in bm_network.nodeSet:
            bm_network.nodeSet[node].resetLabels()
        SE = []
        #tmpNode = bm_network.zoneSet[_origin].getRandomNode()                             #;print tmpOrigNodes
        #bm_network.nodeSet[tmpNode].setForwardLabel(0,0,"","")
        #heapq.heappush(SE, (bm_network.nodeSet[tmpNode].getForwardLabel(), tmpNode))
        tmpOrigNodes = bm_network.zoneSet[_origin].getNodes()                             #;print tmpOrigNodes
        for tmpNode in tmpOrigNodes:
            bm_network.nodeSet[tmpNode].setForwardLabel(0,0,"","")
            heapq.heappush(SE, (bm_network.nodeSet[tmpNode].getForwardLabel(), tmpNode))
        tmpIter = 0
        while len(SE)!=0:
            tmpIter = tmpIter + 1
            tmpTuple = heapq.heappop(SE)
            currentNode = tmpTuple[1]
            currentTime = bm_network.nodeSet[currentNode].getForwardTime()
            currentLabel = bm_network.nodeSet[currentNode].getForwardLabel()
            #if _skim==1 and currentTime >= 600: continue
            tmpLinkList = bm_network.nodeSet[currentNode].getOutboundLinks()
            for adjLink in tmpLinkList:
                newNode = bm_network.linkSet[adjLink].getToNode()
                oldTime = bm_network.nodeSet[newNode].getForwardTime()
                oldLabel = bm_network.nodeSet[newNode].getForwardLabel()
                newTime = currentTime + bm_network.linkSet[adjLink].getTravelTime()
                newLabel = currentLabel + bm_network.linkSet[adjLink].getCost(self.utilityParameters)
                if newLabel < oldLabel:
                    bm_network.nodeSet[newNode].setForwardLabel(newLabel, newTime, currentNode, adjLink)
                    heapq.heappush(SE, (bm_network.nodeSet[newNode].getForwardLabel(), newNode))
        return tmpIter
    def getForwardShortestPath(self, _origin, _destination):
        '''use this line only if the destination is a node and not a zone'''
        ## shortestPathNodes = [_destination]
        #currentNode = bm_network.zoneSet[_destination].getRandomNode()
        currentNode = bm_network.zoneSet[_destination].getMinForwardLabelNode()                       
        shortestPathNodes = [currentNode]
        shortestPathLinks = []
        while currentNode!=_origin:
            newLink = bm_network.nodeSet[currentNode].getForwardLink()
            if newLink=='':
                break
            newNode = bm_network.linkSet[newLink].linkFromNode
            shortestPathLinks.insert(0, newLink)
            shortestPathNodes.insert(0, newNode)

            #if shortestPathLinks == "":
            #    shortestPathLinks =  newLink
            #else:
            #    shortestPathLinks =  newLink + "," + shortestPathLinks
            #currentNode = bm_network.nodeSet[currentNode].getPredecessor()
            currentNode = newNode
        return [shortestPathNodes, shortestPathLinks]
################################################## Hyperpaths ##################################################
    def findForwardHyperpath(self, _origin, _skim):
        'Find path choice set in forward pass'
        minProb = self.utilityParameters[0]
        theta = self.utilityParameters[1]
        diffUtility = (1/theta)*math.log((1-minProb)/minProb)                                                           #;print diffUtility
        for node in bm_network.nodeSet:
            bm_network.nodeSet[node].resetLabels()
        for link in bm_network.linkSet:
            bm_network.linkSet[link].resetLabels()
        SE = []
        tmpOrigNodes = bm_network.zoneSet[_origin].getNodes()                                                           #;print tmpDestNodes
        for tmpNode in tmpOrigNodes:
            bm_network.nodeSet[tmpNode].setForwardHyperLabel(0,0,0,"","")
            heapq.heappush(SE, (bm_network.nodeSet[tmpNode].getForwardLabel(), tmpNode))
        tmpIter = 0
        while len(SE)!=0:
            tmpIter = tmpIter + 1
            tmpTuple = heapq.heappop(SE)
            currentNode = tmpTuple[1]                                                                                   #;print currentNode
            currentTime = bm_network.nodeSet[currentNode].getMinForwardTime()
            currentLabel = bm_network.nodeSet[currentNode].getForwardLabel()
            ### Why skipping trips > 360 when skimming? What is the unit of 360? 
            ## if _skim==1 and currentTime >= 360: continue

            #if bm_network.nodeSet[currentNode].isPermanent():   continue
            #bm_network.nodeSet[currentNode].makePermanent()
            tmpLinkList = bm_network.nodeSet[currentNode].getOutboundLinks()
            for adjLink in tmpLinkList:
                ### Seems like this skipping is for links already in the hyperpath, because it's a label correcting algorithm? 
                if bm_network.linkSet[adjLink].isExcluded(): continue
                newNode = bm_network.linkSet[adjLink].getToNode()
                oldTime = bm_network.nodeSet[newNode].getMinForwardTime()
                oldLabel = bm_network.nodeSet[newNode].getForwardLabel()
                ### What is this skipping for? 
                if currentNode in bm_network.zoneSet[_origin].getNodes() and newNode in bm_network.zoneSet[_origin].getNodes(): continue
                newTime = currentTime + bm_network.linkSet[adjLink].getCost(self.utilityParameters)
                newCost = currentLabel + bm_network.linkSet[adjLink].getCost(self.utilityParameters)
                newLabel = (-1/theta)*math.log(math.exp(-theta*oldLabel)+math.exp(-theta*newCost))
                if newCost < oldLabel + diffUtility:
                    ### if the link returns back to the predecessor
                    if bm_network.nodeSet[currentNode].isPredecessor(newNode):
                        continue 
                        
                    bm_network.linkSet[adjLink].exclude()
                    bm_network.nodeSet[newNode].setForwardHyperLabel(newLabel, newTime, newCost, currentNode, adjLink)
                    tmpRemovedLinks = bm_network.nodeSet[newNode].refineForwardHyperpath(theta, diffUtility)
                    heapq.heappush(SE, (bm_network.nodeSet[newNode].getForwardLabel(), newNode))
                    #for tmpRemovedLink in tmpRemovedLinks:
                    #    bm_network.linkSet[tmpRemovedLink].resetLabels()
        return tmpIter
    def getForwardElementaryPath(self, _origin, _destination):
        minProb = self.utilityParameters[0]
        theta = self.utilityParameters[1]
        diffUtility = (-1/theta)*math.log((1-minProb)/minProb)
        elementaryPathLinks = []
        elementaryPathNodes = [_destination]
        #currentNode = bm_network.zoneSet[_destination].getRandomNode()
        currentNode = bm_network.zoneSet[_destination].getMinForwardLabelNode()
        prevNode = ""
        while currentNode!="":
            j=0
            while j<10:
                newAlt = bm_network.nodeSet[currentNode].getForwardAlternative(theta, minProb)                            #;print newAlt
                if newAlt != None:
                    if newAlt[1] == "":
                        break
                    else:
                        #print (prevNode, currentNode, newAlt, bm_network.linkSet[newAlt[1]].linkFromNode, bm_network.linkSet[newAlt[1]].linkToNode)
                        #time.sleep(1)
                        #if newAlt[0]!=prevNode:
                        if newAlt[0] not in elementaryPathNodes:
                            ''' This means that a next node it found that is not already in the path (i.e., it doesn't create a loop).
                            Therefore, exit the while loop and proceed. '''
                            break
                        else:
                            ''' The node already in the path, so creates a loop. Void it and go to next j to select another node probabilisitically.'''
                            newAlt = None
                j=j+1

            if newAlt==None:
                return ['NA', 'NA']
                
            newNode = newAlt[0]
            newLink = newAlt[1]
            elementaryPathLinks.insert(0, newLink)
            elementaryPathNodes.insert(0, newNode)
            #if elementaryPathLinks == []:
            #    elementaryPathLinks = newLink
            #else:
            #    elementaryPathLinks = newLink + "," + elementaryPathLinks
            if  newNode == _origin:
                break
            else:
                prevNode = currentNode
                currentNode = newNode
#        return [elementaryPathNodes, elementaryPathLinks]    ### This is the complete one before using Zones in MAG 2024 work
        return [elementaryPathNodes[1:], elementaryPathLinks[1:]]
    
################################################## Other Path Functions ##################################################
    def getPathCost(self, _path):
        pathCost = 0
        for tmpLink in _path.split(','):
            if tmpLink==',': continue
            #pathCost = pathCost + bm_network.linkSet[tmpLink].getLength()
            pathCost = pathCost + bm_network.linkSet[tmpLink].getCost(self.utilityParameters)
        return pathCost
    def resetPathSet(self):
        pathSet = {}
    def addPathFlow(self, _OD, _path, _cost, _flow):
        if _path in self.pathSet:
            self.pathSet[_path] = (_OD, _cost, self.pathSet[_path][2] + _flow)
        else:
            self.pathSet[_path] = (_OD, _cost, _flow)
    def calculateLinkFlow(self):
        for tmpLink in bm_network.linkSet:
            bm_network.linkSet[tmpLink].resetFlow()
        tmpPathSet = self.pathSet
        for tmpPath in tmpPathSet:
            tmpFlow = tmpPathSet[tmpPath][2]
            for tmpLink in tmpPath.split(','):
                bm_network.linkSet[tmpLink].addFlow(tmpFlow)
