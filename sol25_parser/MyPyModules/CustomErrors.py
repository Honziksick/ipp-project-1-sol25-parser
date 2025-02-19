"""
********************************************************************************
*                                                                              *
* Název projektu:   Projekt do předmětu IPP 2024/2025 IFJ24:                   *
*                   Úloha 1 - Analyzátor kódu v SOL25 (parse.py)               *
*                                                                              *
* Soubor:           CustomErrors.py                                            *
* Autor:            Jan Kalina <xkalinj00>                                     *
*                                                                              *
* Datum:            17.02.2025                                                 *
* Poslední změna:   xx.xx.2025                                                 *
*                                                                              *
********************************************************************************
"""
"""
@file ustomErrors.py
@author Jan Kalina \<xkalinj00>

@brief
@details
"""

from enum import Enum

class ExitCode(Enum):
    SUCCESS = 0
    ARGUMENT_ERROR = 10
    INPUT_FILE_ERROR = 11
    OUTPUT_FILE_ERROR = 12
    LEXICAL_ERROR = 21
    SYNTAX_ERROR = 22
    SEMANTIC_MAIN_RUN_ERROR = 31
    UNDEFINED_SYMBOL_ERROR = 32
    ARITY_ERROR = 33
    VARIABLE_COLLISION_ERROR = 34
    INTERNAL_ERROR = 99

class CustomError(Exception):
    errorCode = None
    errorMessage = None

    def __init__(self):
        super().__init__(f"Error {self.errorCode}: {self.errorMessage}")

    def handle(self, exitProgram: bool = True):
        import sys  # exit

        print(f"Error {self.errorCode}: {self.errorMessage}", file=sys.stderr)
        if exitProgram:
            sys.exit(self.errorCode)

# Definice specifických výjimek
class ArgumentError(CustomError):
    errorCode = ExitCode.ARGUMENT_ERROR.value
    errorMessage = "Chybějící parametr skriptu (je-li třeba) nebo použití zakázané kombinace parametrů."

class InputFileError(CustomError):
    errorCode = ExitCode.INPUT_FILE_ERROR.value
    errorMessage = "Chyba při otevírání vstupních souborů (např. neexistence, nedostatečné oprávnění)."

class OutputFileError(CustomError):
    errorCode = ExitCode.OUTPUT_FILE_ERROR.value
    errorMessage = "Chyba při otevření výstupních souborů pro zápis (např. nedostatečné oprávnění, chyba při zápisu)."

class LexicalError(CustomError):
    errorCode = ExitCode.LEXICAL_ERROR.value
    errorMessage = "Lexikální chyba ve zdrojovém kódu v SOL25."

class SyntaxError(CustomError):
    errorCode = ExitCode.SYNTAX_ERROR.value
    errorMessage = "Syntaktická chyba ve zdrojovém kódu v SOL25."

class SemanticMainRunError(CustomError):
    errorCode = ExitCode.SEMANTIC_MAIN_RUN_ERROR.value
    errorMessage = "Sémantická chyba - chybějící třída 'Main' či její instanční metoda 'run'\n"

class UndefinedSymbolError(CustomError):
    errorCode = ExitCode.UNDEFINED_SYMBOL_ERROR.value
    errorMessage = "Sémantická chyba - použití nedefinované (a tedy i neinicializované) proměnné, formálního parametru, třídy, nebo třídní metody."

class ArityError(CustomError):
    errorCode = ExitCode.ARITY_ERROR.value
    errorMessage = "Sémantická chyba - chybná arita (špatná arita bloku přiřazeného k selektoru při definici instanční metody)."

class VariableCollisionError(CustomError):
    errorCode = ExitCode.VARIABLE_COLLISION_ERROR.value
    errorMessage = "Sémantická chyba - kolizní proměnná (lokální proměnná koliduje s formálním parametrem bloku)."

class InternalError(CustomError):
    errorCode = ExitCode.INTERNAL_ERROR.value
    errorMessage = "Interní chyba (neovlivněná integrací, vstupními soubory či parametry příkazové řádky)."

### konec souboru 'CustomErrors.py' ###
