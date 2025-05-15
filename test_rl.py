import time
from peaceful_pie.unity_comms import UnityComms
import argparse
from my_env import MyEnv
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.ppo.ppo import PPO



def run(args: argparse.Namespace) -> None:



    print(f"🚀 Initializing Settings")
    print(f"🚀 Model Selection: {args.model}")

    unity_comms = UnityComms(port=args.port)

    ## variables
    maxEpisodes = args.episodes
    modelName = args.model

    my_env = MyEnv(unity_comms=unity_comms)
    my_env = Monitor(my_env)
    print(f"🚀 Model Trying to load")
    ppo = PPO.load(modelName)
    print(f"🚀 Model Loaded Successfully")
    print(f"🚀 Training in Progress")

    for episode in range(maxEpisodes):
        obs, info = my_env.reset()
        done = False
        truncate = False
        total_reward = 0
        while not done and not truncate:
            action, info = ppo.predict(obs)
            obs, reward, done, truncate, info = my_env.step(action)
            total_reward += reward
            time.sleep(1)

        print(f"Episode: {episode + 1}, finished with total reward: {total_reward}")

    my_env.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=9000)
    parser.add_argument('--model', type=str, required=True)
    parser.add_argument('--episodes', type=int, default=100000)
    args = parser.parse_args()
    run(args)

