"""
********************************************************************************
* Název projektu:   Projekt do předmětu IPP 2024/2025:                         *
*                   Úloha 1 - Analyzátor kódu v SOL25 (parse.py)               *
*                                                                              *
* Soubor:           Symtable.py                                                *
* Autor:            Jan Kalina <xkalinj00>                                     *
*                                                                              *
* Datum:            18.02.2025                                                 *
* Poslední změna:   23.02.2025                                                 *
*                                                                              *
* Popis:            Modul pro správu tabulky symbolů. Obsahuje třídy a         *
*                   metody pro definici tříd, metod a spravování lokálních     *
*                   rámců pro proměnné a parametry. Součástí jsou funkce       *
*                   pro zavedení vestavěných symbolů a pro kontrolu kolizí     *
*                   při definici uživatelských tříd a metod.                   *
********************************************************************************
"""

# Import modulů standardní knihovny
from typing import Set

# Import vlastních modulů
from MyPyModules.AbstractSyntaxTree import ASTNodes as AST
from MyPyModules.CustomErrors import (InternalError, SemanticOtherError,
                                      SemanticUndefinedSymbolError,
                                      SemanticVariableCollisionError
                                     )

# Konstanty využívané jako argumenty metod
TOP_MOST_SCOPE = -1         # index nejvyšší rámce uvnitř zásobníku rámců
IS_FORMAL_PARAMETER = True  # vlajka rozlišující formální parametr od proměnné
IS_VARIABLE = False         # vlajka rozlišující porměnnou od formálního parametru


class Symbols:
    """
    Třída zastřešující typy symbolů ukládaných do tabulky symbolů.
    """

    class ClassSymbol:
        """
        Třída reprezentující definici třídy ve symbolické tabulce.

        Atributy:
            - identifier (str): Identifikátor dané třídy.
            - parentIdentifier (str): Identifikátor rodičovské třídy.
            - methods (dict): Slovník metod, kde klíče jsou selektory metod a
                              hodnoty jsou instance třídy `MethodSymbol`.
            - isBuiltIn (bool): Příznak, zda je třída vestavěná.

        Metody:
            - __init__(self, identifier, parentIdentifier, isBuiltIn): Inicializuje symbol třídy.
            - add_method(self, selector, methodSymbol): Přidá novou metodu do třídy.
        """

        def __init__(self, identifier:str, parent:str = None, isBuiltIn:bool = False, isDefined:bool = False):
            """
            Inicializuje instanci třídy ClassSymbol.
            """
            self.identifier = identifier
            self.parentIdentifier = parent
            self.methods = {}  # slovník str(methodSelector) --> MethodSymbol
            self.isBuiltIn = isBuiltIn
            self.isDefined = isDefined

        def add_method(self, selector:str, methodSymbol:"Symbols.MethodSymbol"):
            """
            Asociuje novou metodu do zvolené třídy.

            Parametry:
                - selector (str): Selektor (název) metody.
                - methodSymbol (MethodSymbol): Instance metody, kterou chceme přidat.

            Výjimky:
                - SemanticUndefinedSymbolError
                    - Pokud je metoda již definována nebo je porušeno pravidlo
                      definice ve vestavěné třídě.
            """
            # Kontrola redefinice metody
            if selector in self.methods:
                raise SemanticUndefinedSymbolError(
                    f"Method '{selector}' is already defined in class "
                    f"'{self.identifier}'."
                    )
            # Kontrola pro vestavěnou třídu, nelze v nich definovat uživatelské metody
            if self.isBuiltIn and not methodSymbol.isBuiltIn:
                raise SemanticUndefinedSymbolError(
                    f"Can not define new method '{selector}' inside built-in "
                    f"class '{self.identifier}'."
                    )
            # Přidání nového symbolu metody do slovníku
            self.methods[selector] = methodSymbol

    class MethodSymbol:
        """
        Třída `MethodSymbol` reprezentuje definici metody v jazyce SOL25.

        Atributy:
            - selector (str): Selektor metody.
            - block (AST.BlockNode|None): Tělo metody. Pokud je `None`, metoda
                                          je vestavěná.
            - paramCount (int|None): Očekávaný počet parametrů, nebo `None`
                                     pokud není předem definován.
            - isBuiltIn (bool): Příznak, zda jde o vestavěnou metodu (True)
                                nebo uživatelsky definovanou (False).

        Metody:
            - get_param_count(): Vrací skutečný počet parametrů (z bloku nebo
                                  z `paramCount`).
        """
        def __init__(self, selector:str, block:AST.BlockNode = None,
                     paramCnt:int = None, isBuiltIn:bool = False, isDefined:bool = False
                     ):
            self.selector = selector
            self.block = block
            self.paramCount = paramCnt
            self.isBuiltIn = isBuiltIn
            self.isDefined =  isDefined

        def get_param_count(self) -> int:
            """
            Získá počet parametrů metody. Pokud není `parameterCount` nastaven
            a `block` je `None`, vrací se 0.

            Návratová hodnota:
                - int: Počet parametrů buď z `block.parameterNodeList`, pokud
                       je k dispozici, nebo `paramCount`.
            """
            # Získá skutečný počet parametrů z bloku nebo z uloženého `paramCount`.
            if self.block is not None:
                return len(self.block.parameterNodeList)
            elif self.paramCount >= 0:
                return self.paramCount
            return 0


class BuiltInSymbols:
    """
    Třída `BuiltInSymbols` obsahuje vestavěné třídy a jejich metody pro jazyk SOL25.
    """

    class ObjectClass(Symbols.ClassSymbol):
        """
        Třída `ObjectClass` reprezentuje vestavěnou třídu `Object`.

        Metody:
            - __init__(self): Inicializuje vestavěnou třídu `Object` a přidává její metody.
        """

        def __init__(self):
            super().__init__("Object", parent = None, isBuiltIn = True, isDefined = True)
            self.add_method("new", Symbols.MethodSymbol("new", None, 0, True, True))
            self.add_method("from:", Symbols.MethodSymbol("from:", None, 1, True))
            self.add_method("asString", Symbols.MethodSymbol("asString", None, 0, True, True))
            self.add_method("isNumber", Symbols.MethodSymbol("isNumber", None, 0, True, True))
            self.add_method("isString", Symbols.MethodSymbol("isString", None, 0, True, True))
            self.add_method("isBlock", Symbols.MethodSymbol("isBlock", None, 0, True, True))
            self.add_method("equalTo:", Symbols.MethodSymbol("equalTo:", None, 1, True, True))
            self.add_method("identicalTo:", Symbols.MethodSymbol("identicalTo:", None, 1, True, True))

    class NilClass(Symbols.ClassSymbol):
        """
        Třída `NilClass` reprezentuje vestavěnou třídu `Nil`.

        Metody:
            - __init__(self): Inicializuje vestavěnou třídu `Nil` a přidává její metody.
        """

        def __init__(self):
            super().__init__("Nil", parent = "Object", isBuiltIn = True, isDefined = True)
            self.add_method("asString", Symbols.MethodSymbol("asString", None, 0, True, True))

    class TrueClass(Symbols.ClassSymbol):
        """
        Třída `TrueClass` reprezentuje vestavěnou třídu `True`.

        Metody:
            - __init__(self): Inicializuje vestavěnou třídu `True` a přidává její metody.
        """

        def __init__(self):
            super().__init__("True", parent = "Object", isBuiltIn = True, isDefined = True)
            self.add_method("not", Symbols.MethodSymbol("not", None, 0, True, True))
            self.add_method("and:", Symbols.MethodSymbol("and:", None, 1, True, True))
            self.add_method("or:", Symbols.MethodSymbol("or:", None, 1, True, True))
            self.add_method("ifTrue:ifFalse:", Symbols.MethodSymbol("ifTrue:ifFalse:", None, 2, True, True))

    class FalseClass(Symbols.ClassSymbol):
        """
        Třída `FalseClass` reprezentuje vestavěnou třídu `False`.

        Metody:
            - __init__(self): Inicializuje vestavěnou třídu `False` a přidává její metody.
        """

        def __init__(self):
            super().__init__("False", parent = "Object", isBuiltIn = True, isDefined = True)
            self.add_method("not", Symbols.MethodSymbol("not", None, 0, True, True))
            self.add_method("and:", Symbols.MethodSymbol("and:", None, 1, True, True))
            self.add_method("or:", Symbols.MethodSymbol("or:", None, 1, True, True))
            self.add_method("ifTrue:ifFalse:", Symbols.MethodSymbol("ifTrue:ifFalse:", None, 2, True, True))

    class IntegerClass(Symbols.ClassSymbol):
        """
        Třída `IntegerClass` reprezentuje vestavěnou třídu `Integer`.

        Metody:
            - __init__(self): Inicializuje vestavěnou třídu `Integer` a přidává její metody.
        """

        def __init__(self):
            super().__init__("Integer", parent = "Object", isBuiltIn = True, isDefined = True)
            self.add_method("plus:", Symbols.MethodSymbol("plus:", None, 1, True, True))
            self.add_method("minus:", Symbols.MethodSymbol("minus:", None, 1, True, True))
            self.add_method("divBy:", Symbols.MethodSymbol("divBy:", None, 1, True, True))
            self.add_method("equalTo:", Symbols.MethodSymbol("equalTo:", None, 1, True, True))
            self.add_method("asString", Symbols.MethodSymbol("asString", None, 0, True, True))
            self.add_method("asInteger", Symbols.MethodSymbol("asInteger", None, 0, True, True))
            self.add_method("timesRepeat:", Symbols.MethodSymbol("timesRepeat:", None, 1, True, True))
            self.add_method("multiplyBy:", Symbols.MethodSymbol("multiplyBy:", None, 1, True, True))
            self.add_method("greaterThan:", Symbols.MethodSymbol("greaterThan:", None, 1, True, True))

    class StringClass(Symbols.ClassSymbol):
        """
        Třída `StringClass` reprezentuje vestavěnou třídu `String`.

        Metody:
            - __init__(self): Inicializuje vestavěnou třídu `String` a přidává její metody.
        """

        def __init__(self):
            super().__init__("String", parent = "Object", isBuiltIn = True, isDefined = True)
            self.add_method("read", Symbols.MethodSymbol("read", None, 0, True, True))
            self.add_method("print", Symbols.MethodSymbol("print", None, 0, True, True))
            self.add_method("equalTo:", Symbols.MethodSymbol("equalTo:", None, 1, True, True))
            self.add_method("asString", Symbols.MethodSymbol("asString", None, 0, True, True))
            self.add_method("asInteger", Symbols.MethodSymbol("asInteger", None, 0, True, True))
            self.add_method("concatenateWith:", Symbols.MethodSymbol("concatenateWith:", None, 1, True, True))
            self.add_method("startsWith:endsBefore:", Symbols.MethodSymbol("startsWith:endsBefore:", None, 2, True, True))

    class BlockClass(Symbols.ClassSymbol):
        """
        Třída `BlockClass` reprezentuje vestavěnou třídu `Block`.

        Metody:
            - __init__(self): Inicializuje vestavěnou třídu `Block` a přidává její metody.
        """

        def __init__(self):
            super().__init__("Block", parent = "Object", isBuiltIn = True, isDefined = True)
            self.add_method("value", Symbols.MethodSymbol("value", None, 0, True, True))
            self.add_method("value:", Symbols.MethodSymbol("value:", None, 1, True, True))
            self.add_method("whileTrue:", Symbols.MethodSymbol("whileTrue:", None, 1, True, True))


class Symtable:
    """
    Třída reprezentující tabulku symbolů, která spravuje symboly tříd, metod a
    lokálních proměnných. Instance třídy `Symtable` drží jednu instanci podtřídy
    `ClassManager` a jednu instanci podtřídy `ScopeManager`, které lze používat
    ke správě symbolů.

    Třída `Symtable` sdružuje dvě podtřídy:
        - `ClassManager` pro správu tříd a metod,
        - `ScopeManager` pro správu lokálních rámců a proměnných.
    """

    def __init__(self):
        """
        Vytvoří instance podtříd `ClassManager` a `ScopeManager`.
        """
        self.classManager = self.ClassManager()
        self.scopeManager = self.ScopeManager()

    class ClassManager:
        """
        Podtřída pro správu symbolů tříd a metod. Uchovává slovník `classes`,
        do kterého se vkládají definice tříd a metod.

        Atributy:
            - scopes (list): Zásobník rámců, kde každý rámec je slovník.

        Metody:
            - __init__(self): Inicializuje prázdný slovník identifikátorů a symbolů tříd.
            - load_builtin_symbols(self): Načte vestavěné třídy a jejich metody do tabulky symbolů.
            - insert_class_symbol(self, identifier:str, parentIdentifier:str):
              Vloží do tabulky novou uživatelskou třídu a zkotroluje kolize.
            - insert_method_symbol(self, classIdentifier:str, selector:str, block:AST.BlockNode):
              Přidá (vloží) novou metodu do specifikované třídy.
            - get_class_symbol(self, identifier:str): Vyhledá a vrátí symbol třídy
            - get_method_symbol(self, classIdentifier:str, selector:str, visited:Set[str]):
              Rekurzivně vyhledá metodu v dané třídě a případně v jejích předcích.
        """

        def __init__(self):
            """
            Inicializuje prázdný slovník identifikátorů a symbolů tříd.
            """
            self.classes = {}  # slovník str(classIdentifier) --> ClassSymbol

        def load_builtin_symbols(self):
            """
            Načte vestavěné třídy a jejich metody do tabulky symbolů. Vytvoří
            se třídy Object, Nil, True, False, Integer, String a Block. Každá
            třída má přiřazené své vestavěné metody.
            """
            builtins = [
                BuiltInSymbols.ObjectClass(),  # Třída 'Object'
                BuiltInSymbols.NilClass(),  # Třida 'Nil'
                BuiltInSymbols.TrueClass(),  # Třida 'True'
                BuiltInSymbols.FalseClass(),  # Třída 'False'
                BuiltInSymbols.IntegerClass(),  # Třída 'Integer'
                BuiltInSymbols.StringClass(),  # Třída 'String'
                BuiltInSymbols.BlockClass()  # Třída 'Block'
                ]
            for builtinClass in builtins:
                self.classes[builtinClass.identifier] = builtinClass

        def insert_class_symbol(self, identifier:str, parentIdentifier:str = None,
                                defined:bool = False
                                ):
            """
            Vloží do tabulky novou uživatelskou třídu a zkotroluje kolize.

            Parametry:
                - identifier (str): Název nové třídy.
                - parentIdentifier (str): Název rodičovské třídy, pokud existuje.

            Výjimky:
                - SemanticUndefinedSymbolError:
                    - Pokud rodičovská třída není definována.
                - SemanticOtherError:
                    - Pokud již existuje vestavěná třída se stejným názvem.
                    - Pokud již byla definována uživatelská třída se stejným názvem.
            """
            # Vloží novou třídu do tabulky symbolů.
            if identifier in self.classes:
                existing = self.classes[identifier]
                # Kontrola opakované definice či kolize s vestavěnou třídou.
                if existing.isBuiltIn:
                    raise SemanticOtherError(
                        f"Can not redefine built-in class '{identifier}'."
                        )
                elif not existing.isDefined:
                    existing.isDefined = True
                    return
                else:
                    raise SemanticOtherError(
                        f"Class '{identifier}' is defined multiple times."
                        )
            self.classes[identifier] = (
                Symbols.ClassSymbol(identifier, parentIdentifier, isBuiltIn = False, isDefined = defined))

        def insert_method_symbol(self, classIdentifier:str, selector:str,
                                 block:AST.BlockNode, defined:bool = False
                                 ):
            """
            Přidá (vloží) novou metodu do specifikované třídy.

            Parametry:
                - classIdentifier (str): Název (jméno) třídy, do které metodu vkládáme.
                - selector (str): Selektor (název) metody.
                - block (AST.BlockNode): Blok kódu, který metodu reprezentuje.

            Výjimky:
                - SemanticUndefinedSymbolError:
                    - Pokud neexistuje zadaná třída.
                    - Pokud je metoda již definovaná v této třídě.
                    - Pokud se pokoušíme definovat metodu ve vestavěné třídě.
                - SemanticArityError:
                    - Pokud metoda přetěžuje metodu z rodičovské třídy, ale
                      s jiným počtem parametrů.
            """
            # Získá symbol třídy, ke které má být metoda připojena
            classSymbol = self.classes.get(classIdentifier)

            # Kontrola možných kolizí a chybné definice
            if classSymbol is None:
                raise SemanticUndefinedSymbolError(
                    f"Class '{classIdentifier}' doesn't exist."
                    )
            if classSymbol.isBuiltIn:
                raise SemanticUndefinedSymbolError(
                    f"Can not define method '{selector}' inside built-in class "
                    f"'{classIdentifier}'."
                    )
            if selector in classSymbol.methods:
                raise SemanticUndefinedSymbolError(
                    f"Method '{selector}' is already defined inside class "
                    f"'{classIdentifier}'."
                    )
            # Asociace metody s danou třídou
            classSymbol.add_method(selector, Symbols.MethodSymbol(selector, block, isBuiltIn = False, isDefined = defined))

        def get_class_symbol(self, identifier:str) -> Symbols.ClassSymbol | None:
            """
            Vyhledá a vrátí symbol třídy podle identifikátoru, nebo None pokud
            neexistuje.

            Parametry:
                - identifier (str): Název třídy.

            Návratová hodnota:
                - Symbols.ClassSymbol | None: Objekt reprezentující třídu,
                                              pokud existuje, jinak `None`.
            """
            return self.classes.get(identifier)

        def get_all_class_symbols(self) -> list:
            """
            Vrátí seznam všech symbolů tříd.

            Návratová hodnota:
                - list: Seznam všech symbolů tříd.
            """
            return list(self.classes.values())

        def get_method_symbol(self, classIdentifier:str, selector:str, visited:Set[str] = None):
            """
            Rekurzivně vyhledá metodu v dané třídě a případně v jejích předcích.

            Parametry:
                - classIdentifier (str): Identifikátor třídy, kde vyhledávání začíná.
                - selector (str): Selektor (identifikátor) hledané metody.
                - visited (set): Množina dříve navštívených tříd pro detekci cyklů.

            Návratová hodnota:
                - Symbols.MethodSymbol | None: Metodu, pokud je nalezena, jinak `None`.
            """
            # Pokud nebylo předáno 'visited', vytvoří se nová prázdná množina.
            if visited is None:
                visited = set()

            # Pokud jsme již tuto třídu navštívili, hrozí cyklus, proto vracíme `None`.
            if classIdentifier in visited:
                return None
            # Jinak přidáme tuto třídu do `visited`
            else:
                visited.add(classIdentifier)

            # Pokud je 'classIdentifier' prázdný, nelze pokračovat.
            if not classIdentifier:
                return None
            # Jinak získání symbol třídy podle jejího identifikátoru.
            else:
                classSymbol = self.classes.get(classIdentifier)

            # Pokud symbol třídy neexistuje, vracíme `None` (třída nebyla nalezena).
            if not classSymbol:
                return None

            # Pokud je hledaný selektor mezi metodami aktuální třídy, vrátíme nalezenou metodu.
            if selector in classSymbol.methods:
                return classSymbol.methods[selector]
            # Pokud má třída rodiče, pokusíme se vyhledat metodu rekurzivně v předkovi.
            elif classSymbol.parentIdentifier:
                return self.get_method_symbol(classSymbol.parentIdentifier, selector, visited)
            # Jinak se nepodařilo nic najít, vracíme `None`.
            else:
                return None

        def class_knows_method(self, classIdentifier:str, methodIdentifier:str) -> bool:
            """
            Zkontroluje, zda třída zná danou metodu.

            Parametry:
                - class_name (str): Název třídy.
                - method_identifier (str): Identifikátor metody.

            Návratová hodnota:
                - bool: `True`, pokud třída zná metodu, jinak `False`.
            """
            classSymbol = self.get_class_symbol(classIdentifier)
            if classSymbol is None:
                return False
            return methodIdentifier in classSymbol.methods

        def set_class_as_defined(self, classNode:AST.ClassNode):
            """
            Nastaví atribut `isDefined` na `True` pro třídu s daným identifikátorem.

            Parametry:
                - classNode (AST.ClassNode): Uzel třídy.

            Výjimky:
                - InternalError: Pokud třída není nalezena.
            """
            classSymbol = self.get_class_symbol(classNode.identifier)
            if classSymbol is not None and classSymbol.isDefined:
                raise SemanticOtherError(
                    f"Class '{classNode.identifier}' is already defined."
                    )
            if classSymbol is not None:
                classSymbol.parentIdentifier = classNode.perentIdentifier
                classSymbol.isDefined = True
            else:
                self.insert_class_symbol(classNode.identifier, classNode.perentIdentifier, True)

            parentSymbol = self.get_class_symbol(classNode.perentIdentifier)
            if parentSymbol is None:
               self.insert_class_symbol(classNode.perentIdentifier, None, False)

        def are_all_classes_defined(self):
            """
            Zkontroluje, zda všechny třídy v tabulce symbolů jsou definované.

            Výjimky:
                - SemanticUndefinedSymbolError: Pokud některá třída není definována.
            """
            for classSymbol in self.classes.values():
                if not classSymbol.isDefined:
                    raise SemanticUndefinedSymbolError(
                        f"Class '{classSymbol.identifier}' is not defined."
                        )

    class ScopeManager:
        """
        Podtřída pro správu lokálních rámců (scope) a proměnných.
        Uchovává seznam slovníků `scopes`, které fungují jako zásobník rámců.

        Atributy:
            - scopes (list): Zásobník rámců, kde každý rámec je slovník.

        Metody:
            - __init__(self): Inicializuje zásobník rámců jako prázdný seznam.
            - enter_new_scope(self): Vytvoří nový rámec pro proměnné a parametry.
            - exit_current_scope(self): Ukončí aktuální rámec.
            - top_scope(self): Získá horní rámec ze zásobníku rámců.
            - define_variable(self, identifier:str): Přidá nový formální parametr
            - define_pseudovariable(self, identifier:str, value): Přidá pseudoproměnnou.
            - is_defined(self, identifier:str): Ověří, zda je proměnná definována.
            - is_formal_parameter(self, identifier:str): Zjistí, zda je proměnná formálním parametrem.
        """

        def __init__(self):
            """
            Inicializuje zásobník rámců jako prázdný seznam.
            """
            self.scopes = []  # seznam (zásobník) slovníků `classes`

        def enter_new_scope(self):
            """
            Vytvoří nový (vnořený) rámec (rozsah platnosti) pro proměnné a
            parametry. Pokud nějaký scope již existuje, překopírují se "pseudo"
            položky (tj. `self` a `super`), do rozsahu platnosti.
            """
            newScope = {}
            if self.scopes:
                # Zkopíruje pseudoproměnné.
                for ident, value in self.top_scope().items():
                    if isinstance(value, dict) and value.get("pseudo", False):
                        newScope[ident] = value
            self.scopes.append(newScope)

        def exit_current_scope(self):
            """
            Ukončí (odstraní) aktuální rámec (rozsah platnosti) z vrcholu
            zásobníku.

            Výjimky:
                - InternalError: Pokud nelze ukončit žádný rámec.
            """
            if not self.scopes:
                raise InternalError("There is no scope to exit.")
            self.scopes.pop()

        def top_scope(self) -> dict:
            """
            Získá horní (aktuální) rámec ze zásobníku rámců.

            Návratová hodnota:
                - dict: Aktuální (horní) rámec ze zásobníku rámců.
            """
            return self.scopes[TOP_MOST_SCOPE]

        def define_variable(self, identifier:str):
            """
            Definuje (přidá) novou proměnnou do horního rámece, pokud
            ještě není definovaná.

            Parametry:
                identifier (str): Název nové proměnné.
            """
            # Pokud žádný rámec neexistuje, tak se vytvoří.
            if not self.scopes:
                self.enter_new_scope()

            # Definujeme novou proměnnou v horním rámci.
            topScope = self.top_scope()
            if identifier not in topScope:
                topScope[identifier] = IS_VARIABLE

        def define_formal_parameter(self, identifier:str):
            """
            Definuje (přidá) nový formální parametr v aktuálním (horním) rámci.

            Parametry:
                identifier (str): Název parametru.

            Výjimky:
                - SemanticVariableCollisionError:
                    - Pokud parametr se stejným jménem již existuje v aktuálním rámci.
            """
            #  Pokud žádný rámec neexistuje, tak se vytvoří.
            if not self.scopes:
                self.enter_new_scope()

            # Kontrola kolízí mezi indetifikátory v horním rámci.
            topScope = self.top_scope()
            if identifier in topScope:
                raise SemanticVariableCollisionError(
                    f"Collision of formal parameter '{identifier}'."
                    )
            topScope[identifier] = IS_FORMAL_PARAMETER  # označíme ho jako fromální parametr

        def define_pseudovariable(self, identifier:str, value):
            """
            Definuje pseudoproměnnou (např. `self`, `super`) v aktuálním
            (horním) rámci.

            Parametry:
                identifier (str): Název pseudoproměnné.
                value: Hodnota, která se k pseudoproměnné přiřadí.

            Výjimky:
                - SemanticVariableCollisionError:
                    - Pokud je pseudoproměnná již definována.
            """
            # Kontrola kolízí mezi indetifikátory v horním rámci.
            topScope = self.top_scope()
            if identifier in topScope:
                raise SemanticVariableCollisionError(
                    f"Pseudovariable '{identifier}' is already defined."
                    )
            topScope[identifier] = {"pseudo": True, "value": value}  # přidání pseudoproměnných

        def is_defined(self, identifier:str) -> bool:
            """
            Ověří, zda je proměnná definována v aktuálním (horním) rámci.

            Parametry:
                - identifier (str): Název proměnné.

            Návratová hodnota:
                - bool: `True`, pokud je proměnná definována v aktuálním (horním)
                        rámci., jinak `False`.
            """
            if not self.scopes:
                return False
            return identifier in self.top_scope()

        def is_formal_parameter(self, identifier:str) -> bool:
            """
            Zjistí, zda je proměnná v aktuálním (horním) rámci formálním parametrem.

            Parametry:
                - identifier (str): Název proměnné.

            Návratová hodnota:
                - bool: `True`, pokud je proměnná formálním parametrem, jinak `False`.
            """
            if not self.scopes:
                return False

            topScope = self.top_scope()
            variableType = topScope.get(identifier, IS_VARIABLE)
            return variableType == IS_FORMAL_PARAMETER

### konec souboru 'Symtable.py' ###
