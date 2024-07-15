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

def readDemand(_filePath, _tod):
    ''' Reads trip demand for origin-destinations from a text (.dat) file and add them to the '''
    print('---------- READING', _tod, 'DEMAND ----------')
    ## First, reset any existing demand from other time periods
    for tmpZone in bm_network.zoneSet:
        bm_network.zoneSet[tmpZone].resetDemand()
    ## then determine the index of demand for the time period
    tmpTOD = ['AM', 'MD', 'PM', 'NT']
    todIndex = tmpTOD.index(_tod)
    ## Read the demand file
    inFile = open(_filePath+"input_demand.csv", "r")
    tmpIn = inFile.readline()
    tmpTotalDemand = 0
    while (1):
        tmpIn = inFile.readline()
        if tmpIn == "": break
        token = tmpIn.split(',')
        tmpFromZone = token[0]
        tmpToZone = token[1]
        tmpDemand = float(token[2+todIndex])
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
#################################################################################################
#################################################################################################
#################################################################################################
def deterministicForwardAssignment(_filePath, _tod, _numberOfIterations, _printPath):
    print('---------- ASSIGNING', _tod, 'DEMAND ----------')

    pathFinder = bm_path.PathAlgorithm()
    pathFinder.readUtilityParameters(_filePath)
    [bm_network.linkSet[x].resetFlow()  for x in bm_network.linkSet] 
    startTime = time.time()
    pathFinder.resetPathSet()
    [bm_network.linkSet[x].resetAuxiliaryFlow()  for x in bm_network.linkSet] 
    
    i = 0
    for orig in bm_network.zoneSet:
        i=i+1
        if i%100==0: print ("* Assigning the",i,"th row. Time elapsed =", round(time.time()-startTime,2), "seconds.")
        if bm_network.zoneSet[orig].getTotalTripProduction()<=0:
            #print ("Zone", orig, "does not have trip production")
            continue
        pathFinder.findForwardShortestPath(orig, 0)
        for dest in bm_network.zoneSet:
            if orig == dest:
                continue
            tmpDemand = bm_network.zoneSet[orig].getTripProduction(dest)
            if tmpDemand > 0:
                tmpPath = pathFinder.getForwardShortestPath(orig, dest)
                if tmpPath[1] != "NA":
                    for x in tmpPath[1]:
                        bm_network.linkSet[x].addAuxiliaryFlow(tmpDemand)
                    if _printPath:
                        tmpPathLength = sum([bm_network.linkSet[x].linkLength for x in tmpPath[1]])
                        tmpPathTimeFF = sum([bm_network.linkSet[x].freeFlowTime for x in tmpPath[1]])
                        bm_network.zoneSet[orig].addPathToTheForwardPathSets(1, dest, tmpPath, tmpPathLength, tmpPathTimeFF)
        #if i>50: break
    [bm_network.linkSet[x].updateFlow(1) for x in bm_network.linkSet]
    
    del pathFinder
    endTime = time.time()
    return endTime - startTime
'''
def stochasticForwardAssignment(_filePath, _tod, _numberOfIterations, _printPath):
    pathFinder = bm_path.PathAlgorithm()
    pathFinder.readUtilityParameters(_filePath)
    [bm_network.linkSet[x].resetFlow()  for x in bm_network.linkSet] 
    startTime = time.time()
    pathFinder.resetPathSet()
    [bm_network.linkSet[x].resetAuxiliaryFlow()  for x in bm_network.linkSet] 
    i = 0
    
    for orig in bm_network.zoneSet:
        #print ('O =', orig)
        i=i+1
        if i%100==0: print ("* Assigning the",i,"th row. Time elapsed =", round(time.time()-startTime,2), "seconds.")#; break
        #if bm_network.zoneSet[orig].getTotalTripProduction()<=0:
        #    print ("Origin zone", orig, "does not have trip production")
        #    #continue
        pathFinder.findForwardHyperpath(orig, 0)
        
        
        
#        k = 0
#        for n in bm_network.nodeSet:
#            if bm_network.nodeSet[n].nodeForwardLabel == 999999:
#                #print (n)
#                 #bm_network.nodeSet[n].printForwardShortestpathLabels()
#                k += 1
#        print (orig, k)

        
        for dest in bm_network.zoneSet:
            #print ('D =', dest)
            if orig == dest:
                continue 
            tmpDemand = 1
            #tmpDemand = bm_network.zoneSet[orig].getTripProduction(dest)
            for j in range (0,_numberOfIterations):
                tmpPath = pathFinder.getForwardElementaryPath(orig, dest)
                if tmpPath[1] != "NA":
                    for x in tmpPath[1]:
                        bm_network.linkSet[x].addAuxiliaryFlow(tmpDemand/_numberOfIterations)
                    if _printPath:
                        tmpPathLength = sum([bm_network.linkSet[x].linkLength for x in tmpPath[1]])
                        tmpPathTimeFF = sum([bm_network.linkSet[x].freeFlowTime for x in tmpPath[1]])
                        bm_network.zoneSet[orig].addPathToTheForwardPathSets(_numberOfIterations, dest, tmpPath, tmpPathLength, tmpPathTimeFF)
                                
    [bm_network.linkSet[x].updateFlow(1) for x in bm_network.linkSet]

    del pathFinder
    endTime = time.time()
    return endTime - startTime
'''
#################################################################################################
def printAssignmentResults(_filePath, _tod):
    outFile = open(_filePath+'output_linkFlows_'+_tod+'.dat', "w")
    tmpOut = 'LinkID,fromNode,toNode,Direction,Length,Speed,Flow,Time,treverseFlow,reverseTime\n'
    outFile.write(tmpOut)
    for l in bm_network.linkSet:
        tmpLink = bm_network.linkSet[l]
        linkId = tmpLink.linkId
        linkDir = int(tmpLink.linkDirection)
        if '.' in str(linkId):
            continue
        else:
            tmpOut = str(linkId) 
            tmpOut = tmpOut + ',' + str(tmpLink.getFromNode())
            tmpOut = tmpOut + ',' + str(tmpLink.getToNode())
            tmpOut = tmpOut + ',' + str(linkDir)
            tmpOut = tmpOut + ',' + str(tmpLink.linkLength)
            tmpOut = tmpOut + ',' + str(tmpLink.speed)
            tmpOut = tmpOut + ',' + str(round(tmpLink.getFlow(),3))
            tmpOut = tmpOut + ',' + str(round(tmpLink.freeFlowTime,3))
            if linkDir == 0: ## bidirectional link
                tmRevLink = bm_network.linkSet[linkId+'.1']
                tmpOut = tmpOut + ',' + str(round(tmRevLink.getFlow(),3))
                tmpOut = tmpOut + ',' + str(round(tmRevLink.freeFlowTime,3))
            tmpOut = tmpOut + '\n'
            outFile.write(tmpOut)
    outFile.close()


def printPaths(_filePath, _tod):
    pathFinder = bm_path.PathAlgorithm()
    pathFinder.readUtilityParameters(_filePath)
    startTime = time.time()
    i = 0

    tmpOutFile = open(_filePath+'output_paths_'+_tod+'.dat', "w")
    #tmpOutFile.write("Origin\tDestination\tPathNumber\tProbability\tPathLength\tPathFreeFlowTime\tPathNodes\tPathLinks\n" )
    tmpOutFile.write("Origin\tDestination\tPathNumber\tProbability\tPathLength\tPathFreeFlowTime\tPathLinks\n" )

    for orig in bm_network.zoneSet:
        i=i+1
        if bm_network.zoneSet[orig].forwardPathSets == {}: continue 
        #if i%10==0: print ("* Printing paths for the",i,"th row. Time elapsed =", round(time.time()-startTime,2), "seconds.")
        for dest in bm_network.zoneSet:
            if orig == dest: continue
            if dest not in bm_network.zoneSet[orig].forwardPathSets: continue 
            k = 1
            for tmpPath in bm_network.zoneSet[orig].forwardPathSets[dest]:
                tmpPathInfo = bm_network.zoneSet[orig].forwardPathSets[dest][tmpPath]
                #print (tmpPath, tmpPathInfo)
                tmpOutFile.write(str(orig)+"\t"+str(dest)+"\t"+str(k)
                +"\t"+str(round(tmpPathInfo['probability'],3))
                +"\t"+str(tmpPathInfo['length'])
                +"\t"+str(tmpPathInfo['time'])
                #+"\t"+str(tmpPathInfo['nodes'])
                +"\t"+str(tmpPathInfo['links'])
                +"\n")
                k+=1
                
    tmpOutFile.close()
    del pathFinder
    endTime = time.time()
    return endTime - startTime

#################################################################################################
#################################################################################################
#################################################################################################
