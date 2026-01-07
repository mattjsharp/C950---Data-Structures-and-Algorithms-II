class HashTable:
    
    # O(1)
    def __init__(self, size = 10): # Constructs a chaining hash table with a default size of 10
        self._bucket_list = [[] for i in range(size)] # Creates a list of buckets based off of the provided size

    # O(n)
    def __str__(self): # String representation of the hash table
        if self.is_empty():
            return '{}'
        val = '{\n'
        for bucket in self._bucket_list:
            if bucket:
                for item in bucket:
                    val += '    ' + (str(item) + ',\n')
        
        return val + '}'
    
    # O(n)
    def __iter__(self): # Allows for iteration over the hash table
        for bucket in self._bucket_list:
            if bucket:
                for item in bucket:
                    yield item.value

    # O(n)
    def insert(self, key, value): # Insert function
        self._get_bucket(key).append(self.Item(key, value))

    # O(n)
    def lookup(self, key): # Lookup function
        bucket = self._get_bucket(key)
        value = None
        for item in bucket:
            if item.key == key:
                value = item.value
                break
        return value

    # O(n)
    def replace(self, key, value): # Replacement function
        bucket = self._get_bucket(key)
        for item in bucket:
            if item.key == key:
                item.value = value

    # O(n)
    def remove(self, key): # Removal Function
        bucket = self._get_bucket(key)
        for i in range(len(bucket)):
            if bucket[i].key == key:
                bucket.pop(i)
                break
    
    # O(1)
    def is_empty(self): # Checks if the hash table is empty
        for i in self._bucket_list:
            if len(i) > 0:
                return False
        return True
    
    # O(1)
    def _get_bucket(self, key): # Private function for getting hash
        return self._bucket_list[hash(key) % len(self._bucket_list)]

    # O(1)
    def clear(self): # Clears the hash map
        self._bucket_list = [[] for i in range(len(self._bucket_list))]

    # O(1)
    def __len__(self): # Returns the number of items in the hash table.
        count = 0
        for bucket in self._bucket_list:
            count += len(bucket)
        return count
    
    # Internal Item Class
    class Item:
        # O(1)
        def __init__(self, key, value):
            self.key = key
            self.value = value

        # O(1)
        def __str__(self):
            return f'{self.key} : {self.value}'

# Test code   
if __name__ == '__main__':
    map = HashTable()
    
    map.insert('a', 1)
    map.insert('b', 2)
    map.replace('a', 4)
    map.insert('c', 3)
    print(map.lookup('a'))
    print(map.lookup('b'))
    print(map.lookup('c'))
    print(map)
    map.remove('a')
    print(map)
    print(map.lookup('a'))

    map.clear()
    print(map)
    print(map.is_empty())