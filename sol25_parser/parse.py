"""
********************************************************************************
*                                                                              *
* Název projektu:   Projekt do předmětu IPP 2024/2025 IFJ24:                   *
*                   Úloha 1 - Analyzátor kódu v SOL25 (parse.py)               *
*                                                                              *
* Soubor:           parse.py                                                   *
* Autor:            Jan Kalina <xkalinj00>                                     *
*                                                                              *
* Datum:            17.02.2025                                                 *
* Poslední změna:   xx.xx.2025                                                 *
*                                                                              *
********************************************************************************
"""
"""
@file parse.py
@author Jan Kalina \<xkalinj00>

@brief Hlavní skript 1. úlohy 'Analyzátor kódu v SOL25 (parse.py)' projektu
       do předmětu IPP.
@details Tento skript slouží jako hlqvní skript analyzátoru kódu v SOL25.
         Jde o tzv. vstupní bod  (resp. funkci `main()`). Tento skript slouží k
         zpracování parametrů příkazové řádky (pomocí `argparse`), načtení
         analyzovaného zdrojového kódu ze STDIN a následnému vytvoření třídy
         tzv. fasády tvořící rozhraní celého analyzátoru (viz dokumentace).
"""

from sys import exit, stdin, stderr  # exit(), stdin.read(), stderr
from MyPyModules import CustomErrors as err
from MyPyModules.ArgumentParser import ArgumentParser
from MyPyModules.LarkParser import LarkParser
from MyPyModules.SemanticAnalyser import SemanticAnalyser

class Facade:
    def __init__(self, SOL25Code):
        self._code = SOL25Code
        self._parser = LarkParser()
        self._checker = SemanticAnalyser()

    def run_analysis(self):
        ASTRoot = self._parser.parse(self._code)
        self._checker.analyse(ASTRoot)
        return ASTRoot

def main():
    try:
        # Instanciace parseru argumentů
        argParser = ArgumentParser()
        args = None

        # Zpracování argumentů příkazové řádky
        try:
            args = argParser.parse()
        except SystemExit as e:
            if e.code != 0:
                raise err.ArgumentError()

        if args:
            exit(err.ExitCode.SUCCESS.value)

        # Načteme zdrojový kód SOL25 ze STDIN
        try:
            SOL25Code = stdin.read()
            if not SOL25Code:
                raise err.InputFileError()
        except OSError:
            raise err.InputFileError()

        # Vytvoříme fasádu analýzy zrojového kódu SOL25
        facade = Facade(SOL25Code)

        # Provedeme analýzu zrojového kódu SOL25
        try:
            ASTroot = facade.run_analysis()
        except err.LexicalError as e:
            e.handle()
        except err.SyntaxError as e:
            e.handle()
        except err.SemanticMainRunError as e:
            e.handle()
        except err.UndefinedSymbolError as e:
            e.handle()
        except err.ArityError as e:
            e.handle()
        except err.VariableCollisionError as e:
            e.handle()
        except Exception as e:
            print(f"{e.message}", file=stderr)
            exit(err.InternalError.errorCode)

    except err.ArgumentError as e:
        e.handle()
    except err.InputFileError as e:
        e.handle()
    except err.OutputFileError as e:
        e.handle()
    except err.InternalError as e:
        e.handle()
    except Exception as e:
        print(f"{e.message}", file=stderr)
        exit(err.InternalError.errorCode)

    exit(err.ExitCode.SUCCESS.value)


if __name__ == "__main__":
    main()

### konec souboru 'parse.py' ###
