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
roadwork = {}
accident = {}
toll = {}
"""
drive = {}
transit = {}
plane = {}




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
    entry["province/state"] = province
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
    for x in canada:
        print (x)
        for y in canada[x]:
            print (y,':',canada[x][y])
    coord1 = (52.2296756, 21.0122287)
    coord2 = (52.406374, 16.9251681)"""

def raw_location_input(canada_cities, america_cities):
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
    duplicates_start = []
    duplicates_end = []

    raw_start_city = raw_location["starting city"]
    raw_start_country = raw_location["starting country"]
    raw_end_city = raw_location["ending city"]
    raw_end_country = raw_location["ending country"]

    if(raw_start_country == "canada"):
      for entry in canada:
        if(entry["city"].lower() == raw_start_city):
          duplicates_start.append(entry)
    else:
      for entry in america:
        if(entry["city"].lower() == raw_start_city):
          duplicates_start.append(entry)
    if(raw_end_country == "united states"):
      for entry in america:
        if(entry["city"].lower() == raw_end_city):
          duplicates_end.append(entry)
    else:
      for entry in canada:
        if(entry["city"].lower() == raw_end_city):
          duplicates_end.append(entry)

    if(len(duplicates_start) == 1):
      start_city = duplicates_start[0]
    else:
      print("Please enter the number beside the starting city you are referring to.") 
      for i in range(len(duplicates_start)):
        print(i)
        for value in duplicates_start[i].values():
          print(value)
        print("\n")
      choice = int(input("Enter your choice:"))
      start_city = duplicates_start[choice]

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



def get_international(start_city, end_city, canada_cities, america_cities):
    # checking if the trip is international or not (from Canada to USA and vice versa)
    if((start_city in canada_cities and end_city in america_cities) or (start_city in america_cities and end_city in canada_cities)):
      border = True
    else:
      border = False

    return border

def calc_time(distance, mode):
    if(mode == "drive"):
      speed = 80.0
    elif(mode == "transit"):
      speed = 200.0
    elif(mode == "plane"):
      speed = 850.0
    return distance / speed

def determine_travel_modes(drive_time, transit_time, plane_time):
    travel = {}
    if(drive_time < 24):
        travel["drive"] = drive_time
    if(transit_time < 10):
        travel["transit"] = transit_time
    if(plane_time > 2):
        travel["plane"] = plane_time
    return travel




if __name__ == "__main__":
    canada = read_files("canada", "Canada Cities.csv")
    america = read_files("america", "US Cities.csv")

    # create a list for canadian and american cities
    canada_cities = []
    america_cities = []
    for entry in canada:
      canada_cities.append(entry["city"].lower())
    for entry in america:
      america_cities.append(entry["city"].lower())    
    T = example_theory()

    raw_location = raw_location_input(canada_cities,america_cities)
    start_city, end_city = clarify_duplicates(canada, america, raw_location)
    start_country = raw_location["starting country"]
    end_country = raw_location["ending country"]

    border = get_international(start_city, end_city, canada_cities, america_cities)
    if(border):
      T.add_constraint(international)
      print("here")
    else:
      T.add_constraint(~international)
  
    start_coord = (start_city["latitude"], start_city["longitude"])
    end_coord = (end_city["latitude"], end_city["longitude"])
    total_dist = calc_distance(start_coord, end_coord)

    print("A trip from " + start_city["city"] + ", " + start_city["province/state"] + " to " + end_city["city"]
     + ", " + end_city["province/state"] + " is " + str(total_dist)+ " km long.")

    next_dist = total_dist/10
  
    geodesic = pyproj.Geod(ellps='WGS84')
    #calculates the initial bearing (fwd_azimuth)
    fwd_azimuth,back_azimuth,distance = geodesic.inv(start_city["longitude"], start_city["latitude"], end_city["longitude"], end_city["latitude"])
    final_bearing = back_azimuth - 180

    # Define starting point.
    start = geopy.Point(start_city["latitude"], start_city["longitude"])
    end = geopy.Point(end_city["latitude"], end_city["longitude"])

    # Define a general distance object, initialized with a distance of 1 km.
    d = geopy.distance.distance(kilometers=next_dist)

    all_stops = []
    chosen_stops = []

    #define the geolocator
    geolocator = Nominatim(user_agent="Bing")

    #add the starting location to the chosen stops
    chosen_stops.append({"location": start_city["city"], "coord": start})
    for i in range(10):
      # Use the `destination` method with a bearing of 0 degrees (which is north)
      # in order to go from point `start` 1 km to north.
      #finds the next point from the starting point given the bearing
      if(i < 5):
        final = d.destination(point=start, bearing=fwd_azimuth)
      else:
        final = d.destination(point=start, bearing=final_bearing)
       
      #finds the location
      location = geolocator.reverse(str(final))
      print(str(i) + ": " + str(location))
      all_stops.append({"location":str(location),"coord":final})
      start = final

    user_input = int(input("Please enter which stops you would like to take along the way." + 
    "If you are done entering stops, please enter '-1'. If you don't want to take any stops," +
    "enter -1 right away."))
    while(user_input != -1):
      chosen_stops.append(all_stops[user_input])
      user_input = int(input("Enter your next stop: "))

    #add the ending location to the chosen stops
    chosen_stops.append({"location": end_city["city"], "coord": end})

    for element in chosen_stops:
      print(element)
    print()

    stop_distance = []
    for i in range(len(chosen_stops) - 1):
      distance = calc_distance(chosen_stops[i]["coord"], chosen_stops[i + 1]["coord"])
      print("The distance between " + str(chosen_stops[i]["location"]) + " and " + 
      str(chosen_stops[i + 1]["location"]) + " is " + str(distance) + "km. ")

      dict_string = str(chosen_stops[i]["location"]) + " to " + str(chosen_stops[i+1]["location"])
      print(dict_string)
      entry = {"location": dict_string, "distance" : distance}
      stop_distance.append(entry)

    for i in range(len(stop_distance)):
      drive[stop_distance[i]["location"]] = Var('drive' + str(i))
      transit[stop_distance[i]["location"]] = Var('transit' + str(i))
      plane[stop_distance[i]["location"]] = Var('plane' + str(i))
      
      distance = stop_distance[i]["distance"]
      drive_time = calc_time(distance, "drive")
      transit_time = calc_time(distance, "transit")
      plane_time = calc_time(distance, "plane")
      travel = determine_travel_modes(drive_time, transit_time, plane_time)
      stop_distance[i]["travel"] = travel

    for i in range(len(stop_distance)):
      print(str(stop_distance[i]))

    for entry in stop_distance:
      print(entry["travel"].keys())
      if "drive" in entry["travel"].keys():
        T.add_constraint(drive[entry["location"]])
      else:
        T.add_constraint(~drive[entry["location"]])
      if "transit" in entry["travel"].keys():
        T.add_constraint(transit[entry["location"]])
      else:
        T.add_constraint(~transit[entry["location"]])
      if "plane" in entry["travel"].keys():
        T.add_constraint(plane[entry["location"]])
      else:
        T.add_constraint(~plane[entry["location"]])
      


        
    

    
    print("\nSatisfiable: %s" % T.is_satisfiable())
    print("# Solutions: %d" % T.count_solutions())
    print("   Solution: %s" % T.solve())
    """
    print("\nVariable likelihoods:")
    for v,vn in zip([a,b,c,x,y,z], 'abcxyz'):
        print(" %s: %.2f" % (vn, T.likelihood(v)))
    print()
    """