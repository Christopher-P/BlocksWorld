from pyblocks import BlocksWorldEnv


def main():
    # Environment Params
    slots = 3
    blocks = 5
    score = None
    tick_limit = None

    # Example params
    human_input = True

    # Create env
    env = BlocksWorldEnv(slots, blocks)
    env.reset()
    done = False

    while not done:
        # Draw Environment
        env.render()

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
        print(obs, reward, done, info)

    return None


if __name__ == "__main__":
    main()
