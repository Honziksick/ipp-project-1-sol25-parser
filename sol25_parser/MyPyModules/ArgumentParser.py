"""
********************************************************************************
*                                                                              *
* Název projektu:   Projekt do předmětu IPP 2024/2025 IFJ24:                   *
*                   Úloha 1 - Analyzátor kódu v SOL25 (parse.py)               *
*                                                                              *
* Soubor:           ArgumentParser.py                                          *
* Autor:            Jan Kalina <xkalinj00>                                     *
*                                                                              *
* Datum:            17.02.2025                                                 *
* Poslední změna:   xx.xx.2025                                                 *
*                                                                              *
********************************************************************************
"""
"""
@file ArgumentParser.py
@author Jan Kalina \<xkalinj00>

@brief
@details
"""

import argparse

class ArgumentParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            formatter_class=argparse.RawTextHelpFormatter,
            add_help=False,
            allow_abbrev=False,
            usage="python3.11 %(prog)s [-h | --help]",
            description="Skript typu filtr (v jazyce Python 3.11) načte ze "
                        "standardního vstupu (STDIN) zdrojový kód v jazyce SOL25, "
                        "zkontroluje lexikální, syntaktickou a statickou sémantickou "
                        "správnost kódu a vypíše na standardní výstup (STDOUT) XML "
                        "reprezentaci abstraktního syntaktického stromu programu.",
            epilog="return codes:\n"
                   "  0  - bezchybné ukončení skriptu\n"
                   "  10 - chybějící parametr skriptu (je-li třeba) nebo použití zakázané kombinace parametrů\n"
                   "  11 - chyba při otevírání vstupních souborů (např. neexistence, nedostatečné oprávnění)\n"
                   "  12 - chyba při otevření výstupních souborů pro zápis (např. nedostatečné oprávnění, chyba při zápisu)\n"
                   "  21 - lexikální chyba ve zdrojovém kódu v SOL25\n"
                   "  22 - syntaktická chyba ve zdrojovém kódu v SOL25\n"
                   "  31 - sémantická chyba: chybějící třída 'Main' či její instanční metoda 'run'\n"
                   "  32 - sémantická chyba: použití nedefinované (a tedy i neinicializované) proměnné, formálního parametru, třídy, nebo třídní metody\n"
                   "  33 - sémantická chyba: chybná arita (špatná arita bloku přiřazeného k selektoru při definici instanční metody)\n"
                   "  34 - sémantická chyba: kolizní proměnná (lokální proměnná koliduje s formálním parametrem bloku)\n"
                   "  99 - interní chyba (neovlivněná integrací, vstupními soubory či parametry příkazové řádky)\n",
        )

        self.parser.add_argument(
            "-h", "--help",
            action='store_true',
            help="Vypíše na standardní výstup (STDOUT) nápovědu skriptu (nenačítá "
                 "žádný vstup) a vrací návratovou hodnotu 0. Tento parametr nelze "
                 "kombinovat s žádným dalším parametrem, jinak skript ukončete "
                 "s chybou 10."
        )

    def parse(self):
        args = self.parser.parse_args()

        if args.help:
            self.parser.print_help()

        return args.help

### konec souboru 'ArgumentParser.py' ###
