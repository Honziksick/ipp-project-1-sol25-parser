"""
********************************************************************************
*                                                                              *
* Název projektu:   Projekt do předmětu IPP 2024/2025:                         *
*                   Úloha 1 - Analyzátor kódu v SOL25 (parse.py)               *
*                                                                              *
* Soubor:           __init__.py                                                *
* Autor:            Jan Kalina <xkalinj00>                                     *
*                                                                              *
* Datum:            17.02.2025                                                 *
* Poslední změna:   22.02.2025                                                 *
*                                                                              *
* Popis: Tento soubor inicializuje modul MyPyModules a nastavuje cestu         *
*        k nadřazenému adresáři, aby bylo možné importovat moduly z tohoto     *
*        adresáře.                                                             *
********************************************************************************
"""

# Import modulů standardní knihovny
import os
import sys

# Získání aktuálního adresáře (__init__.py je ve složce MyPyModules)
currentDirectory = os.path.dirname(os.path.abspath(__file__))

# Určení nadřazeného adresáře (ten obsahuje složku MyPyModules)
rootDirectory = os.path.abspath(os.path.join(currentDirectory, ".."))

# Přidá rootDirectory na začátek sys.path, pokud tam již není
if rootDirectory not in sys.path:
    sys.path.insert(0, rootDirectory)

### konec souboru '__init__.py' ###
