from dataclasses import dataclass

from peaceful_pie.unity_comms import UnityComms
import argparse

@dataclass
class MyVector3:
    x: float
    y: float
    z: float

def run(args: argparse.Namespace) -> None:
    unity_comms = UnityComms(port=args.port)
    res = unity_comms.Reset(ResultClass = MyVector3)
    print (res)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=9000)
    args = parser.parse_args()
    run(args)