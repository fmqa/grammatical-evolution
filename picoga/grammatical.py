"""Grammatical evolution utilities."""

__all__ = ["expand", "selector", "ripple", "codons"]

from collections import abc
import random
import math

def expand(S, choice, maxdepth=math.inf):
    """Given starting symbol S of a grammar G, expand G using
    the selector function G.
    
    The maxdepth parameter may be used to control the depth
    of the expansion. ValueError is raised if the depth is exceeded.
    
    The grammar must be specified using generators. See the arithmetic
    grammar included for an example."""
    
    # Queue of incomplete symbols.
    q = [S()]
    # Current symbol.
    x = None
    # Expansion loop.
    while q:
        # Check expansion depth.
        if len(q) >= maxdepth:
            raise ValueError("Expansion depth exceeded")
        try:
            # Send current symbol to last incomplete symbol.
            x = q[-1].send(x)
        except StopIteration as e:
            # If symbol signals completion by raising StopIteration,
            # delete it from the incomplete symbol queue.
            del q[-1]
            # If symbol returns a generator (i.e. incomplete symbol),
            # add it to the incomplete symbol queue, otherwise it
            # becomes the current symbol.
            if isinstance(e.value, abc.Generator):
                q.append(e.value)
                x = None
            else:
                x = e.value
        else:
            # Symbol does not signal completion, but yields another
            # incomplete symbol, in which case it is added to the queue.
            if isinstance(x, abc.Generator):
                q.append(x)
                x = None
            else:
                # Symbol does not signal completion, but yields
                # a sequence of choices. Use the choice function to
                # select from this sequence.
                x = choice(x)
    return x

class selector:
    """A selector that uses the given codons.
    
    If the supply of given codons was exhausted, the hash of the codon
    structure is used as a seed to a random number generator, which
    is subsequently used to perform selections even after the codon
    supply is exhausted."""
    
    def __init__(self, codons, random=random.Random):
        # Grab iterator from iterable.
        self.iterator = iter(codons)
        # Create RNG and seed with the hash of the codons.
        self.random = random(hash(codons))
        # Counter for number of consumed integers.
        self.n = 0
    
    def __call__(self, choices):
        try:
            # Consume iterator.
            x = next(self.iterator)
        except StopIteration:
            # Use the RNG if the iterator is exhausted.
            return self.random.choice(choices)
        else:
            # Increment counter and perform the selection.
            self.n += 1
            return choices[x % len(choices)]

class ripple:
    """One-point tail-exchange (ripple) crossover operator typically used in
    grammatical evolution."""
    def __init__(self, most, bias=0.5, random=random):
        self.most = most
        self.bias = bias
        self.random = random
    
    def __call__(self, first, second):
        # Cut-off point for first parent (prefix parent).
        i = self.random.randrange(len(first))
        # Cut-off point for second parent (suffix parent).
        j = self.random.randrange(len(second))
        # Construct child, varying prefix/suffix order depending
        # on bias.
        if self.random.random() < self.bias:
            third = first[:i] + second[j:]
        else:
            third = second[j:] + first[:i]
        # Truncate child suffix if maximum length exceeded.
        return third[:self.most]

class codons:
    """Codon mutator/sampler."""
    def __init__(self, omega, most, weights=(1.0, 1.0, 1.0), random=random):
        self.omega = omega
        self.most = most
        self.weights = weights
        self.random = random
    
    def samples(self, n):
        """Returns N random codon sequences."""
        while n >= 0:
            yield tuple(self.random.choices(self.omega, k=self.random.randint(1, self.most)))
            n -= 1

    def __call__(self, member):
        # Select random action: (c)lone, (d)elete, or (r)eplace.
        [action] = self.random.choices("cdr", self.weights)
        # Index to perform the action on.
        index = self.random.randrange(len(member))
        # Convert to list to allow for mutation.
        member = list(member)
        # Clone random element and add it to the suffix unless the
        # length bound is reached, in case we perform a removal instead.
        if action == "c":
            if len(member) < self.most:
                member.append(member[index])
            else:
                action = "d"
        # Delete random element unless the member is a singleton, in which
        # case we perform a replacement instead.
        if action == "d":
            if len(member) > 1:
                del member[index]
            else:
                action = "r"
        # Replace random element with its nearest neighbor.
        if action == "r":
            member[index] = self.omega[(self.omega.index(member[index]) + 1) % len(self.omega)]
        return tuple(member)

class arithmetic:
    """Simple grammar for infix arithmetic with binary operators.""" 
    def __init__(self, vars, binops):
        self.vars = vars
        self.binops = binops
    def var(self):
        return (yield self.vars)
    def binary(self):
        op = (yield self.binops)
        return op((yield self.exp()), (yield self.exp()))
    def exp(self):
        return (yield self.binary(), self.var())
    S = exp

if __name__ == "__main__":
    add = "({} + {})".format
    sub = "({} - {})".format
    mul = "({} * {})".format
    div = "({} / {})".format

    G = arithmetic(("x0", "x1", "x2"), (add, sub, mul, div))
    print(expand(G.S, random.choice, 32))

