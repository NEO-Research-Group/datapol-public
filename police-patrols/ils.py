import copy
from random import randrange
import networkx as nx

def oneRandomFromList(myList):
    return myList[randrange(0, len(myList))]

class Solution:
    patrols = None
    patrolOfNode = None
    graph: nx.Graph = None
    sumOfWeightsForPatrols: list = None # Keep here the weights for efficiency
    minSpanningTreeTreeWeightForPatrols: list = None # Keep here the weight of the min Spanning tree for efficiency
    adjacentNodesForPatrol = None

    def __init__(self, graph: nx.Graph, numberOfPatrols: int):
        self.patrols = list()
        self.sumOfWeightsForPatrols = list()
        self.minSpanningTreeTreeWeightForPatrols = list()
        self.adjacentNodesForPatrol = list()
        for i in range(numberOfPatrols):
            self.patrols.append({}) # Adding empty sets
            self.sumOfWeightsForPatrols.append(0)
            self.minSpanningTreeTreeWeightForPatrols.append(0)
            self.adjacentNodesForPatrol.append({})

        self.patrolOfNode = dict()
        for n in graph.nodes():
            self.patrolOfNode[n] = None

    def addNodesToPatrol(self, nodes, patrol):
        for n in nodes:
            if self.patrolOfNode[n] != None:
                self.patrols[self.patrolOfNode[n]].remove(n)
            self.patrolOfNode[n] = patrol
            self.patrols[patrol].append(n)

    def randomInitialization(self):
        for n in self.patrolOfNode.keys():
            self.patrolOfNode[n] = None

        unvisitedNodes = list(self.patrolOfNode.keys())
        maxNodesInPatrol = len(self.patrolOfNode)/len(self.patrols)

        def bfs(seedNode):
            nodesToChooseFrom = []
            nodesToChooseFrom.append(seedNode)
            elementsInSet = 0
            resultSet = {}

            while len(nodesToChooseFrom)>0 and elementsInSet < maxNodesInPatrol:
                newNode = oneRandomFromList(nodesToChooseFrom)
                resultSet.add(newNode)
                unvisitedNodes.remove(newNode)
                nodesToChooseFrom.remove(newNode)
                for adj in self.graph.neighbors(newNode):
                    if self.patrolOfNode[adj] == None and not (adj in resultSet) and not (adj in nodesToChooseFrom):
                        nodesToChooseFrom.append(adj)

            return resultSet


        for i in range(len(self.patrols)):
            seedNode = oneRandomFromList(unvisitedNodes)
            nodesInPatrol = bfs(seedNode)
            self.addNodesToPatrol(nodesInPatrol, i)

    def move(self):
        # TODO: move of local search
        return

    def localSearch(self):
        while self.move() > 0:
            pass

    def perturb(self, perturbationFactor):
        # TODO: do 'perturbationFActor' random moves
        return

    def evaluate(self):
        fitness=0
        for p in range(len(self.patrols)):
            fitness += self.sumOfWeightsForPatrols[p]/self.minSpanningTreeTreeWeightForPatrols[p]

        return fitness


def ils():
    graph = None # TODO: here we should have the graph
    numberOfPatrol = 10 # FIXME: put the correct number of patrols

    maxIterations = 1000 # FIXME: this should be a parameter
    perturbationFactor = 100 # FIXME: this should be a parameters

    # Initialize the random solution
    solution = Solution(graph, numberOfPatrol)
    solution.randomInitialization()

    iterations = 0

    bestSoFarSolution = None

    while iterations < maxIterations:
        solution.localSearch()
        if bestSoFarSolution == None or solution.evaluate() > bestSoFarSolution.evaluate():
            bestSoFarSolution = copy.deepcopy(solution)
        solution.perturb(perturbationFactor)