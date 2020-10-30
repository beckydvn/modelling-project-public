from nnf import Var
from lib204 import Encoding
from nnf import true
from nnf import false

#TEST
newtest = Var("newtest")

# Call your variables whatever you want
sunny = Var('sunny') # 🌞 
rainy = Var('rainy') # rainy 1-hour delay
snowstorm = Var('snowstorm') # snow storm 2-hour delay
virus = Var('virus') # 🦠 
documents = Var('documents') # document
roadwork = Var('roadwork') # 🚧 0.75-hour delay
holiday = Var('holiday') # holiday 1.25-hour delay
accident = Var('accident') # accident 1.5-hour delay
money = Var('money') # money
fail = Var('fail') # failed to generate a trip with a reasonable time (fail model)


ottawa_start = Var('ottawa_start') # Starting in Ottawa  
ottawa_end = Var('ottawa_end') # Ending in Ottawa
scranton_start = Var('scranton_start') # Starting in Scranton
scranton_end = Var('scranton_end') # Ending in Scranton
toronto_start = Var('toronto_start') # Starting in Toronto
toronto_end = Var('toronto_end') # Ending in Toronto
baltimore_start = Var('baltimore_start') # Starting in Baltimore
baltimore_end = Var('baltimore_end') # Ending in Baltimore

 #hello2
# Build an example full theory for your setting and return it.
#
#  There should be at least 10 variables, and a sufficiently large formula to describe it (>50 operators).
#  This restriction is fairly minimal, and if there is any concern, reach out to the teaching staff to clarify
#  what the expectations are.

def iff(left, right):
  return (left.negate() | right) & (right.negate() | left)
  
def example_theory():
    E = Encoding()
    drive = Var('drive') # 🚗 
    transit = Var('transit') # transit 
    plane = Var('plane') # 🛩    
    international = Var('international') # crossing the border
    toll = Var('toll') # 30-min delay
     
    #also need to add a constraint that you can only have one start and one end...
    E.add_constraint(~toronto_start | (ottawa_start | scranton_start | baltimore_start).negate())
    E.add_constraint(~ottawa_start | (toronto_start | scranton_start | baltimore_start).negate())
    E.add_constraint(~scranton_start | (ottawa_start | toronto_start | baltimore_start).negate())
    E.add_constraint(~baltimore_start | (ottawa_start | scranton_start | toronto_start).negate())
    E.add_constraint(~toronto_end | (ottawa_end | scranton_end | baltimore_end).negate())
    E.add_constraint(~ottawa_end | (toronto_end | scranton_end | baltimore_end).negate())
    E.add_constraint(~scranton_end | (ottawa_end | toronto_end | baltimore_end).negate())
    E.add_constraint(~baltimore_end | (ottawa_end | scranton_end | toronto_end).negate())
    E.add_constraint(toronto_start | ottawa_start | scranton_start | baltimore_start)
    E.add_constraint(toronto_end | ottawa_end | scranton_end | baltimore_end)

    if(((toronto_start | ottawa_start) & (scranton_end | baltimore_end)) | ((toronto_end | ottawa_end) & (scranton_start | baltimore_start))):
      international = true
    else:
      international = false

    #make sure weather is valid
    E.add_constraint(iff(sunny, ~rainy))
    E.add_constraint(iff(rainy, ~sunny))
    E.add_constraint(iff(sunny, ~snowstorm))
    E.add_constraint(iff(snowstorm, ~sunny))
    
    
    #good weather and holiday implies tickets will be sold out and you have to drive
    E.add_constraint((sunny & holiday).negate() | (transit | plane).negate())
    #rainy or snowstorm increases the likelihood of accidents
    E.add_constraint((rainy | snowstorm).negate() | accident)
    #snowstorm implies that transit and planes will be shut down
    E.add_constraint(~snowstorm | (transit | plane).negate())
    #if you have tested positive for the virus/been in contact, you can't cross the border
    E.add_constraint(~virus | ~documents)
    #no documents means you can't cross the border
    E.add_constraint((~documents & international).negate() | fail)
    
    #driving constraints (come into play if they are driving):
    #bad weather and roadwork implies unfeasible trip
    E.add_constraint((((rainy | snowstorm) & roadwork) & drive).negate() | fail)
    #bad weather and holiday implies unfeasible trip
    E.add_constraint((((rainy | snowstorm) & holiday) & drive).negate() | fail)
    #roadwork and holiday implies unfeasible trip
    E.add_constraint(((roadwork & holiday) & drive).negate() | fail)
    #roadwork and accident implies unfeasible trip
    E.add_constraint(((roadwork & accident) & drive).negate() | fail)
    #holiday and accident implies unfeasible trip
    E.add_constraint(((holiday & accident) & drive).negate() | fail)
    #tolls and no money implies unfeasible trip
    #E.add_constraint(((toll & ~money) & drive).negate() | fail)
    E.add_constraint((plane | transit | drive) | fail)
    E.add_constraint(~fail)

    return E


if __name__ == "__main__":

    T = example_theory()

    print("\nSatisfiable: %s" % T.is_satisfiable())
    print("# Solutions: %d" % T.count_solutions())
    print("   Solution: %s" % T.solve())
    """"
    print("\nVariable likelihoods:")
    for v,vn in zip([a,b,c,x,y,z], 'abcxyz'):
        print(" %s: %.2f" % (vn, T.likelihood(v)))
    print()
    """