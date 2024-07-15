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

import bm_assignment, bm_network, bm_netX
import sys, time
print ('--------------------')
''' Enter the network name be added to the input file path''' 
inputDataLocation = "examples/SiouxFalls/"


################################################## Reading Input Parameters ##################################################
inFile = open(inputDataLocation+"input_parameters.dat", "r")
tmpIn = inFile.readline()
tmpParameters = []
while (1):
    tmpIn = inFile.readline()
    if tmpIn == "": break
    tmpParameters.append(tmpIn.split()[0])
inFile.close()

## Define the route choice type
DETERMINISTIC_ROUTE_CHOICE, STOCHASTIC_ROUTE_CHOICE = False, False
if int(tmpParameters[0])==1:
    DETERMINISTIC_ROUTE_CHOICE = True
elif int(tmpParameters[0])==2:
    STOCHASTIC_ROUTE_CHOICE = True
else:
    print ("Route choice type parameter out of range {1,2}")
    time.sleep(1)
    sys.exit()

## Define the model application type
SKIMMING, ASSIGNMENT, PATH_EVALUATION = False, False, False
if int(tmpParameters[1])==1:
    SKIMMING = True
elif int(tmpParameters[1])==2:
    ASSIGNMENT = True
elif  int(tmpParameters[1])==3:
    PATH_EVALUATION = True
else:
    print ("Model application parameter out of range {1,2}")
    time.sleep(1)
    sys.exit()
    
## Define the maximum number of iterations
if DETERMINISTIC_ROUTE_CHOICE:
    MAX_ITERATIONS = 1
if STOCHASTIC_ROUTE_CHOICE:
    if int(tmpParameters[2]) > 0:
        MAX_ITERATIONS = int(tmpParameters[2])
    else:
        print ('Maximum iterations parameter must be a positive integer. By default, 10 iterations will be performed.')
        MAX_ITERATIONS = 10
'''
if SKIMMING or PATH_EVALUATION:
    MAX_ITERATIONS = 1
else:
    if int(tmpParameters[2])>=1: 
        if int(tmpParameters[2])<=100:
            MAX_ITERATIONS = int(tmpParameters[2])
        else:
            print ("Maximum iterations parameter must be less than or equal to 100. 100 iterations will be performed.")
            MAX_ITERATIONS = 100
    else:
        print ("Maximum iterations parameter must be a positive integer. One iterations will be performed by default.")
        MAX_ITERATIONS = 1
'''
## Define whether and what to visualize
SHOW_THE_NETWORK, SHOW_FLOWS, SHOW_PATH = False, False, False
if SKIMMING:
    if int(tmpParameters[3])==0:
        NO_VISUALIZATION = True
    elif int(tmpParameters[3])==1:
        SHOW_THE_NETWORK = True
    else:
        print ("Visualization parameter out of range {0,1} for skimming. No visualization will be performed.")        
    
if ASSIGNMENT:
    if int(tmpParameters[3])==0:
        NO_VISUALIZATION = True
    elif int(tmpParameters[3])==1:
        SHOW_THE_NETWORK = True
    elif int(tmpParameters[3])==2:
        SHOW_FLOWS = True
    else:
        print ("Visualization parameter out of range {0,1,2} for assignment. No visualization will be performed.")
if PATH_EVALUATION:
    SHOW_THE_NETWORK = True
    SHOW_PATH = True

## Define whether to print paths
PRINT_PATHS = False
if ASSIGNMENT or SKIMMING:
    if int(tmpParameters[4]) == 0:
        PRINT_PATHS = False
    elif int(tmpParameters[4])==1:
        PRINT_PATHS = True
    else:
        print ("Parameter for printing paths is out of range {0,1}. Paths will not be printed.")

print ('--------------------')

################################################## Reading Input Data ##################################################
print ('Number of Nodes: ', bm_network.readNodes(inputDataLocation))
print ('Number of Links: ', bm_network.readLinks(inputDataLocation))
print ('Number of Connected Nodes: ', bm_network.refineNodes())
print ('Number of Zones: ', bm_network.readZones(inputDataLocation))
print ('Number of Connected Zones: ', bm_network.refineZones())
print ('Number of Trips: ', bm_assignment.readDemand(inputDataLocation))
visNet = bm_netX.networkVisualization()
if SHOW_THE_NETWORK:
    visNet.plotNetwrok(False)

print ('--------------------')

################################################## SKIMMING ##################################################
if SKIMMING:
    if DETERMINISTIC_ROUTE_CHOICE:
        print ("Assignment completed. Run time =", round(bm_assignment.generateSkimTable(inputDataLocation),2), 'seconds.')
    elif STOCHASTIC_ROUTE_CHOICE:
        print ("Assignment completed. Run time =", round(bm_assignment.generateLogsumTable(inputDataLocation, MAX_ITERATIONS),2), 'seconds')

################################################## ASSIGNMENT/LOADING ##################################################
if ASSIGNMENT:
    if DETERMINISTIC_ROUTE_CHOICE:
        print ("Assignment completed. Elapsed time =", round(bm_assignment.deterministicForwardAssignment(MAX_ITERATIONS),2), 'seconds')
    elif STOCHASTIC_ROUTE_CHOICE:
        print ("Assignment completed. Elapsed time =", round(bm_assignment.stochasticForwardAssignment(inputDataLocation, MAX_ITERATIONS),2), 'seconds') 

bm_assignment.printAssignmentResults(inputDataLocation)
print ("Assignment results have been printed.") 
if PRINT_PATHS:
    bm_assignment.printPaths(inputDataLocation)
    print ("Paths have been printed.")


################################################## PATH_EVALUATION ##################################################
if PATH_EVALUATION:
    if DETERMINISTIC_ROUTE_CHOICE:
        bm_assignment.deterministicForwardPathEvaluation(inputDataLocation, visNet, SHOW_PATH)
    elif STOCHASTIC_ROUTE_CHOICE:
        bm_assignment.stochasticForwardPathEvaluation(inputDataLocation, visNet, SHOW_PATH, MAX_ITERATIONS)

################################################## Network Visualization ##################################################

if SHOW_FLOWS:
    visNet.addAssignmentResults()
    visNet.plotFlows("flow")  # ' the parameter is "flow" or "time" for showing link labels '

# visNet.plotPathforOD('4', '20') # 'parameters are origin and destination nodes'

del visNet