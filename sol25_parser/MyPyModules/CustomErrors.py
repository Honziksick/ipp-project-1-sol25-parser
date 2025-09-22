"""
********************************************************************************
* Název projektu:   Projekt do předmětu IPP 2024/2025:                         *
*                   Úloha 1 - Analyzátor kódu v SOL25 (parse.py)               *
*                                                                              *
* Soubor:           CustomErrors.py                                            *
* Autor:            Jan Kalina <xkalinj00>                                     *
*                                                                              *
* Datum:            17.02.2025                                                 *
* Poslední změna:   21.02.2025                                                 *
*                                                                              *
* Popis:            Tento soubor obsahuje definice vlastních výjimek pro       *
*                   analyzátor kódu v jazyce SOL25. Výjimky jsou definovány    *
*                   jako třídy odvozené od základní třídy `CustomError`, která *
*                   poskytuje základní strukturu pro chybové kódy, zprávy a    *
*                   detaily. Každá specifická výjimka má svůj vlastní chybový  *
*                   kód a zprávu, které jsou definovány pomocí výčtového typu  *
*                   `ExitCode`.                                                *
********************************************************************************
"""

# Import modulů standardní knihovny
from sys import exit, stderr
from enum import Enum

################################################################################
#                                                                              #
#                 OBECNÉ VÝJIMKY A JEJICH PARAMETRY (PRIVÁTNÍ)                 #
#                                                                              #
################################################################################

# Konstanty reprezentující ANSI escape sekvence barev
RED_COLOR = "\033[91m"  # červená
YELLOW_COLOR = "\033[0;93m"  # žlutá
RESET_COLOR = "\033[0m"  # resetování původní barvy


class ExitCode(Enum):
    """
    Výčtový datový typ reprezentující chybové návratové kódy.
    """
    SUCCESS = 0
    PARAMETER_ERROR = 10
    INPUT_FILE_ERROR = 11
    OUTPUT_FILE_ERROR = 12
    LEXICAL_ERROR = 21
    SYNTAX_ERROR = 22
    SEMANTIC_MAIN_RUN_ERROR = 31
    UNDEFINED_SYMBOL_ERROR = 32
    ARITY_ERROR = 33
    VARIABLE_COLLISION_ERROR = 34
    OTHER_SEMANTIC_ERROR = 35
    INTERNAL_ERROR = 99


class CustomError(Exception):
    """
    Základní třída pro vlastní specializované výjimky.

    Atributy:
        - errorCode (int):    Kód chyby (výchozí None).
        - errorMessage (str): Zpráva popisující chybu (výchozí None).
        - errorDetail (str):  Detailní popis chyby (výchozí None).

    Metody:
        - __init__(detail:str = None): Inicializuje výjimku s volitelným detailem.
        - handle(shouldExit:bool = True): Vytiskne chybovou hlášku a ukončí program.
    """
    errorCode = None
    errorMessage = None
    errorDetail = None

    def __init__(self, detail: str = None):
        """
        Inicializuje výjimku s volitelným detailem a formátuje chybovou hlášku.

        Parametry:
            - detail (str): Detailní popis chyby (výchozí None).
        """
        message = f"{RED_COLOR}Error {self.errorCode}: {self.errorMessage}{RESET_COLOR}"
        if detail:
            self.errorDetail = detail
            message += f"\n{YELLOW_COLOR}Detail: {detail}{RESET_COLOR}"
        super().__init__(message)

    def handle(self, shouldExit: bool = True):
        """
        Vytiskne na STDERR chybovou hlášku dané výjimky a ukončí program
        s chybovým návratovým kódem.

        Parametry:
            - shouldExit (bool): Určuje, zda ukončit program (výchozí True).
        """
        print(self, file = stderr)
        if shouldExit:
            exit(self.errorCode)


################################################################################
#                                                                              #
#                         SPECIFICKÉ VÝJIMKY (VEŘEJNÉ)                         #
#                                                                              #
################################################################################

def handle_exception(exception: Exception):
    """
    Na základě předané výjimky se rozhodne, zda bude zpracována jako specifická
    vlastní výjímka `CustomError` nebo jak obecná výjimka převedená na vlastní
    výjimku typu `InternalError`.

    Parametry:
        - exception (Exception): Výjimka ke zpracování.
    """
    if isinstance(exception, CustomError):
        exception.handle()
    else:
        print(str(exception), file = stderr)
        exit(InternalError.errorCode)


class ScriptParameterError(CustomError):
    """
    Výjimka pro chybné parametry skriptu.
    """
    errorCode = ExitCode.PARAMETER_ERROR.value
    errorMessage = ("Missing script parameter (if required) or use of a "
                    "prohibited combination of parameters.")


class InputFileError(CustomError):
    """
    Výjimka pro chyby při otevírání vstupních souborů.
    """
    errorCode = ExitCode.INPUT_FILE_ERROR.value
    errorMessage = ("Error opening input files (e.g., non-existence, "
                    "insufficient permissions).")


class OutputFileError(CustomError):
    """
    Výjimka pro chyby při otevírání výstupních souborů.
    """
    errorCode = ExitCode.OUTPUT_FILE_ERROR.value
    errorMessage = ("Error opening output files for writing (e.g., insufficient "
                    "permissions, write error).")


class LexicalError(CustomError):
    """
    Výjimka pro lexikální chyby ve zdrojovém kódu v SOL25.
    """
    errorCode = ExitCode.LEXICAL_ERROR.value
    errorMessage = "Lexical error in the SOL25 source code."


class SyntacticError(CustomError):
    """
    Výjimka pro syntaktické chyby ve zdrojovém kódu v SOL25.
    """
    errorCode = ExitCode.SYNTAX_ERROR.value
    errorMessage = "Syntactic error in the SOL25 source code."


class SemanticMainRunError(CustomError):
    """
    Výjimka pro sémantické chyby - chybějící třída 'Main' či metoda 'run'.
    """
    errorCode = ExitCode.SEMANTIC_MAIN_RUN_ERROR.value
    errorMessage = ("Semantic error - missing 'Main' class or its instance "
                    "method 'run'.")


class SemanticUndefinedSymbolError(CustomError):
    """
    Výjimka pro sémantické chyby - použití nedefinované proměnné, formálního
    parametru, třídy, nebo třídní metody.
    """
    errorCode = ExitCode.UNDEFINED_SYMBOL_ERROR.value
    errorMessage = ("Semantic error - use of undefined (and therefore "
                    "uninitialized) variable, formal parameter, class, or "
                    "class method.")


class SemanticArityError(CustomError):
    """
    Výjimka pro sémantické chyby - chybná arita bloku přiřazeného k selektoru
    při definici instanční metody.
    """
    errorCode = ExitCode.ARITY_ERROR.value
    errorMessage = ("Semantic error - incorrect arity (wrong arity of the block "
                    "assigned to the selector when defining an instance method).")


class SemanticVariableCollisionError(CustomError):
    """
    Výjimka pro sémantické chyby - kolizní proměnná (lokální proměnná
    koliduje s formálním parametrem bloku).
    """
    errorCode = ExitCode.VARIABLE_COLLISION_ERROR.value
    errorMessage = ("Semantic error - variable collision (local variable "
                    "collides with the formal parameter of the block).")


class SemanticOtherError(CustomError):
    """
    Výjimka pro sémantické chyby - ostatní sémantické chyby.
    """
    errorCode = ExitCode.OTHER_SEMANTIC_ERROR.value
    errorMessage = "Semantic error - other semantic errors."


class InternalError(CustomError):
    """
    Výjimka pro interní chyby (neovlivněné integrací, vstupními soubory
    či parametry příkazové řádky).
    """
    errorCode = ExitCode.INTERNAL_ERROR.value
    errorMessage = ("Internal error (not affected by integration, input files, "
                    "or command line parameters).")


class ParsingSuccess(CustomError):
    """
    Výjimka pro oznámená úspěšného ukončení parsování parametrů skriptu s nimiž
    je spojeno volání `exit()`.
    """
    errorCode = ExitCode.SUCCESS.value

    def handle(self, shouldExit: bool = True):
        """
        Ukončí program s chybovým návratovým kódem určeným pro úspěšné ukončení
        skriptu.
        """
        exit(self.errorCode)

### konec souboru 'CustomErrors.py' ###
