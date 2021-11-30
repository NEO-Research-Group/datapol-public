import osmnx as ox
import networkx as nx
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import csv
from deap import base,creator,tools
import random


###esto pilla el mapa de fuengirola
state = ox.geocode_to_gdf('Fuengirola, Spain')

# Defining the map boundaries de Fuengirola para el grafo
north, east, south, west = 36.5893, -4.5899, 36.5193, -4.6367 
# Downloading the map as a graph object 
G = ox.graph_from_bbox(north, south, east, west, network_type = 'drive')
###o podemos bajarlo como nombre de la localidad
###G = ox.graph_from_place('Fuengirola, Spain') 

# Plotting the graph 
###ox.plot_graph(G)

###creo diccionario con atributo "incidencias" para cada nodo
dicc_nodes = dict()
for node in G.nodes():
#    print(node)
    dicc_nodes[node] = {"incidencias": 0}

###le meto al grafo el diccionario con el nuevo atributo para cada nodo
nx.set_node_attributes(G,dicc_nodes)

###visualizo los nodos del grafo con atributos
#for node in G.nodes(data=True):
#    print(node)

###leer fichero incidencias
#all_incidencias=pd.read_csv("all_incidencias.tsv",delimiter='\t', usecols=['lon','lat'], header=0)
trafico=pd.read_csv("trafico2017.tsv",delimiter='\t', usecols=['lon','lat'])
#seguridad=pd.read_csv("seguridad2017.tsv",delimiter='\t', usecols=['lon','lat'], header=0)
#incendios=pd.read_csv("incendios2017.tsv",delimiter='\t', usecols=['lon','lat'], header=0)

tsvfile = trafico
for i in range(len(tsvfile)):
    point = (tsvfile.loc[i]['lat'], tsvfile.loc[i]['lon'])
    point_node = ox.distance.get_nearest_node(G, point)
    G.nodes[point_node]["incidencias"] += 1
    
###imprime nodos+atributos para ver incidencias modificadas
#for node in G.nodes(data=True):
#    print(node)

#me imprime por pantalla el grafo en json
#print (json_graph.node_link_data(G))

###pintar el grafo con nodos coloreados según incidencias
nc = ox.plot.get_node_colors_by_attr(G, "incidencias", cmap="plasma")
fig, ax = ox.plot_graph(G, bgcolor="k", node_color=nc, node_size=5, edge_linewidth=1, edge_color="#333333")


nodeID_list = list(G.nodes)

exit(0)
#######   rollito evolutivo con DEAP

###creación del tipo individuo y fitness
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", np.array, fitness=creator.FitnessMin)

IND_SIZE = len(G.nodes)

toolbox = base.Toolbox()
toolbox.register("attribute", random.randint, 0, 1)
toolbox.register("individual", tools.initRepeat, creator.Individual,toolbox.attribute, n=IND_SIZE)
toolbox.register("population", tools.initRepeat, np.array, toolbox.individual)

###evaluación de cada individuo
def evaluate(individual):
    nonzeronodes = np.nonzero(individual)[0]
    individualnodes = [nodeID_list[i] for i in nonzeronodes]
    sumnodes = sum([G.nodes[i]["incidencias"] for i in individualnodes])
    subgraph = G.subgraph(individualnodes)
    spantree = nx.minimum_spanning_tree(subgraph.to_undirected())
    lenspantree = sum([sorted(spantree.edges(data=True))[i][2]['length'] for i in range(len(spantree.edges))])
    return sumnodes/lenspantree,

#registro de funciones, algo de DEAP
toolbox.register("evaluate", evaluate)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=1, indpb=0.1)
toolbox.register("select", tools.selTournament, tournsize=3)

pop = toolbox.population(n=50)
CXPB, MUTPB, NGEN = 0.5, 0.2, 40

###evaluación de toda la población
fitnesses = map(toolbox.evaluate, pop)
for ind, fit in zip(pop, fitnesses):
    ind.fitness.values = fit

for g in range(NGEN):
    ###siguiente generación
    offspring = toolbox.select(pop, len(pop))
    ###clonar los individuos seleccionados
    offspring = map(toolbox.clone, offspring)

    ###aquí viene el cruce y la mutación de los offspring
    for child1, child2 in zip(offspring[::2], offspring[1::2]):
        if random.random() < CXPB:
            toolbox.mate(child1, child2)
            del child1.fitness.values
            del child2.fitness.values

    for mutant in offspring:
        if random.random() < MUTPB:
            toolbox.mutate(mutant)
            del mutant.fitness.values

    ###evaluación de individuos con fitness chungo
    invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
    fitnesses = map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit

    ###reemplazo de la población por el offspring
    pop[:] = offspring

