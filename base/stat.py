import os

statinfo = os.stat("modelform.py")
print(statinfo.st_size)
statinfo = os.stat("views.py")
print(statinfo.st_size)