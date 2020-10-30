from nnf import Var
from lib204 import Encoding
import geopy.distance

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

# Build an example full theory for your setting and return it.
#
#  There should be at least 10 variables, and a sufficiently large formula to describe it (>50 operators).
#  This restriction is fairly minimal, and if there is any concern, reach out to the teaching staff to clarify
#  what the expectations are.

# read in a database of cities from a specific country and write it to a list of dictionaries
def read_files(country, filename):
  file1 = open(filename, "r")
  country = []
  line = "."
  while(line != ""):
    line = file1.readline()
    if(line == ""):
      break
    line = line.strip("\ufeff")
    splitline = line.split(",")

    city = splitline[0]
    province = splitline[1]
    latitude = splitline[2]
    longitude = splitline[3]
    timezone = splitline[4].strip("\n")
    entry = {}
    entry["city"] = city
    entry["province"] = province
    entry["latitude"] = latitude
    entry["longitude"] = longitude
    entry["timezone"] = timezone
    country.append(entry)

  file1.close()
  return country
    
# if and only if
def iff(left, right):
  return (left.negate() | right) & (right.negate() | left)

# calculate the distance between two locations using latitudes and longtitudes
def calc_distance(coord1, coord2):
  return geopy.distance.distance(coord1, coord2).km 

def example_theory():
    E = Encoding()

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

"""def testing():
    for x in canada:
        print (x)
        for y in canada[x]:
            print (y,':',canada[x][y])

    coord1 = (52.2296756, 21.0122287)
    coord2 = (52.406374, 16.9251681)"""

def location_input():
    canada = read_files("canada", "Canada Cities.csv")
    america = read_files("america", "US Cities.csv")

    # create a list for canadian and american cities
    canada_cities = []
    america_cities = []
    for entry in canada:
      canada_cities.append(entry["city"].lower())
    for entry in america:
      america_cities.append(entry["city"].lower())    

    start = ""
    end = ""
    inputOK = False
    # loop until the cities entered are valid and ready to be used for calculation
    while(not inputOK):
      start = input("Please enter your starting city and country, separated by a comma:")
      end = input("Please enter your ending city and country, separated by a comma:")
      start_city = start.split(",")[0].lower()
      start_country = start.split(",")[1].lower()
      end_city = end.split(",")[0].lower()
      end_country = end.split(",")[1].lower()

      if(start_city == end_city and start_country == end_country):
        print("Your starting and ending city can't be the same.")
      elif((start_city not in canada_cities and start_city not in
      america_cities) or (end_city not in canada_cities and end_city
      not in america_cities)):
        print("You must start and end in a city in Canada or the United States.")
      elif(start_country not in ["canada","america","united states", 
      "snited states of america", "usa"] or end_country not in ["canada","america","united states", 
      "united states of america", "usa"]):
        print("The country you enter must be in Canada or the United States.")
      else:
        inputOK = True

    return start_city, end_city


def get_international(start_city, end_city, canada_cities, america_cities):
    # checking if the trip is international or not (from Canada to USA and vice versa)
    if((start_city in canada_cities and end_city in america_cities) or (start_city in america_cities and end_city in canada_cities)):
      border = True
    else:
      border = False

    return border

if __name__ == "__main__":
    T = example_theory()

    border = get_international()
    if(border):
      T.add_constraint(international)
    else:
      T.add_constraint(~international)
  
    """"
    print("\nSatisfiable: %s" % T.is_satisfiable())
    print("# Solutions: %d" % T.count_solutions())
    print("   Solution: %s" % T.solve())
    
    print("\nVariable likelihoods:")
    for v,vn in zip([a,b,c,x,y,z], 'abcxyz'):
        print(" %s: %.2f" % (vn, T.likelihood(v)))
    print()
    """
    