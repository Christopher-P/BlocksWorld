# 

class Simulator():

    def __init__(self, world_size, blocks, score):
        self.world_size = world_size
        self.blocks = blocks
        self.score_function = score
        self.is_done = None


    def get_state(self):

    def act(self):

    def score(self):

    def reset(self):
        # reset done bool
        self.is_done = False
        # generate new world
        self.gen()

    def gen(self):
        world = None
        world = []

        # Create empty world
        for size in self.world_size:
            world.append(Stack())

        # Create goal state
        for block in self.blocks:
            world[self.world_size - 1].push(self.blocks - blocks - 1)
    
    def alphabet(self, num)
        alph = "abcdefghijklmnopqrstuvwxyz"
        return alph[num]
        


# http://interactivepython.org/courselib/static/pythonds/BasicDS/ImplementingaStackinPython.html
class Stack:
     def __init__(self):
         self.items = []

     def isEmpty(self):
         return self.items == []

     def push(self, item):
         self.items.append(item)

     def pop(self):
         return self.items.pop()

     def peek(self):
         return self.items[len(self.items)-1]

     def size(self):
         return len(self.items)
