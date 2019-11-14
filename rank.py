

class rank:

    def __init__(self, size):
        self.size = size
        self.collect = []
        self.collect_t = []

    def collection(self):
        return self.collect

    def collection_t(self):
        return self.collect_t


    def insert(self, item, t):
        if len(self.collect)==0 or self.collect_t[-1]<=t:
            if len(self.collect)>= self.size:
                del self.collect[-1]
                del self.collect_t[-1]
            return self.__insert(item, t)
        return -1

    def __insert(self, item, t):
        for i in range(0, self.size):
            if len(self.collect)<=i or t>self.collect_t[i]:
                self.collect.insert(i, item)
                self.collect_t.insert(i, t)
                return i
                
