# OpenSource BlocksWorld simulator
# The goal is to place all the blocks on
# the set spot with blocks from (0-bot to n-top)

# v0 will use random placement for blocks in the world
# v0 will assume goal stack is right-most column
# v0 scores off euclidean

import math
import time
import random


class Simulator:

    def __init__(self, slots, blocks, score, limit=10):
        self.slots = slots
        self.blocks = blocks
        self.score_function = None
        self.hand_location = None
        self.holding = None
        self.start_time = None
        self.limit = limit
        self.world = None
        self.viewer = None

        self.colors = [(0.2, 0.2, 0.2), (0.3, 0.7, 0.6), (0.9, 0.1, 0.2)]

        return None

    def check_done(self):
        # Check if time limit passed
        if time.time() - self.start_time >= self.limit:
            return True

        # Check if goal state achieved
        standard = list(reversed(range(0, self.blocks)))
        for ind, block in enumerate(self.world[-1]):
            if block != standard[ind]:
                return False
                break

        # Check if final world slot is empty (above wont work)
        if len(self.world[-1]) == 0:
            return False

        return True

    def act(self, action):
        # Expects number
        # 0 = move left
        if action == 0:
            if self.hand_location > 0:
                self.hand_location = self.hand_location - 1

        # 1 = move right
        if action == 1:
            if self.hand_location < self.slots - 1:
                self.hand_location = self.hand_location + 1

        # 2 = grab
        if action == 2:
            if self.holding is None:
                if len(self.world[self.hand_location]) > 0:
                    self.holding = self.world[self.hand_location].pop(-1)

        # 3 = release
        if action == 3:
            if self.holding is not None:
                self.world[self.hand_location].append(self.holding)
                self.holding = None

        return self.get_state()

    def score(self):
        counter = 0
        total_distance = 0.0
        # Compute for blocks in world
        for ind1, slot in enumerate(self.world):
            for ind2, block in enumerate(slot):
                # Goal state location
                x2 = len(self.world) - 1
                y2 = counter

                total_distance += math.sqrt(math.pow(ind1 - x2, 2) + math.pow(ind2 - y2, 2))

                counter = counter + 1

        # Compute for block in hand
        # Consider block to be at 0 height
        if self.holding is not None:
            height = 0
            last_slot = len(self.world) - 1
            total_distance += math.sqrt(math.pow(self.hand_location - last_slot, 2)
                                        + math.pow(height - self.holding, 2))

        return total_distance

    def reset(self):
        self.viewer = None
        self.hand_location = 0
        self.holding = None
        self.start_time = time.time()
        self.gen()

        return None

    def get_state(self):
        obs = list()
        obs.append(self.hand_location)
        obs.append(self.holding)
        obs.append(self.world)

        return obs, self.score(), self.check_done(), {}
        
    def gen(self):
        world = list()

        # Create empty world
        for size in range(self.slots):
            world.append(list())

        # Fill world with blocks
        for block in range(self.blocks):
            location = random.randint(0, self.slots - 1)
            world[location].append(block)

        self.world = world

        return None

    def render(self, mode='human'):
        screen_width = 600
        screen_height = 400

        world_width = 300 * 2
        scale = screen_width/world_width

        if self.viewer is None:
            from gym.envs.classic_control import rendering
            self.viewer = rendering.Viewer(screen_width, screen_height)

            # Render each slot
            block_width = 25
            p = 5

            # Fill background with black
            background = rendering.FilledPolygon([(0, 0), (0, 300), (600, 300), (600, 0)])
            background.add_attr(rendering.Transform())
            self.viewer.add_geom(background)

            # On start draw white squares
            for ind1, slot in enumerate(self.world):
                for ind2, block in enumerate(range(self.blocks)):
                    p1 = (p * (ind1 + 1) + block_width * ind1, p * (ind2 + 1) + block_width * ind2)
                    p2 = (p * (ind1 + 1) + block_width * ind1, (p + block_width) * (ind2 + 1))
                    p3 = ((p + block_width) * (ind1 + 1), (p + block_width) * (ind2 + 1))
                    p4 = ((p + block_width) * (ind1 + 1), p * (ind2 + 1) + block_width * ind2)

                    # Always draw white square
                    block_draw = rendering.FilledPolygon([p1, p2, p3, p4])
                    block_draw.set_color(1.0, 1.0, 1.0)
                    block_draw.add_attr(rendering.Transform())
                    self.viewer.add_geom(block_draw)

            # Draw other squares
            self.block_draws = list()
            for ind1, slot in enumerate(self.world):
                for ind2, block in enumerate(slot):
                    p1 = (p * (ind1 + 1) + block_width * ind1, p * (ind2 + 1) + block_width * ind2)
                    p2 = (p * (ind1 + 1) + block_width * ind1, (p + block_width) * (ind2 + 1))
                    p3 = ((p + block_width) * (ind1 + 1), (p + block_width) * (ind2 + 1))
                    p4 = ((p + block_width) * (ind1 + 1), p * (ind2 + 1) + block_width * ind2)

                    block_draw = rendering.FilledPolygon([p1, p2, p3, p4])
                    block_draw.set_color(*self.colors[block])
                    block_trans = rendering.Transform()
                    block_draw.add_attr(block_trans)
                    self.block_draws.append(block_trans)
                    self.viewer.add_geom(block_draw)

        # On update
        # Moves by absolute value in pixels
        self.block_draws[0].set_translation(150, 200)

        '''
        # Edit the pole polygon vertex
        pole = self._pole_geom
        l, r, t, b = -polewidth / 2, polewidth / 2, polelen - polewidth / 2, -polewidth / 2
        pole.v = [(l, b), (l, t), (r, t), (r, b)]

        x = self.state
        cartx = x[0] * scale + screen_width / 2.0  # MIDDLE OF CART
        self.carttrans.set_translation(cartx, carty)
        self.poletrans.set_rotation(-x[2])
        '''

        return self.viewer.render(return_rgb_array=mode == 'rgb_array')


# Params
slots = 2
blocks = 2
score = None
time_limit = 5

# Create env
env = Simulator(slots, blocks, score, time_limit)
env.reset()
is_done = False

while not is_done:
    action = random.randint(0, 3)
    obs, reward, done, info = env.act(action)
    env.render()
    is_done = done
    time.sleep(1)
    print(obs, is_done, reward)
