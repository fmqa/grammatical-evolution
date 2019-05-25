"""Utilities for encoding GA problems."""

__all__ = ["integers", "grid", "subset", "composite"]

import random
from typing import NamedTuple, Iterable, Sequence, OrderedDict, Callable, Any
import math

class grid(NamedTuple):
    """Mutator/Sampler for a parameter grid."""
    
    space: OrderedDict[Any, Callable[[Any], Any]]
    rate: float
    random: Any = random
    
    @classmethod
    def auto(cls, space, random=random):
        return cls(space, 1 / len(space), random)
    
    def samples(self, n):
        """Yields n random samples."""
        space, rate, random = self
        while n > 0:
            yield frozenset((k, v(random)) for k, v in space.items())
            n -= 1
    
    def __call__(self, member):
        """Mutates a single parameter within the grid."""
        space, rate, random = self
        return frozenset((k, space[k](random) if random.random() < rate else v) for k, v in member)

class subset(NamedTuple):
    """Mutator/Sampler for algebraic sets."""

    omega: Sequence
    least: int
    rate: float = 0.5
    random: Any = random
    
    @classmethod
    def auto(cls, omega, least=1, rate=0.5, random=random): 
        return cls(omega, least, rate, random)
    
    def samples(self, n):
        """Yields n random samples."""
        omega, least, rate, random = self
        while n > 0:
            yield frozenset(random.sample(omega, random.randint(least, len(omega))))
            n -= 1
    
    def mutate(self, member):
        """Mutation operator that removes or adds an element to the operand."""
        omega, least, rate, random = self
        member = set(member)
        # Mutate
        if random.random() < rate:
            member.pop()
        else:
            member.add(random.choice(omega))
        # Ensure invariants
        if len(member) < least:
            member.update(random.sample(omega, least - len(member)))
        return frozenset(member)
    
    def ucrossover(self, first, second):
        """Crossover that returns the set union of the operands."""
        omega, least, rate, random = self
        return frozenset(first | second)
    
    def uncrossover(self, first, second):
        """Crossover that returns the intersection or union of the operands."""
        omega, least, rate, random = self
        result = first | second if random.random() < 0.5 else first & second
        # Ensure invariants
        if len(result) < least:
            result = set(result)
            result.update(random.sample(omega, least - len(result)))
        return frozenset(result)

class composite(NamedTuple):
    """Helper for composite chromosomes."""
     
    mutators: Iterable[Any]
    crossovers: Iterable[Any]
    
    def samples(self, n):
        return zip(*(x.samples(n) for x in self.mutators))
    
    def mutate(self, member):
        return tuple(f(x) for f, x in zip(self.mutators, member))
    
    def crossover(self, first, second):
        return tuple(f(x, y) for f, x, y in zip(self.crossovers, first, second))

        
