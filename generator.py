# OpenSource BlocksWorld simulator
# The goal is to place all the blocks on
# the set spot with blocks from (0-bot to n-top)

# v0 will use random placement for blocks in the world
# v0 will assume goal stack is right-most column
# v0 scores off euclidean

import math
import time
import random

from gym import Env, spaces


class BlocksWorldEnv(Env):

    def __init__(self, world_length, block_number, score_type, limit=10):
        self.world_length = world_length
        self.block_number = block_number
        self._get_score_function = None
        self.hand_location = None
        self.holding = None
        self.start_time = None
        self.limit = limit
        self.world = None
        self.viewer = None

        self.colors = [(0.2, 0.2, 0.2), (0.3, 0.7, 0.6), (0.9, 0.1, 0.2)]

        # Open AI Gym Obs/act spaces
        self.observation_space = spaces.Dict({"world": spaces.Box(low=0.0, high=self.block_number,
                                                                  shape=(self.world_length, self.block_number),
                                                                  dtype=int),
                                              "holding": spaces.Discrete(self.block_number),
                                              "location": spaces.Discrete(self.world_length)})
        self.action_space = spaces.Discrete(4)

        return None

    def step(self, action):
        # Expects number
        # 0 = move left
        if action == 0:
            if self.hand_location > 0:
                self.hand_location = self.hand_location - 1

        # 1 = move right
        elif action == 1:
            if self.hand_location < self.world_length - 1:
                self.hand_location = self.hand_location + 1

        # 2 = grab
        elif action == 2:
            if self.holding is None:
                if len(self.world[self.hand_location]) > 0:
                    self.holding = self.world[self.hand_location].pop(-1)

        # 3 = release
        elif action == 3:
            if self.holding is not None:
                self.world[self.hand_location].append(self.holding)
                self.holding = None

        # Error
        else:
            print()

        return self._get_state()

    def reset(self):
        self.viewer = None
        self.hand_location = 0
        self.holding = None
        self.start_time = time.time()
        self._generate_world()

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
                for ind2, block in enumerate(range(self.block_number)):
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

    def close(self):
        return None

    def _get_score(self):
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

    def _get_state(self):
        observation = dict()
        observation['location'] = self.hand_location
        observation['holding'] = self.holding
        observation['world'] = self.world

        return observation, self._get_score(), self._is_done(), {}

    def _generate_world(self):
        world = list()

        # Create empty world
        for size in range(self.world_length):
            world.append(list())

        # Fill world with blocks
        for block in range(self.block_number):
            location = random.randint(0, self.world_length - 1)
            world[location].append(block)

        self.world = world

        return None

    def _is_done(self):
        # Check if time limit passed
        if time.time() - self.start_time >= self.limit:
            return True

        # Check if goal state achieved
        standard = list(reversed(range(0, self.block_number)))
        for ind, block in enumerate(self.world[-1]):
            if block != standard[ind]:
                return False
                break

        # Check if final world slot is empty (above wont work)
        if len(self.world[-1]) == 0:
            return False

        return True


def main():
    # Params
    slots = 2
    blocks = 2
    score = None
    time_limit = 5

    # Create env
    env = BlocksWorldEnv(slots, blocks, score, time_limit)
    env.reset()
    is_done = False
    print(env.observation_space)

    while not is_done:
        action = random.randint(0, 3)
        obs, reward, done, info = env.step(action)
        env.render()
        is_done = done
        print(obs, is_done, reward)


if __name__ == "__main__":
    main()
