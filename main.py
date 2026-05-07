# Student ID: 011877111

import csv
import datetime

# Hash Table
class HashTable:
    def __init__(self, capacity=40):
        # initialize the table w/ empty bucket lists
        self.capacity = capacity
        self.table = [[] for _ in range(self.capacity)]

    def _hash(self, key):
        return int(key) % self.capacity

    def insert(self, package_id, package):
        index = self._hash(package_id)
        bucket = self.table[index]
        for i, (k, v) in enumerate(bucket):
            if k == package_id:
                bucket[i] = (package_id, package)
                return
        bucket.append((package_id, package))

    #need to def lookup

# Package


# Truck


# Load Distances


# Load Packages


# Distance Lookup


