import pydot
import xdot
import gtk
import cPickle

class MyDotWindow(xdot.DotWindow):

    def __init__(self):
        xdot.DotWindow.__init__(self)


# class for the graph

class Graph(object):
    
    def __init__(self):
        '''
        Constructor
        '''
        # create the graph
        self.graph = pydot.Dot(graph_type ='graph')
    
    
    def add_vessel(self,node1, node2, name):
        ## creates vessel in the network graph
        
        # create start node if not existing
        if self.graph.get_node(node1) == None or self.graph.get_node(node1) == []:
            self.graph.add_node(pydot.Node(node1))
            if type(self.graph.get_node(node1)) == list:
            	self.graph.get_node(node1)[0].set_shape('circle')
                self.graph.get_node(node1)[0].set_fontsize('9')
            else:
            	self.graph.get_node(node1).set_shape('circle')
                self.graph.get_node(node1).set_fontsize('9')
            	
        # create end node if not existing
        if self.graph.get_node(node2) == None or self.graph.get_node(node2) == []:
            self.graph.add_node(pydot.Node(node2))
            if type(self.graph.get_node(node2)) == list:
            	self.graph.get_node(node2)[0].set_shape('circle')
                self.graph.get_node(node2)[0].set_fontsize('9')
            else:
            	self.graph.get_node(node2).set_shape('circle')
                self.graph.get_node(node2).set_fontsize('9')
            
        # create vessel
        self.graph.add_edge(pydot.Edge(node1,node2, label= name))
        
        
    def add_bc(self,networkNode, bcNode, name, rootCON = False):
        ## creates boundary node
        
        # check if networkNode exists
        if self.graph.get_node(networkNode) == None or self.graph.get_node(networkNode) == []:
            print 'Error: something went wrong, not such network nodes'
        
        # creates boundary condition node
        if self.graph.get_node(bcNode) == None or self.graph.get_node(bcNode) == []:
            self.graph.add_node(pydot.Node(bcNode, label= name))
            if type(self.graph.get_node(bcNode)) == list:
                self.graph.get_node(bcNode)[0].set_shape('box')
                self.graph.get_node(bcNode)[0].set_color('darkgreen')
            else:
                self.graph.get_node(bcNode).set_shape('box')
                self.graph.get_node(bcNode).set_color('darkgreen')
                
        # cretes edge connection
        if rootCON: 
            self.graph.add_edge(pydot.Edge(bcNode,networkNode,color = 'darkgreen'))
        else: 
            self.graph.add_edge(pydot.Edge(networkNode,bcNode,color = 'darkgreen'))


    def getGraph(self):
        return self.graph.to_string()
    
    
    def update_graph(self, vascularNetwork, window):
     
        self.resetGraph()
        vascularNetwork.evaluateConnections()
             
        
        if vascularNetwork.vessels.keys() != []:
            ## go through network as a binary tree and create vessel graph
            
            # vessels with non visualized daughters:
            viz = []
            #find root
            if len(vascularNetwork.root) == 0:
                print 'no root in graph' 
                return
            root = vascularNetwork.root[0]
            # add root to graph
            self.add_vessel(node1 = str(vascularNetwork.vessels[root].start), node2=str(vascularNetwork.vessels[root].end), name=str('#'+str(root)+' '+vascularNetwork.vessels[root].name))
            # add root to the viz vessels if root has daughters:
            if vascularNetwork.vessels[root].leftDaughter != None:
                viz.append(root)
            # loop through tree until all daughters are added to the graph
            while len(viz) != 0:
                # get the mother vessel (already added) and add its daughters
                motherVessel = viz.pop(0)
                # find left daughter
                leftDaughter = vascularNetwork.vessels[motherVessel].leftDaughter
                # add left daughter
                self.add_vessel(node1 = str(vascularNetwork.vessels[leftDaughter].start), node2=str(vascularNetwork.vessels[leftDaughter].end), name=str('#'+str(leftDaughter)+' '+vascularNetwork.vessels[leftDaughter].name))
                # check if leftDaughter has also daughters which should be visualized
                if vascularNetwork.vessels[leftDaughter].leftDaughter != None:
                    viz.append(leftDaughter)
                # find right daughter
                if vascularNetwork.vessels[motherVessel].rightDaughter != None:
                    rightDaughter = vascularNetwork.vessels[motherVessel].rightDaughter
                    # add right daughter
                    self.add_vessel(node1 = str(vascularNetwork.vessels[rightDaughter].start), node2=str(vascularNetwork.vessels[rightDaughter].end), name=str('#'+str(rightDaughter)+' '+vascularNetwork.vessels[rightDaughter].name))
                    # check if rightDaughter has also daughters which should be visualized
                    if vascularNetwork.vessels[rightDaughter].leftDaughter != None:
                        viz.append(rightDaughter)
            
            ## create boundary condition nodes
        
            ## root node bc condition
            # find applied bc conditions
            bcNames = ['?']
            bcTrue = False
            if root in vascularNetwork.boundaryConditions.keys() and vascularNetwork.boundaryConditions[root] != {}:
                    bcNames.pop(0)
                    for boundaryInstance in vascularNetwork.boundaryConditions[root]:
                        bcNames.append(boundaryInstance.name)
            for bcName in bcNames:
                if '_' not in bcName:
                    self.add_bc(str(vascularNetwork.vessels[root].start), ''.join(['bcR',str(root),str(bcNames.index(bcName))]), bcName, rootCON = True) 
                    bcTrue = True
            if bcTrue == False:
                self.add_bc(str(vascularNetwork.vessels[root].start), ''.join(['bcR',str(root),'0']), '?', rootCON = True)
            # end node bc conditions
            for endNode in vascularNetwork.ends:
                bcNames = ['?']
                if endNode in vascularNetwork.boundaryConditions.keys() and vascularNetwork.boundaryConditions[endNode] != {}:
                        bcNames.pop(0)
                        for boundaryInstance in vascularNetwork.boundaryConditions[endNode]:
                            bcNames.append(boundaryInstance.name)
                if endNode == root:
                    bcTrue = False
                    for bcName in bcNames:
                        if '_' in bcName: 
                            self.add_bc(str(vascularNetwork.vessels[endNode].end), ''.join(['bcEq',str(endNode),str(bcNames.index(bcName))]), bcName) 
                            bcTrue = True
                    if bcTrue == False:
                        self.add_bc(str(vascularNetwork.vessels[endNode].end), ''.join(['bcEq',str(endNode),'0']), '?')
                else:
                    for bcName in bcNames:
                        self.add_bc(str(vascularNetwork.vessels[endNode].end), ''.join(['bcEq',str(endNode),str(bcNames.index(bcName))]), bcName) 
        # save the vascularNetwork temporary                          
        tempSave(vascularNetwork)
        window.set_dotcode(self.graph.to_string())
        window.show()
    
    def resetGraph(self):
        self.graph = pydot.Dot(graph_type ='graph')
    

def bifTest(vessels,testNode):
    # bifTest returns true if less then 2 nodes start at testNode
    # bifTest retruns false if already 2 nodes start here
    bifCounter = 0
    for vessel_i in vessels.itervalues():
        if vessel_i.start == testNode:
            bifCounter = bifCounter + 1
    if bifCounter <2:
        return True
    else:
        return False
    
def enterFilename(filename, endString,recentFilenames = None):
    print "     current filename: ",filename
    filenameT = str(raw_input("     enter/change filename (only!) (ENTER to use current filename):\n     "))
    if filenameT == "":
        if filename != None:
            filenameT = filename+endString
        else:
            filenameT = None
        
    if filenameT in ['1','2','3','4','5'] and len(filenameT)==1 and recentFilenames!= None:
        number = int(filenameT)
        print number,filenameT
        if len(recentFilenames)>= number:
            filenameT = (recentFilenames[number-1]+endString)
            
    if endString not in filenameT:
        filenameT = (filenameT+endString)
        
    return filenameT
    
def tempSave(vascularNetwork):
    FILE = open('tempData.pickle',"w")
    vascularNetwork.quiet = True
    # store pickle
    #cPickle.dump(vascularNetwork, FILE, protocol=2)
    FILE.close()
    
def tempLoad():
    try:
        FILE = open('tempData.pickle',"rb")
        # store pickle
        vascularNetwork = cPickle.load(FILE)
        FILE.close()
        return vascularNetwork
    except:
        print "Error - could nof find tempData.pickle"
    


def findAllDaughters(vascularNetwork, motherVesselID):
    daughters = []
    viz = []
    root = motherVesselID
    if vascularNetwork.vessels[root].leftDaughter != None:
        viz.append(root)
    # loop through tree until all daughters are added to the graph
    while len(viz) != 0:
        # get the mother vessel (already added) and add its daughters
        motherVessel = viz.pop(0)
        # find left daughter
        leftDaughter = vascularNetwork.vessels[motherVessel].leftDaughter
        # add left daughter
        daughters.append(leftDaughter)
        # check if leftDaughter has also daughters 
        if vascularNetwork.vessels[leftDaughter].leftDaughter != None:
            viz.append(leftDaughter)
        # find right daughter
        if vascularNetwork.vessels[motherVessel].rightDaughter != None:
            rightDaughter = vascularNetwork.vessels[motherVessel].rightDaughter
            # add right daughter
            daughters.append(rightDaughter)
            # check if rightDaughter has also daughters
            if vascularNetwork.vessels[rightDaughter].leftDaughter != None:
                viz.append(rightDaughter)
    return daughters
    
