from dataclasses import dataclass
from peaceful_pie.unity_comms import UnityComms
import argparse
import gymnasium as gym
import numpy as np
from numpy.typing import NDArray
from typing import Tuple, Any
from gymnasium import spaces
from stable_baselines3.common.env_checker import check_env


@dataclass
class MyVector3:
    x: float
    y: float
    z: float

@dataclass
class RlResult:
    reward: float
    finished: bool
    truncate: bool
    obs: MyVector3


class MyEnv(gym.Env):
    def __init__(self, unity_comms: UnityComms):

        self.unity_commes = unity_comms
        #self.action_space = spaces.Discrete(4)
        self.action_space = spaces(6)
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(3,), dtype=np.float32)


    def step(self, action: NDArray[np.uint8]) -> Tuple[NDArray[np.float32], float, bool, bool, dict[str, Any]]:

        action_str = [
            "north","south",
            "east","west"][action]

        # action_str = [
        #     "Drive","Reverse",
        #     "DriveLeft", "DriveRight",
        #     "ReverseLeft","ReverseRight"][action]

        rlResult: RlResult = self.unity_commes.Step(action=action_str, ResultClass = RlResult)
        info = {"finished": rlResult.finished}

        return self._obs_vec3_to_np(rlResult.obs), rlResult.reward, rlResult.finished, rlResult.truncate, info


    def reset(self, seed=None) -> Tuple[NDArray[np.float32], dict[str, Any]]:
        obs_vec3: MyVector3 = self.unity_commes.Reset(ResultClass = MyVector3)

        info = {"finished": False}

        return self._obs_vec3_to_np(obs_vec3), {}

    def _obs_vec3_to_np(self, vec3: MyVector3) -> NDArray[np.float32]:
        return np.array([vec3.x, vec3.y, vec3.z], dtype=np.float32)




def run(args: argparse.Namespace) -> None:
    unity_comms = UnityComms(port=args.port)
    my_env = MyEnv(unity_comms=unity_comms)
    check_env(my_env)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=9000)
    args = parser.parse_args()
    run(args)