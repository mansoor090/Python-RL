from dataclasses import dataclass
from peaceful_pie.unity_comms import UnityComms
import argparse


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
    if args.action != '':
        res = unity_comms.Step(action=args.action, ResultClass=RlResult)
        print("reward: ", res)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=9000)
    parser.add_argument('--action', type= str, default = '')
    args = parser.parse_args()
    run(args)