"""Genetic algorithm toolbox."""

__all__ = ["tournament", "reassemble2p", "twopoint", "uniform", "evolve"]

import random
from itertools import chain
from typing import NamedTuple, Callable, Sequence, Any
from collections import OrderedDict

class tournament(NamedTuple):
    """Deterministic tournament selection strategy."""
    # Default to binary tournament.
    k: int = 2
    def __call__(self, population, fitness, elite, random=random):
        # Tournament size
        [k] = self
        # Save the elites (Lowest N elements).
        result = population[:elite]
        # Non-elite population size.
        n = len(population) - elite
        # Extend result list by stochastically selected elements.
        result += (min(random.choices(population, k=k), key=fitness) for index in range(n))
        # Return new population.
        return result

def reassemble2p(prefix, old, new, suffix):
    """Two-point crossover reassembly operator."""
    return prefix + new + suffix

class twopoint(NamedTuple):
    """Two-point crossover of two members. Returns the offspring of first and second."""
    reassemble: Callable[[Sequence, Sequence, Sequence, Sequence], Sequence] = reassemble2p
    random: Any = random

    def __call__(self, first, second):
        if first and second:
            reassemble, random = self
            k = random.randint(1, min(len(first), len(second)))
            a = random.randint(0, len(first) - k)
            b = random.randint(0, len(second) - k)
            third = reassemble(first[:a], first[a:a+k], second[b:b+k], first[a+k:])
            return third
        else:
            return first or second

class uniform(NamedTuple):
    """Uniform crossover of two members."""
    type: Callable[[Any], Any] = tuple
    bias: float = 0.5
    random: Any = random
    def __call__(self, first, second):
        if first and second:
            type, bias, random = self
            k = min(len(first), len(second))
            a = random.randint(0, len(first) - k)
            child = type(a if random.random() < bias else b for a, b in zip(first, chain(chain(first[:a], second), first[a+k:])))
            return child
        else:
            return first or second

def breeding(population, crossover, rate, elite, random=random):
    """Apply crossover operator to the population at the given rate."""
    # Save the elites (Lowest N elements).
    result = population[:elite]
    # Non-elite population size.
    n = len(population) - elite
    result += (crossover(member, random.choice(population)) if random.random() < rate else member for member in random.choices(population, k=n))
    # Return children plus the saved elites.
    return result

def mutation(population, mutate, elite, random=random):
    """Apply mutation operator to every member of the population."""
    # Save the elites (Lowest N elements).
    result = population[:elite]
    # Non-elite population size.
    n = len(population) - elite
    result += (mutate(member) for member in random.choices(population, k=n))
    # Return mutants plus the saved elites.
    return result

def evolve(population, fitness, mutate, elite=20, rate=0.7, crossover=twopoint(), selection=tournament(2), map=map, remember=0, random=random):
    """Genetic algorithm. Returns an iterable of evolving populations."""
    # Ensure that population is a list.
    population = list(population)
    # Check if the number of elite members to be kept across generations makes sense.
    if elite >= len(population):
        raise ValueError("Elite count must be lower than population count")
    # Cache at least as much many individuals as contained in the population.
    remember = max(remember, len(population))
    # Cache of fitness values for each individual. New elements are on the right side (last/end), while
    # old elements are on the left side (first/beginning).
    cache = OrderedDict()
    # Cache accessor - returns cache[key] while moving the entry for key to the right side. 
    def access(key):
        value = cache[key]
        cache.move_to_end(key)
        return value
    # Evolution loop.
    while True:
        # Calculate individual fitness values.
        cache.update(zip((x for x in population if x not in cache), map(fitness, (x for x in population if x not in cache))))
        # Sort by fitness.
        population.sort(key=access)
        # Yield selection back to caller.
        yield population, cache
        # Select members for crossover.
        population = selection(population, access, elite, random)
        # Remove old elements from cache
        while len(cache) > remember: cache.popitem(False)
        # Breed selected members.
        population = breeding(population, crossover, rate, elite, random)
        # Calculate individual fitness values of offspring.
        cache.update(zip((x for x in population if x not in cache), map(fitness, (x for x in population if x not in cache))))
        # Pull best offspring to front.
        population.sort(key=access)
        # Remove old elements from cache.
        while len(cache) > remember: cache.popitem(False)
        # Mutate members.
        population = mutation(population, mutate, elite, random)


