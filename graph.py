#!/usr/bin/env python

from pycallgraph2 import PyCallGraph
from pycallgraph2 import Config
from pycallgraph2.output import GraphvizOutput


config = Config(max_depth=3)
graphviz = GraphvizOutput(output_file='filter_max_depth.png')

with PyCallGraph(output=graphviz, config=config):
  from main import main
  main()