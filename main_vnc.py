import pydot
import xdot
import gtk

# import dependencies

import sys,os
# set the path relative to THIS file not the executing file!
cur = os.path.dirname( os.path.realpath( __file__ ) )

# syspaths and functions for vascular1DFlow_v0.2
sys.path.append(cur+'/../vascular1Dflow_v0.2/UtilityLib')
sys.path.append(cur+'/../vascular1Dflow_v0.2/NetworkLib')
from classVascularNetwork import VascularNetwork 
from classBoundaryConditions import *
from modulXML import writeNetworkToXML 
from modulXML import loadNetworkFromXML 

from modulCSV import readVesselDataFromCSV 
from modulCSV import writeVesselDataToCSV 
from modulCSV import writeBCToCSV 
from modulCSV import readBCFromCSV

from vnc_classes import *

import cPickle
import pprint as pprint
import numpy as np
import thread



def main():
    # set graphs directory
    graphPath = str(cur+'/../vascular1Dflow_v0.2/NetworkFiles/')
    
    # create a new window
    window = MyDotWindow()    
    window.connect('destroy',gtk.main_quit)
    window.show()
    
    #create the main graph instance of a graph class
    mainGraph = Graph()
    
    #START THE MAIN LOOP
    menuInput = ""
    subMenuInput = ''
    
    # create vascularNetwork instance
    vascularNetwork = VascularNetwork()
    filename = None
    networkTopologyMode = True
    networkTopologyModes = {0: 'node Description', 1:'mother-daugther Description'}
    k = None
    while menuInput != "q":
        menuInput = ""
        print ""
        print "vnc 2.1 - menu"
        print ""
        print " [a] - add vessel to network"
        print " [d] - delete vessel in network"
        print " [n] - new network"
        print " [b] - set boundary conditions"
        print " [l] - load network"
        print " [s] - save network"
        print " [u] - update XML form CSV file"
        print " [g] - print network graph"
        print " [f] - print network informations"
        print " [m] - change network topology mode; current: ", networkTopologyModes[networkTopologyMode]
        print " [q] - quit"
        print ""
        print '  current network: ', filename
        while  menuInput not in ("l","b","q","a","s","g","f","d","u",'n','m'): #(menuInput != "l") and (menuInput != "b") and (menuInput != "q") and (menuInput != "a") and (menuInput != "s") and (menuInput != "g") and (menuInput != "d") and (menuInput != "f"):
            menuInput = raw_input("what to do? ")
        
        if menuInput == "a": 
            print "Add new vessel"
            
            existing = False
            vesselID = raw_input(" enter the vessel id:  ")
            while True:
                try:
                     vesselID = int(vesselID)
                     if vesselID not in vascularNetwork.vessels:
                         break
                     else:
                         existing = True
                except ValueError:
                    print "TYPE-ERROR: vessel id must be type(int) not type(string)"
                    vesselID = raw_input(" enter non existing id: ")
                if existing == True:
                    print " the vessel id exists already enter a new one"
                    vesselID = raw_input(" enter non existing id: ")
                    existing = False
            
            
            if not networkTopologyMode:
                # define start node ony bifurctaion are allowed
                startNode = int(raw_input(" enter starting node:  "))
                while bifTest(vascularNetwork.vessels, startNode) == False:
                    print "   only bifurcations possible!"
                    startNode = int(raw_input(" enter starting node:  "))
                # define end node
                endNode = int(raw_input (" enter ending node:    "))
                # create vessel obj and save them in vessels-dict
                
                dataDict = {'end': endNode, 'start': startNode}
                vascularNetwork.addVessel(vesselID, dataDict)
                
            else:
                if vascularNetwork.vessels != {}:
#                    mother = int(raw_input(" enter existing mother id:  "))
#                    while mother not in vascularNetwork.vessels or (mother in vascularNetwork.vessels and vascularNetwork.vessels[mother].rightDaughter != None):
#                        if mother not in vascularNetwork.vessels: print " there exists no vessel with this ID"
#                        else: print "   only bifurcations possible!"
#                        mother = int(raw_input(" enter existing mother id: "))
                        
                    existing = False
                    mother = raw_input(" enter existing mother id:  ")
                    while True:
                        try:
                             mother = int(mother)
                             if mother in vascularNetwork.vessels and vascularNetwork.vessels[mother].rightDaughter == None:
                                 break
                             else:
                                 existing = True
                        except ValueError:
                            print "TYPE-ERROR: mother id must be type(int) not type(string)"
                            mother = raw_input(" enter existing mother id:  ")
                        if existing == True:
                            if mother not in vascularNetwork.vessels: print " there exists no vessel with this id"
                            else: print "   only bifurcations possible!"
                            mother = raw_input(" enter existing mother id:  ")
                            existing = False
                        
                    if vascularNetwork.vessels[mother].leftDaughter == None: vascularNetwork.vessels[mother].leftDaughter = vesselID
                    else: vascularNetwork.vessels[mother].rightDaughter = vesselID
                    vascularNetwork.vessels[mother].end = None
                
                vascularNetwork.addVessel(vesselID)
            mainGraph.update_graph(vascularNetwork, window)
                    
        if menuInput == "d":
            print "Delete a vessel and all its daugthers"
            if vascularNetwork.vessels.keys() != []:
                
#                vesselID = int(raw_input(" enter the vessel id: "))
#                while (vesselID in vascularNetwork.vessels) == False:
#                    print " the vessel does not exist"
#                    vesselID = int(raw_input(" enter existing vessel id: "))
                
                existing = False
                vesselID = raw_input(" enter existing vessel id: ")
                while True:
                    try:
                         vesselID = int(vesselID)
                         if vesselID in vascularNetwork.vessels:
                             break
                         else:
                             existing = True
                    except ValueError:
                        print "TYPE-ERROR: vessel id must be type(int) not type(string)"
                        vesselID = raw_input(" enter existing vessel id: ")
                    if existing == True:
                        print " the vessel does not exist"
                        vesselID = raw_input(" enter existing vessel id: ")
                        existing = False
                
                #travers the tree starting with the vessel and collect all ids
                toDelete = findAllDaughters(vascularNetwork,vesselID)
                
                toDelete.append(vesselID)
                for vesselToDelete in toDelete:
                    vascularNetwork.deleteVessel(vesselToDelete)
                    
                # empty the graph to redraw it
                mainGraph.update_graph(vascularNetwork, window)
                
            else:
                print " there are no vessels to delete"
                
        elif menuInput == "n":
            print "new network"
            question = raw_input(" are u sure to delete all current data? [n] - yes: ")
            if question == 'n':
                # delet vascularNetwork
                del vascularNetwork
                # create vascularNetwork instance
                vascularNetwork = VascularNetwork()
                mainGraph.update_graph(vascularNetwork, window)
            
        elif menuInput == "m":
            networkTopologyMode = not networkTopologyMode
        
        elif menuInput == "f":
            vascularNetwork.showVessels()
            vascularNetwork.showNetwork()
            vascularNetwork.calculateNetworkResistance()
            
            
        elif menuInput == "g":
            print mainGraph.getGraph()
            
        elif menuInput == "b":
            subMenuInput = ''
            
            print 'create/load/save/delete/show BoundaryCondistions, not implemented yet'
#           
#            while  subMenuInput not in ['1','2','3','4','5','b']:         
#                # evaluate boundarys in Network
#                boundarys = []
#                notDefinedBoundarys = []
#                
#                boundarys.extend(vascularNetwork.ends)
#                if vascularNetwork.root != [] and vascularNetwork.root[0] not in boundarys: 
#                    boundarys.extend(vascularNetwork.root)
#                    
#                boundarysSaved = vascularNetwork.boundaryConditions.keys()
#                
#                # update saved boundary conditions
#                for boundarysCurrent in boundarys:
#                    if boundarysCurrent not in boundarysSaved:
#                        print " boundary added to vascularNetwork"
#                        vascularNetwork.boundaryConditions[boundarysCurrent] = {}
#                        boundarysSaved.append(boundarysCurrent)
#                        
#                    if vascularNetwork.boundaryConditions[boundarysCurrent] == {}:
#                        notDefinedBoundarys.append(boundarysCurrent)
#                    
#                nonBoundarys = list(set(boundarys).symmetric_difference(set(boundarysSaved)))
#                for nonBoundary in nonBoundarys:
#                    print " boundary removed from vacularNetwork"
#                    del(vascularNetwork.boundaryConditions[nonBoundary])
#                    if nonBoundary in notDefinedBoundarys: notDefinedBoundarys.remove(nonBoundary)
#                    
#                vascularNetwork.evaluateConnections()
#                print ""
#                print "    sub menu: boundary conditions"
#                print ""
#                print "     [1] - show  boundary conditions"
#                print "     [2] - add   boundary condition "
#                print "     [3] - del   boundary condition "
#                print "     [4] - load  boundary conditions from CSV"
#                print "     [5] - write boundary conditions to CSV"
#                print "     [b] - back to the main menu"
#                print ""     
#                subMenuInput = raw_input("     what to do? ") 
#                
#                if subMenuInput == '1':
#                    print "     boundary conditions"
#                    pprint.pprint(vascularNetwork.boundaryConditions)
#                    subMenuInput = ''
#                    
#                elif subMenuInput == '2' and vascularNetwork.root != []:
#                    
#                    print "     add   boundary condition"
#                    print ""
#                    
#                    definedBoundarys = list(set(notDefinedBoundarys).symmetric_difference(set(vascularNetwork.boundaryConditions.keys())))
#                    print "     vessels with defined boundary condition:"
#                    print "       ",'  '.join(str(i) for i in definedBoundarys)
#                    
#                    print "     vessels with undefined boundary condition:"
#                    print "       ",'  '.join(str(i) for i in notDefinedBoundarys)
#                    print ""
#                                        
#                    existing = False
#                    vesselID = raw_input(" enter existing vessel id: ")
#                    while True:
#                        try:
#                             vesselID = int(vesselID)
#                             if vesselID in vascularNetwork.vessels:
#                                 break
#                             else:
#                                 existing = True
#                        except ValueError:
#                            print " TYPE-ERROR: vessel id must be type(int) not type(string)"
#                            vesselID = raw_input(" enter existing vessel id: ")
#                        if existing == True:
#                            print " the vessel does not exist"
#                            vesselID = raw_input(" enter existing vessel id: ")
#                            existing = False
#                    
#                    
#                    inType = '0'
#                    print "     add boundary condition type"
#                    print ""
#                    print "      'Qa'   'Q2a'   'Qm'   'Q2m'   'Pa'    'P2a'   'Pm'   'P2m'   'Ue' "
#                    print "       [1]    [2]    [3]     [4]     [5]     [6]     [7]    [8]     [9]"
#                    print ""
#                    print "      'Rt'    'R'    'WK2'  'WK3'   'QPhy'  'Lnet'  'Fou'   'D'    'PhyQ' "
#                    print "      [10]    [11]   [12]    [13]    [14]    [15]    [16]   [17]    [18]"
#                    print ""
#                    
#                    types = ['Qa','Q2a','Qm','Q2m','Pa','P2a','Pm','P2m','Ue','Rt','R','WK2','WK3','QPhy','Lnet','Fou','D','PhyQ']
#                    
#                    existing = False
#                    inType = raw_input ("      choose type ")
#                    while True:
#                        try:
#                             inType = int(inType)
#                             if inType in np.linspace(1,18,18):
#                                 break
#                             else:
#                                 existing = True
#                        except ValueError:
#                            print "      TYPE-ERROR: vessel id must be type(int) not type(string)"
#                            inType = (raw_input ("      choose type "))
#                        if existing == True:
#                            print "       the type does not exist"
#                            inType = (raw_input ("      choose type "))
#                            existing = False
#                    
#                    
#                    type = types[int(inType)-1]
#                     
#                    bcTags = {'Rt':['Rt'],
#                              'R':['Rc'],
#                              'WK2':['Rc','C'],
#                              'WK3':['Rc','C','R1','RT'],
#                              'QPhy':['Q0_a','Npulse','freq','Tpulse','Tspace'],
#                              'Qa':['Q0_a','Npulse','freq'],
#                              'Q2a':['Q0_a','Npulse','freq','Tpulse'],
#                              'Qm':['Q0_m','Tmean','Traise'],
#                              'Q2m':['Q0_m','Tmean','Traise'],
#                              'Ue':['Upeak','C','Traise'],
#                              'Pa':['P0_a','Npulse','freq'],
#                              'P2a':['P0_a','Npulse','freq','Tpulse'],
#                              'Pm':['P0_m','Tmean','Traise'],
#                              'P2m':['P0_m','Tmean','Traise'],
#                              'Fou':['P0_m','Tmean','Traise','scale','Npulse','Tpulse'],
#                              'D':[''],
#                              'PhyQ':[''],
#                              'Lnet':['Z','C']}
#                    
#                    
#                    bcList = []
#                    print "      set values for the BC condition"
#                    print "          enter 'b' for the first value to skip this procedure"
#                    question = True
#                    for arg in bcTags[type]:
#                        if question == True: 
#                            currValue = raw_input (str("            set value for "+str(arg)+' '))
#                            if currValue == 'b': question=False
#                            test = True
#                            try: float(currValue)
#                            except:
#                                print '            VALUE or TYPE ERROR, set to None'
#                                test = False
#                            if test == True: bcList.append(float(currValue))
#                            else: bcList.append(None)
#                        else: bcList.append(None)
#                    if len(vascularNetwork.boundaryConditions.keys()) == 1:
#                        print "      set position of the BC condition"
#                        position = '2'
#                        while position not in ['1','0']:
#                            position = raw_input ("          enter '0' for the start or '1' for the end of the vessel ")
#                        if position == '1':
#                            type = ''.join(['_',type])
#                    
#                    vascularNetwork.boundaryConditions[vesselID].update({type : bcList})
#                    mainGraph.update_graph(vascularNetwork, window)
#                    subMenuInput = ''
#                        
#                elif subMenuInput == '3' and vascularNetwork.root != []:
#                    print "     delete boundary condition"
#                    print ""
#                    pprint.pprint(vascularNetwork.boundaryConditions)
#                    
#                    vesselID = -1
#                    while vesselID not in vascularNetwork.boundaryConditions.keys():
#                        vesselID = int(raw_input ("      choose vessel id "))
#                    
#                    bcs = vascularNetwork.boundaryConditions[vesselID].keys()
#                    if bcs != []:                 
#                        print ""
#                        print '        ','  '.join(str(' '+i+' ') for i in bcs)
#                        print '        ','   '.join(str('['+str(int(i))+']') for i in np.linspace(1,len(bcs),len(bcs)))
#                        print ""
#                        inType = '0'
#                        while inType not in np.linspace(1,len(bcs),len(bcs)):
#                            inType = int(raw_input ("      choose condition to delete "))
#                            
#                        vascularNetwork.boundaryConditions[vesselID].pop(bcs[inType-1])
#                        print ""
#                        print "     boundary condition ",bcs[inType-1]," removed!"
#                        print ""
#                        mainGraph.update_graph(vascularNetwork, window)
#                    else:
#                        print "     nothing to delete!"
#                    subMenuInput = ''
#                
#                elif subMenuInput == '4' and vascularNetwork.root != []:
#                    
#                    print "     load  boundary conditions from CSV"
#                    print ""
#                    filename = enterFilename(filename,'')
#                    vascularNetwork.boundaryConditions = readBCFromCSV(filename = ''.join([filename,'BC','.csv']))
#                    mainGraph.update_graph(vascularNetwork, window)
#                                                           
#                elif subMenuInput == '5' and vascularNetwork.root != []:
#                    print "     write boundary conditions to CSV"
#                    print ""
#                    filename = enterFilename(filename,'')
#                    writeBCToCSV(vascularNetwork.boundaryConditions,filename = ''.join([filename,'BC','.csv']))
#                                                         
#                    
#                elif subMenuInput == 'b':
#                    break
            
        elif menuInput == "l":
            try:
                FILE = open('recentFilenames.pickle',"rb")
                # store pickle
                recentFilenames = cPickle.load(FILE)
                FILE.close()
            except:
                recentFilenames = []
                
            subMenuInput = ''
            print ""
            print "    sub menu: load data"
            print ""
            print "     [1] - load network from XML"
            print "     [2] - load vessel data from CSV"
            print "     [3] - load vessel data and boundary conditions from CSV"
            print "     [b] - back to the main menu"
            print ""
            while  subMenuInput not in ["1","2","3","b"]:
                subMenuInput = raw_input("what to do? ")
            
                print ""
                print "         resent used networks"
                i = 1
                for name in recentFilenames:
                    print "          [",i,'] - ',name
                    i = 1+i
                print ""
                if subMenuInput == '1':
                    print "     load from XML"
                    
                    filename = enterFilename(filename,'.xml',recentFilenames = recentFilenames)
                    if filename == None:break
                    # delete the old network
                    del vascularNetwork
                    #load the new network
                    vascularNetwork = loadNetworkFromXML(filename= filename)
                    if vascularNetwork == None:
                        vascularNetwork = VascularNetwork()
                        mainGraph.update_graph(vascularNetwork, window)
                        filename = None
                        break
                    
                    mainGraph.update_graph(vascularNetwork, window)
                    filename, value = filename.split(".",1)
                    break
                
                elif subMenuInput == '2':
                    print "     load vessel data from CSV - non existing vessels are added automatically"
                    print ""
                    filename = enterFilename(filename,'.csv',recentFilenames = recentFilenames)
                    if filename == None:break
                    vascularNetwork.updateNetwork(readVesselDataFromCSV(filename=filename))
                    
                    mainGraph.update_graph(vascularNetwork, window)
                    filename, value = filename.split(".",1)
                    break
                
                elif subMenuInput == '3':
                    print "     load vessel data and boundary conditions from CSV"
                    filename = enterFilename(filename,'.csv',recentFilenames = recentFilenames)
                    if filename == None:break
                    vascularNetwork.updateNetwork(readVesselDataFromCSV(filename=filename))
                    mainGraph.update_graph(vascularNetwork, window)
                    filename, value = filename.split(".",1)
                    
                    vascularNetwork.boundaryConditions = readBCFromCSV(filename = ''.join([filename,'BC','.csv']))
                    mainGraph.update_graph(vascularNetwork, window)
                    break
                
                elif subMenuInput == 'b':
                    break
            
            if filename != None:    
                if filename not in recentFilenames: recentFilenames.insert(0,filename)
                else: 
                    recentFilenames.remove(filename)
                    recentFilenames.insert(0,filename)
                if len(recentFilenames) > 5: recentFilenames.pop(-1)
                            
                FILE = open('recentFilenames.pickle',"w")
                # store pickle
                cPickle.dump(recentFilenames, FILE, protocol=2)
                FILE.close()
            
        elif menuInput == "s":
            subMenuInput = ''
            print ""
            print "    sub menu: save data"
            print ""
            print "     [1] - write to XML"
            print "     [2] - write vessel data to CSV"
            print "     [3] - write vessel data and boundary conditions to CSV"
            print "     [4] - write graph to .png and .dot files"
            print "     [b] - back to the main menu"
            print ""
            while subMenuInput not in ["1","2","3","b"]:
                subMenuInput = raw_input("what to do? ")
                     
                if subMenuInput == '1':
                    print "     write to XML"
                    filename = enterFilename(filename,'.xml')
                    if filename == None:break
                    writeNetworkToXML(vascularNetwork,filename = filename)
                    filename, value = filename.split(".",1)
                    break
                    
                elif subMenuInput == '2':
                    print "     write vessel data to CSV"
                    filename = enterFilename(filename,'.csv') 
                    if filename == None:break
                    writeVesselDataToCSV(vessels = vascularNetwork.vessels, filename = filename)
                    filename, value = filename.split(".",1)
                    break
                
                elif subMenuInput == '3':
                    print "     write vessel data and boundary conditions to CSV"
                    filename = enterFilename(filename,'.csv') 
                    if filename == None:break
                    writeVesselDataToCSV(vessels = vascularNetwork.vessels, filename = filename)
                    filename, value = filename.split(".",1)
                    writeBCToCSV(vascularNetwork.boundaryConditions,filename = ''.join([filename,'BC','.csv']))
                    break
                
                elif subMenuInput == '4':
                    print "     write graph to .png and .dot files"
                    pictureName = str(raw_input("     enter pictureName (only!):"))
                    if pictureName == "":
                        pictureName = 'pydotTest'
                    mainGraph.graph.write(graphPath+filename+'/'+pictureName+'.dot')
                    mainGraph.graph.write_png(graphPath+filename+'/'+pictureName+'.png')
                    break
                    
                if subMenuInput == 'b':
                    break
        
        elif menuInput == "u":
            subMenuInput = ''
            print ""
            print "    sub menu: update XML from CSV"
            print ""
            print "     load from XML"
            
            filename = enterFilename(filename,'.xml')
            if filename == None:break
            # delete the old network
            del vascularNetwork
            #load the new network
            vascularNetwork = loadNetworkFromXML(filename= filename)
            if vascularNetwork == None:
                vascularNetwork = VascularNetwork()
                break
            
            mainGraph.update_graph(vascularNetwork, window)
            
            filename, value = filename.split(".",1)
            
            print "     load vessel data from CSV - non existing vessels are added automatically"
            filenameCSV = ''.join([filename,'.csv'])
            vascularNetwork.updateNetwork(readVesselDataFromCSV(filename=filenameCSV))
            
            mainGraph.update_graph(vascularNetwork, window)
            
            print "     write to XML"
            filenameXML = ''.join([filename,'.xml'])
            writeNetworkToXML(vascularNetwork,filename = filenameXML)
            
            
    print "bye bye .."

if __name__ == '__main__':
    main()
