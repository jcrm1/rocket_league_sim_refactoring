#!/usr/bin/env python3

"""
Deep learning interface for ROS.

License:
  BSD 3-Clause License
  Copyright (c) 2021, Autonomous Robotics Club of Purdue (Purdue ARC)
  All rights reserved.
  Redistribution and use in source and binary forms, with or without
  modification, are permitted provided that the following conditions are met:
  1. Redistributions of source code must retain the above copyright notice, this
     list of conditions and the following disclaimer.
  2. Redistributions in binary form must reproduce the above copyright notice,
     this list of conditions and the following disclaimer in the documentation
     and/or other materials provided with the distribution.
  3. Neither the name of the copyright holder nor the names of its
     contributors may be used to endorse or promote products derived from
     this software without specific prior written permission.
  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
  FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
  DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
  SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
  CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
  OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import sys
from rocket_league_drl import makeAgent, makeTrainer, makeEvaluator
from rocket_league_drl.interfaces import SnakeInterface, CartpoleInterface, CartpoleDirectInterface

from pdb import set_trace

assert len(sys.argv) >= 2
env = sys.argv[1]
mode = sys.argv[2]
print("Running " + env + " in " + mode + " mode.")

if env == "snake":
    Interface = SnakeInterface
elif env == "cartpole_ros":
    Interface = CartpoleInterface
elif env == "cartpole_direct":
    Interface = CartpoleDirectInterface
else:
    print(f"Unrecognized environment {env}!")

Agent = makeAgent(Interface)

if mode == "train":
    Trainer = makeTrainer(Agent)
    Trainer()
elif mode == "eval":
    Evaluator = makeEvaluator(Agent)
    Evaluator()
else:
    print("Unrecognized mode!")
