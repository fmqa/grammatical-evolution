# Minimal Implementation of Grammatical Evolution in Python

This is a minimal, dependency-free module for *Grammatical Evolution* (Collins & O'Neill, 1998). I originally wrote this for use in a project involving automated evolution of a scikit-learn feature selection/transformation pipeline.

Unlike traditional/classic GE which uses BNF, this module uses grammars specified using Python generators (See `picoga/grammatical.py` for an example).

A basic genetic algorithm module is also included.

## Demonstration

`symbolic-regression.py` demonstrates basic symbolic regression using randomly sampled points from *f(x)=x⁴ + x³ + x² + x*. Typically, the output looks like this:

```
1: L=28, SCORE=98.14708157694972
	x
		 #0: 28 -> 98.14708157694972
		 #1: 26 -> 98.14708157694972
		 #2: 53 -> 98.14708157694972
                 ...
                 ...
                 ...
		 #119: 64 -> inf
		 #120: 39 -> inf
2: L=13, SCORE=80.98186072182682
3: L=35, SCORE=43.75006328238336
4: L=35, SCORE=43.75006328238336
5: L=35, SCORE=43.75006328238336
6: L=35, SCORE=43.75006328238336
7: L=35, SCORE=43.75006328238336
8: L=35, SCORE=43.75006328238336
9: L=35, SCORE=43.75006328238336
10: L=35, SCORE=43.75006328238336
11: L=35, SCORE=43.75006328238336
12: L=35, SCORE=43.75006328238336
13: L=35, SCORE=43.75006328238336
14: L=35, SCORE=43.75006328238336
15: L=12, SCORE=25.274712319012547
16: L=12, SCORE=25.274712319012547
17: L=12, SCORE=25.274712319012547
18: L=12, SCORE=25.274712319012547
19: L=12, SCORE=25.274712319012547
20: L=12, SCORE=25.274712319012547
21: L=12, SCORE=25.274712319012547
22: L=12, SCORE=25.274712319012547
23: L=12, SCORE=25.274712319012547
24: L=12, SCORE=25.274712319012547
25: L=12, SCORE=25.274712319012547
26: L=12, SCORE=25.274712319012547
27: L=12, SCORE=25.274712319012547
28: L=12, SCORE=25.274712319012547
29: L=12, SCORE=25.274712319012547
30: L=12, SCORE=25.274712319012547
31: L=12, SCORE=25.274712319012547
32: L=12, SCORE=25.274712319012547
33: L=20, SCORE=1.6991616447192825e-14
33: L=20, SCORE=1.6991616447192825e-14
	(x / (1 / (x * ((x + 1) * ((1 / x) + x)))))
```

Expanding [the result][1] yields *x⁴ + x³ + x² + x*, which is the original function. Typically, a solution is reached within 30-100 generations. Tuning the GA parameters may affect convergence.

## Parallelization

The included GA is parallelizable by using `evolve(..., map=executor.map)`, where `executor` is e.g. a `ProcessPoolExecutor`. Other parallel `map` implementations with a similar signature may be used.

## Requirements

Python 3.6+

[1]: https://www.wolframalpha.com/input/?i=(x+%2F+(1+%2F+(x+*+((x+%2B+1)+*+((1+%2F+x)+%2B+x)))))
