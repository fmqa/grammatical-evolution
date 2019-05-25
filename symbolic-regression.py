if __name__ == "__main__":
    import random
    from picoga.grammatical import arithmetic, expand, selector, ripple, codons
    from picoga import evolve, tournament
    from functools import lru_cache
    import math
    
    # Binary operators.
    add = "({} + {})".format
    sub = "({} - {})".format
    mul = "({} * {})".format
    div = "({} / {})".format
    
    # Grammar.
    G = arithmetic(("x", "1"), (add, sub, mul, div))
    
    # Problem representation; Use integers {0..3} as the source
    # sequence, as the binary operator rules has 4 possible
    # productions (add, sub, mul, div).
    rep = codons(omega=range(4), most=100)
    
    # Example function.
    func = lambda x: x ** 4 + x ** 3 + x ** 2 + x
    
    # Sample 200 distinct points from the example function.
    table = {}
    while len(table) < 200:
        x = random.uniform(-1, 1)
        table[x] = func(x)
    
    # Candidate expansion cache.
    @lru_cache(maxsize=1024)
    def expansion(code):
        sel = selector(code)
        try:
            return expand(G.S, sel, 40)
        except ValueError:
            return None
    
    # Fitness value cache per candidate: L1 loss.
    @lru_cache(maxsize=1024)
    def fit(code):
        prg = expansion(code)
        if prg is None:
            return math.inf
        f = 0
        for k, yt in table.items():
            try:
                yp = eval(prg, {"x":k})
            except ZeroDivisionError:
                return math.inf
            # L1 distance.
            f += abs(yt - yp)
        return f
    
    # Initial population.
    pop = rep.samples(120)
    
    # Evolver.
    evo = evolve(pop, fit, rep, elite=5, rate=0.8, remember=256, selection=tournament(2), crossover=ripple(rep.most))
    
    # Evolution loop.
    n = 0
    for pop, cache in evo:
        best = pop[0]
        score = cache[best]
        p = expand(G.S, selector(best))
        print("{}: L={}, SCORE={}".format(n + 1, len(best), score))
        if n % 100 == 0:
            print("\t"+p)
            for i, blob in enumerate(pop):
                print("\t\t #{}: {} -> {}".format(i, len(blob), cache[blob]))
        # End evolution if L1 loss is less than epsilon.
        if score < 1e-6:
            break
        n += 1
    print("{}: L={}, SCORE={}".format(n + 1, len(best), score))
    print("\t"+p)

