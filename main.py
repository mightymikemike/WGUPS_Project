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


### Load Distances ###


### Load Packages ###


### Distance Lookup ###


