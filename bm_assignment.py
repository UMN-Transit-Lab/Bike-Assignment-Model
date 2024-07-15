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

import time
import math
import random
import bm_network
import bm_path

def readDemand(_filePath):
    ''' Reads trip demand for origin-destinations from a text (.dat) file and add them to th '''
    inFile = open(_filePath+"input_demand.dat", "r")
    tmpIn = inFile.readline()
    tmpTotalDemand = 0
    while (1):
        tmpIn = inFile.readline()
        if tmpIn == "": break
        token = tmpIn.split()
        tmpFromZone = token[0]
        tmpToZone = token[1]
        tmpDemand = float(token[2])
        tmpTotalDemand = tmpTotalDemand + tmpDemand
        if tmpFromZone not in bm_network.zoneSet:
            print ("Zone", tmpFromZone, "is not in 'zoneSet' but has production demand", tmpDemand)
            continue
        if tmpToZone not in bm_network.zoneSet:
            print ("Zone", tmpToZone, "is not in 'zoneSet' but has attraction demand", tmpDemand)
            continue
        bm_network.zoneSet[tmpFromZone].addTripProduction(tmpToZone, tmpDemand)
        bm_network.zoneSet[tmpToZone].addTripAttraction(tmpFromZone, tmpDemand)
    inFile.close()
    return round(tmpTotalDemand)

####################################### GENERATING SKIM ####################################################
def generateSkimTable(_filePath):
    pathFinder = bm_path.PathAlgorithm()
    #pathFinder.readUtilityParameters()
    pathFinder.resetPathSet()
    outFile = open(_filePath+"output_skim_time.dat", "w")
    outFile.write('Origin\tDestination\tTime\n')
    startTime = time.time()
    i=0
    for orig in bm_network.zoneSet:
        i=i+1
        if i%1000==0: print ("* Assigning the",i,"th row. Time elapsed =", round(time.time()-startTime,2), "seconds.")
        pathFinder.findForwardShortestPath(orig, 1)
        tmpInternalTime = math.sqrt(bm_network.zoneSet[orig].getArea())/10*60 # divide by 10mph speed and convert to minutes
        for dest in bm_network.zoneSet:
            tmpAveTime = 999999
            tmpAveCost = 999999
            j = 0
            tmpNodes = bm_network.zoneSet[dest].getNodes()
            for tmpNode in tmpNodes:
                tmpTime = bm_network.nodeSet[tmpNode].getForwardTime()
                tmpCost = bm_network.nodeSet[tmpNode].getForwardLabel()
                if tmpCost>=999999:
                    continue
                else:
                    tmpAveTime = (tmpAveTime*j + tmpTime)/(1.0*(j+1))
                    tmpAveCost = (tmpAveCost*j + tmpCost)/(1.0*(j+1))
                    j = j + 1
            if tmpAveCost!=999999:
                if tmpAveTime==0:
                    tmpCostTimeRatio = 1
                else:
                    tmpCostTimeRatio = tmpAveCost/tmpAveTime
                tmpAveTime = round(tmpAveTime + tmpInternalTime, 2)
                tmpAveCost = round(tmpAveCost + tmpInternalTime*tmpCostTimeRatio, 2)
                if tmpAveTime<=600:
                    tmpOut = (orig + '\t' + dest + '\t' + str(tmpAveCost))
                    outFile.write(tmpOut+'\n')
    endTime = time.time()
    outFile.close()
    del pathFinder
    return endTime - startTime
    
def generateLogsumTable(_filePath, _numberOfIterations):
    pathFinder = bm_path.PathAlgorithm()
    #pathFinder.readUtilityParameters()
    pathFinder.resetPathSet()
    outFile = open(_filePath+"output_skim_logsum.dat", "w")
    outFile.write('Origin\tDestination\tLogsum\n')
    startTime = time.time()
    i=0
    for orig in bm_network.zoneSet:
        i=i+1
        if 1%1000==0:
            print (i, orig, round(time.time()-startTime,2))
        pathFinder.findForwardHyperpath(orig, 1)
        tmpInternalTime = math.sqrt(bm_network.zoneSet[orig].getArea())/10*60
        for dest in bm_network.zoneSet:
            tmpAveTime = 999999
            tmpAveLogsum = 999999
            j = 0
            tmpNodes = bm_network.zoneSet[dest].getNodes()
            for tmpNode in tmpNodes:
                tmpTime = bm_network.nodeSet[tmpNode].getMinForwardTime()
                tmpLogsum = bm_network.nodeSet[tmpNode].getForwardLabel()
                if tmpLogsum>=999999:
                    continue
                else:
                    tmpAveTime = (tmpAveTime*j + tmpTime)/(1.0*(j+1))
                    tmpAveLogsum = (tmpAveLogsum*j + tmpLogsum)/(1.0*(j+1))
                    j = j + 1
            if tmpAveLogsum!=999999:
                if tmpAveTime==0:
                    tmpLogsumTimeRatio = 1
                else:
                    tmpLogsumTimeRatio = tmpAveLogsum/tmpAveTime
                tmpAveTime = round(tmpAveTime + tmpInternalTime, 2)
                tmpAveLogsum = round(tmpAveLogsum + tmpInternalTime*tmpLogsumTimeRatio, 2)
                if tmpAveTime<=300:
                    tmpOut = (orig + '\t' + dest + '\t' + str(tmpAveLogsum))
                    outFile.write(tmpOut+'\n')
    endTime = time.time()
    outFile.close()
    del pathFinder
    return endTime - startTime

#################################################################################################
def deterministicForwardAssignment(_filePath):
    pathFinder = bm_path.PathAlgorithm()
    #pathFinder.readUtilityParameters()
    [bm_network.linkSet[x].resetFlow()  for x in bm_network.linkSet] 
    startTime = time.time()
    pathFinder.resetPathSet()
    [bm_network.linkSet[x].resetAuxiliaryFlow()  for x in bm_network.linkSet] 
    
    i = 0
    for orig in bm_network.zoneSet:
        i=i+1
        if i%100==0: print ("* Assigning the",i,"th row. Time elapsed =", round(time.time()-startTime,2), "seconds.")
        if bm_network.zoneSet[orig].getTotalTripProduction()<=0:
            print ("Zone", orig, "does not have trip production")
        #    continue
        pathFinder.findForwardShortestPath(orig, 0)                
        for dest in bm_network.zoneSet:
            if orig == dest:
                continue
            tmpDemand = bm_network.zoneSet[orig].getTripProduction(dest)
            tmpPath = pathFinder.getForwardShortestPath(orig, dest)
            if tmpPath[1] != "NA":
                tmpPathLength = sum([bm_network.linkSet[x].linkLength for x in tmpPath[1]])
                tmpPathTimeFF = sum([bm_network.linkSet[x].freeFlowTime for x in tmpPath[1]])
                bm_network.zoneSet[orig].addPathToTheForwardPathSets(1, dest, tmpPath, tmpPathLength, tmpPathTimeFF)
                for x in tmpPath[1]:
                    bm_network.linkSet[x].addAuxiliaryFlow(tmpDemand)

    [bm_network.linkSet[x].updateFlow(1) for x in bm_network.linkSet]
    [bm_network.linkSet[x].updateTravelTime() for x in bm_network.linkSet]
    TSTT = round(1/60.0*sum([bm_network.linkSet[x].getFlow()*bm_network.linkSet[x].getTravelTime() for x in bm_network.linkSet]), 3)
    print ("time:", round(time.time()-startTime,3), "TSTT:", TSTT)
    
    del pathFinder
    endTime = time.time()
    return endTime - startTime

def stochasticForwardAssignment(_filePath, _numberOfIterations):
    pathFinder = bm_path.PathAlgorithm()
    pathFinder.readUtilityParameters(_filePath)
    [bm_network.linkSet[x].resetFlow()  for x in bm_network.linkSet] 
    startTime = time.time()
    pathFinder.resetPathSet()
    [bm_network.linkSet[x].resetAuxiliaryFlow()  for x in bm_network.linkSet] 
    i = 0
    
    for orig in bm_network.zoneSet:
        i=i+1
        if i%10==0:
            print ("* Assigning the",i,"th row. Time elapsed =", round(time.time()-startTime,2), "seconds.")
        if bm_network.zoneSet[orig].getTotalTripProduction()<=0:
            print ("Zone", orig, "does not have trip production")
        #    continue
        pathFinder.findForwardHyperpath(orig, 0)
        for dest in bm_network.zoneSet:
            if orig == dest:
                continue 
            tmpDemand = bm_network.zoneSet[orig].getTripProduction(dest)
            for j in range (0,_numberOfIterations):
                tmpPath = pathFinder.getForwardElementaryPath(orig, dest)
                if tmpPath[1] != "NA":
                    tmpPathLength = sum([bm_network.linkSet[x].linkLength for x in tmpPath[1]])
                    tmpPathTimeFF = sum([bm_network.linkSet[x].freeFlowTime for x in tmpPath[1]])
                    bm_network.zoneSet[orig].addPathToTheForwardPathSets(_numberOfIterations, dest, tmpPath, tmpPathLength, tmpPathTimeFF)
                    for x in tmpPath[1]:
                        bm_network.linkSet[x].addAuxiliaryFlow(tmpDemand/_numberOfIterations)
                        
    [bm_network.linkSet[x].updateFlow(1) for x in bm_network.linkSet]
    [bm_network.linkSet[x].updateTravelTime() for x in bm_network.linkSet]
    TSTT = round(1/60.0*sum([bm_network.linkSet[x].getFlow()*bm_network.linkSet[x].getTravelTime() for x in bm_network.linkSet]), 3)
    print ("time:", round(time.time()-startTime,3), "TSTT:", TSTT)

    del pathFinder
    endTime = time.time()
    return endTime - startTime
#################################################################################################
def printAssignmentResults(_filePath):
    outFile = open(_filePath+"output_linkFlows.dat", "w")
    tmpOut = 'LinkID\tfromNode\ttoNode\tCapacity\tFlow\tflowToCapacityRatio\tfreeFlowTime\ttravelTime\n'
    outFile.write(tmpOut)
    for tmpLink in bm_network.linkSet:
        tmpOut = str(tmpLink) 
        tmpOut = tmpOut + '\t' + str(bm_network.linkSet[tmpLink].getFromNode())
        tmpOut = tmpOut + '\t' + str(bm_network.linkSet[tmpLink].getToNode())
        tmpOut = tmpOut + '\t' + str(round(bm_network.linkSet[tmpLink].capacity,3))
        tmpOut = tmpOut + '\t' + str(round(bm_network.linkSet[tmpLink].getFlow(),3))
        tmpOut = tmpOut + '\t' + str(round(bm_network.linkSet[tmpLink].getFlow() / bm_network.linkSet[tmpLink].capacity, 3))
        tmpOut = tmpOut + '\t' + str(round(bm_network.linkSet[tmpLink].freeFlowTime,3))
        tmpOut = tmpOut + '\t' + str(round(bm_network.linkSet[tmpLink].getTravelTime(),3))
        tmpOut = tmpOut + '\n'
        outFile.write(tmpOut)
    outFile.close()


def printPaths(_filePath):
    pathFinder = bm_path.PathAlgorithm()
    pathFinder.readUtilityParameters(_filePath)
    startTime = time.time()
    i = 0

    tmpOutFile = open(_filePath+"output_paths.dat", "w")
    tmpOutFile.write("Origin\tDestination\tPathNumber\tProbability\tPathLength\tPathFreeFlowTime\tPathNodes\tPathLinks\n" )

    for orig in bm_network.zoneSet:
        i=i+1
        #if i%10==0: print ("* Printing paths for the",i,"th row. Time elapsed =", round(time.time()-startTime,2), "seconds.")
        for dest in bm_network.zoneSet:
            if orig == dest: continue 
            k = 1
            for tmpPath in bm_network.zoneSet[orig].forwardPathSets[dest]:
                tmpPathInfo = bm_network.zoneSet[orig].forwardPathSets[dest][tmpPath]
                #print (tmpPath, tmpPathInfo)
                tmpOutFile.write(str(orig)+"\t"+str(dest)+"\t"+str(k)
                +"\t"+str(round(tmpPathInfo['probability'],3))
                +"\t"+str(tmpPathInfo['length'])
                +"\t"+str(tmpPathInfo['time'])
                +"\t"+str(tmpPathInfo['nodes'])
                +"\t"+str(tmpPathInfo['links'])
                +"\n")
                k+=1
                
    tmpOutFile.close()
    del pathFinder
    endTime = time.time()
    return endTime - startTime

#################################################################################################
def deterministicForwardPathEvaluation(_filePath, _visNet, _showPath):
    pathFinder = bm_path.PathAlgorithm()
    pathFinder.readUtilityParameters(_filePath)


    tmpContinue = True
    while (tmpContinue):
        tmpOrig = input("Enter the origin zone ID:")
        while (tmpOrig not in bm_network.zoneSet):
            tmpOrig = input("Origin ID is not in the Zone Set. Please enter the origin zone ID:")
        tmpDest = input("Enter the destination zone ID:")
        while (tmpDest not in bm_network.zoneSet):
            tmpDest = input("Destination ID is not in the Zone Set. Please enter the destination zone ID:")
        if tmpOrig == tmpDest:
            print ("Origin and destinations are the same. Please start again.")
            continue
        
        pathFinder.findForwardShortestPath(tmpOrig, tmpDest)                
        tmpPath = pathFinder.getForwardShortestPath(tmpOrig, tmpDest)
        endTime = time.time()
        print ("Path =", tmpPath[1])
        if _showPath:
            _visNet.plotPath(tmpPath[1])

        
        tmpIn = ""
        while (tmpIn not in ['y','n']):
            tmpIn = input("Do you want to try another origin-destination pair? Enter 'y' or 'n':")
        if tmpIn=='n':
            tmpContinue = False
    del pathFinder

def stochasticForwardPathEvaluation(_filePath, _visNet, _showPath, _numberOfIterations):
    pathFinder = bm_path.PathAlgorithm()
    pathFinder.readUtilityParameters(_filePath)

    tmpContinue = True
    while (tmpContinue):
        tmpOrig = input("Enter the origin zone ID:")
        while (tmpOrig not in bm_network.zoneSet):
            tmpOrig = input("Origin ID is not in the Zone Set. Please enter the origin zone ID:")
        tmpDest = input("Enter the destination zone ID:")
        while (tmpDest not in bm_network.zoneSet):
            tmpDest = input("Destination ID is not in the Zone Set. Please enter the destination zone ID:")
        if tmpOrig == tmpDest:
            print ("Origin and destinations are the same. Please start again.")
            continue
        
        tmpHyperPathLinks = []
        pathFinder.findForwardHyperpath(tmpOrig, 0)
        for i in range(0,_numberOfIterations):
            tmpPath = pathFinder.getForwardElementaryPath(tmpOrig, tmpDest)
            tmpHyperPathLinks += tmpPath[1]
            #print ("Path =", tmpPath[1])
        print (tmpHyperPathLinks)
        if _showPath:
            _visNet.plotPath(set(tmpHyperPathLinks))
        
        tmpIn = ""
        while (tmpIn not in ['y','n']):
            tmpIn = input("Do you want to try another origin-destination pair? Enter 'y' or 'n':")
        if tmpIn=='n':
            tmpContinue = False
    del pathFinder
#################################################################################################
#################################################################################################
#################################################################################################
#################################################################################################
#################################################################################################



################################################## INACTIVE FUNCTIONS ##################################################
'''def deterministicBackwardAssignment():
    GUI1 = bm_GUI.graphicUserInterface('Path Diplay')
    pathFinder = bm_path.PathAlgorithm()
    pathFinder.readUtilityParameters()
    pathFinder.resetPathSet()
    startTime = time.time()
    i=1
    for dest in bm_network.zoneSet:
        i=i+1
        if i%100==0:
            print i, dest, time.time()-startTime
        if bm_network.zoneSet[dest].getTotalTripAttraction()<100:
            continue
        pathFinder.findBackwardShortestPath(dest)
        for orig in bm_network.zoneSet:
            #if orig == dest: continue
            tmpOD = str(orig) + "," + str(dest)           
            tmpDemand = bm_network.zoneSet[dest].getTripAttraction(orig)
            while(tmpDemand>0):
                incDemand = min(tmpDemand, 1)
                tmpPath = pathFinder.getBackwardShortestPathLinks(orig, dest)
                j=0
                while j<100 and tmpPath=='':
                    tmpPath = pathFinder.getBackwardShortestPathLinks(orig, dest)
                    j = j + 1
                if tmpPath=='':
                    break
                tmpPathCost = pathFinder.getPathCost(tmpPath)
                pathFinder.addPathFlow(tmpOD, tmpPath, tmpPathCost, incDemand)
                tmpDemand = tmpDemand - incDemand

    #GUI1.clearDisplay()
    #GUI1.createNetwork()
    #GUI1.createPath(orig, dest, tmpPathTree, 2, 'red')
    #GUI1.updateDisplay()
    #time.sleep(0.1)
    #GUI1.closeDisplay()
    outFile = open("output_pathFlows.dat", "w")
    tmpOut = 'OD\tPath\tCost\tFlow\n'
    outFile.write(tmpOut)
    for tmpPath in pathFinder.pathSet:
        tmpOut = str(pathFinder.pathSet[tmpPath][0]) + "\t" + str(tmpPath) + '\t' + str(pathFinder.pathSet[tmpPath][1]) + '\t' + str(pathFinder.pathSet[tmpPath][2]) + '\n'
        outFile.write(tmpOut)
    outFile.close()
    
    pathFinder.calcLinkFlow()
    del pathFinder
    endTime = time.time()
    return endTime - startTime'''
####
'''def stochasticBackwardAssignment():
    GUI1 = bm_GUI.graphicUserInterface('Path Diplay')
    pathFinder = bm_path.PathAlgorithm()
    pathFinder.readUtilityParameters()
    pathFinder.resetPathSet()
    startTime = time.time()
    for dest in bm_network.nodeSet:
        #print 'Assigning Origin: ', dest
        pathFinder.findBackwardHyperpath(dest)
        for orig in bm_network.nodeSet:
            if orig == dest: continue
            tmpOD = str(orig) + "," + str(dest)
            tmpDemand = bm_network.nodeSet[dest].getTripAttraction(orig)
            for i in range(int(tmpDemand)/1):
                tmpPath = pathFinder.getBackwardElementaryPath(orig, dest)
                tmpPathCost = pathFinder.getPathCost(tmpPath) 
                pathFinder.addPathFlow(tmpOD, tmpPath, tmpPathCost, 1)
        GUI1.clearDisplay()
        GUI1.createNetwork()
        GUI1.createPath(orig, dest, tmpPath, 2, 'red')
        #GUI1.updateDisplay()
        #time.sleep(0.1)
    GUI1.closeDisplay()

    outFile = open("output_pathFlows.dat", "w")
    tmpOut = 'OD\tPath\tCost\tFlow\n'
    outFile.write(tmpOut)
    for tmpPath in pathFinder.pathSet:
        tmpOut = str(pathFinder.pathSet[tmpPath][0]) + "\t" + str(tmpPath) + '\t' + str(pathFinder.pathSet[tmpPath][1]) + '\t' + str(pathFinder.pathSet[tmpPath][2]) + '\n'
        outFile.write(tmpOut)
    outFile.close()
    
    pathFinder.calcLinkFlow()
    del pathFinder
    endTime = time.time()
    return endTime - startTime'''
