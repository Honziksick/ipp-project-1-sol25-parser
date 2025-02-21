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

import sys  # exit(), stdin.read(), stderr
import re
from MyPyModules import CustomErrors as err
from MyPyModules.ArgumentParser import ArgumentParser
from MyPyModules.LarkParser import LarkParser
from MyPyModules.SemanticAnalyser import SemanticAnalyser
from MyPyModules.XMLGenerator import XMLGenerator

class Facade:
    def __init__(self, SOL25Code):
        self._code = SOL25Code
        self._parser = LarkParser()
        self._checker = SemanticAnalyser()
        self._generator = XMLGenerator()

    def run_analysis(self):
        try:
            ASTRoot = self._parser.parse_code(self._code)
        except:
            raise

        try:
            self._checker.analyse_semantic(ASTRoot)
        except:
            raise

        try:
            match = re.search(r'"(.*?)"', self._code, re.DOTALL)
            firstComment = match.group(0) if match else None
            XMLcode = self._generator.generate_XML(ASTRoot, firstComment)
        except:
            raise

        try:
            print(XMLcode)
        except:
            raise

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
            sys.exit(err.ExitCode.SUCCESS.value)

        # Načteme zdrojový kód SOL25 ze STDIN
        try:
            SOL25Code = sys.stdin.read()
            if not SOL25Code:
                raise err.InputFileError()
        except OSError:
            raise err.InputFileError()

        # Vytvoříme fasádu analýzy zrojového kódu SOL25
        facade = Facade(SOL25Code)

        # Provedeme analýzu zrojového kódu SOL25
        try:
            facade.run_analysis()
        except err.LexicalError as e:
            e.handle()
        except err.SyntaxError as e:
            e.handle()
        except err.SemanticMainRunError as e:
            e.handle()
        except err.SemanticUndefinedSymbolError as e:
            e.handle()
        except err.SemanticArityError as e:
            e.handle()
        except err.SemanticVariableCollisionError as e:
            e.handle()
        except Exception as e:
            print(str(e), file=sys.stderr)
            sys.exit(err.InternalError.errorCode)

    except err.ArgumentError as e:
        e.handle()
    except err.InputFileError as e:
        e.handle()
    except err.OutputFileError as e:
        e.handle()
    except err.InternalError as e:
        e.handle()
    except Exception as e:
        print(str(e), file=sys.stderr)
        sys.exit(err.InternalError.errorCode)

    sys.exit(err.ExitCode.SUCCESS.value)


if __name__ == "__main__":
    main()

### konec souboru 'parse.py' ###
