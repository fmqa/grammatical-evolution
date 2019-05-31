"""Utilities for encoding GA problems."""

__all__ = ["integers", "grid", "subset", "composite"]

import random
import math

class grid:
    """Mutator/Sampler for a parameter grid."""
    def __init__(self, space, rate, random=random):
        self.space = space
        self.rate = rate
        self.random = random
    
    @classmethod
    def auto(cls, space, random=random):
        return cls(space, 1 / len(space), random)
    
    def samples(self, n):
        """Yields n random samples."""
        while n > 0:
            yield frozenset((k, v(self.random)) for k, v in self.space.items())
            n -= 1
    
    def __call__(self, member):
        """Mutates a single parameter within the grid."""
        return frozenset((k, self.space[k](self.random) if self.random.random() < self.rate else v) for k, v in member)

class subset:
    """Mutator/Sampler for algebraic sets."""

    def __init__(self, omega, least, rate=0.5, random=random):
        self.omega = omega
        self.least = least
        self.rate = rate
        self.random = random
    
    @classmethod
    def auto(cls, omega, least=1, rate=0.5, random=random): 
        return cls(omega, least, rate, random)
    
    def samples(self, n):
        """Yields n random samples."""
        while n > 0:
            yield frozenset(self.random.sample(self.omega, self.random.randint(self.least, len(self.omega))))
            n -= 1
    
    def mutate(self, member):
        """Mutation operator that removes or adds an element to the operand."""
        member = set(member)
        # Mutate
        if self.random.random() < self.rate:
            member.pop()
        else:
            member.add(self.random.choice(self.omega))
        # Ensure invariants
        if len(member) < self.least:
            member.update(self.random.sample(self.omega, self.least - len(member)))
        return frozenset(member)
    
    def ucrossover(self, first, second):
        """Crossover that returns the set union of the operands."""
        return frozenset(first | second)
    
    def uncrossover(self, first, second):
        """Crossover that returns the intersection or union of the operands."""
        result = first | second if self.random.random() < 0.5 else first & second
        # Ensure invariants
        if len(result) < self.least:
            result = set(result)
            result.update(self.random.sample(self.omega, self.least - len(result)))
        return frozenset(result)

class composite:
    """Helper for composite chromosomes."""
    def __init__(self, mutators, crossovers):
        self.mutators = mutators
        self.crossovers = crossovers
    
    def samples(self, n):
        return zip(*(x.samples(n) for x in self.mutators))
    
    def mutate(self, member):
        return tuple(f(x) for f, x in zip(self.mutators, member))
    
    def crossover(self, first, second):
        return tuple(f(x, y) for f, x, y in zip(self.crossovers, first, second))

        
