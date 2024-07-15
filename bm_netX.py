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
import bm_network
import networkx as nx 
import matplotlib.pyplot as plt
################################################## GUI ##################################################
class networkVisualization:
    ''' Visualization of network, link flows, and pahts '''

    def __init__(self):
        self.network = nx.DiGraph()
        for node in bm_network.nodeSet:
            self.network.add_node(node, pos=bm_network.nodeSet[node].getCoordinates())
        #print (self.network.nodes)
        for _link in bm_network.linkSet:
            self.network.add_edge(bm_network.linkSet[_link].getFromNode(), bm_network.linkSet[_link].getToNode()
                                  , length = bm_network.linkSet[_link].getLength()
                                  , capacity = bm_network.linkSet[_link].getCapacity()
                                  )
        #print (self.network.edges)
        #print (bm_network.linkSet[_link].getFlow())
        self.nodePositions = nx.get_node_attributes(self.network, 'pos')
        
    def addAssignmentResults(self):
        for _link in bm_network.linkSet:
            self.network.edges[bm_network.linkSet[_link].getFromNode(), bm_network.linkSet[_link].getToNode()]['flow'] = bm_network.linkSet[_link].getFlow()
            self.network.edges[bm_network.linkSet[_link].getFromNode(), bm_network.linkSet[_link].getToNode()]['travelTime'] = bm_network.linkSet[_link].getTravelTime()
    
    def plotNetwrok(self, _style):
        plt.figure(figsize=(10,12)) 
        if _style:
            nx.draw_networkx(self.network, self.nodePositions, with_labels=True
                             , edgecolors='maroon', node_color='gold'#, node_size=100, font_size=7
                             , edge_color='grey', connectionstyle="arc3,rad=0.1")
        else:
            nx.draw_networkx(self.network, self.nodePositions, with_labels=False
                             , edgecolors='grey', node_color='black', node_size=0.1, font_size=7
                             , edge_color='grey')#, connectionstyle="arc3,rad=0.2")
        plt.show()

    def plotFlows(self, _label):      
        #tmpCapacities = nx.get_edge_attributes(self.network, "capacity")
        tmpFlows = nx.get_edge_attributes(self.network, "flow")
        #tmpFlowToCapacity = nx.get_edge_attributes(self.network, "capacity") Doesn't seem correct! 
        #tmpTravelTimes = nx.get_edge_attributes(self.network, "travelTime")
        plt.figure(figsize=(10,12))
        nx.draw_networkx(self.network, self.nodePositions, with_labels=True
                         , edgecolors='maroon', node_color='gold'#, node_size=100, font_size=7
                         , width=list(tmpFlows.values())
                         , edge_color='grey', connectionstyle="arc3,rad=0.2")
        if _label=="flow":
            nx.draw_networkx_edge_labels(self.network, self.nodePositions
                                         , edge_labels=tmpFlows, font_size=8, label_pos=0.3, alpha=0.8 )
        #elif _label=="time":
        #    nx.draw_networkx_edge_labels(self.network, self.nodePositions
        #                                 , edge_labels=tmpTravelTimes, font_size=8, label_pos=0.3, alpha=0.8 )
            
    def plotPathforOD(self, _orig, _dest):
        if _dest not in bm_network.zoneSet[_orig].forwardShortestPaths.keys():
            print ("It seems that a path from zone", _orig, "to zone", _dest, "is not available! This could be a path finding issue!")
        else:
            nx.draw_networkx(self.network, self.nodePositions, with_labels=True
                             , edgecolors='maroon', node_color='gold'#, node_size=100, font_size=7
                             , edge_color='grey', connectionstyle="arc3,rad=0.2")
            tmpPathLinks = bm_network.zoneSet[_orig].forwardShortestPaths[_dest].split(",")
            tmpPathEdges = [(bm_network.linkSet[x].linkFromNode,bm_network.linkSet[x].linkToNode) for x in tmpPathLinks]    
            nx.draw_networkx_edges(self.network,self.nodePositions
                               , edgelist=tmpPathEdges, edge_color='red', connectionstyle='arc3, rad = 0.2')
    
    def plotPath(self, _path):
        plt.figure(figsize=(10,12))
        nx.draw_networkx(self.network, self.nodePositions, with_labels=False
                         , edgecolors='grey', node_color='black', node_size=0.1, font_size=7
                         , edge_color='grey') #, connectionstyle="arc3,rad=0.2")
        tmpPathLinks = _path # bm_network.zoneSet[_orig].forwardShortestPaths[_dest].split(",")
        tmpPathEdges = [(bm_network.linkSet[x].linkFromNode,bm_network.linkSet[x].linkToNode) for x in tmpPathLinks]    
        nx.draw_networkx_edges(self.network,self.nodePositions
                           , edgelist=tmpPathEdges, edge_color='red', connectionstyle='arc3, rad = 0.2')
        plt.show()
               


