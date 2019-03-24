# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 20:42:23 2017
revised on Oct 15 2017
@author:xiaoke
"""

import networkx as nx
import random
import copy
"""
selfloop:config_model\random_1k
"""

__all__ = ['count_degree_nodes',  # dict_degree_nodes
           'er_graph',  # ER_model
           'config_model',
           'random_0k',
           'random_1k',
           'random_2k',
           'random_25k',
           'random_3k',
           'rich_club_create',
           'rich_club_break',
           'assort_mixing',
           'disassort_mixing',
           'random_1kd']


def count_degree_nodes(degree_nodes):
    """Count nodes with the same degree

    Parameters
    ----------
    degree_nodes : list
        a list contains nodes and degree [[degree,node]]

    Returns
    -------
    a dict contains nodes and degree {degree:[node1,node2...]}
    where node1 and node2 have the same degree

    Examples
    --------
    >>> from unweighted_null_model import count_degree_node
    >>> n_list = [[1,2],[1,3],[2,4],[2,5]]
    >>> count_degree_node(n_list)
    ... {1: [2, 3], 2: [4, 5]}s
    """
    degree_dict = {}
    for n_d in degree_nodes:
        if n_d[0] not in degree_dict:
            degree_dict[n_d[0]] = [n_d[1]]
        else:
            degree_dict[n_d[0]].append(n_d[1])
    return degree_dict


def er_graph(G):
    """Return a random graph G_{n,p} (Erdős-Rényi graph, binomial graph).

    Chooses each of the possible edges with probability p.

    Parameters
    ----------
    G : undirected and unweighted graph
    n : int
        The number of nodes.
    p : float
        Probability for edge creation.
    directed : bool, optional (default=False)
        If True return a directed graph

    Notes
    -----
    The G_{n,p} graph algorithm chooses each of the [n(n-1)]/2
    (undirected) or n(n-1) (directed) possible edges with probability p.

    References
    ----------
    .. [1] P. Erdős and A. Rényi, On Random Graphs, Publ. Math. 6, 290 (1959).
    .. [2] E. N. Gilbert, Random Graphs, Ann. Math. Stat., 30, 1141 (1959).
    """
    n = len(G.nodes())
    m = len(G.edges())
    p = 2.0 * m / (n * n)
    return nx.random_graphs.erdos_renyi_graph(n, p, directed=False)


def config_model(G):
    """Returns a random bipartite graph from the given graph

    Parameters
    ----------
    G : undirected and unweighted graph
    degree_seq : list
        Degree sequence of the given graph G
    """
    degree_seq = list(G.degree().values())
    return nx.configuration_model(degree_seq)


def random_0k(G0, n_swap=1, max_tries=100, connected=1):
    """Return a 0K null model beased on random reconnection algorithm

    Parameters
    ----------
    G0 : undirected and unweighted graph
    n_swap : int (default = 1)
        coefficient of change successfully
    max_tries : int (default = 100)
        number of changes
    connected : int
        keep the connectivity of the graph or not.
        1:keep,    0:not keep

    Notes
    -----
    The 0K null models have the same average node degree as the original graph

    See Also
    --------
    er_graph

    """
    if G0.is_directed():
        raise nx.NetworkXError("It is only allowed for undirected graphs.")
    if n_swap > max_tries:
        raise nx.NetworkXError("Number of swaps > number of tries allowed.")
    if len(G0) < 3:
        raise nx.NetworkXError("This graph has less than three nodes.")

    G = copy.deepcopy(G0)

    n_try = 0
    count_swap = 0
    edges = G.edges()
    nodes = G.nodes()
    while count_swap < n_swap:
        n_try = n_try + 1
        # choose a edge randomly
        u, v = random.choice(edges)
        # choose two nodes which are not connected
        x, y = random.sample(nodes, 2)
        if len(set([u, v, x, y])) < 4:
            continue
        if (x, y) not in edges and (y, x) not in edges:
            # cut the original edge
            G.remove_edge(u, v)
            # connect the new edge
            G.add_edge(x, y)
            edges.remove((u, v))
            edges.append((x, y))

            # if connected = 1 but the original graph is not connected fully,
            # withdraw the operation about the swap of edges.
            if connected == 1:
                if not nx.is_connected(G):
                    G.add_edge(u, v)
                    G.add_edge(x, y)
                    G.remove_edge(u, y)
                    G.remove_edge(x, v)
                    continue
            count_swap = count_swap + 1

        if n_try >= max_tries:
            e = ('Maximum number of swap attempts (%s) exceeded ' %
                 n_try + 'before desired swaps achieved (%s).' % n_swap)
            print e
            break
    return G


def random_1k(G0, n_swap=1, max_tries=100, connected=1):
    """
    Return a 1K null model beased on random reconnection algorithm

    Parameters
    ----------
    G0 : undirected and unweighted graph
    n_swap : int (default = 1)
        coefficient of change successfully
    max_tries : int (default = 100)
        number of changes
    connected : int
        keep the connectivity of the graph or not.
        1:keep,    0:not keep

    Notes
    -----
    The 1K null models require reproducing the original graph’s
    node degree distribution.

    """

    if not nx.is_connected(G0):
        raise nx.NetworkXError("It is only allowed for connected graphs.")
    if G0.is_directed():
        raise nx.NetworkXError("It is only allowed for undirected graphs.")
    if n_swap > max_tries:
        raise nx.NetworkXError("Number of swaps > number of tries allowed.")
    if len(G0) < 4:
        raise nx.NetworkXError("This graph has less than three nodes.")

    n_try = 0
    count_swap = 0

    G = copy.deepcopy(G0)
    keys, degrees = zip(*G.degree().items())
    cdf = nx.utils.cumulative_distribution(degrees)

    while count_swap < n_swap:
        if n_try >= max_tries:
            e = ('尝试次数 (%s) 已超过允许的最大次数' % n_try + '有效交换次数（%s)' % count_swap)
            print(e)
            break
        n_try += 1

        # make sure the degree distribution unchanged,choose two edges
        # (u-v,x-y) randomly
        (ui, xi) = nx.utils.discrete_sequence(2, cdistribution=cdf)
        if ui == xi:
            continue
        u = keys[ui]
        x = keys[xi]
        v = random.choice(list(G[u]))
        y = random.choice(list(G[x]))
        # make sure the four nodes are not repeated
        if len(set([u, v, x, y])) == 4:
            # make sure the new edges are not exist in the original graph
            if (y not in G[u]) and (v not in G[x]):
                # add two new edges
                G.add_edge(u, y)
                G.add_edge(v, x)
                # delete two old edges
                G.remove_edge(u, v)
                G.remove_edge(x, y)
                # if connected = 1 but the original graph is not connected fully,
                # withdraw the operation about the swap of edges.
                if connected == 1:
                    if not nx.is_connected(G):
                        G.add_edge(u, v)
                        G.add_edge(x, y)
                        G.remove_edge(u, y)
                        G.remove_edge(x, v)
                        continue
                count_swap = count_swap + 1
    return G


def random_2k(G0, n_swap=1, max_tries=100, connected=1):
	"""Return a 2K null model beased on random reconnection algorithm

    Parameters
    ----------
    G0 : undirected and unweighted graph
    n_swap : int (default = 1)
        coefficient of change successfully
    max_tries : int (default = 100)
        number of changes
    connected : int
        keep the connectivity of the graph or not.
        1:keep,    0:not keep

    Notes
    -----
    The 2K null models have the same joint degree distribution as the original graph

    """

    # make sure the 2K-characteristic unchanged and the graph is connected
    # swap the edges inside the community
    if not nx.is_connected(G0):
        raise nx.NetworkXError("It is only allowed for connected graphs.")
    if G0.is_directed():
        raise nx.NetworkXError("It is only allowed for undirected graphs.")
    if n_swap > max_tries:
        raise nx.NetworkXError("Number of swaps > number of tries allowed.")
    if len(G0) < 3:
        raise nx.NetworkXError("This graph has less than three nodes.")

    n_try = 0
    count_swap = 0

    G = copy.deepcopy(G0)
    keys, degrees = zip(*G.degree().items())
    cdf = nx.utils.cumulative_distribution(degrees)

    while count_swap < n_swap:
        if n_try >= max_tries:
            e = ('尝试次数 (%s) 已超过允许的最大次数' % n_try + '有效交换次数（%s)' % count_swap)
            print(e)
            break
        n_try += 1

        # make sure the degree distribution unchanged,choose two edges (u-v,x-y) randomly
        (ui, xi) = nx.utils.discrete_sequence(2, cdistribution=cdf)
        if ui == xi:
            continue
        u = keys[ui]
        x = keys[xi]
        v = random.choice(list(G[u]))
        y = random.choice(list(G[x]))

        # make sure the four nodes are not repeated
        if len(set([u, v, x, y])) == 4:
            if G.degree(v) == G.degree(y):  # 保证节点的度匹配特性不变
                # make sure the new edges are not exist in the original graph
                if (y not in G[u]) and (v not in G[x]):
                	# add two new edges
                    G.add_edge(u, y)
                    G.add_edge(v, x)
                    # delete two old edges
                    G.remove_edge(u, v)
                    G.remove_edge(x, y)
                    # if connected = 1 but the original graph is not connected fully,
                    # withdraw the operation about the swap of edges.
                    if connected == 1:
                        if not nx.is_connected(G):
                            G.add_edge(u, v)
                            G.add_edge(x, y)
                            G.remove_edge(u, y)
                            G.remove_edge(x, v)
                            continue
                    count_swap = count_swap + 1
    return G


def random_25k(G0, n_swap=1, max_tries=100, connected=1):
	"""Return a 2.5K null model beased on random reconnection algorithm

    Parameters
    ----------
    G0 : undirected and unweighted graph
    n_swap : int (default = 1)
        coefficient of change successfully
    max_tries : int (default = 100)
        number of changes
    connected : int
        keep the connectivity of the graph or not.
        1:keep,    0:not keep

    Notes
    -----
    The 2.5K null models has the same clustering spectrum and joint degree distribution with the original network

    """
    # make sure the 2K-characteristic unchanged and the graph is connected
    # swap the edges inside the community
    if not nx.is_connected(G0):
        raise nx.NetworkXError("It is only allowed for connected graphs.")
    if G0.is_directed():
        raise nx.NetworkXError("It is only allowed for undirected graphs.")
    if n_swap > max_tries:
        raise nx.NetworkXError("Number of swaps > number of tries allowed.")
    if len(G0) < 3:
        raise nx.NetworkXError("This graph has less than three nodes.")

    n_try = 0
    count_swap = 0

    G = copy.deepcopy(G0)
    keys, degrees = zip(*G.degree().items())
    cdf = nx.utils.cumulative_distribution(degrees)

    while count_swap < n_swap:
        if n_try >= max_tries:
            e = ('尝试次数 (%s) 已超过允许的最大次数' % n_try + '有效交换次数（%s)' % count_swap)
            print(e)
            break
        n_try += 1

        # make sure the degree distribution unchanged,choose two edges (u-v,x-y) randomly
        (ui, xi) = nx.utils.discrete_sequence(2, cdistribution=cdf)
        if ui == xi:
            continue
        u = keys[ui]
        x = keys[xi]
        v = random.choice(list(G[u]))
        y = random.choice(list(G[x]))
        # make sure the four nodes are not repeated
        if len(set([u, v, x, y])) == 4:
            if G.degree(v) == G.degree(y):  # 保证节点的度匹配特性不变
                # make sure the new edges are not exist in the original graph
                if (y not in G[u]) and (v not in G[x]):
                    G.add_edge(u, y)
                    G.add_edge(v, x)

                    G.remove_edge(u, v)
                    G.remove_edge(x, y)
                    # get the degree of four nodes and their neighbor nodes, degree_node_list : [[degree,node]]
                    degree_node_list = map(lambda t: (t[1], t[0]), G0.degree(
                        [u, v, x, y] + list(G[u]) + list(G[v]) + list(G[x]) + list(G[y])).items())
                    # get all nodes of each degree :{degree:[node1,node2...]}
                    dict_degree = count_degree_nodes(degree_node_list)

                    for i in range(len(dict_degree)):
                        avcG0 = nx.average_clustering(
                            G0, nodes=dict_degree.values()[i], weight=None, count_zeros=True)
                        avcG = nx.average_clustering(
                            G, nodes=dict_degree.values()[i], weight=None, count_zeros=True)
                        i += 1
                    # if the clustering coefficient about dgree changed after scrambling ,withdraw this operation
                    if avcG0 != avcG:
                        G.add_edge(u, v)
                        G.add_edge(x, y)
                        G.remove_edge(u, y)
                        G.remove_edge(x, v)
                        break
                    # if connected = 1 but the original graph is not connected fully,
                    # withdraw the operation about the swap of edges.
                    if connected == 1:
                        if not nx.is_connected(G):
                            G.add_edge(u, v)
                            G.add_edge(x, y)
                            G.remove_edge(u, y)
                            G.remove_edge(x, v)
                            continue

                    count_swap = count_swap + 1
    return G


def random_3k(G0, n_swap=1, max_tries=100, connected=1):
	"""Return a 3K null model beased on random reconnection algorithm

    Parameters
    ----------
    G0 : undirected and unweighted graph
    n_swap : int (default = 1)
        coefficient of change successfully
    max_tries : int (default = 100)
        number of changes
    connected : int
        keep the connectivity of the graph or not.
        1:keep,    0:not keep

    Notes
    -----
    3K null model, which is considered interconnectivity among triples of nodes

    """

    # make sure the 2K-characteristic unchanged and the graph is connected
    # swap the edges inside the community
    if not nx.is_connected(G0):
        raise nx.NetworkXError("It is only allowed for connected graphs.")
    if G0.is_directed():
        raise nx.NetworkXError("It is only allowed for undirected graphs.")
    if n_swap > max_tries:
        raise nx.NetworkXError("Number of swaps > number of tries allowed.")
    if len(G0) < 3:
        raise nx.NetworkXError("This graph has less than three nodes.")

    n_try = 0
    count_swap = 0

    G = copy.deepcopy(G0)
    keys, degrees = zip(*G.degree().items())
    cdf = nx.utils.cumulative_distribution(degrees)

    while count_swap < n_swap:
        if n_try >= max_tries:
            e = ('尝试次数 (%s) 已超过允许的最大次数' % n_try + '有效交换次数（%s)' % count_swap)
            print(e)
            break
        n_try += 1

        # make sure the degree distribution unchanged,choose two edges (u-v,x-y) randomly
        (ui, xi) = nx.utils.discrete_sequence(2, cdistribution=cdf)
        if ui == xi:
            continue
        u = keys[ui]
        x = keys[xi]
        v = random.choice(list(G[u]))
        y = random.choice(list(G[x]))
        # make sure the four nodes are not repeated
        if len(set([u, v, x, y])) == 4:
            if G.degree(v) == G.degree(y):  # 保证节点的度匹配特性不变
                # make sure the new edges are not exist in the original graph
                if (y not in G[u]) and (v not in G[x]):
                    G.add_edge(u, y)
                    G.add_edge(v, x)

                    G.remove_edge(u, v)
                    G.remove_edge(x, y)

                    # get the set of four nodes and their neighbor nodes
                    node_list = [u, v, x, y] + \
                        list(G[u]) + list(G[v]) + list(G[x]) + list(G[y])
                    # cal the clustering coefficient of the four nodes in the original and the new graph
                    avcG0 = nx.clustering(G0, nodes=node_list)
                    avcG = nx.clustering(G, nodes=node_list)
                    # if the clustering coefficient about dgree changed after scrambling ,withdraw this operation
                    if avcG0 != avcG:
                        G.add_edge(u, v)
                        G.add_edge(x, y)
                        G.remove_edge(u, y)
                        G.remove_edge(x, v)
                        continue
                    # if connected = 1 but the original graph is not connected fully,
                    # withdraw the operation about the swap of edges.
                    if connected == 1:
                        if not nx.is_connected(G):
                            G.add_edge(u, v)
                            G.add_edge(x, y)
                            G.remove_edge(u, y)
                            G.remove_edge(x, v)
                            continue
                    count_swap = count_swap + 1
    return G


def rich_club_create(G0, k=1, n_swap=1, max_tries=100, connected=1):
    """
    任选两条边(富节点和非富节点的连边)，若富节点间无连边，非富节点间无连边，则断边重连
    达到最大尝试次数或全部富节点间都有连边，循环结束
    """
    # G0：待改变结构的网络
    # k 为富节点度值的门限值
    # n_swap：是改变成功的系数，默认值为1
    # max_tries：是尝试改变的次数，默认值为100
    # connected：是否需要保证网络的联通特性，参数为1需要保持，参数为0不需要保持

    if not nx.is_connected(G0):
        raise nx.NetworkXError("It is only allowed for connected graphs.")
    if G0.is_directed():
        raise nx.NetworkXError("It is only allowed for undirected graphs.")
    if n_swap > max_tries:
        raise nx.NetworkXError("Number of swaps > number of tries allowed.")
    if len(G0) < 3:
        raise nx.NetworkXError("This graph has less than three nodes.")

    n_try = 0
    count_swap = 0

    G = copy.deepcopy(G0)
    keys, degrees = zip(*G.degree().items())
    cdf = nx.utils.cumulative_distribution(degrees)

    hubs = [e for e in G.nodes() if G.degree()[e] >= k]  # 全部富节点
    hubs_edges = [e for e in G.edges() if G.degree()[e[0]] >= k and G.degree()[
        e[1]] >= k]  # 网络中已有的富节点和富节点的连边
    len_possible_edges = len(hubs) * (len(hubs) - 1) / 2  # 全部富节点间都有连边的边数

    while count_swap < n_swap and len(hubs_edges) < len_possible_edges:
        if n_try >= max_tries:
            e = ('尝试次数 (%s) 已超过允许的最大次数' % n_try + '有效交换次数（%s)' % count_swap)
            print(e)
            break
        n_try += 1

        u, y = random.sample(hubs, 2)  # 任选两个富节点
        v = random.choice(list(G[u]))
        x = random.choice(list(G[y]))
        if len(set([u, v, x, y])) == 4:
            if G.degree()[v] > k or G.degree()[x] > k:
                continue  # 另一端节点为非富节点
        if (y not in G[u]) and (v not in G[x]):  # 保证新生成的连边是原网络中不存在的边
            G.add_edge(u, y)
            G.add_edge(x, v)

            G.remove_edge(u, v)
            G.remove_edge(x, y)
            hubs_edges.append((u, y))  # 更新已存在富节点和富节点连边

            if connected == 1:
                if not nx.is_connected(G):  # 保证网络是全联通的:若网络不是全联通网络，则撤回交换边的操作
                    G.add_edge(u, v)
                    G.add_edge(x, y)

                    G.remove_edge(u, y)
                    G.remove_edge(x, v)
                    hubs_edges.remove((u, y))
                    continue

        if n_try >= max_tries:
            print('Maximum number of attempts (%s) exceeded ' % n_try)
            break
        count_swap = count_swap + 1
    return G


def rich_club_break(G0, k=10, n_swap=1, max_tries=100, connected=1):
    """
    富边：富节点和富节点的连边
    非富边：非富节点和非富节点的连边
    任选两条边(一条富边，一条非富边)，若富节点和非富节点间无连边，则断边重连
    达到最大尝试次数或无富边或无非富边，循环结束
    """
    # G0：待改变结构的网络
   # k 为富节点度值的门限值
    # n_swap：是改变成功的系数，默认值为1
    # max_tries：是尝试改变的次数，默认值为100
    # connected：是否需要保证网络的联通特性，参数为1需要保持，参数为0不需要保持

    if not nx.is_connected(G0):
        raise nx.NetworkXError("It is only allowed for connected graphs.")
    if G0.is_directed():
        raise nx.NetworkXError("It is only allowed for undirected graphs.")
    if n_swap > max_tries:
        raise nx.NetworkXError("Number of swaps > number of tries allowed.")
    if len(G0) < 3:
        raise nx.NetworkXError("This graph has less than three nodes.")

    n_try = 0
    count_swap = 0

    G = copy.deepcopy(G0)
    hubedges = []  # 富边
    nothubedges = []  # 非富边
    hubs = [e for e in G.nodes() if G.degree()[e] > k]  # 全部富节点
    for e in G.edges():
        if e[0] in hubs and e[1] in hubs:
            hubedges.append(e)
        elif e[0] not in hubs and e[1] not in hubs:
            nothubedges.append(e)

    count_swap = 0
    while count_swap < n_swap and hubedges and nothubedges:
        u, v = random.choice(hubedges)  # 随机选一条富边
        x, y = random.choice(nothubedges)  # 随机选一条非富边
        if len(set([u, v, x, y])) < 4:
            continue
        if (y not in G[u]) and (v not in G[x]):  # 保证新生成的连边是原网络中不存在的边
            G.add_edge(u, y)
            G.add_edge(x, v)
            G.remove_edge(u, v)
            G.remove_edge(x, y)
            hubedges.remove((u, v))
            nothubedges.remove((x, y))
            if connected == 1:
                if not nx.is_connected(G):  # 不保持连通性，撤销
                    G.add_edge(u, v)
                    G.add_edge(x, y)
                    G.remove_edge(u, y)
                    G.remove_edge(x, v)
                    hubedges.append((u, v))
                    nothubedges.append((x, y))
                    continue
        if n_try >= max_tries:
            print('Maximum number of attempts (%s) exceeded ' % n_try)
            break
        count_swap = count_swap + 1
    return G


def assort_mixing(G0, k=10, n_swap=1, max_tries=100, connected=1):
    """
    随机选取两条边，四个节点，将这四个节点的度值从大到小排序，
    将度值较大的两个节点进行连接，度值较小的两个节点进行连接，
    最终形成了同配网络
    """
    # G0：待改变结构的网络
   # k 为富节点度值的门限值
    # n_swap：是改变成功的系数，默认值为1
    # max_tries：是尝试改变的次数，默认值为100
    # connected：是否需要保证网络的联通特性，参数为1需要保持，参数为0不需要保持

    if not nx.is_connected(G0):
        raise nx.NetworkXError("It is only allowed for connected graphs.")
    if G0.is_directed():
        raise nx.NetworkXError("It is only allowed for undirected graphs.")
    if n_swap > max_tries:
        raise nx.NetworkXError("Number of swaps > number of tries allowed.")
    if len(G0) < 3:
        raise nx.NetworkXError("This graph has less than three nodes.")

    n_try = 0
    count_swap = 0

    G = copy.deepcopy(G0)
    keys, degrees = zip(*G.degree().items())
    cdf = nx.utils.cumulative_distribution(degrees)

    while count_swap < n_swap:
        n_try += 1

        # 在保证度分布不变的情况下，随机选取两条连边u-v，x-y
        (ui, xi) = nx.utils.discrete_sequence(2, cdistribution=cdf)
        if ui == xi:
            continue
        u = keys[ui]
        x = keys[xi]
        v = random.choice(list(G[u]))
        y = random.choice(list(G[x]))

        if len(set([u, v, x, y])) < 4:
            continue
        sortednodes = zip(
            *sorted(G.degree([u, v, x, y]).items(), key=lambda d: d[1], reverse=True))[0]
        if (sortednodes[0] not in G[sortednodes[1]]) and (sortednodes[2] not in G[sortednodes[3]]):
            # 保证新生成的连边是原网络中不存在的边

            G.add_edge(sortednodes[0], sortednodes[1])  # 连新边
            G.add_edge(sortednodes[2], sortednodes[3])
            G.remove_edge(x, y)  # 断旧边
            G.remove_edge(u, v)

            if connected == 1:
                if not nx.is_connected(G):
                    G.remove_edge(sortednodes[0], sortednodes[1])
                    G.remove_edge(sortednodes[2], sortednodes[3])
                    G.add_edge(x, y)
                    G.add_edge(u, v)
                    continue
        if n_try >= max_tries:
            e = ('Maximum number of swap attempts (%s) exceeded ' %
                 n_try + 'before desired swaps achieved (%s).' % n_swap)
            print(e)
            break
        count_swap += 1
    return G


def disassort_mixing(G0, k=10, n_swap=1, max_tries=100, connected=1):
    """
    随机选取两条边，四个节点，将这四个节点的度值从大到小排序，
    将度值差异较大的两个节点进行连接，第一和第四两个节点相连，
    将度值差异较小的两个节点进行连接，第二和第三两个节点相连
    最终形成了异配网络
    """
    # G0：待改变结构的网络
   # k 为富节点度值的门限值
    # n_swap：是改变成功的系数，默认值为1
    # max_tries：是尝试改变的次数，默认值为100
    # connected：是否需要保证网络的联通特性，参数为1需要保持，参数为0不需要保持

    if not nx.is_connected(G0):
        raise nx.NetworkXError("It is only allowed for connected graphs.")
    if G0.is_directed():
        raise nx.NetworkXError("It is only allowed for undirected graphs.")
    if n_swap > max_tries:
        raise nx.NetworkXError("Number of swaps > number of tries allowed.")
    if len(G0) < 3:
        raise nx.NetworkXError("This graph has less than three nodes.")

    n_try = 0
    count_swap = 0

    G = copy.deepcopy(G0)
    keys, degrees = zip(*G.degree().items())
    cdf = nx.utils.cumulative_distribution(degrees)

    while count_swap < n_swap:
        n_try += 1

        # 在保证度分布不变的情况下，随机选取两条连边u-v，x-y
        (ui, xi) = nx.utils.discrete_sequence(2, cdistribution=cdf)
        if ui == xi:
            continue
        u = keys[ui]
        x = keys[xi]
        v = random.choice(list(G[u]))
        y = random.choice(list(G[x]))

        if len(set([u, v, x, y])) < 4:
            continue
        sortednodes = zip(
            *sorted(G.degree([u, v, x, y]).items(), key=lambda d: d[1], reverse=True))[0]
        if (sortednodes[0] not in G[sortednodes[3]]) and (sortednodes[1] not in G[sortednodes[2]]):
            # 保证新生成的连边是原网络中不存在的边

            G.add_edge(sortednodes[0], sortednodes[3])  # 连新边
            G.add_edge(sortednodes[1], sortednodes[2])
            G.remove_edge(x, y)  # 断旧边
            G.remove_edge(u, v)

            if connected == 1:
                if not nx.is_connected(G):
                    G.remove_edge(sortednodes[0], sortednodes[3])
                    G.remove_edge(sortednodes[1], sortednodes[2])
                    G.add_edge(x, y)
                    G.add_edge(u, v)
                    continue
        if n_try >= max_tries:
            e = ('Maximum number of swap attempts (%s) exceeded ' %
                 n_try + 'before desired swaps achieved (%s).' % n_swap)
            print(e)
            break
        count_swap += 1
    return G


# 下面的程序暂时未修改
def random_1kd(G0, n_swap=1, max_tries=100):  # 有向网络基于随机断边重连的1阶零模型
    """
    随机取两条边 u->v 和 x->y, 若u->y,x->v不存在, 断边重连
    """
    if not G0.is_directed():
        raise nx.NetworkXError("Graph not directed")
    if n_swap > max_tries:
        raise nx.NetworkXError("Number of swaps > number of tries allowed.")
    if len(G0) < 4:
        raise nx.NetworkXError("Graph has less than four nodes.")
    G = copy.deepcopy(G0)
    n = 0
    count_swap = 0
    while count_swap < n_swap:
        (u, v), (x, y) = random.sample(G.edges(), 2)
        if len(set([u, v, x, y])) < 4:
            continue
        if (x, v) not in G.edges() and (u, y) not in G.edges():  # 断边重连
            G.add_edge(u, y)
            G.add_edge(x, v)
            G.remove_edge(u, v)
            G.remove_edge(x, y)
            count_swap += 1
        if n >= max_tries:
            e = ('Maximum number of swap attempts (%s) exceeded ' %
                 n + 'before desired swaps achieved (%s).' % n_swap)
            print e
            break
        n += 1
    return G
