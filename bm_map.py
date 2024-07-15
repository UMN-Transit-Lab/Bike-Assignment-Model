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

import folium
import folium.plugins as fl_plg
import bm_network

def createFoliumMap(_mapLocation=(33.44753282502129, -112.0364836577163), _initialZoom=10):
    # Create a map centered around the provided location
    tmpBikeMap = folium.Map(location=_mapLocation, zoom_start=_initialZoom, tiles='cartodbpositron')
    folium.TileLayer('openstreetmap').add_to(tmpBikeMap)
    folium.TileLayer('cartodbpositron').add_to(tmpBikeMap)
    folium.TileLayer('cartodbdark_matter').add_to(tmpBikeMap)
    #folium.TileLayer('mapquestopen').add_to(tmpBikeMap)
    folium.LayerControl().add_to(tmpBikeMap)
    '''
    # Add nodes to the map
    for n in bm_network.nodeSet:
        tmpNode = bm_network.nodeSet[n]
        nodeId = tmpNode.nodeId
        nodeLon, nodeLat = tmpNode.getCoordinates()
        popup = 'Node ' + str(nodeId)
        folium.Marker(
            location=(nodeLat, nodeLon),
            #popup=popup,
            icon=folium.Icon(color='blue')#, icon='info-sign')
        ).add_to(tmpBikeMap)
    '''
    # Add links to the map
    #maxFlow = max([bm_network.linkSet[l].getFlow() for l in bm_network.linkSet])
    i=0
    for l in bm_network.linkSet:
        tmpLink = bm_network.linkSet[l]
        linkId = tmpLink.linkId
        linkDir = tmpLink.linkDirection
        if '.' in str(linkId):
            continue
        else:
            startCoordinates = bm_network.nodeSet[tmpLink.linkFromNode].getCoordinates()
            endCoordinates = bm_network.nodeSet[tmpLink.linkToNode].getCoordinates()
            linkFlow = [tmpLink.getFlow()]
            if linkDir == 0: ## bidirectional link
                linkFlow.append(bm_network.linkSet[linkId+'.1'].getFlow())
            line = fl_plg.PolyLineOffset(locations=[tuple(reversed(startCoordinates)), tuple(reversed(endCoordinates))]
                                   , weight=0.1+sum(linkFlow)/100, color='blue'
                                   , offset = 0.0
                                   , tooltip = str(linkFlow)
                                   #, popup = str(linkFlow)
                                   )
            tmpBikeMap.add_child(line)
    return tmpBikeMap
