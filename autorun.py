import subprocess
import time
import socket
from stable_baselines3.common.vec_env import SubprocVecEnv
from my_env import MyEnv
from peaceful_pie.unity_comms import UnityComms
from stable_baselines3 import PPO


def launch_unity_instance(build_path, port):
    """Launch a single Unity instance."""
    process = subprocess.Popen([
        build_path,
        "--port", str(port)
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process


def make_env(port):
    """Factory function for each environment."""
    def _init():
        unity_comms = UnityComms(port=port)
        env = MyEnv(unity_comms=unity_comms)
        return env
    return _init

def main():
    build_path = "C:\\Users\\manso\\Autonomous Car\\New2\\Autonomous Car.exe"
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
        env_fns = [make_env(port) for port in ports]
        env = SubprocVecEnv(env_fns)

        print("🚀 Training PPO across multiple instances with MultiInputPolicy...")
        model = PPO(
            "MultiInputPolicy",
            env=env,
            verbose=1,
            tensorboard_log='./tensorboard/',
            learning_rate=3e-4,
            n_steps=4096,
            batch_size=512,
            gamma=0.99,
            gae_lambda=0.95,
            clip_range=0.2,
            ent_coef=0.01,
            vf_coef=0.5,
            max_grad_norm=0.5,
        )
        model.learn(total_timesteps=200000)

        model.save("PPO_MultiInstance_Model")

    finally:
        print("🛑 Closing Unity instances...")
        for proc in unity_processes:
            proc.terminate()
            proc.wait()

if __name__ == "__main__":
    main()
