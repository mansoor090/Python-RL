from dataclasses import dataclass
from peaceful_pie.unity_comms import UnityComms
import argparse
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
    my_env = MyEnv(unity_comms=unity_comms)
    my_env = Monitor(my_env)
    ppo = PPO("MlpPolicy", env=my_env, verbose=1, ent_coef= 0.1)
    ppo.learn(total_timesteps=30000)

    ppo.save("PPO_Test_Model_1")

    my_env.close()



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=9000)
    args = parser.parse_args()
    run(args)