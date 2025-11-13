from peaceful_pie.unity_comms import UnityComms
import argparse
from my_env import MyEnv
from stable_baselines3.common.monitor import Monitor
from stable_baselines3 import PPO



def run(args: argparse.Namespace) -> None:
    unity_comms = UnityComms(port=args.port)
    model_name = "models\\" + args.model
    episodes = args.episodes
    my_env = Monitor(MyEnv(unity_comms=unity_comms))

    ppo = PPO.load(model_name, env=my_env)
    ppo.learn(total_timesteps=episodes)

    ppo.save(model_name)

    my_env.close()



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=9000)
    parser.add_argument('--model', type=str, default='PPO_HardEnv')
    parser.add_argument('--episodes', type=int, default=50000)
    args = parser.parse_args()
    run(args)