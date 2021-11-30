import os.path

import osmnx as ox
import networkx as nx
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import csv
from random import randrange
import copy


def oneRandomFromList(myList):
    return myList[randrange(0, len(myList))]

def removeOneRandomFromList(myList):
    index = randrange(0, len(myList))
    return myList.pop(index)

class Solution:
    patrols = None
    patrolOfNode = None
    graph: nx.Graph = None
    sumOfWeightsForPatrols: list = None # Keep here the weights for efficiency
    minSpanningTreeWeightForPatrols: list = None # Keep here the weight of the min Spanning tree for efficiency
    adjacentNodesForPatrol = None

    def __init__(self, graph: nx.Graph, numberOfPatrols: int):
        self.graph = graph  ### TODO: incluyo esta para poder guardar graph en la class
        self.patrols = list()
        self.sumOfWeightsForPatrols = list()
        self.minSpanningTreeWeightForPatrols = list()
        self.adjacentNodesForPatrol = list()
        for i in range(numberOfPatrols):
            self.patrols.append(set()) # Adding empty sets
            self.sumOfWeightsForPatrols.append(0)
            self.minSpanningTreeWeightForPatrols.append(0)
            self.adjacentNodesForPatrol.append(set())

        self.patrolOfNode = dict()
        for n in graph.nodes():
            self.patrolOfNode[n] = None

    def __str__(self):
        str = ''
        for p in range(len(self.patrols)):
            str += f'Patrol: {p}, events: {self.sumOfWeightsForPatrols[p]}, spanning tree: {self.minSpanningTreeWeightForPatrols[p]}\n'
        return str

    def addNodesToPatrol(self, nodes, patrol):
        for n in nodes:
            if self.patrolOfNode[n] != None:
                self.patrols[self.patrolOfNode[n]].remove(n)
            self.patrolOfNode[n] = patrol
            self.patrols[patrol].add(n)

    def computeAdjacentNodesForPatrol(self, patrol):
        self.adjacentNodesForPatrol[patrol].clear()
        for n in self.patrols[patrol]:
            self.adjacentNodesForPatrol[patrol].update(self.graph.neighbors(n))
        self.adjacentNodesForPatrol[patrol].difference_update(self.patrols[patrol])

    def updateAdjacentNodesForPatrolWhenAddingNode(self, node, patrol):
        self.adjacentNodesForPatrol[patrol].update(self.graph.neighbors(node))
        self.adjacentNodesForPatrol[patrol].remove(node)

    def randomInitialization(self):
        for n in self.patrolOfNode.keys():
            self.patrolOfNode[n] = None

        unvisitedNodes = list(self.patrolOfNode.keys())
        maxNodesInPatrol = len(self.patrolOfNode)/len(self.patrols)
        #print(f'Number of nodes: {self.graph.number_of_nodes()}')
        #print(f'Number of patrols: {len(self.patrols)}')
        #print(f'Max nodes in patrol: {maxNodesInPatrol}')
        #print(f'Unvisited nodes: {len(unvisitedNodes)}')

        def bfs(seedNode):
            nodesToChooseFrom = []
            nodesToChooseFrom.append(seedNode)
            elementsInSet = 0
            resultSet = set()

            while len(nodesToChooseFrom)>0 and elementsInSet < maxNodesInPatrol:
                newNode = oneRandomFromList(nodesToChooseFrom)
                resultSet.add(newNode)
                elementsInSet += 1
                unvisitedNodes.remove(newNode)
                nodesToChooseFrom.remove(newNode)
                for adj in self.graph.neighbors(newNode):
                    if self.patrolOfNode[adj] == None and not (adj in resultSet) and not (adj in nodesToChooseFrom):
                        nodesToChooseFrom.append(adj)

            return resultSet

        for i in range(len(self.patrols)):
            #print(f'Initializing patrol {i}')
            seedNode = oneRandomFromList(unvisitedNodes)
            nodesInPatrol = bfs(seedNode)
            #print(f'Assigned nodes: {len(nodesInPatrol)}')
            self.addNodesToPatrol(nodesInPatrol, i)
            #print(f'Unvisited nodes: {len(unvisitedNodes)}')
        for i in range(len(self.patrols)):
            self.evaluatePatrol(i)
            self.computeAdjacentNodesForPatrol(i)

    def move(self):
        for p in range(len(self.patrols)):
            contributionOfP = self.contributionOfPatrol(p)
            for n in self.adjacentNodesForPatrol[p]:
                ###print("bucle move: explorando nodo", n)
                if contributionOfP == 0 and self.graph.nodes[n]["incidencias"]==0:
                    continue

                if self.patrolOfNode[n] == p:
                    raise "This should not happen: adjacent nodes of patrols are wrong"
                previousPatrol = self.patrolOfNode[n]
                contributionOfPreviousPatrol = 0
                newContributionOfPreviousPatrol = 0

                if previousPatrol != None:
                    subgraph_patrol = self.graph.subgraph(self.patrols[previousPatrol]) ### TODO: subgrafo patrulla "previousPatrol"
                    if n in nx.articulation_points(subgraph_patrol): ### TODO: es punto de articulación?
                        continue
                    contributionOfPreviousPatrol = self.contributionOfPatrol(previousPatrol)
                    self.patrols[previousPatrol].remove(n)
                    self.evaluatePatrol(previousPatrol)
                    newContributionOfPreviousPatrol = self.contributionOfPatrol(previousPatrol)

                self.patrolOfNode[n] = p
                self.patrols[p].add(n)
                self.evaluatePatrol(p)
                newContributionOfPatrolP = self.contributionOfPatrol(p)

                delta = (newContributionOfPatrolP+newContributionOfPreviousPatrol) - (contributionOfP+contributionOfPreviousPatrol)
                if delta > 0:
                    # Move to new solution, leave the change as it is
                    self.computeAdjacentNodesForPatrol(p)
                    if previousPatrol != None:
                        self.computeAdjacentNodesForPatrol(previousPatrol)
                    return delta
                else:
                    self.patrolOfNode[n] = previousPatrol
                    self.patrols[p].remove(n)
                    if previousPatrol != None:
                        self.patrols[previousPatrol].add(n)
                        self.evaluatePatrol(previousPatrol)
                    self.evaluatePatrol(p)  # We can do this more efficient, storing previous numbers

        return 0

    def localSearch(self):
        while self.move() > 0:
            pass

    def randomMove(self):
        patrol = randrange(0, len(self.patrols))
        adjacentNodes = list(self.adjacentNodesForPatrol[patrol])
        while len(adjacentNodes) == 0:
            patrol = randrange(0, len(self.patrols))
            adjacentNodes = list(self.adjacentNodesForPatrol[patrol])

        node = None
        while node == None and len(adjacentNodes)>0:
            node = removeOneRandomFromList(adjacentNodes)
            previousPatrol = self.patrolOfNode[node]
            if previousPatrol != None:
                subgraph_patrol = self.graph.subgraph(self.patrols[previousPatrol]) ### TODO: subgrafo patrulla "previousPatrol"
                if node in nx.articulation_points(subgraph_patrol): ### TODO: es punto de articulación?
                    node = None
                    continue
                self.patrols[previousPatrol].remove(node)
                self.evaluatePatrol(previousPatrol)
                self.computeAdjacentNodesForPatrol(previousPatrol)

            self.patrolOfNode[node] = patrol
            self.patrols[patrol].add(node)
            self.evaluatePatrol(patrol)
            self.computeAdjacentNodesForPatrol(patrol)

    def perturb(self, perturbationFactor):
        for i in range(perturbationFactor):
            self.randomMove()

    def evaluate(self):
        fitness=0
        for p in range(len(self.patrols)):
            fitness += self.contributionOfPatrol(p)
        return fitness

    def contributionOfPatrol(self, p):
        return self.sumOfWeightsForPatrols[p] / (1 + self.minSpanningTreeWeightForPatrols[p])

    def evaluatePatrol(self, p: int):
        self.sumOfWeightsForPatrols[p] = sum([self.graph.nodes[n]["incidencias"] for n in self.patrols[p]])
        ### subgraph = self.graph.subgraph(self.patrols[p]).to_undirected() ### NO ES NECESARIO to_undirected()
        subgraph = self.graph.subgraph(self.patrols[p])
        ###print("subgrafo evaluacion patrol", p)
        spanTree = nx.minimum_spanning_tree(subgraph, weight='length')
        ###print("Spaning Tree: ", spanTree)
        self.minSpanningTreeWeightForPatrols[p] = sum([e[2]['length'] for e in spanTree.edges(data=True)])

def readGraph():
    filename='graph.pickle'
    if os.path.exists(filename):
        graph = nx.read_gpickle(filename)
    else:
        ###north, east, south, west = 36.5893, -4.5899, 36.5193, -4.6367  ### TODO: coordinates for the graph
        north, east, south, west = 36.57, -4.6, 36.53, -4.62  ### TODO: smaller graph for Fuengirola
        graph = ox.graph_from_bbox(north, south, east, west, network_type='drive')  ### TODO: obtenemos graph
        #graph =  ox.graph_from_place('Fuengirola, Spain')
        #graph = ox.project_graph(graph)
        #graph = ox.consolidate_intersections(graph, tolerance=10, rebuild_graph=True, dead_ends=True, rebuild_graph=True)

        graph = graph.to_undirected()
        nodes = max(nx.connected_components(graph), key=len)
        graph = graph.subgraph(nodes)

        ### diccionario para incluir atributo "incidencias" a los nodos
        dicc_nodes = dict()
        for node in graph.nodes():
            dicc_nodes[node] = {"incidencias": 0}
        nx.set_node_attributes(graph, dicc_nodes)  ### TODO: nuevo atributo de nodos al grafo

        print('Reading issues')
        ### carga fichero de incidencias
        tsvfile = pd.read_csv("incendios2017.tsv", delimiter='\t', usecols=['lon', 'lat'])
        print('Issues read')

        print('Assigning incidences to nodes')
        ### asigna incidencias a cada nodo del grafo
        for i in range(len(tsvfile)):
            point = (tsvfile.loc[i]['lat'], tsvfile.loc[i]['lon'])
            ###point_node = ox.nearest_nodes(graph, point[0], point[1])
            point_node = ox.get_nearest_node(graph, point)
            graph.nodes[point_node]["incidencias"] += 1
        print('Incidences assigned')

        nx.write_gpickle(graph, filename)

    return graph

def ils():
    print('Reading graph')
    graph = readGraph()
    print('Graph read')

    for n in graph.nodes(data=True):
       if n[1]['incidencias'] > 0:
           print(n)

    numberOfPatrols = 15 # FIXME: put the correct number of patrols

    ###pintar el grafo con nodos coloreados según incidencias
    #nc = ox.plot.get_node_colors_by_attr(G, "incidencias", cmap="plasma")
    #fig, ax = ox.plot_graph(G, bgcolor="k", node_color=nc, node_size=5, edge_linewidth=1, edge_color="#333333")

    nodeID_list = list(graph.nodes) ### TODO: lista de nodos del grafo

    maxIterations = 10 # FIXME: this should be a parameter
    perturbationFactor = 1000 # FIXME: this should be a parameters

    print('Initializing solution')
    # Initialize the random solution
    solution = Solution(graph, numberOfPatrols)
    solution.randomInitialization()
    print(f'Solution initialized (fitness={solution.evaluate()})')

    iterations = 0

    bestSoFarSolution = None

    while iterations < maxIterations:
        print(f'Iteration {iterations}')
        solution.localSearch()
        if bestSoFarSolution == None or solution.evaluate() > bestSoFarSolution.evaluate():
            bestSoFarSolution = copy.deepcopy(solution)
            print(f'Best so far solution has fitness {bestSoFarSolution.evaluate()}')
        solution.perturb(perturbationFactor)
        iterations += 1
    
    print(bestSoFarSolution)


ils()