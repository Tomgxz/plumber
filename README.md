# Plumber

Simple plumbing game coded using Pygame

## Game Overview

Code uses a main object to use pygame with, objects for individual pipes and a map object.
Player wins by following instructions: rotate pipes until the water flow reaches the exit pipe.
Levels can be infinitly generated using a seed generation based on the level counter.

## Issues

+ Sometimes the code will generate levels which cannot be completed
+ Pipes can retain water flow after being disconnected, which can lead to winning when there is not a connected route
+ Scoring system is not implemented, and there is no timer
