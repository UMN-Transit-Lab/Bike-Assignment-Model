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

import bm_assignment, bm_network, bm_map
import sys, time
print ('----------------------------------------')
''' Enter the network name be added to the input file path''' 
inputDataLocation = "Bike Model IO/"


################################################## Reading Input Parameters ##################################################
''' Read the Input Parameters ''' 
try:
    inFile = open(inputDataLocation+"input_parameters.txt", "r")
except: 
    print('Unable to read input_parameters.txt file. Program is terminating.')
tmpIn = inFile.readline()
tmpParameters = []
while (1):
    tmpIn = inFile.readline()
    if tmpIn == "": break
    tmpParameters.append(tmpIn.split()[0])
inFile.close()

''' The next few sections assigns the parameters from the inpit file to 
variables used for the model run '''
## Define the route choice type
DETERMINISTIC_ROUTE_CHOICE, STOCHASTIC_ROUTE_CHOICE = False, False
if int(tmpParameters[0])==1:
    DETERMINISTIC_ROUTE_CHOICE = True
elif int(tmpParameters[0])==2:
    print ('Stochastic Assignment is not available yet. Program is terminating.')
    time.sleep(2)
    sys.exit()
    STOCHASTIC_ROUTE_CHOICE = True
else:
    print ("Assignment type parameter out of range {1,2}. Program is terminating.")
    time.sleep(1)
    sys.exit()

## Define the model application type
ASSIGNMENT, SKIMMING = False, False
if int(tmpParameters[1])==1:
    ASSIGNMENT = True
elif int(tmpParameters[1])==2:
    print ('Skimming is not available yet. Program is terminating.')
    time.sleep(2)
    sys.exit()
    SKIMMING = True
else:
    print ("Model application parameter out of range {1,2}. Program is terminating.")
    time.sleep(1)
    sys.exit()
    
## Define the maximum number of iterations
MAX_ITERATIONS = 1
if ASSIGNMENT:
    if STOCHASTIC_ROUTE_CHOICE:
        if int(tmpParameters[2]) > 0 and int(tmpParameters[2]) <= 1000:
            MAX_ITERATIONS = int(tmpParameters[2])
        else:
            print ('Number of draws parameter must be an integer between 1 and 1,000. By default, 10 draws will be performed.')
            MAX_ITERATIONS = 10

## Define whether and what to visualize
SHOW_FLOWS, SHOW_PATH = False, False
if ASSIGNMENT:
    if int(tmpParameters[3])==0:
        SHOW_FLOWS = False
    elif int(tmpParameters[3])==1:
        SHOW_FLOWS = True
    else:
        print ("Visualization parameter out of range {0,1}. Results will not be visualized.")        

## Define whether to print paths
PRINT_PATHS = False
if ASSIGNMENT or SKIMMING:
    if int(tmpParameters[4]) == 0:
        PRINT_PATHS = False
    elif int(tmpParameters[4])==1:
        PRINT_PATHS = True
    else:
        print ("Parameter for printing paths is out of range {0,1}. Paths will not be printed.")

## Determine the time periods of assignment
ASSIGNMENT_PERIODS = {'AM':0, 'MD':0, 'PM':0, 'NT':0}
if ASSIGNMENT:
    if int(tmpParameters[5]) == 1:
        ASSIGNMENT_PERIODS['AM'] = 1
    elif int(tmpParameters[5]) == 0:
        ASSIGNMENT_PERIODS['AM'] = 0
    else:
        ASSIGNMENT_PERIODS['AM'] = 0
        print ("Parameter for assignment time period AM is out of range {0,1}. Time period will be excluded from assignment.")
    if int(tmpParameters[6]) == 1:
        ASSIGNMENT_PERIODS['MD'] = 1
    elif int(tmpParameters[6]) == 0:
        ASSIGNMENT_PERIODS['MD'] = 0
    else:
        ASSIGNMENT_PERIODS['MD'] = 0
        print ("Parameter for assignment time period MD is out of range {0,1}. Time period will be excluded from assignment.")
    if int(tmpParameters[7]) == 1:
        ASSIGNMENT_PERIODS['PM'] = 1
    elif int(tmpParameters[7]) == 0:
        ASSIGNMENT_PERIODS['PM'] = 0
    else:
        ASSIGNMENT_PERIODS['PM'] = 0
        print ("Parameter for assignment time period PM is out of range {0,1}. Time period will be excluded from assignment.")
    if int(tmpParameters[8]) == 1:
        ASSIGNMENT_PERIODS['NT'] = 1
    elif int(tmpParameters[8]) == 0:
        ASSIGNMENT_PERIODS['NT'] = 0
    else:
        ASSIGNMENT_PERIODS['NT'] = 0
        print ("Parameter for assignment time period NT is out of range {0,1}. Time period will be excluded from assignment.")

BIKE_TO_TRANSIT = False
if ASSIGNMENT:
    if int(tmpParameters[9]) == 0:
        BIKE_TO_TRANSIT = [False]
    elif int(tmpParameters[9]) == 1:
        BIKE_TO_TRANSIT = [True]
    else:
        print ("Parameter for Bike-to-Transit is out of range {0,1}. Trips will be assigned as bike-only.")
    
    if BIKE_TO_TRANSIT:
        MIN_BIKE_TO_TRANSIT_DIST = min(0.5, max(0.2, float(tmpParameters[10]))) 
        MAX_BIKE_TO_TRANSIT_DIST = min(2.0, max(0.5, float(tmpParameters[11])))
        if MIN_BIKE_TO_TRANSIT_DIST < MAX_BIKE_TO_TRANSIT_DIST:
            BIKE_TO_TRANSIT.append(MIN_BIKE_TO_TRANSIT_DIST)
            BIKE_TO_TRANSIT.append(MAX_BIKE_TO_TRANSIT_DIST)
        else:
            print ("Bike-to-tranit distances are not valid. Default values (0.25, 0.75) will be used.")
            BIKE_TO_TRANSIT.append(0.25, 0.75)
print ('----------------------------------------')

################################################## Reading Input Data ##################################################
print ('Number of Nodes: ', bm_network.readNodes(inputDataLocation))
print ('Number of Directional Links: ', bm_network.readLinks(inputDataLocation))
print ('Link Speeds and Times Were Calculated/Updated!', bm_network.calculateLinkSpeeds())
print ('Number of Connected Nodes: ', bm_network.refineNodes())
print ('Number of Zones: ', bm_network.readZones(inputDataLocation))
print ('Number of Connected Zones: ', bm_network.refineZones())
print ('----------------------------------------')
time.sleep(1)

################################################## ASSIGNMENT/LOADING ##################################################
if ASSIGNMENT:    
    for tod in ASSIGNMENT_PERIODS:
        if ASSIGNMENT_PERIODS[tod] == 1:
            print ('Number of', tod, 'Trips: ', bm_assignment.readDemand(inputDataLocation, tod, BIKE_TO_TRANSIT))
            if DETERMINISTIC_ROUTE_CHOICE:
                bm_assignment.deterministicForwardAssignment(inputDataLocation, tod, BIKE_TO_TRANSIT, MAX_ITERATIONS, PRINT_PATHS)
                print ("Assignment was completed.")# Elapsed time =", round(bm_assignment.deterministicForwardAssignment(inputDataLocation, MAX_ITERATIONS, PRINT_PATHS),2), 'seconds')
            elif STOCHASTIC_ROUTE_CHOICE:
                bm_assignment.stochasticForwardAssignment(inputDataLocation, tod, MAX_ITERATIONS, PRINT_PATHS)
                print ("Assignment was completed.")# Elapsed time =", round(bm_assignment.stochasticForwardAssignment(inputDataLocation, MAX_ITERATIONS, PRINT_PATHS),2), 'seconds') 
            bm_assignment.printLinkFlows(inputDataLocation, tod, BIKE_TO_TRANSIT)
            print ('Link flows for the time period', tod, 'were printed.') 
            bm_assignment.printNodeFlows(inputDataLocation, tod, BIKE_TO_TRANSIT)
            print ('Node flows for the time period', tod, 'were printed.') 
            if SHOW_FLOWS:
                bike_map = bm_map.createFoliumMap()
                if BIKE_TO_TRANSIT[0]:
                    bike_map.save(inputDataLocation+'Bike_Assignment_Map_'+tod+'_bike2transit.html')
                else:
                    bike_map.save(inputDataLocation+'Bike_Assignment_Map_'+tod+'.html')
                print ('Link flows for the time period', tod, 'were plotted on the map.')
            if PRINT_PATHS:
                bm_assignment.printPaths(inputDataLocation, tod, BIKE_TO_TRANSIT)
                print ("Path flows were printed.")
            print ('----------------------------------------')
            time.sleep(1)

################################################## SKIMMING ##################################################
if SKIMMING:
    print ('Skimming is not available. The program is terminating.')
    time.sleep(2)
    sys.exit()
    if DETERMINISTIC_ROUTE_CHOICE:
        print ("Assignment process was completed.")# Run time =", round(bm_assignment.generateSkimTable(inputDataLocation),2), 'seconds.')
    elif STOCHASTIC_ROUTE_CHOICE:
        print ("Assignment process was completed.")# Run time =", round(bm_assignment.generateLogsumTable(inputDataLocation, MAX_ITERATIONS),2), 'seconds')



