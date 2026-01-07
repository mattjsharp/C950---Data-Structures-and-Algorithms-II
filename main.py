# Matthew Sharp 008211210
import os
import csv
import datetime
from HashTable import HashTable

num_trucks = 3
num_drivers = 2

max_packages = 16
truck_speed = 18

packages = HashTable()
addresses = HashTable()
trucks = HashTable()
drivers = HashTable()
debug_log = []

'''
    Loads packages onto a specified truck.

    Appends a list of of packages IDs and appends them to the to the specified truck.
    Accepts a string an optional that represents the time to see advance the time of the specified truck
    and checks if the action can be performed based on the status of the specified truck.

    O(N) time complexity.
'''
def load_packages(truck, package_list, time=None):
    if time == None: # If no time is provided, the current time is used
        time = truck.lookup('return_time')
    else:
        time = get_time(time)

        if time < truck.lookup('return_time'): # If the time is before the truck is scheduled to return, the function is aborted
            truck.lookup('log_event')(f'# Truck is currently on route and cannot be loaded.', time)
            return
        
    truck.replace('return_time', time)
        
    for item in package_list:
        if len(truck.lookup('packages')) >= max_packages: # Checking if the truck is full
            truck.lookup('log_event')(f'# Truck is full, no more packages can be loaded.', time)
            return
        
        package = packages.lookup(item)

        if package == None: # Checking if the package exists
            truck.lookup('log_event')(f'# Package {item} does not exist.', time)
            continue

        if package.lookup('loaded_time'): # Checking if package is already loaded onto a truck
            truck.lookup('log_event')(f'# Package {item} is already loaded onto Truck #{package.lookup("truck").lookup("id")} at {format_time(package.lookup("loaded_time"))}.', time)
            package.lookup('log_event')(f'# Cannot be loaded onto Truck #{truck.lookup("id")} as it is already loaded on to Truck #{package.lookup("truck").lookup("id")} since {format_time(package.lookup("loaded_time"))}.', time)
            continue

        truck.lookup('packages').append(package)
        package.replace('loaded_time', True)
        truck.lookup('log_event')(f'- Package {item} loaded.', time)
        package.lookup('log_event')(f'- Loaded onto Truck #{truck.lookup('id')}.', time)
        package.replace('loaded_time', time)
        package.replace('truck', truck)


'''
    Returns the address HastTable object associated with a provided address string as the key.

    O(N) time complexity.
'''
def get_address(address_str):
    for address in addresses:
        if address.lookup('address') == address_str:
            return address

'''
    Returns the distance(float) between 2 address specified address objects.

    O(1) time complexity
'''  
def get_distance(address1, address2):
    return address1.lookup('distances')[address2.lookup('id')]

'''
    Generates a route for the provided truck based off of the packages in the 'packages' list property.
    Accepts a string an optional that represents the time to see advance the time of the specified truck
    and checks if the action can be performed based on the status of the specified truck.

    O(N^2) time complexity.
'''
def generate_route(truck, time=None):
    if time == None: # If no time is provided, the current time is used
        time = truck.lookup('return_time')
    else:
        time = get_time(time)

        if time < truck.lookup('return_time'): # If the time is before the truck is scheduled to return, the function is aborted
            truck.lookup('log_event')(f'# Route cannot be generated as Truck is on route.', time)
            return
    
    truck.replace('return_time', time)

    packages = truck.lookup('packages')
    route = truck.lookup('route')

    if len(packages) == 0:
        truck.lookup('log_event')(f'# Route cannot be generated as no packages are provided.', time)
        return

    to_route = HashTable(len(packages))
    for package in packages:
        to_route.insert(package.lookup('id'), package)

    # Starting at WGUPS Hub
    current_location = addresses.lookup(0)
    destination = HashTable()
    destination_index = 1
    destination.insert('id', destination_index)
    destination.insert('address', addresses.lookup(0))
    destination.insert('package', None)
    destination.insert('arrival_time', None)

    destination_index += 1
    
    route.append(destination) # Adding the hub to the route

    while len(to_route):
        nearest_distance = float('inf')
        nearest_address = None
        for package in to_route:
            distance = get_distance(current_location, package.lookup('address'))
            if distance < nearest_distance: # Finding the nearest package address
                nearest_distance = distance
                nearest_address = package.lookup('address')
                next_delivery = package

        current_location = nearest_address # Updating the trucks current position

        destination = HashTable() # Creating a new destination hash table object
        destination.insert('id', destination_index)
        destination.insert('address', current_location)
        destination.insert('package', next_delivery)
        destination.insert('arrival_time', None)

        route.append(destination)
        
        destination_index += 1

        to_route.remove(next_delivery.lookup('id')) # Removing the package from the list of packages to be delivered

    destination = HashTable()
    destination.insert('id', destination_index)
    destination.insert('address', addresses.lookup(0))
    destination.insert('package', None)
    destination.insert('arrival_time', None)
    route.append(destination) # Add return to hub to the route

    truck.replace('packages', [])
    truck.lookup('log_event')(f'- Route generated.', time)

'''
    Sends a specified truck out on it's route provided in it's route property.
    Advances the internal time of the truck and empties out the 'route' list.
    Accepts a string an optional that represents the time to see advance the time of the specified truck
    and checks if the action can be performed based on the status of the specified truck.

    O(N) time complexity
'''
def depart(truck, time=None):
    if time == None: # If no time is provided, the current time is used
        time = truck.lookup('return_time')
    else:
        time = get_time(time)

        if time < truck.lookup('return_time'): # If the time is before the truck is scheduled to return, the function is aborted
            truck.lookup('log_event')(f'# Truck is currently on route and cannot depart.', time)
            return
    
    truck.replace('return_time', time)
    
    if len(truck.lookup('route')) == 0: # If the truck does not have a route generated, the function is aborted
        truck.lookup('log_event')(f'# Route has not been generated.', time)
        return

    route = truck.lookup('route')
    truck.lookup('log_event')(f'- Departed from hub.', time)

    for destination in route: # Updating the departed time for each package
        if destination.lookup('address').lookup('id') == 0: # Skip the hub
            continue
        package = destination.lookup('package')
        package.lookup('log_event')(f'- Departed from hub.', time)
        package.replace('departed_time', time)

    new_time = time
    for i in range(1, len(route)):
        current_location = route[i - 1].lookup('address') # Setting the current location to the previous destination
        destination = route[i].lookup('address') # Setting the destination to the next destination
        distance = get_distance(current_location, destination) # Getting the distance between the current location and the destination
        new_time += datetime.timedelta(hours=(distance / truck_speed)) # Updating the time based on the distance and speed
        truck.replace('milage', truck.lookup('milage') + distance) # Updating the truck's milage

        package = route[i].lookup('package') # Checking if package is late
        if package:
            package.replace('delivered_time', new_time)
            if package.lookup('deadline') < new_time:
                package.replace('late', True)
                package.lookup('log_event')(f'# Package delivered late.', new_time)
            else:
                package.lookup('log_event')(f'- Delivered.', new_time)

            truck.lookup('log_event')(f'{"#" if package.lookup("late") else "-"} Delivered package {package.lookup("id")}{" late" if package.lookup("late") else ""} to {package.lookup("address").lookup("address")}. (Milage : {truck.lookup("milage"):,.1f})', new_time)
    
    truck.replace('return_time', new_time)
    truck.replace('route', [])
    truck.lookup('log_event')(f'- Arrived back at hub. (Milage : {truck.lookup("milage"):,.1f})', new_time)

'''
    Returns a string based off of the time that is provided.

    O(1) time complexity
'''
def format_time(time, _24h=False):
    if _24h: # If 24 hour format flag is set, the time is returned in 24 hour format
        return time.time().strftime('%H:%M')
    
    return time.time().strftime('%I:%M %p')

'''
    Returns a datetime object based off of a provided string.
    Allows 24 hour time if the flag is set.

    O(1) time complexity
'''
def get_time(time_str):
    time = datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day, int(time_str.split(':')[0]), int(time_str.split(':')[1]), 0)
    return time

'''
    Assigns a secified driver to a specified truck.
    Accepts a string an optional that represents the time to see advance the time of the specified truck
    and checks if the action can be performed based on the status of the specified truck.

    O(1) time complexity
'''
def assign_driver(truck, driver, time=None):
    if time == None: # If no time is provided, the current time is used
        time = truck.lookup('return_time')
    else:
        time = get_time(time)

        if time < truck.lookup('return_time'): # If the time is before the truck is scheduled to return, the function is aborted
            truck.lookup('log_event')(f'# Truck is currently on route and cannot assin a driver.', time)
            return
    truck.replace('return_time', time)

    valid = True
    if truck.lookup('driver') != None or driver.lookup('assigned_truck') != None:
        truck.lookup('log_event')(f'# Driver {truck.lookup('driver').lookup('id')} already assigned to truck {truck.lookup('id')}.', time)
        valid = False

    if not valid:
        return
    
    truck.replace('driver', driver)
    driver.replace('assigned_truck', truck)

    truck.lookup('log_event')(f'- Driver {truck.lookup('driver').lookup('id')} assigned.', time)

'''
    Unassigns a driver from a specifed truck.
    Accepts a string an optional that represents the time to see advance the time of the specified truck
    and checks if the action can be performed based on the status of the specified truck.

    O(1) time complexity
'''
def unassign_driver(truck, time=None):
    if time == None: # If no time is provided, the current time is used
        time = truck.lookup('return_time')
    else:
        time = get_time(time)

        if time < truck.lookup('return_time'): # If the time is before the truck is scheduled to return, the function is aborted
            truck.lookup('log_event')(f'# Truck is currently on route and cannot unassign a driver.', time)
            return
    truck.replace('return_time', time)

    if truck.lookup('driver') == None: # If the truck does not have a driver assigned, the function is aborted
        truck.lookup('log_event')(f'# Truck does not have a driver assigned.', time)
        return
    
    driver_id = truck.lookup('driver').lookup('id')

    truck.lookup('driver').replace('assigned_truck', None)
    truck.replace('driver', None)

    truck.lookup('log_event')(f'- Driver {driver_id} unassigned.', time)

'''
    Adds a log entry to the a provided entity.

    O(1) time complexity.
'''
def log_event(entity, message, time):
    message_id = len(entity.lookup('event_log')) + 1
    new_message = HashTable()
    new_message.insert('id', message_id)
    new_message.insert('time', time)
    new_message.insert('message', message)
    entity.lookup('event_log').append(new_message)

'''
    Chages the address of a package specified by the id to an address specified by the id.
'''
def change_address(package_id, address_id, time):
    time = get_time(time)
    package = packages.lookup(package_id)
    address = addresses.lookup(address_id)

    if package == None: # If the package does not exist, the function is aborted
        return
    
    if address == None: # If the address does not exist, the function is aborted
        return
    
    package.lookup('reassignments')[time] = address # Appends new address to a list of reassignments
    package.lookup('log_event')(f'- Address updated to {address.lookup("address")}.', time)

'''
    Initializes the user interface for whomever is using the program

    Time complexity varies based off of the operation performed.
'''
def init_gui():
    # Clearing the console
    os.system('cls' if os.name == 'nt' else 'clear')
    print('*' * 80) # Only displays header on the first run
    print('*' + (' ' * 78) + '*')
    print('*' + (' ' * 78) + '*')
    print('*' + 'Western Governors University Parcel Delivery Service'.center(78) + '*')
    print('*' + (' ' * 78) + '*')
    print('*' + (' ' * 78) + '*')
    print('*' * 80)

    # Program Loop
    while True:
        print()
        print(f'Total milage driven: {sum([truck.lookup("milage") for truck in trucks]):,.1f} miles'.center(80))
        print()
        print('Select and option to view the status:')
        option = input('    1. Packages\n    2. Trucks\n* Enter anything else to exit *\n\n    Option: ').strip()
        print()

        match (option):
            case '1': # Package Statuses
                package_id = None
                package = None
                time = None

                os.system('cls' if os.name == 'nt' else 'clear')
                print()
                print('Select and option to view the status:')
                option = input('    1. One Package\n    2. All packages\n* Enter anything else to go back *\n\n    Option: ').strip()
                print()

                if option == '1':
                    valid_id = True
                    try: # Verifying the package ID. If invalid it autoselects option 2
                        package_id = int(input('Enter a package ID: ').strip())

                        package = packages.lookup(package_id)

                        if package == None:
                            valid_id = False

                    except:
                        valid_id = False
                        package_id = None
                    
                    if not valid_id:
                        print()
                        print('# Invalid package ID. Selecting option 2.')

                elif option == '2':
                    package_id = None
                else:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    continue

                try:
                    time = get_time(input('\nEnter a valid time (HH:MM) to the view status at a specific time or press enter to view the final status: ').strip())
                except:
                    time = get_time('23:59')

                os.system('cls' if os.name == 'nt' else 'clear')
                if package_id:
                    print()
                    print(f'Report for Package: {package_id} at {format_time(time)}.'.center(80))
                    print('-' * 80)
                    status = 'At the hub'

                    if package.lookup('delivered_time') and package.lookup('delivered_time') <= time:
                        status = f'Delivered at {format_time(package.lookup("delivered_time"))}'
                    elif package.lookup('departed_time') and package.lookup('departed_time') <= time:
                        status = f'En route since {format_time(package.lookup("departed_time"))}'
                    
                    print(f'    Status: {status}')
                    print(f'    ID: {package.lookup("id")}')
                    print(f'    Address:')
                    address = package.lookup('address')
                    reassignments = sorted(package.lookup('reassignments').keys()) # Checking to see if address was updated
                    if reassignments:
                        filtered_reassignments = [ assignment for assignment in reassignments if assignment <= time]
                        if filtered_reassignments:
                            address = package.lookup('reassignments')[filtered_reassignments[-1]] # Getting latest revison before current time
                        print(f'        {address.lookup("name")}\n        {address.lookup("address")}\n        {package.lookup("city")}, {package.lookup("state")} {package.lookup("zip")}')
                    print(f'    Deadline: {format_time(package.lookup("deadline"))}')
                    print(f'    Weight: {package.lookup('weight')}lbs')
                    if package.lookup('Notes') != '':
                        print(f'    Notes: {package.lookup("notes")}')
                    print(f'    Truck: {f'Truck #{package.lookup('truck').lookup('id')} at {format_time(package.lookup("loaded_time"))}' if package.lookup("loaded_time") <= time else "Not loaded onto a truck."}')
                    print()
                    print('Event Log:'.center(80))
                    print('-' * 80)
                    for event in package.lookup('event_log'):
                        if event.lookup('time') > time:
                            break
                        print(f'[{format_time(event.lookup("time"))}] {event.lookup("message")}')
                    print()
                    input('Press any key to continue: ').strip()
                    os.system('cls' if os.name == 'nt' else 'clear')
                else:
                    print()
                    print(f'Report for all packages at {format_time(time)}.'.center(80))
                    print('-' * 80)
                    for i in range(1, len(packages) + 1):
                        package = packages.lookup(i)
                        status = 'At the hub'

                        if package.lookup('delivered_time') and package.lookup('delivered_time') <= time:
                            status = f'Delivered at {format_time(package.lookup("delivered_time"))}'
                        elif package.lookup('departed_time') and package.lookup('departed_time') <= time:
                            status = f'En route since {format_time(package.lookup("departed_time"))}'
                    
                        print(f'    Status: {status}')
                        print(f'    ID: {package.lookup("id")}')
                        print(f'    Address:')
                        address = package.lookup('address')
                        reassignments = sorted(package.lookup('reassignments').keys()) # Checking to see if address was updated
                        if reassignments:
                            filtered_reassignments = [ assignment for assignment in reassignments if assignment <= time]
                            if filtered_reassignments:
                                address = package.lookup('reassignments')[filtered_reassignments[-1]] # Getting latest revison before current time
                        print(f'        {address.lookup("name")}\n        {address.lookup("address")}\n        {package.lookup("city")}, {package.lookup("state")} {package.lookup("zip")}')
                        print(f'    Deadline: {format_time(package.lookup("deadline"))}')
                        print(f'    Weight: {package.lookup('weight')}lbs')
                        if package.lookup('Notes') != '':
                            print(f'    Notes: {package.lookup("notes")}')
                        print(f'    Truck: {f'Truck #{package.lookup('truck').lookup('id')} at {format_time(package.lookup("loaded_time"))}' if package.lookup("loaded_time") <= time else "Not loaded onto a truck."}')
                        print()
                        print('-' * 80)
                        print()
                    input('Press any key to continue: ').strip()
                    os.system('cls' if os.name == 'nt' else 'clear')

            case '2': # Truck reports
                truck_id = None

                os.system('cls' if os.name == 'nt' else 'clear')
                print()
                print('Choose a truck to view the event log:')
                [print(f'    Truck: {truck.lookup("id")} - {truck.lookup("milage"):,.1f} miles') for truck in trucks]
                print('* Enter anyting else to go back *')
                print()
                option = input('    Option: ').strip()
                if option not in [ str(truck.lookup('id')) for truck in trucks ]:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    continue

                truck_id = int(option)

                truck = trucks.lookup(truck_id)

                os.system('cls' if os.name == 'nt' else 'clear')
                print()
                print(f'Truck #{truck.lookup("id")} Event Log:'.center(80))
                print('-' * 80)
                for event in truck.lookup('event_log'):
                    print(f'[{format_time(event.lookup('time'))}] {event.lookup('message')}')

                print()
                input('Press any key to continue: ').strip()
                os.system('cls' if os.name == 'nt' else 'clear')
            case _:
                print('Goodbye\n')
                break

# Program Start
if __name__ == '__main__':
        
    # Reading address data from the addresses.csv
    with open('addresses.csv', encoding='utf-8-sig') as file:
        reader = csv.reader(file)

        # Populating address hash table with address data
        for row in reader:
            new_address = HashTable()
            new_address.insert('id', int(row[0]))
            new_address.insert('name', row[1])
            new_address.insert('address', row[2])
            new_address.insert('get_distance', lambda address, base=new_address: get_distance(base, address))

            addresses.insert(new_address.lookup('id'), new_address)

    
    # Creating a distance matrix from the distances.csv
    with open('distances.csv', encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        matrix = []
        for row in reader:
            entry = []
            for item in row:
                if item == '':
                    entry.append(-1)
                else:
                    entry.append(float(item))
            matrix.append(entry)
    
        # Filling in the empty parts of the matrix
        for i in range(len(matrix)):
            for j in range(len(matrix) - 1, i, -1):
                matrix[i][j] = matrix[j][i]
            
            # Assigning each row of distances to its respective address
            addresses.lookup(i).insert('distances', matrix[i])

    # Reading package data from the packages.csv
    with open('packages.csv', encoding='utf-8-sig') as file:
        reader = csv.reader(file)

        # Populating packages hash table with package data
        for row in reader:
            new_package = HashTable()
            new_package.insert('id', int(row[0]))
            new_package.insert('address', get_address(row[1])) # Returns associated address hash table object
            new_package.insert('city', row[2])
            new_package.insert('state', row[3])
            new_package.insert('zip', row[4])
            if row[5] == 'EOD':
                hour = 23
                minute = 59
            else:
                hour = int(row[5].split(':')[0])
                minute = int(row[5].split(':')[1][:2])
                if row[5][-2:2] == 'PM':
                    hour += 12
            new_package.insert('deadline', datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day, hour, minute, 0))
            new_package.insert('weight', row[6])
            new_package.insert('notes', row[7])
            new_package.insert('event_log', [])
            new_package.insert('late', False)
            new_package.insert('loaded_time', None)
            new_package.insert('departed_time', None)
            new_package.insert('delivered_time', None)
            new_package.insert('truck', None)
            new_package.insert('reassignments', dict())
            new_package.insert('log_event', lambda message, time, package=new_package : log_event(package, message, time))
            new_package.insert('change_address', lambda address_id, time, package=new_package : change_address(package.lookup('id'), address_id, time))

            packages.insert(new_package.lookup('id'), new_package) # Inserting the package into the packages hash table
    
    # Creating trucks
    for i in range(1, num_trucks + 1):
        new_truck = HashTable()
        new_truck.insert('id', i)
        new_truck.insert('packages', [])
        new_truck.insert('driver', None)
        new_truck.insert('route', [])
        new_truck.insert('milage', 0)
        new_truck.insert('return_time', get_time('7:00'))
        new_truck.insert('event_log', [])
        new_truck.insert('load_packages', lambda packages, time=None, truck=new_truck: load_packages(truck, packages, time))
        new_truck.insert('assign_driver', lambda driver, time=None, truck=new_truck: assign_driver(truck, driver, time))
        new_truck.insert('unassign_driver', lambda time=None, truck=new_truck: unassign_driver(truck, time))
        new_truck.insert('generate_route', lambda time=None, truck=new_truck : generate_route(truck, time))
        new_truck.insert('depart', lambda time=None, truck=new_truck : depart(truck, time))
        new_truck.insert('log_event', lambda message, time, truck=new_truck : log_event(truck, message, time))

        trucks.insert(new_truck.lookup('id'), new_truck) # Inserting the truck into the trucks hash table

    # Creating drivers
    for i in range(1, num_drivers + 1):
        new_driver = HashTable()
        new_driver.insert('id', i)
        new_driver.insert('assigned_truck', None)

        drivers.insert(new_driver.lookup('id'), new_driver) # Inserting the driver into the drivers hash table

    # Making references for convenience
    truck_1 = trucks.lookup(1)
    truck_2 = trucks.lookup(2)
    truck_3 = trucks.lookup(3)
    driver_1 = drivers.lookup(1)
    driver_2 = drivers.lookup(2)

# Events

    # Assigning drivers to trucks
    truck_1.lookup('assign_driver')(driver_1)
    truck_3.lookup('assign_driver')(driver_2)

    ''' Package Notes:
    -- Packages 3, 18, 36, 38 have to be on truck 2.
    -- Packages 13, 14, 15, 16, 20 have to be on to be delivered together.
    -- The delivery address for package #9, Third District Juvenile Court, is wrong and will be corrected at 10:20 a.m. 
        WGUPS is aware that the address is incorrect and will be updated at 10:20 a.m. However, WGUPS does not know the correct address (410 S. State St., Salt Lake City, UT 84111) until 10:20 a.m.
    -- Packages 6, 25, 28, 32 delayed on flight until 9:05 a.m.
    '''

    ''' Package Deadlines:
    -- Packages 1, 6, 13, 14, 16, 20, 25, 29, 30, 31, 34, 37, 40 have deadlines of 10:30 a.m.
    -- Packages 15 has a deadline of 9:00 a.m.
    '''


    truck_1.lookup('load_packages')([1,13,14,15,16,19,20,29,30,31,34,37,40])
    truck_1.lookup('generate_route')()
    truck_1.lookup('depart')('8:00') # Departing at the earliest time possible
    truck_1.lookup('unassign_driver')() # Unassigning the driver from the truck

    packages.lookup(9).lookup('change_address')(19, '10:20') # Changing the address of package 9 to the correct address at 10:20 a.m.

    truck_2.lookup('assign_driver')(driver_1, format_time(truck_1.lookup('return_time'), True)) # Assigning driver 1 to truck 2 as soon as they return
    truck_2.lookup('load_packages')([2,3,4,5,7,8,9,18,26,28,32,35,36,38], '10:30') # All packages have no deadline
    truck_2.lookup('generate_route')()
    truck_2.lookup('depart')()

    truck_3.lookup('load_packages')([6,10,11,12,17,21,22,23,24,25,27,33,39], '9:05') # Loading packages 6, 25, 28, 32 at 9:05 as soon as they arrive
    truck_3.lookup('generate_route')()
    truck_3.lookup('depart')()

    init_gui() # Start the User Interface