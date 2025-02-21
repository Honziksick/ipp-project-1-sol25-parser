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

from sys import exit, stderr
from enum import Enum

RED_COLOR   = "\033[91m"
GOLD_COLOR  = "\033[0;93m"
RESET_COLOR = "\033[0m"

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
    errorDetail = None

    def __init__(self, detail:str = None):
        message = f"{RED_COLOR}Error {self.errorCode}: {self.errorMessage}{RESET_COLOR}"
        if detail:
            self.errorDetail = detail
            message += f"\n{GOLD_COLOR}Detail: {detail}{RESET_COLOR}"
        super().__init__(message)

    def handle(self, exitProgram:bool = True):
        print(self, file=stderr)
        if exitProgram:
            exit(self.errorCode)

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

class SemanticUndefinedSymbolError(CustomError):
    errorCode = ExitCode.UNDEFINED_SYMBOL_ERROR.value
    errorMessage = "Sémantická chyba - použití nedefinované (a tedy i neinicializované) proměnné, formálního parametru, třídy, nebo třídní metody."

class SemanticArityError(CustomError):
    errorCode = ExitCode.ARITY_ERROR.value
    errorMessage = "Sémantická chyba - chybná arita (špatná arita bloku přiřazeného k selektoru při definici instanční metody)."

class SemanticVariableCollisionError(CustomError):
    errorCode = ExitCode.VARIABLE_COLLISION_ERROR.value
    errorMessage = "Sémantická chyba - kolizní proměnná (lokální proměnná koliduje s formálním parametrem bloku)."

class InternalError(CustomError):
    errorCode = ExitCode.INTERNAL_ERROR.value
    errorMessage = "Interní chyba (neovlivněná integrací, vstupními soubory či parametry příkazové řádky)."

### konec souboru 'CustomErrors.py' ###
