from map import Map


def run(start, goal):
    my_map = Map(r, c, cost_of_each_place)
    my_map.setup_nodes_places(position_to_label_dict)
    print('Start = ' + start + ', Goal = ' + goal)
    my_map.a_star_search(start, goal)
    my_map.show_map()
    print()


r, c = 4, 4
position_to_label_dict = {2: 'V', 5: 'V', 1: 'V', 12: 'V',
                          6: 'Q', 11: 'Q', 8: 'Q',
                          3: 'P', 9: 'P', 14: 'P', 15: 'P'}
cost_of_each_place = {'Q': 0, 'V': 2, 'P': 3, 'Default': 1}
goal = ['P']

my_map = Map(r, c, cost_of_each_place)
my_map.setup_nodes_places(position_to_label_dict)
my_map.show_map()


run('P', 'U')
run('Q', 'U')
run('V', 'U')
run('K', 'U')
run('L', 'U')
run('M', 'U')
run('R', 'U')
run('W', 'U')
run('F', 'U')
run('G', 'U')
run('H', 'U')
run('I', 'U')
run('N', 'U')
run('S', 'U')
run('X', 'U')
run('A', 'U')
run('B', 'U')
run('C', 'U')
run('D', 'U')
run('E', 'U')
run('J', 'U')
run('O', 'U')
run('T', 'U')
run('Y', 'U')
