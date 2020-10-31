from nnf import Var
from lib204 import Encoding
import geopy
import geopy.distance
from geopy.geocoders import Nominatim
import pyproj


virus = Var('virus') # 🦠 
documents = Var('documents') # document
international = Var('international') # crossing the border
money = Var('money') # money
holiday = Var('holiday') # holiday 1.25-hour delay

sunny = Var('sunny') # 🌞 
rainy = Var('rainy') # rainy 1-hour delay
snowstorm = Var('snowstorm') # snow storm 2-hour delay

roadwork = Var('roadwork') # 🚧 0.75-hour delay
accident = Var('accident') # accident 1.5-hour delay
toll = Var('toll') # 30-min delay
"""
drive = Var('drive') # 🚗 
transit = Var('transit') # transit 
plane = Var('plane') # 🛩  
"""

"""
#sunny = {"Toronto to Ottawa": proposition, "Ottawa to Scranton": proposition}
sunny = {}
rainy = {}
snowstorm = {}
"""
#roadwork = {}
#accident = {}
#toll = {}

drive = {}
transit = {}
plane = {}

#stop_info is a list of dictionaries, where each entry contains the starting    
#and ending location for each stop in user's chosen stops, and the distance between the two.
#(in short it contains all the relevant info for the stops the user will take).
stop_info = []


# Build an example full theory for your setting and return it.
#
#  There should be at least 10 variables, and a sufficiently large formula to describe it (>50 operators).
#  This restriction is fairly minimal, and if there is any concern, reach out to the teaching staff to clarify
#  what the expectations are.

def read_files(country, filename):
  """read in a database of cities from a specific country and write it to a list 
  of dictionaries"""
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
    entry["province/state"] = province
    entry["latitude"] = latitude
    entry["longitude"] = longitude
    entry["timezone"] = timezone
    country.append(entry)

  file1.close()
  return country
    
def iff(left, right):
  """emulate an if and only if statement"""
  return (left.negate() | right) & (right.negate() | left)

def calc_distance(coord1, coord2):
  """calculate the distance between two locations using latitudes and longtitudes"""
  return geopy.distance.distance(coord1, coord2).km 


def get_international(start_country, end_country):
    """checking if the trip is international or not (from Canada to USA and vice versa)"""
    return start_country != end_country

def calc_time(distance, mode):
    """calculates the amount of time a trip would take given the mode of transportation.
    note that speed estimates are used for each mode."""
    if(mode == "drive"):
      speed = 80.0
    elif(mode == "transit"):
      speed = 200.0
    elif(mode == "plane"):
      speed = 850.0
    return distance / speed

def determine_travel_modes(drive_time, transit_time, plane_time):
    """based on the time it would take to travel from one spot to another with each mode of 
    transportation, only add reasonable modes of transportation to the travel dictionary."""
    travel = {}
    if(drive_time < 24):
        travel["drive"] = drive_time
    if(transit_time < 10):
        travel["transit"] = transit_time
    if(plane_time > 2):
        travel["plane"] = plane_time
    return travel

def raw_location_input(canada_cities, america_cities):
    """gets input of the starting city/country and ending city/country from the user"""
    start = ""
    end = ""
    inputOK = False
    # loop until the cities entered are valid and ready to be used for calculation
    while(not inputOK):
      print("When entering your cities, you can only travel to and from Canada and the United States.")
      start = input("Please enter your starting city, and country, separated by (just) a comma:")
      end = input("Please enter your ending city, and country, separated by a comma:")
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
      elif(start_country not in ["canada", "united states"] or end_country not in ["canada", "united states"]):
        print("The country you enter must be in Canada or the United States.")
      else:
        inputOK = True

    return {"starting city":start_city, "starting country": start_country, "ending city": end_city,
    "ending country": end_country}

def clarify_duplicates(canada, america, raw_location):
    """This function asks the user to clarify their chosen city if duplicates exist."""
    duplicates_start = []
    duplicates_end = []

    raw_start_city = raw_location["starting city"]
    raw_start_country = raw_location["starting country"]
    raw_end_city = raw_location["ending city"]
    raw_end_country = raw_location["ending country"]

    #if their city is in canada, search through all the cities in canada and
    #add all the duplicates to a list
    if(raw_start_country == "canada"):
      for entry in canada:
        if(entry["city"].lower() == raw_start_city):
          duplicates_start.append(entry)
    #do the same but for american cities if their city was in the US
    else:
      for entry in america:
        if(entry["city"].lower() == raw_start_city):
          duplicates_start.append(entry)
    #repeat for the destination city
    if(raw_end_country == "united states"):
      for entry in america:
        if(entry["city"].lower() == raw_end_city):
          duplicates_end.append(entry)
    else:
      for entry in canada:
        if(entry["city"].lower() == raw_end_city):
          duplicates_end.append(entry)

    #if there are duplicates, the starting city is the first (original) city
    if(len(duplicates_start) == 1):
      start_city = duplicates_start[0]
    #otherwise, allow the user to pick the city they want
    else:
      print("Please enter the number beside the starting city you are referring to.") 
      for i in range(len(duplicates_start)):
        print(i)
        for value in duplicates_start[i].values():
          print(value)
        print("\n")
      choice = int(input("Enter your choice:"))
      start_city = duplicates_start[choice]

    #do the same for the destination city
    if(len(duplicates_end) == 1):
      end_city = duplicates_end[0]
    else:
      print("Please enter the number beside the destination city you are referring to.") 
      for i in range(len(duplicates_end)):
        print(i)
        for value in duplicates_end[i].values():
          print(value)
        print("\n")
      choice = int(input("Enter your choice:"))
      end_city = duplicates_end[choice]

    return start_city, end_city


def example_theory():
    E = Encoding()

    for i in range(len(stop_info)):
      #set up propositions for travel
      drive[stop_info[i]["location"]] = Var('drive' + str(i))
      transit[stop_info[i]["location"]] = Var('transit' + str(i))
      plane[stop_info[i]["location"]] = Var('plane' + str(i))

    #loop through each stop; if a given mode of transportation is missing, set the
    #constraint that it can't be true
    #note: we don't necessarily set it that proposition to true if it ISN'T missing because
    #it could still be set false by other constraints.
    for entry in stop_info:
      if "drive" not in entry["travel"].keys():
        E.add_constraint(~drive[entry["location"]])
      if "transit" not in entry["travel"].keys():
        E.add_constraint(~transit[entry["location"]])
      if "plane" not in entry["travel"].keys():
        E.add_constraint(~plane[entry["location"]])

    #make sure weather is valid
    E.add_constraint(iff(sunny, ~rainy))
    E.add_constraint(iff(rainy, ~sunny))
    E.add_constraint(iff(sunny, ~snowstorm))
    E.add_constraint(iff(snowstorm, ~sunny))
    
    """
    #good weather and holiday implies tickets will be sold out and you have to drive
    E.add_constraint((sunny & holiday).negate() | (transit | plane).negate())
    """

    #rainy or snowstorm increases the likelihood of accidents
    E.add_constraint((rainy | snowstorm).negate() | accident)

    """
    #snowstorm implies that transit and planes will be shut down
    E.add_constraint(~snowstorm | (transit | plane).negate())
    """

    #only relevant if travel is international
    #if you have tested positive for the virus/been in contact, you can't cross the border
    E.add_constraint(~international | (~virus & documents))
    #no documents means you can't cross the border
    E.add_constraint((international & documents) | ~international)

    """
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

    #tentative
    E.add_constraint(((toll & ~money) & drive).negate())

    #you must have at least one form of travel
    E.add_constraint(plane | transit | drive)
    """

    return E

"""def testing():
  print("HERE")
  print(return_info())
  
    for x in canada:
        print (x)
        for y in canada[x]:
            print (y,':',canada[x][y])
    coord1 = (52.2296756, 21.0122287)
    coord2 = (52.406374, 16.9251681)
    """
    

if __name__ == "__main__":
    #read in the databases (each database contains the city name and its 
    #longitude/latitude coordinate).
    canada = read_files("canada", "Canada Cities.csv")
    america = read_files("america", "US Cities.csv")

    # create a list for canadian and american cities
    canada_cities = []
    america_cities = []
    for entry in canada:
      canada_cities.append(entry["city"].lower())
    for entry in america:
      america_cities.append(entry["city"].lower())    

    #get the raw location from the user and clarify any duplicates to get the
    #starting and ending city (the countries will of course remain the same)
    raw_location = raw_location_input(canada_cities,america_cities)
    start_city, end_city = clarify_duplicates(canada, america, raw_location)
    start_country = raw_location["starting country"]
    end_country = raw_location["ending country"]

    #calculate the total distance between the starting and ending city
    start_coord = (start_city["latitude"], start_city["longitude"])
    end_coord = (end_city["latitude"], end_city["longitude"])
    total_dist = calc_distance(start_coord, end_coord)

    #tell the user the total number of km
    print("A trip from " + start_city["city"] + ", " + start_city["province/state"] + " to " + end_city["city"]
     + ", " + end_city["province/state"] + " is " + str(total_dist)+ " km long.")

    #calculate 1/tenth of the distance from the start to the end
    #the user will be given 10 choices of evenly spaced cities to stop at along the way 
    #they can stop at 0, 1, or multiple; their choice
    next_dist = total_dist/10
  
    geodesic = pyproj.Geod(ellps='WGS84')
    #calculates the initial bearing (fwd_azimuth) and the final bearing 
    fwd_azimuth,back_azimuth,distance = geodesic.inv(start_city["longitude"], start_city["latitude"], end_city["longitude"], end_city["latitude"])
    final_bearing = back_azimuth - 180

    #Define the starting and ending points.
    start = geopy.Point(start_city["latitude"], start_city["longitude"])
    end = geopy.Point(end_city["latitude"], end_city["longitude"])

    #Define a general distance object, initialized with a distance of the stop distance (in km).
    d = geopy.distance.distance(kilometers=next_dist)

    #lists that will hold all the stops and the stops that the user chooses, respectively
    all_stops = []
    chosen_stops = []

    #define the geolocator
    geolocator = Nominatim(user_agent="Bing")

    #loop 10 times (for 10 stops)
    for i in range(10):
      # Use the destination method with our starting point and initial bearing
      # in order to go from our starting point to the next city in the line of stops.
      #finds the next point from the starting point given the bearing
      #if we are closer to the start, use our initial bearing; otherwise, use the final bearing
      if(i < 5):
        final = d.destination(point=start, bearing=fwd_azimuth)
      else:
        final = d.destination(point=start, bearing=final_bearing)
       
      #finds the location 
      location = geolocator.reverse(str(final))
      print(str(i) + ": " + str(location))
      #add it to the list of all stops
      all_stops.append({"location":str(location),"coord":final})
      #reset the next starting point
      start = final

    #add the starting location to the chosen stops
    chosen_stops.append({"location": start_city["city"], "coord": start})

    #get the user input for the stops they would like and store it in chosen_stops
    user_input = int(input("Please enter which stops you would like to take along the way." + 
    "If you are done entering stops, please enter '-1'. If you don't want to take any stops," +
    "enter -1 right away."))
    while(user_input != -1):
      chosen_stops.append(all_stops[user_input])
      user_input = int(input("Enter your next stop: "))

    #add the ending location to the chosen stops
    #chosen_stops is now a list of all stops including the start and end
    chosen_stops.append({"location": end_city["city"], "coord": end})
    
    for i in range(len(chosen_stops) - 1):
      #calculate the distance between each stop
      distance = calc_distance(chosen_stops[i]["coord"], chosen_stops[i + 1]["coord"])
      print("The distance between " + str(chosen_stops[i]["location"]) + " and " + 
      str(chosen_stops[i + 1]["location"]) + " is " + str(distance) + "km. ")
      dict_string = str(chosen_stops[i]["location"]) + " to " + str(chosen_stops[i+1]["location"])
      print(dict_string)
      #set up the dictionary and append it to the list
      entry = {"location": dict_string, "distance" : distance}
      stop_info.append(entry)

    #loop through every stop 
    for i in range(len(stop_info)):
      #now that we know the distance, we can calculate the time needed to travel
      #between each stop with each mode of transportation
      distance = stop_info[i]["distance"]
      drive_time = calc_time(distance, "drive")
      transit_time = calc_time(distance, "transit")
      plane_time = calc_time(distance, "plane")
      travel = determine_travel_modes(drive_time, transit_time, plane_time)
      #add a new key, the dictionary of available travel modes, to the list
      stop_info[i]["travel"] = travel

    for i in range(len(stop_info)):
      print(str(stop_info[i]))

    #set up the solver
    T = example_theory()

    #determine if the travel is international or not and set the appropriate constraint
    border = get_international(start_country, end_country)
    if(border):
      T.add_constraint(international)
      print("This trip is international...")
    else:
      T.add_constraint(~international)
      print("This trip is not international...")




    print("\nSatisfiable: %s" % T.is_satisfiable())
    print("# Solutions: %d" % T.count_solutions())
    print("   Solution: %s" % T.solve())
    """
    print("\nVariable likelihoods:")
    for v,vn in zip([a,b,c,x,y,z], 'abcxyz'):
        print(" %s: %.2f" % (vn, T.likelihood(v)))
    print()
    """