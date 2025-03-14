from dataclasses import dataclass
from peaceful_pie.unity_comms import UnityComms
import argparse

from sympy import false

from my_env import MyEnv
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.ppo.ppo import PPO

@dataclass
class MyVector3:
    x: float
    y: float
    z: float

@dataclass
class RlResult:
    reward: float
    finished: bool
    obs: MyVector3

def run(args: argparse.Namespace) -> None:
    unity_comms = UnityComms(port=args.port)

    ## variables
    maxEpisodes = args.episodes
    modelName = args.model

    my_env = MyEnv(unity_comms=unity_comms)
    my_env = Monitor(my_env)

    ppo = PPO.load(modelName)

    for episode in range(maxEpisodes):
        obs, info = my_env.reset()
        done = false
        total_reward = 0
        while not done:
            action, info = ppo.predict(obs)

            obs, reward, done, truncate, info = my_env.step(action)
            total_reward += reward

        print(f"Episode 1: {episode + 1}, finished with total reward: {total_reward}")

    my_env.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=9000)
    parser.add_argument('--model', type=str, required=True)
    parser.add_argument('--episodes', type=int, default=100000)
    args = parser.parse_args()
    run(args)

    ### COmmenting: Muneeb is newbie