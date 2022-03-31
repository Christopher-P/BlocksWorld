# OpenSource BlocksWorld simulator
# The goal is to place all the blocks on
# the set spot with blocks from (0-bot to n-top)

# v0 will use random placement for blocks in the world
# v0 will assume goal stack is right-most column
# v0 scores off euclidean

import math
import random

import numpy as np

from gym import Env, spaces

import pygame
from pygame import gfxdraw


class BlocksWorldEnv(Env):

    def __init__(self, world_length, block_number, score_type, tick_limit=None):
        self.world_length = world_length
        self.block_number = block_number
        self._get_score_function = None
        self.hand_location = None
        self.holding = None
        self.start_time = None
        self.tick_limit = tick_limit
        self.current_tick = None
        self.world = None
        self.screen = None
        self.surf = None

        # Handle color values
        self.colors_all = pygame.colordict.THECOLORS.items()
        self.colors = list()
        for name in self.colors_all:
            if not any(char.isdigit() for char in name[0]):
                self.colors.append(name[1])

        # Open AI Gym Obs/act spaces
        self.observation_space = spaces.Dict({"world": spaces.Box(low=0.0, high=self.block_number,
                                                                  shape=(self.world_length, self.block_number),
                                                                  dtype=int),
                                              "holding": spaces.Discrete(self.block_number),
                                              "location": spaces.Discrete(self.world_length)})

        self.action_space = spaces.Discrete(4)

        return

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
            print('Error: Invalid action sent to step !')

        # After environment updates
        self.current_tick = self.current_tick + 1

        return self._get_state()

    def reset(self, seed=None):
        # Seed here now
        random.seed(seed)
        self.hand_location = 0
        self.holding = None
        self.current_tick = 0
        self._generate_world()

        return None

    def render(self, mode='human'):
        # Width of a block
        block_width = 25
        # Padding between blocks
        p = 5

        # screen size
        screen_width = (block_width + p) * (self.world_length + 1) + p
        screen_height = (block_width + p) * self.block_number + p + block_width

        # Create game instance
        if self.screen is None:
            pygame.init()
            pygame.display.init()
            self.screen = pygame.display.set_mode((screen_width, screen_height))

        # Create window
        self.surf = pygame.Surface((screen_width, screen_height))
        self.surf.fill((0, 0, 0))

        # On start draw squares
        for x, slot in enumerate(self.world):
            for y, block in enumerate(slot):
                # Left pos
                left = x * (block_width + p) + p
                # Top pos
                top = (self.block_number - y) * (block_width + p) + p

                # Always draw white square
                rect = pygame.Rect(left, top, block_width, block_width)
                pygame.gfxdraw.box(self.surf, rect, self.colors[block])

        # Draw holding hand box
        grey = (122, 122, 122)
        bigger = 3
        p1 = self.hand_location * (block_width + p) + p - bigger
        p2 = p - bigger
        rect = pygame.Rect(p1, p2, block_width + bigger * 2, block_width + bigger * 2)
        pygame.gfxdraw.box(self.surf, rect, grey)

        # Draw block if holding
        if self.holding is not None:
            p1 = self.hand_location * (block_width + p) + p
            p2 = p
            rect = pygame.Rect(p1, p2, block_width, block_width)
            pygame.gfxdraw.box(self.surf, rect, self.colors[self.holding])

        # Draw line
        line_x = (block_width + p) * self.world_length + 2
        pygame.gfxdraw.line(self.surf, line_x, 0, line_x, screen_height, (255, 0, 0))

        # Draw Goal State
        for y, block in enumerate(np.arange(self.block_number)):
            # Left pos
            left = self.world_length * (block_width + p) + p
            # Top pos
            top = (self.block_number - y) * (block_width + p) + p

            # Always draw white square
            rect = pygame.Rect(left, top, block_width, block_width)
            pygame.gfxdraw.box(self.surf, rect, self.colors[block])

        # Render the drawn window
        self.surf = pygame.transform.flip(self.surf, False, False)
        self.screen.blit(self.surf, (0, 0))
        pygame.event.pump()
        pygame.display.flip()
        return None

    def close(self):
        self.screen = None
        self.surf = None
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
        # Consider block to be at highest point
        if self.holding is not None:
            height = self.block_number
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
        if self.tick_limit is not None:
            if self.current_tick > self.tick_limit:
                return False

        # Determine states
        goal_state = np.arange(0, self.block_number)
        current_state = np.asarray(self.world[-1])

        # Check if all the blocks are stacked correctly
        if np.array_equal(goal_state, current_state):
            return True
        else:
            return False
