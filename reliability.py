"""
Graph reliability from MC simulation
====================================

This code tries to compute the connectivity reliability between the first and
last node of a graph given by Matlab ``.mat`` file containing the connectivity
matrix. All the nodes in the graph can only have uniform failure rate.

"""

from __future__ import print_function

import argparse
import random

import networkx as nx
import scipy.io


#
# Reading the graph
# -----------------
#

def read_graph(file_name, mat_name):

    """Reads a graph from given file name

    :param file_name: The name of the mat file for the adjacency matrix
    :param mat_name: The identifier of the adjacency matrix in the mat file
    :returns: A NetworkX graph

    """

    file_content = scipy.io.loadmat(file_name)
    adj_mat = file_content[mat_name]
    return nx.Graph(adj_mat)


#
# MC simulation
# -------------
#

def if_conn(graph):

    """Tests the connectivity of the first and last node of the graph"""

    nodes = graph.nodes()
    first_node = nodes[0]
    last_node = nodes[-1]
    return nx.has_path(graph, first_node, last_node)


def count_simple_path(graph):

    """Counts the number of simple path from the first to the last node"""

    nodes = graph.nodes()
    first_node = nodes[0]
    last_node = nodes[-1]
    return len(list(nx.all_simple_paths(graph, first_node, last_node)))


def gen_graph_w_failure(graph, rate):

    """Generates a graph from a given graph with nodes fail by a given rate

    :param graph: The source graph
    :param rate: The probability that any node would fail

    """

    nodes = graph.nodes()

    new_nodes = []
    for i in nodes:
        rand_number = random.random()
        if rand_number < rate:
            continue
        else:
            new_nodes.append(i)

    return graph.subgraph(new_nodes)


def do_one_MC(graph, rate, count_path=False):

    """Performs one MC simulation

    It will return a boolean value indicating the connectivity after the
    failure, with ``True`` being still connected.

    """

    sub_graph = gen_graph_w_failure(graph, rate)
    if count_path:
        return count_simple_path(sub_graph)
    else:
        return if_conn(sub_graph)


def compute_reliability(graph, rate, n_samples, count_path=False):

    """Compute the reliability by MC method

    A set of ``n_sample`` graphs will be generated from the graph based on the
    failure rate. The probability of still being connected are returned.

    """

    if count_path:

        init_path_cnt = count_simple_path(graph)
        path_cnt_after = [
            do_one_MC(graph, rate, True) for i in xrange(0, n_samples)
            ]
        ratios = [i * 1.0 / init_path_cnt for i in path_cnt_after]
        return sum(ratios) / len(ratios)

    else:
        result = [do_one_MC(graph, rate, False) for i in xrange(0, n_samples)]
        return len([i for i in result if i]) * 1.0 / len(result)


#
# The driver function
# -------------------
#


def main():

    """The main driver function"""

    parser = argparse.ArgumentParser(
        description='Compute the reliability of network by MC simulation'
        )
    parser.add_argument('mat', metavar='FILE',
                        help='The mat file with the adjacency matrix')
    parser.add_argument('-n', '--name', metavar='NAME', default='A',
                        help='Name of the adjacency matrix in the mat file')
    parser.add_argument('-r', '--rate', default=0.1, type=float,
                        help='The failure rate')
    parser.add_argument('-s', '--sample', default=2000, type=int,
                        help='The number of sampling in the MC simulation')
    parser.add_argument('-c', '--count-paths', default=False,
                        action='store_true', help='If count the actual number'
                        'of simple paths')
    args = parser.parse_args()

    graph = read_graph(args.mat, args.name)

    reliability = compute_reliability(graph, args.rate,
                                      args.sample, args.count_paths)

    print(
        'After %d MC simulation, the network with %d nodes' % (args.sample,
                                                               graph.order())
        )
    print(
        'has been computed to have reliability %f ' % reliability
        )

    return 0


if __name__ == '__main__':
    main()
