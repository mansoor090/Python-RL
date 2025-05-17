import sys, os
import argparse

try:
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
except NameError:
    parent_dir = os.path.abspath("..")  # fallback if __file__ is undefined

if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)


import subprocess
import time
from stable_baselines3.common.vec_env import SubprocVecEnv
from my_env import MyEnv
from peaceful_pie.unity_comms import UnityComms
from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor

def launch_unity_instance(build_path, port):
    """Launch a single Unity instance."""
    process = subprocess.Popen([
        build_path,
        "--port", str(port)
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process


def make_env(port, args: argparse.Namespace):
    """Factory function for each environment."""
    def _init():
        unity_comms = UnityComms(port=port)
        model_name = args.model
        env = MyEnv(unity_comms=unity_comms)
        env = Monitor(env, filename=f"./logs/{model_name}")
        return env
    return _init

def main(args: argparse.Namespace):
    build_path = args.buildPath
    ports = [17000, 17010, 17020]
    unity_processes = []

    print("🚀 Launching Unity instances...")
    for port in ports:
        proc = launch_unity_instance(build_path, port)
        unity_processes.append(proc)

    print("⌛ Giving 5 seconds for Unity scenes to stabilize...")
    time.sleep(5)

    try:
        print("🚀 Setting up environments...")
        env_fns = [make_env(port, args) for port in ports]
        env = SubprocVecEnv(env_fns)
        model_name = args.model
        print("🚀 Training PPO across multiple instances with MultiInputPolicy...")
        model = PPO.load(model_name, env=env)

        ## Use this, if you want to train from 0 again.
        # model = PPO(
        #     "MultiInputPolicy",
        #     env=env,
        #     verbose=1,
        #     tensorboard_log='./tensorboard/',
        #     learning_rate=3e-4,
        #     n_steps=2048,
        #     batch_size=512,
        #     gamma=0.99,
        #     gae_lambda=0.95,
        #     clip_range=0.2,
        #     ent_coef=0.01,
        #     vf_coef=0.5,
        #     max_grad_norm=0.5,
        # )

        episodes = args.episodes
        model.learn(total_timesteps=episodes)

        model.save(model_name)

    finally:
        print("🛑 Closing Unity instances...")
        for proc in unity_processes:
            proc.terminate()
            proc.wait()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, default='PPO_Test_Model_1')
    parser.add_argument('--episodes', type=int, default=50000)
    parser.add_argument('--buildPath', type=str, default='PPO_Test_Model_1')
    args = parser.parse_args()
    main(args)
