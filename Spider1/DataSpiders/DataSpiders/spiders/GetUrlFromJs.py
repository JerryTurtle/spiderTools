import os

pwd = os.getcwd()

path = os.path.join(os.path.abspath(os.path.dirname(pwd)+os.path.sep+".."),"DataSpiders","DatabaseConfig.ini")
print(path)