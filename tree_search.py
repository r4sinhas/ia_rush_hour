import asyncio
from abc import ABC, abstractmethod
from mimetypes import init
from queue import Empty


class SearchDomain(ABC):

    # construtor
    @abstractmethod
    def __init__(self):
        pass

    # lista de accoes possiveis num estado
    @abstractmethod
    def actions(self, state):
        pass

    # resultado de uma accao num estado, ou seja, o estado seguinte
    @abstractmethod
    def result(self, state, action):
        pass

    # custo estimado de chegar de um estado a outro
    @abstractmethod
    def heuristic(self, state, goal):
        pass

    # test if the given "goal" is satisfied in "state"
    @abstractmethod
    def satisfies(self, state):
        pass


class SearchProblem:
    def __init__(self, domain, initial):
        self.domain = domain
        self.initial = initial

    def goal_test(self, state):
        return self.domain.satisfies(state)


# Nos de uma arvore de pesquisa
class SearchNode:

    nnodes = 0

    def __init__(
        self, state, parent, depth=0, cost=0, heuristic=0, action=None, keys=[]
    ):
        self.state = state
        self.parent = parent
        self.depth = depth
        self.cost = cost  # note that the cost is actually the number of moves
        # which is the same as the depth lol
        self.heuristic = heuristic
        self.action = action
        self.keys = keys

        SearchNode.add_node()

    @classmethod
    def add_node(cls):
        cls.nnodes += 1

    def __str__(self):
        return "no(" + str(self.state) + "," + str(self.parent) + ")"

    def __repr__(self):
        return str(self)


class SearchTree:
    def __init__(self, problem):
        self.problem = problem
        root = SearchNode(problem.initial, None)
        self.open_nodes = [root]
        self.solution = None

    def get_path(self, node):
        if node.parent == None:  # -> root
            return [node.state]
        path = self.get_path(node.parent)
        path += [node.state]
        return path

    def get_actions(self, node):
        if node.parent == None or node == None:  # -> root
            return []
        path = self.get_actions(node.parent)
        path += [node.action]
        return path

    def search(self):
        visited_nodes = set()
        visited_nodes.add(self.problem.initial)
        while self.open_nodes != []:
            node = self.open_nodes.pop(0)
            if self.problem.goal_test(node.state):
                self.solution = node  # solution will be the path of NODES we got
                """ print("----------SOLUTION----------")
                print("TOTAL NODES VISITED x: ", SearchNode.nnodes)
                print("solution depth: ", self.solution.depth)
                print("solution cost: ", self.solution.cost)
                print("----------SOLUTION----------") """
                # shows how many boards we had to go through
                # -> Note that we need to keep track of the moves we made
                return self.get_actions(node)

            lnewnodes = []
            for a in self.problem.domain.actions(node.state):
                newstate = self.problem.domain.result(node.state, a)
                if not (newstate in visited_nodes):
                    newnode = SearchNode(
                        newstate,
                        node,
                        node.depth + 1,
                        node.cost + 1,
                        # heuristic here
                        self.problem.domain.heuristic(newstate, self.problem.initial),
                        a,
                    )
                    lnewnodes.append(newnode)
                    visited_nodes.add(newstate)

            self.add_to_open(lnewnodes)

        return None

    def add_to_open(self, new_nodes):
        self.open_nodes.extend(new_nodes)
        self.open_nodes.sort(key=lambda node: node.heuristic)
