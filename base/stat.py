import os

statinfo = os.stat("backends.py")
print(statinfo.st_size)
statinfo = os.stat("views.py")
size = statinfo.st_size/1000
print(f"Size of 'views.py' is {size} KB")