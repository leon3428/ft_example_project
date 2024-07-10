import math

def tanh(x):
    return ( math.exp(x) - math.exp(-x) ) / ( math.exp(x) + math.exp(-x) )