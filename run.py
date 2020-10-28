
from nnf import Var
from lib204 import Encoding

# Call your variables whatever you want
x = Var('x') # 🌞 
y = Var('y') # rainy
z = Var('z') # snow storm
v = Var('v') # 🦠 
d = Var('d') # document
r = Var('r') # 🚧 
h = Var('h') # holiday
a = Var('a') # accident
u = Var('u') # unreasonable time (fail model)
c = Var('c') # 🚗 
b = Var('b') # 🚌  
t = Var('t') # 🚂 
p = Var('p') # 🛩 

ottawa_start = Var('ottawa_start') # Starting in Ottawa  
ottawa_end = Var('ottawa_end') # Ending in Ottawa
scranton_start = Var('scranton_start') # Starting in Scranton
scranton_end = Var('scranton_end') # Ending in Scranton
toronto_start = Var('toronto_start') # Starting in Toronto
toronto_end = Var('toronto_end') # Ending in Toronto
baltimore_start = Var('baltimore_start') # Starting in Baltimore
baltimore_end = Var('baltimore_end') # Ending in Baltimore
 
# Build an example full theory for your setting and return it.
#
#  There should be at least 10 variables, and a sufficiently large formula to describe it (>50 operators).
#  This restriction is fairly minimal, and if there is any concern, reach out to the teaching staff to clarify
#  what the expectations are.
def example_theory():
    E = Encoding()
    E.add_constraint(a | b)
    E.add_constraint(~a | ~x)
    E.add_constraint(c | y | z)
    return E


if __name__ == "__main__":

    T = example_theory()

    print("\nSatisfiable: %s" % T.is_satisfiable())
    print("# Solutions: %d" % T.count_solutions())
    print("   Solution: %s" % T.solve())

    print("\nVariable likelihoods:")
    for v,vn in zip([a,b,c,x,y,z], 'abcxyz'):
        print(" %s: %.2f" % (vn, T.likelihood(v)))
    print()
    
    
