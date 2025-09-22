"""
********************************************************************************
* Název projektu:   Projekt do předmětu IPP 2024/2025:                         *
*                   Úloha 1 - Analyzátor kódu v SOL25 (parse.py)               *
*                                                                              *
* Soubor:           ArgumentParser.py                                          *
* Autor:            Jan Kalina <xkalinj00>                                     *
*                                                                              *
* Datum:            17.02.2025                                                 *
* Poslední změna:   10.03.2025                                                 *
*                                                                              *
* Popis:            Tento soubor obsahuje třídu ArgumentParser, která          *
*                   zpracovává argumenty příkazové řádky pro skript            *
*                   `parse.py`.                                                *
********************************************************************************
"""

# Import modulů standardní knihovny
from sys import argv

# Import modulů instalovaných pomocí 'pip'
import argparse

# Import vlastních modulů
from MyPyModules.CustomErrors import ScriptParameterError, ParsingSuccess

# Zdroj (manuál): https://docs.python.org/3/library/argparse.html
class ArgumentParser:
    """
    Třída `ArgumentParser` zpracovává argumenty příkazové řádky pro skript
    `parse.py`.

    Atributy:
        - parser (argparse.ArgumentParser): Instance parseru pro zpracování argumentů.

    Metody:
        - __init__(): Inicializuje parser s definovanými argumenty.
        - parser_result(): Zpracovává a vrací výsledky parsování argumentů.
        - parse_arguments(): Zpracovává argumenty příkazové řádky.
    """
    def __init__(self):
        """
        Inicializuje parser s definovanými argumenty příkazové řádky.
        """
        self.parser = argparse.ArgumentParser(
            formatter_class = argparse.RawTextHelpFormatter,
            add_help = False,
            allow_abbrev = False,
            usage = "python3.11 %(prog)s [-h | --help]",
            description = "This filter-type script (written in Python 3.11) reads SOL25 source code \n"
                          "from the standard input (STDIN), checks the lexical, syntactic, and static \n"
                          "semantic correctness of the code, and prints the XML representation of the \n"
                          "abstract syntax tree of the program to the standard output (STDOUT).\n",
            epilog = "return codes:\n"
                     "  0  - successful script termination\n"
                     "  10 - missing script parameter (if required) or use of a forbidden parameter \n"
                     "       combination\n"
                     "  11 - error opening input files (exception.g. non-existent, insufficient permissions)\n"
                     "  12 - error opening output files for writing (exception.g. insufficient permissions, \n"
                     "       writing error)\n"
                     "  21 - lexical error in SOL25 source code\n"
                     "  22 - syntactic error in SOL25 source code\n"
                     "  31 - semantic error: missing 'Main' class or its instance method 'run'\n"
                     "  32 - semantic error: use of an undefined (and thus uninitialized) variable, \n"
                     "       formal parameter, class, or class method\n"
                     "  33 - semantic error: incorrect arity (bad blockNode arity assigned to a selector \n"
                     "       during instance method definition)\n"
                     "  34 - semantic error: variable collision (local variable colliding with a formal \n"
                     "       parameter of the blockNode)\n"
                     "  99 - internal error (not influenced by integration, input files, or command-line \n"
                     "       parameters)\n",
            )

        # Přidání argumentu pro nápovědu
        self.parser.add_argument(
            "-h", "--help",
            action = 'store_true',
            help = "Prints the script help to STDOUT (does not read any input) and returns exit code 0. \n"
                   "This parameter cannot be combined with any other parameters, otherwise the script exits \n"
                   "with error 10."
            )

    def parser_result(self) -> bool:
        """
        Zpracovává a vrací výsledky parsování argumentů.

        Návratová hodnota:
            - bool: True, pokud se tiskne nápověda (help), jinak False.
        """
        args = self.parser.parse_args()

        # argv[0] je název skriptu, argv[1] je první argument
        if len(argv) > 2:
            raise ScriptParameterError()

        if args.help:
            self.parser.print_help()
        return args.help

    def parse_arguments(self):
        """
        Zpracovává argumenty příkazové řádky a vyvolává výjimky při chybách.

        Výjimky:
            - ScriptParameterError: Pokud dojde k chybě při zpracování argumentů.
            - ParsingSuccess: Pokud se tiskne nápověda (help).
        """
        # True, pokud se tiskne nápověda (help), jinak False
        shouldExit = False

        # Zpracování argumentů příkazové řádky
        try:
            shouldExit = self.parser_result()
        except SystemExit as e:
            if e.code != 0:
                raise ScriptParameterError()
        if shouldExit:
            raise ParsingSuccess()

### konec souboru 'ArgumentParser.py' ###
