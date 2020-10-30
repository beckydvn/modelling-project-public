from nnf import Var
from lib204 import Encoding
import geopy.distance


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

drive = Var('drive') # 🚗 
transit = Var('transit') # transit 
plane = Var('plane') # 🛩    
international = Var('international') # crossing the border
toll = Var('toll') # 30-min delay

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

def read_files(country, filename):
  file = open(filename, "r")
  country = {}
  line = "."
  while(line != ""):
    line = file.readline()
    if(line == ""):
      break
    splitline = line.split(",")
    cityname = splitline[0]
    province = splitline[1]
    latitude = splitline[2]
    longitude = splitline[3]
    timezone = splitline[4]
    country[cityname] = {}
    country[cityname]["province"] = province
    country[cityname]["latitude"] = latitude
    country[cityname]["longitude"] = longitude
    country[cityname]["timezone"] = timezone
  return country
    
  #while()







def iff(left, right):
  return (left.negate() | right) & (right.negate() | left)

def calcdistance(coord1, coord2):
  return geopy.distance.distance(coord1, coord2).km 

def example_theory():
    E = Encoding()

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
    #adds constraints that you can't start and end in the same city
    E.add_constraint(~toronto_start | ~toronto_end)
    E.add_constraint(~ottawa_start | ~ottawa_end)
    E.add_constraint(~scranton_start | ~scranton_end)
    E.add_constraint(~baltimore_start | ~baltimore_end)

    #international variable can only be true if you are travelling from america to canada/vice versa
    E.add_constraint(iff((((toronto_start | ottawa_start) & (scranton_end | baltimore_end)) |
     ((toronto_end | ottawa_end) & (scranton_start | baltimore_start))), international))

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

    #only relevant if travel is international
    #if you have tested positive for the virus/been in contact, you can't cross the border
    E.add_constraint(~international | (~virus & documents))
    #no documents means you can't cross the border
    E.add_constraint((international & documents) | ~international)

    #driving constraints (come into play if they are driving):
    #bad weather and roadwork implies unfeasible trip
    E.add_constraint((((rainy | snowstorm) & roadwork) & drive).negate())
    #bad weather and holiday implies unfeasible trip
    E.add_constraint((((rainy | snowstorm) & holiday) & drive).negate())
    #roadwork and holiday implies unfeasible trip
    E.add_constraint(((roadwork & holiday) & drive).negate())
    #roadwork and accident implies unfeasible trip
    E.add_constraint(((roadwork & accident) & drive).negate())
    #holiday and accident implies unfeasible trip
    E.add_constraint(((holiday & accident) & drive).negate())
    #tolls and no money implies unfeasible trip
    #E.add_constraint(((toll & ~money) & drive).negate() | fail)
    E.add_constraint(plane | transit | drive)

    return E


if __name__ == "__main__":
    
    canada = read_files("canada", "Canada Cities.csv")
    america = read_files("america", "US Cities.csv")
    for x in america:
        print (x)
        for y in america[x]:
            print (y,':',america[x][y])

    coord1 = (52.2296756, 21.0122287)
    coord2 = (52.406374, 16.9251681)
    print(calcdistance(coord1, coord2))
    T = example_theory()
    T.add_constraint(toronto_start)
    T.add_constraint(baltimore_end)
    print("\nSatisfiable: %s" % T.is_satisfiable())
    print("# Solutions: %d" % T.count_solutions())
    print("   Solution: %s" % T.solve())
    #for i in range(3):
    #T = example_theory()
    #print()
    """"
    print("\nVariable likelihoods:")
    for v,vn in zip([a,b,c,x,y,z], 'abcxyz'):
        print(" %s: %.2f" % (vn, T.likelihood(v)))
    print()
    """