# Student ID: 011877111

import csv
import datetime

### Hash Table ###
class HashTable:
    #init table w/ empty bucket lists
    def __init__(self, capacity=40):
        self.capacity = capacity
        self.table = [[] for _ in range(self.capacity)]

    #hash function
    #maps package ID to bucket index
    def _hash(self, key):
        return int(key) % self.capacity

    #insert or update package in hash table w/ package ID as key
    def insert(self, package_id, package):
        index = self._hash(package_id)
        bucket = self.table[index]
        for i, (k, v) in enumerate(bucket):
            if k == package_id:
                bucket[i] = (package_id, package)
                return
        bucket.append((package_id, package))

    #need to def lookup
    def lookup(self, package_id):
        index = self._hash(package_id)
        bucket = self.table[index]
        for k, v in bucket:
            if k == package_id:
                return v
        return None

### Package ###
class Package:
    def __init__(self, id, address, city, state, zip_code, deadline, weight, notes):
        self.id = int(id)
        self.address = address.strip()
        self.city = city.strip()
        self.state = state.strip()
        self.zip_code = zip_code.strip()
        self.deadline = deadline.strip()
        self.weight = weight.strip()
        self.notes = notes.strip()
        self.status = "At Hub"          #initial status
        self.delivery_time = None       #set when delivered
        self.departure_time = None      #set after departure

    #return status based on check time
    def update_status(self, check_time):
        if self.departure_time and check_time < self.departure_time:
            return "At Hub"
        elif self.delivery_time and check_time >= self.delivery_time:
            return f"Delivered at {self.delivery_time.strftime('%I:%M %p')}"
        else:
            return "En Route"

    def __str__(self):
        return (f"Package {self.id:>2} | {self.address:<40} | Deadline: {self.deadline:<8} "
                f"| Weight: {self.weight:<4} | Status: {self.status}") ##Double check this aligns

### Truck ###
class Truck:
    def __init__(self, truck_id, departure_time):
        self.truck_id = truck_id
        self.packages = []                      #list of package ids for packages on current truck
        self.mileage = 0.0
        self.current_location = "HUB"
        self.time = departure_time
        self.departure_time = departure_time
        self.speed = 18                         #mph

### Load Distances ###
# Uses distance csv #
def load_distances(filepath):
    distances = {}
    with open(filepath) as f:
        reader = csv.reader(f)
        header = next(reader)
        addresses = header[1:]
        for row in reader:
            from_addr = row[0]
            if not from_addr.strip(): #skip empty rows
                continue
            for j, dist in enumerate(row[1:]):
                if dist.strip() == "": #skip empty cells
                    continue
                to_addr = addresses[j]
                distances[(from_addr, to_addr)] = float(dist)
                distances[(to_addr, from_addr)] = float(dist)
    return distances, addresses

### Load Packages ###
# Uses package csv #
def load_packages(filepath, hash_table):
    with open(filepath) as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or not row[0].strip():
                continue
            pkg = Package(
                id=row[0],
                address=row[1],
                city=row[2],
                state=row[3],
                zip_code=row[4],
                deadline=row[5],
                weight=row[6],
                notes=row[7] if len(row) > 7 else ""
            )
            hash_table.insert(pkg.id, pkg)

### Distance Lookup ###
# Tries direct lookup first (get_distance) #
# Tries a fuzzy match (best_match) if addresses don't exactly match #
def get_distance(addr1, addr2, distances, address_list):
    if (addr1, addr2) in distances:
        return distances[(addr1, addr2)]

    def best_match(target):
        target_clean = target.lower(). replace(",", "").replace(".", "").replace("#", "")
        best = None
        best_score = 0
        for a in address_list:
            a_clean = a.lower().replace(",", "").replace(".", "").replace("#", "")
            score = sum(word in a_clean for word in target_clean.split())
            if score > best_score:
                best_score = score
                best = a
        return best

    key1 = best_match(addr1)
    key2 = best_match(addr2)
    return distances.get((key1, key2), 0.0)

### Nearest Neighbor Routing ###
def deliver_packages(truck, hash_table, distances, address_list):
    undelivered = list(truck.packages)

    while undelivered:
        nearest_pkg_id = None
        nearest_dist = float('inf')

        for pkg_id in undelivered:
            pkg = hash_table.lookup(pkg_id)

            #Deal with package9 wrong address
            if pkg.id == 9:
                corrected_time = datetime.datetime(2000, 1, 1, 10, 20)
                if truck.time < corrected_time:
                    continue

            dist = get_distance(truck.current_location, pkg.address, distances, address_list)
            if dist < nearest_dist:
                nearest_dist = dist
                nearest_pkg_id = pkg_id

        #advance time if no valid packages found
        if nearest_pkg_id is None:
            truck.time = datetime.datetime(2000, 1, 1, 10, 20)
            continue

        #travel to selected package
        pkg = hash_table.lookup(nearest_pkg_id)
        travel_time = nearest_dist / truck.speed
        truck.time += datetime.timedelta(hours=travel_time)
        truck.mileage += nearest_dist
        truck.current_location = pkg.address

        #mark package as delivered
        pkg.status = f"Delivered at {truck.time.strftime('%I:%M %p')}"
        pkg.delivery_time = truck.time
        undelivered.remove(nearest_pkg_id)

    #retrns truck to hub after all deliveries
    hub_dist = get_distance(truck.current_location, "HUB", distances, address_list)
    truck.mileage += hub_dist
    truck.current_location = "HUB"

### Interface ###
# Displays status of all packages at a selected time #
def run_interface(hash_table, trucks):
    print("\n" + "="*60)
    print("   WGUPS PACKAGE DELIVERY STATUS INTERFACE")
    print("="*60)

    total_miles = sum(t.mileage for t in trucks)
    print(f"\nTotal mileage traveled by all trucks: {total_miles:.2f} miles")
    for t in trucks:
        print(f"  Truck {t.truck_id}: {t.mileage:.2f} miles")

    while True:
        print("\nOptions:")
        print("  1  -  Check status of all packages at a specific time")
        print("  2  -  Look up a single package by ID")
        print("  3  -  Exit")
        choice = input("Enter Choice: ").strip()

        if choice == "1":
            time_input = input("Enter time (e.g. 9:00 AM or 13:00): ").strip()
            try:
                try: #12 and 24-hour format
                    check_time = datetime.datetime.strptime(time_input, "%I:%M %p").replace(year=2000, month=1, day=1)
                except ValueError:
                    check_time = datetime.datetime.strptime(time_input, "%H:%M").replace(year=2000, month=1, day=1)

                print(f"\n{'='*60}")
                print(f"Package status at {check_time.strftime('%I:%M %p')}")
                print(f"{'='*60}")
                print(f"{'ID':<4} {'Address':<42} {'Deadline':<10} {'Weight':<7} {'Status'}")
                print("-"*100)

                for pkg_id in range(1, 41):
                    pkg = hash_table.lookup(pkg_id)
                    if pkg: #package 9
                        display_addr = pkg.address
                        if pkg.id == 9 and check_time < datetime.datetime(2000, 1, 1, 10, 20):
                            display_addr = "300 State St (address pending correction"
                        status = pkg.update_status(check_time)
                        print(f"{pkg.id:<4} {display_addr:<42} {pkg.deadline:<10} {pkg.weight:<7} {status}")

            except ValueError:
                print("Invalid time format. Try '9:00 AM' or '09:00'.")

        elif choice == "2":
             try:
                 pkg_id = int(input("Enter package ID (1 - 40): ").strip())
                 pkg = hash_table.lookup(pkg_id)
                 if pkg:
                     print(f"\nPackage {pkg.id}:")
                     print(f"   Address:   {pkg.address}, {pkg.city}, {pkg.state}, {pkg.zip_code}")
                     print(f"   Deadline:   {pkg.deadline}")
                     print(f"   Weight:   {pkg.weight} kg")
                     print(f"   Notes:   {pkg.notes if pkg.notes else 'None'}")
                     print(f"   Status:   {pkg.status}")
                 else:
                     print("Package not found.")
             except ValueError:
                     print("Please enter a valid numeric package ID.")

        elif choice == "3":
             print("Exiting. Goodbye")
             break
        else:
             print("Invalid choice.")

### Main ###
def main():
    #load distance table and package data
    distances, address_list = load_distances("distances.csv")
    hash_table = HashTable(capacity=40)
    load_packages("packages.csv", hash_table)

    #set departure times using fixed reference date
    t800 = datetime.datetime(2000, 1, 1, 8, 0)
    t905 = datetime.datetime(2000, 1, 1, 9, 5)

    #Truck 1 (departs at 8 AM)
    #prioritizes early deadlines and packages that need to be delivered together
    truck1 = Truck(1, t800)
    truck1.packages = [1, 13, 14, 15, 16, 19, 20, 29, 30, 31, 34, 37, 40]

    #Truck 2 (departs at 8 AM)
    #handles packages that can only go on truck 2
    truck2 = Truck(2, t800)
    truck2.packages = [3, 5, 8, 10, 18, 21, 26, 33, 35, 36, 38, 39]

    #Truck 3 (departs at 9:05 AM)
    #handles delayed packages that dont arrive until 9:05 AM
    truck3 = Truck(3, t905)
    truck3.packages = [2, 4, 6, 7, 9, 11, 12, 17, 22, 23, 24, 25, 27, 28, 32]

    #set departure time on each package
    all_trucks = [truck1, truck2, truck3]
    for truck in all_trucks:
        for pkg_id in truck.packages:
            pkg = hash_table.lookup((pkg_id))
            if pkg:
                pkg.departure_time = truck.departure_time

    #run nearest neighbor for each truck
    for truck in all_trucks:
        deliver_packages(truck, hash_table, distances, address_list)

    #print summary
    print("\nDelivery simulation complete.")
    total = sum(t.mileage for t in all_trucks)
    for truck in all_trucks:
        print(f"Truck {truck.truck_id} mileage: {truck.mileage:.2f} miles")
    print(f"Total mileage: {total:.2f} miles")

    #verify all deadlines are met
    print("\nDeadline check:")
    all_met = True
    for pkg_id in range(1,41):
        pkg = hash_table.lookup(pkg_id)
        if pkg and pkg.deadline != "EOD" and pkg.delivery_time:
            deadline_time = datetime.datetime.strptime(pkg.deadline, '%I:%M %p').replace(year=2000, month=1, day=1)
            if pkg.delivery_time > deadline_time:
                print(f"  MISSED: Package {pkg_id} delivered at {pkg.delivery_time.strftime('%I:%M %p')}, deadline was {pkg.deadline}")
                all_met = False
    if all_met:
        print("  All deadlines met.")

    #launch UI
    run_interface(hash_table, all_trucks)


if __name__ == '__main__':
    main()