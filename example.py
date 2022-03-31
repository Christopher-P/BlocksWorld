import time

from pyblocks import BlocksWorldEnv


def main():
    # Environment Params
    slots = 3
    blocks = 5
    score = None
    tick_limit = None

    # Example params
    human_input = False

    # Create env
    env = BlocksWorldEnv(slots, blocks, score, tick_limit)
    env.reset()
    is_done = False
    print(env.observation_space)

    while not is_done:
        env.render_2()

        # Select human entry or not
        if human_input:
            action = input("Enter action: ")
            if action == 'a':
                action = 0
            elif action == 'd':
                action = 1
            elif action == 'w':
                action = 2
            elif action == 's':
                action = 3
            else:
                continue
        else:
            action = env.action_space.sample()
        obs, reward, done, info = env.step(action)

        is_done = done
        time.sleep(0.2)
        print(obs, is_done, reward)


if __name__ == "__main__":
    main()
