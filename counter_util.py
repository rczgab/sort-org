#counter_util.py

class Counter:
    def __init__(self):
        self.cr = 0
        self.mr = 0

    def update(self):
        if self.cr > 999:
            self.mr += self.cr
            print(f"Feldolgozott fájlok száma: {self.mr}")
            self.cr = 1
        else:
            self.cr += 1

    def clear(self):
        self.cr = 0
        self.mr = 0

    def show(self):
        print(f"Elemszám: {self.mr + self.cr}")
