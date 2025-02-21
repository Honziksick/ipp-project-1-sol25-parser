import os
import sys

# Získání aktuálního adresáře (__init__.py je ve složce MyPyModules)
currentDirectory = os.path.dirname(os.path.abspath(__file__))
# Určení nadřazeného adresáře – tj. sol25_parser (adresář, který obsahuje složku MyPyModules)
rootDirectory = os.path.abspath(os.path.join(currentDirectory, ".."))

# Přidá rootDirectory na začátek sys.path, pokud tam již není
if rootDirectory not in sys.path:
    sys.path.insert(0, rootDirectory)
