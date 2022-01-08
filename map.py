import networkx as nx
from matplotlib import pyplot as plt


class Map:
    nbr_of_rows = None
    nbr_of_cols = None
    graph = None
    node_positions = None

    node_labels = {}
    cost_of_each_place = {}
    edge_labels = {}
    node_color = []
    edge_color = []
    edge_widths = []
    path_found = []

    def __init__(self, r, c, costs):
        self.nbr_of_rows = r + 1
        self.nbr_of_cols = c + 1
        self.cost_of_each_place = costs

        # create empty 2d graph
        self.graph = nx.grid_2d_graph(self.nbr_of_rows, self.nbr_of_cols)

        # add inner nodes for places
        for x, y in self.graph.copy().nodes():
            if 0 < x < self.nbr_of_rows and 0 < y < self.nbr_of_cols:
                self.graph.add_node((x - 0.5, y - 0.5))

        # set location of each node to look like a table
        self.node_positions = {(x, y): (y, -x) for x, y in self.graph.nodes()}

        # set default labels and colors
        self.set_node_labels({})
        self.set_node_colors()
        self.set_edge_colors(self.path_found)

    # region DisplayGrid

    def show_map(self):
        # blue for default edge, thicker red edge for nodes in path_found

        plt.clf()  # clear previous drawing
        plt.figure(figsize=(8, 8))  # set grid cell size
        plt.axis('off')
        plt.gca().margins(0.1)  # set margin

        # draw graph
        nx.draw(G=self.graph,
                pos=self.node_positions,
                labels=self.node_labels,
                edge_color=self.edge_color,
                node_size=500,
                node_color=self.node_color,
                width=self.edge_widths)

        # draw edges on graph
        nx.draw_networkx_edge_labels(G=self.graph, pos=self.node_positions, edge_labels=self.edge_labels)

        plt.show()  # show table

    def setup_nodes_places(self, position_to_label_dict):
        self.set_node_labels(position_to_label_dict)
        self.set_node_colors()
        self.set_edge_cost_labels()

    def set_edge_colors(self, red_edges):
        self.edge_color = []
        self.edge_widths = []
        for x, y in self.graph.edges():
            if x in red_edges and y in red_edges:
                self.edge_color.append('red')
                self.edge_widths.append(5)
            else:
                self.edge_color.append('tab:blue')
                self.edge_widths.append(2)

    def set_node_labels(self, position_to_place_dict):
        corner_idx = 1
        place_idx = 1

        for x, y in self.graph.nodes():
            if x % 1 == 0:  # if coordinate is an integer, it is a cell corner, so set corner style labels
                self.node_labels[(x, y)] = convert_to_alphabetical_name(corner_idx)  # set name as letter
                corner_idx += 1
            else:  # if is a place
                if place_idx in position_to_place_dict.keys():  # if place was specified
                    place = str(position_to_place_dict.get(place_idx)).upper()
                    # set place as label
                    self.node_labels[(x, y)] = place + str(place_idx)
                    # corresponding cost to the place as node attribute "cost"
                    nx.set_node_attributes(self.graph, {(x, y): self.cost_of_each_place.get(place)}, 'cost')
                else:  # if place was unspecified
                    # set default place name
                    self.node_labels[(x, y)] = place_idx
                    # set default cost
                    nx.set_node_attributes(self.graph, {(x, y): self.cost_of_each_place.get('Default')}, 'cost')
                place_idx += 1

    def set_node_colors(self):
        # set specific color for each place
        self.node_color = []

        for (x, y), value in self.node_labels.items():
            if x % 1 == 0:  # cell corners
                self.node_color.append('tab:blue')
            elif 'V' in str(value):
                self.node_color.append('red')
            elif 'P' in str(value):
                self.node_color.append('pink')
            elif 'Q' in str(value):
                self.node_color.append('green')
            else:
                self.node_color.append('lightblue')

    def set_edge_cost_labels(self):
        self.edge_labels = dict([((u, v), self.calculate_edge_cost(u, v))
                                 for u, v in self.graph.edges(data=False)])

    # endregion

    def calculate_edge_cost(self, first_node, second_node):
        (y1, x1) = first_node
        (y2, x2) = second_node

        # calculate midpoint of the edge
        x = (x1 + x2) / 2
        y = (y1 + y2) / 2

        top_position = ()
        bot_position = ()

        # if edge is horizontal, places are above and/or below the midpoint
        if x == x1:
            top_position = (y, (x + 0.5))
            bot_position = (y, (x - 0.5))

        # if edge is vertical, places are on the left and/or right of the midpoint
        if y == y1:
            top_position = (y + 0.5, x)
            bot_position = (y - 0.5, x)

        # get place(s) node
        top_node = self.graph.nodes.get(top_position)
        bot_node = self.graph.nodes.get(bot_position)

        # calculate cost
        if top_node is None:  # side node
            cost = bot_node.get("cost")
        elif bot_node is None:  # side node
            cost = top_node.get("cost")
        else:  # node between places
            cost = (top_node.get("cost") + bot_node.get("cost")) / 2
            if cost == self.cost_of_each_place.get("P"):
                # edge between 2 PlayingGrounds is inaccessible
                cost = 'block'

        nx.set_edge_attributes(self.graph, {(first_node, second_node): cost}, 'edge_cost')
        return cost

    def a_star_search(self, start_node_name, goal_node_names):
        #  if there is no goal, don't search for it
        if not goal_node_names:
            print('There is no goal')
            return

        # convert label to position
        start_position = get_dict_key(self.node_labels, start_node_name.upper())
        goal_positions = get_dict_keys(self.node_labels, [x.upper() for x in goal_node_names])

        start_position = calc_place_right_corner(start_position)
        goal_positions = calc_places_right_corners(goal_positions)

        goal_found = None
        visited = []
        to_visit = [start_position]  # start_position node will be first node visited

        # calculate first h, g=0
        start_h = calc_best_heuristic(start_position, goal_positions)
        self.set_node_ghf(start_position, 0, start_h)

        while to_visit:  # as long as nodes need to be visited
            current = self.get_smallest_f(to_visit)[0]  # current = node to visit with smallest f()
            if current in goal_positions:  # if current reached goal, search is done
                goal_found = current
                # print(self.node_labels[current], " Goal reached")
                break

            for c, neighbor in self.graph.edges(current):  # for every neighbor of current
                if neighbor not in visited:  # only unvisited neighbors
                    #  calculate new h for neighbor
                    edge_cost = self.calculate_edge_cost(current, neighbor)

                    #  skip blocked edges (e.g. between 2 PlayGrounds)
                    if edge_cost == 'block':
                        continue

                    #  calculate g for neighbor
                    new_neighbor_g = edge_cost + self.get_node_attribute(current, 'g')

                    #  get previously set g for neighbor
                    current_neighbor_g = self.get_node_attribute(neighbor, 'g')

                    #  if no g has been calculated yet, or the new g is smaller (found a better paths to a known node)
                    if (not current_neighbor_g) or (new_neighbor_g < current_neighbor_g):
                        h = calc_best_heuristic(neighbor, goal_positions)
                        self.set_node_ghf(neighbor, new_neighbor_g, h)  # set g, h, f
                        to_visit.append(neighbor)  # neighbor should now be visited
                        nx.set_node_attributes(self.graph, {neighbor: current}, 'prev')  # save current node in neighbor

            # done visiting current, so move it to visited
            visited.append(to_visit.pop(to_visit.index(current)))

        # if goal wasn't found
        if goal_found is None:
            print("No path was found. Please try again!")
            return

        self.path_found = self.get_shortest_path_label_string(goal_found)
        print('path found =', self.get_nodes_label(self.path_found))
        self.set_edge_colors([])
        self.set_edge_colors(self.path_found)

        print(self.node_labels[start_position] + ': h = ' + str(start_h))
        tc = self.get_node_attribute(goal_found, 'f')
        print('Total Cost = ', tc)
        # print('h <= TC = ', str(start_h <= tc))

        return self.path_found

    # region SearchNodeUtilities
    def get_shortest_path_label_string(self, goal):
        #  check prev of prev of goal to get path
        path = [goal]

        while self.get_node_attribute(goal, 'prev'):
            goal = self.get_node_attribute(goal, 'prev')
            path.append(goal)

        return path[::-1]

    def get_smallest_f(self, nodes):
        smallest_node = None
        f = None

        for n in nodes:
            a = self.get_node_attribute(n, 'f')
            if (f is None) or (a < f):
                smallest_node = n
                f = self.get_node_attribute(n, 'f')

        return smallest_node, f

    def get_nodes_label(self, nodes):
        r = ''
        for v in nodes:
            r += self.node_labels[v]
        return r

    def get_node_attribute(self, node, attribute_name):
        return self.graph.nodes.get(node).get(attribute_name)

    def set_node_ghf(self, node, g, h):
        nx.set_node_attributes(self.graph, {node: g}, 'g')
        nx.set_node_attributes(self.graph, {node: h}, 'h')
        nx.set_node_attributes(self.graph, {node: g + h}, 'f')
    #  endregion


def calc_places_right_corners(node_positions):
    # apply get_place_right_corner(node_position) to list of node positions

    new_nodes = []
    for np in node_positions:
        new_nodes.append(calc_place_right_corner(np))

    return new_nodes


def calc_place_right_corner(node_position):
    # used to get place coordinate to right corner
    (y, x) = node_position

    # if coordinate is not an integer, then it is a place
    if x % 1 != 0:
        x += .5  # move right by .5
        y -= .5  # move up by .5

    return y, x


def convert_to_alphabetical_name(number):
    result = ''
    while number > 0:
        index = (number - 1) % 26
        result += chr(index + ord('A'))
        number = (number - 1) // 26

    return result[::-1]


def calc_best_heuristic(start, goals):
    # calculate heuristic for each goal and return the smalest one
    h = []
    for goal in goals:
        h.append(calc_heuristic(start, goal))
    return min(h)


def calc_heuristic(start, goal):
    # Manhattan distance: calculate distance from goal to current node.
    # Assumes no diagonal moves allowed

    dx = abs(start[0] - goal[0])
    dy = abs(start[1] - goal[1])
    return dx + dy


def get_dict_key(dictionary, value):
    a = list(dictionary.keys())[list(dictionary.values()).index(value)]
    return a


def get_dict_keys(dictionary, values):
    keys = []
    for v in values:
        keys.append(list(dictionary.keys())[list(dictionary.values()).index(v)])
    return keys
