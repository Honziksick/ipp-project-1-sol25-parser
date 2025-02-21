"""
********************************************************************************
*                                                                              *
* Název projektu:   Projekt do předmětu IPP 2024/2025 IFJ24:                   *
*                   Úloha 1 - Analyzátor kódu v SOL25 (parse.py)               *
*                                                                              *
* Soubor:           Symtable.py                                                *
* Autor:            Jan Kalina <xkalinj00>                                     *
*                                                                              *
* Datum:            18.02.2025                                                 *
* Poslední změna:   xx.xx.2025                                                 *
*                                                                              *
********************************************************************************
"""

"""
@file Symtable.py
@author Jan Kalina \<xkalinj00>

@brief
@details
"""

from MyPyModules.ASTNodes import ASTNodes as AST
from MyPyModules.CustomErrors import (
    SemanticUndefinedSymbolError,
    SemanticArityError,
    SemanticVariableCollisionError,
    InternalError,
)

IS_FORMAL_PARAMETER = True
IS_VARIABLE = False
TOP_MOST_SCOPE = -1


class ClassSymbol:
    def __init__(self, identifier: str, parent: str, isBuiltIn: bool = False):
        self.identifier = identifier
        self.parentName = parent
        self.methods = {}  # {str, MethodSymbol}
        self.isBuiltIn = isBuiltIn

    def add_method(self, selector: str, methodSymbol: "MethodSymbol"):
        if selector in self.methods:
            raise SemanticUndefinedSymbolError(
                f"Metoda '{selector}' je již definována ve třídě '{self.identifier}'."
            )

        # Pokud je to vestavěná třída, user by neměl umět definovat vestavěné metody:
        if self.isBuiltIn and not methodSymbol.isBuiltIn:
            raise SemanticUndefinedSymbolError(
                f"Nelze definovat novou metodu '{selector}' ve vestavěné třídě '{self.identifier}'."
            )
        self.methods[selector] = methodSymbol


class MethodSymbol:
    def __init__(
        self, selector: str, block: AST.BlockNode, paramCount=None, isBuiltIn=False
    ):
        self.selector = selector
        self.block = block
        self.paramCount = paramCount
        self.isBuiltIn = isBuiltIn

    def get_param_count(self):
        if self.block is not None:
            return len(self.block.paramNodeList)
        elif self.paramCount >= 0:
            return self.paramCount
        return 0


class Symtable:
    def __init__(self):
        self.classes = {}  # {str, ClassSymbol}
        # Scopes pro lokální proměnné a formální parametry – každý scope je reprezentován slovníkem,
        # kde klíče jsou identifikátory a hodnota bool (True = formální parametr, False = běžná proměnná)
        self.scopes = (
            []
        )  # stack (list) slovníků: ident -> bool (IS_FORMAL_PARAMETER/IS_VARIABLE)

    def load_builtin_symbols(self):
        """
        Hard-coded zavedení vestavěných tříd a jejich metod.
        """
        # 1) Vytvoříme ClassSymbol pro Object (bez parent)
        objectClassSymbol = ClassSymbol("Object", parent=None, isBuiltIn=True)
        # Třídní metody new, from: definujeme spíš až v BĚŽNÝCH potomcích,
        # ale zadání říká, že new/from: je definováno v Object a dědí se do potomků,
        # a nejde je redefinovat.
        objectClassSymbol.add_method(
            "new", MethodSymbol("new", block=None, paramCount=0, isBuiltIn=True)
        )
        objectClassSymbol.add_method(
            "from:", MethodSymbol("from:", block=None, paramCount=1, isBuiltIn=True)
        )
        # Instanční metody (jen příklad): identicalTo:, equalTo:, asString, ...
        objectClassSymbol.add_method(
            "identicalTo:",
            MethodSymbol("identicalTo:", block=None, paramCount=1, isBuiltIn=True),
        )
        objectClassSymbol.add_method(
            "equalTo:",
            MethodSymbol("equalTo:", block=None, paramCount=1, isBuiltIn=True),
        )
        objectClassSymbol.add_method(
            "asString",
            MethodSymbol("asString", block=None, paramCount=0, isBuiltIn=True),
        )
        objectClassSymbol.add_method(
            "isNumber",
            MethodSymbol("isNumber", block=None, paramCount=0, isBuiltIn=True),
        )
        objectClassSymbol.add_method(
            "isString",
            MethodSymbol("isString", block=None, paramCount=0, isBuiltIn=True),
        )
        objectClassSymbol.add_method(
            "isBlock", MethodSymbol("isBlock", block=None, paramCount=0, isBuiltIn=True)
        )
        objectClassSymbol.add_method(
            "isNil", MethodSymbol("isNil", block=None, paramCount=0, isBuiltIn=True)
        )

        self.classes["Object"] = objectClassSymbol

        # 2) Nil : Object (singleton)
        nilClassSymbol = ClassSymbol("Nil", parent="Object", isBuiltIn=True)
        # vestavěné metody asString => 'nil'
        nilClassSymbol.add_method(
            "asString",
            MethodSymbol("asString", block=None, paramCount=0, isBuiltIn=True),
        )
        self.classes["Nil"] = nilClassSymbol

        # 3) True : Object
        trueClassSymbol = ClassSymbol("True", parent="Object", isBuiltIn=True)
        trueClassSymbol.add_method(
            "not", MethodSymbol("not", block=None, paramCount=0, isBuiltIn=True)
        )
        trueClassSymbol.add_method(
            "and:", MethodSymbol("and:", block=None, paramCount=1, isBuiltIn=True)
        )
        trueClassSymbol.add_method(
            "or:", MethodSymbol("or:", block=None, paramCount=1, isBuiltIn=True)
        )
        trueClassSymbol.add_method(
            "ifTrue:ifFalse:",
            MethodSymbol("ifTrue:ifFalse:", None, paramCount=2, isBuiltIn=True),
        )
        self.classes["True"] = trueClassSymbol

        # 4) False : Object
        falseClassSymbol = ClassSymbol("False", parent="Object", isBuiltIn=True)
        falseClassSymbol.add_method(
            "not", MethodSymbol("not", block=None, paramCount=0, isBuiltIn=True)
        )
        falseClassSymbol.add_method(
            "and:", MethodSymbol("and:", block=None, paramCount=1, isBuiltIn=True)
        )
        falseClassSymbol.add_method(
            "or:", MethodSymbol("or:", block=None, paramCount=1, isBuiltIn=True)
        )
        falseClassSymbol.add_method(
            "ifTrue:ifFalse:",
            MethodSymbol("ifTrue:ifFalse:", None, paramCount=2, isBuiltIn=True),
        )
        self.classes["False"] = falseClassSymbol

        # 5) Integer : Object
        integerClassSymbol = ClassSymbol("Integer", parent="Object", isBuiltIn=True)
        integerClassSymbol.add_method(
            "equalTo:",
            MethodSymbol("equalTo:", block=None, paramCount=1, isBuiltIn=True),
        )
        integerClassSymbol.add_method(
            "greaterThan:",
            MethodSymbol("greaterThan:", block=None, paramCount=1, isBuiltIn=True),
        )
        integerClassSymbol.add_method(
            "plus:", MethodSymbol("plus:", block=None, paramCount=1, isBuiltIn=True)
        )
        integerClassSymbol.add_method(
            "minus:", MethodSymbol("minus:", block=None, paramCount=1, isBuiltIn=True)
        )
        integerClassSymbol.add_method(
            "multiplyBy:",
            MethodSymbol("multiplyBy:", block=None, paramCount=1, isBuiltIn=True),
        )
        integerClassSymbol.add_method(
            "divBy:", MethodSymbol("divBy:", block=None, paramCount=1, isBuiltIn=True)
        )
        integerClassSymbol.add_method(
            "asString",
            MethodSymbol("asString", block=None, paramCount=0, isBuiltIn=True),
        )
        integerClassSymbol.add_method(
            "asInteger",
            MethodSymbol("asInteger", block=None, paramCount=0, isBuiltIn=True),
        )
        integerClassSymbol.add_method(
            "timesRepeat:",
            MethodSymbol("timesRepeat:", block=None, paramCount=1, isBuiltIn=True),
        )
        self.classes["Integer"] = integerClassSymbol

        # 6) String : Object
        stringClassSymbol = ClassSymbol("String", parent="Object", isBuiltIn=True)
        stringClassSymbol.add_method(
            "print", MethodSymbol("print", block=None, paramCount=0, isBuiltIn=True)
        )
        stringClassSymbol.add_method(
            "equalTo:",
            MethodSymbol("equalTo:", block=None, paramCount=1, isBuiltIn=True),
        )
        stringClassSymbol.add_method(
            "asString",
            MethodSymbol("asString", block=None, paramCount=0, isBuiltIn=True),
        )
        stringClassSymbol.add_method(
            "asInteger",
            MethodSymbol("asInteger", block=None, paramCount=0, isBuiltIn=True),
        )
        stringClassSymbol.add_method(
            "concatenateWith:",
            MethodSymbol("concatenateWith:", None, paramCount=1, isBuiltIn=True),
        )
        stringClassSymbol.add_method(
            "startsWith:endsBefore:",
            MethodSymbol("startsWith:endsBefore:", None, paramCount=2, isBuiltIn=True),
        )
        # Třídní metoda read => musíme zapsat do Object ???
        # Podle zadání je to "String read". Tj. je to vestavěná "class method" => definujeme i sem:
        stringClassSymbol.add_method(
            "read", MethodSymbol("read", block=None, paramCount=0, isBuiltIn=True)
        )
        self.classes["String"] = stringClassSymbol

        # 7) Block : Object
        blockClassSymbol = ClassSymbol("Block", parent="Object", isBuiltIn=True)
        # vestavěné inst. metody for block => "value", "value:", "whileTrue:", ...
        blockClassSymbol.add_method(
            "whileTrue:",
            MethodSymbol("whileTrue:", block=None, paramCount=1, isBuiltIn=True),
        )
        # atd. "value", "value:", "value:value:" => v základu by se generovaly dle počtu param.
        blockClassSymbol.add_method(
            "value", MethodSymbol("value", block=None, paramCount=0, isBuiltIn=True)
        )
        blockClassSymbol.add_method(
            "value:", MethodSymbol("value:", block=None, paramCount=1, isBuiltIn=True)
        )
        self.classes["Block"] = blockClassSymbol

    # ----------------- Vkládání user-def třídy a metody -----------------

    # Práce s třídami a metodami
    def insert_class_symbol(self, identifier: str, parent: str = None):
        """
        Přidá uživatelskou třídu. Kontroluje kolizi s vestavěnou i existující user definicí.
        """
        if identifier in self.classes:
            # buď už je vestavěná, nebo definovaná
            existing = self.classes[identifier]
            if existing.isBuiltIn:
                raise SemanticUndefinedSymbolError(
                    f"Nelze znovu definovat vestavěnou třídu '{identifier}'."
                )
            else:
                raise SemanticUndefinedSymbolError(
                    f"Třída '{identifier}' je definována dvakrát."
                )
        self.classes[identifier] = ClassSymbol(identifier, parent, isBuiltIn=False)

    def insert_method_symbol(self, className: str, selector: str, block: AST.BlockNode):
        classSymbol = self.classes.get(className)
        if classSymbol is None:
            raise SemanticUndefinedSymbolError(f"Třída '{className}' neexistuje!")
        if selector in classSymbol.methods:
            raise SemanticUndefinedSymbolError(
                f"Metoda '{selector}' je již definována ve třídě '{className}'."
            )

        classSymbol = self.classes.get(className)
        if classSymbol is None:
            raise SemanticUndefinedSymbolError(f"Třída '{className}' neexistuje!")

        # Ověřit, jestli to už není definované
        if selector in classSymbol.methods:
            raise SemanticUndefinedSymbolError(
                f"Metoda '{selector}' je již definována ve třídě '{className}'."
            )

        # Zákaz override vestavěné metody, pokud třída je vestavěná:
        if classSymbol.isBuiltIn:
            # Nelze definovat user method ve vestavěné třídy
            raise SemanticUndefinedSymbolError(
                f"Nelze definovat metodu '{selector}' ve vestavěné třídě '{className}'."
            )

        # override v parentu: pokud existuje, zkontroluj stejnou aritu
        parentMethod = self.get_method_symbol(classSymbol.parentName, selector)
        if parentMethod is not None:
            paramCount = len(block.paramNodeList)
            if parentMethod.get_param_count() != paramCount:
                raise SemanticArityError(
                    f"Override metody '{selector}' ve třídě '{className}' má nesprávnou aritu. "
                    f"Původní metoda má {parentMethod.get_param_count()} parametrů, ale nová {paramCount}."
                )
        # Vložíme
        classSymbol.add_method(selector, MethodSymbol(selector, block, isBuiltIn=False))

    def get_class_symbol(self, identifier: str):
        return self.classes.get(identifier)


    def get_method_symbol(self, className: str, selector: str, visited=None):
        """
        Vyhledává metodu (selector) v dané třídě a pokud nic, rekurzivně v parentu.
        """
        if visited is None:
            visited = set()

        if className in visited:
            return None
        visited.add(className)

        if not className:
            return None

        classSymbol = self.classes.get(className)
        if not classSymbol:
            return None

        if selector in classSymbol.methods:
            return classSymbol.methods[selector]

        if classSymbol.parentName:
            return self.get_method_symbol(classSymbol.parentName, selector, visited)

        return None

    # ---------------- Lokální scopy pro proměnné a parametry ---------------

    def enter_new_scope(self):
        """Vytvoří nový lokální rozsah se zděděním speciálních proměnných."""
        new_scope = {}
        if self.scopes:
            # Zkopírujeme položky označené jako special (např. self, super) do nového scope
            for ident, value in self.top_scope().items():
                if isinstance(value, dict) and value.get("special", False):
                    new_scope[ident] = value
        self.scopes.append(new_scope)

    def exit_current_scope(self):
        """Ukončí aktuální lokální rozsah."""
        if not self.scopes:
            raise InternalError("Žádný scope k ukončení.")
        self.scopes.pop()

    def top_scope(self):
        return self.scopes[TOP_MOST_SCOPE]

    def define_variable(self, identifier: str):
        """
        Definuje proměnnou v aktuálním rozsahu, pokud ještě nebyla definována.
        Běžné přiřazení nepřepisuje již existující proměnnou.
        """
        if not self.scopes:
            self.enter_new_scope()

        topScope = self.top_scope()
        if identifier not in topScope:
            topScope[identifier] = IS_VARIABLE

    def define_parameter(self, identifier: str):
        """
        Definuje formální parametr v aktuálním rozsahu. Pokud již parametr se stejným jménem existuje,
        vyvolá se chyba kolize.
        """
        if not self.scopes:
            self.enter_new_scope()

        topScope = self.top_scope()
        if identifier in topScope:
            raise SemanticVariableCollisionError(
                f"Kolize formálního parametru: {identifier}"
            )
        topScope[identifier] = IS_FORMAL_PARAMETER

    def define_pseudovariable(self, identifier: str, value):
        """
        Definuje rezervovanou pseudoproměnnou (self, super) v aktuálním scope.
        Tyto bindingy jsou immutable – nelze je později přepsat.
        """
        topScope = self.top_scope()
        if identifier in topScope:
            raise SemanticVariableCollisionError(f"Pseudoproměnná '{identifier}' je již definována.")
        # Uložíme hodnotu společně s příznakem jako special
        topScope[identifier] = {"special": True, "value": value}

    def is_defined(self, identifier: str):
        """
        Ověří, zda je proměnná definována v aktuálním rozsahu.
        Podle zadání nejsou proměnné z jednoho bloku viditelné v lexikálně zanořených blocích.
        """
        if not self.scopes:
            return False
        return identifier in self.top_scope()

    def is_defined_in_current_scope(self, identifier: str):
        """Vrátí, zda je proměnná definována přímo v aktuálním (horním) rozsahu."""
        if not self.scopes:
            return False
        return identifier in self.top_scope()

    def is_formal_parameter(self, identifier: str):
        """Ověří, zda je proměnná v aktuálním rozsahu formálním parametrem."""
        if not self.scopes:
            return False
        # Pokud parametr neexistuje, default by měl být IS_VARIABLE (tj. False)
        topScope = self.top_scope()
        variableType = topScope.get(identifier, IS_VARIABLE)
        return variableType == IS_FORMAL_PARAMETER

    def __str__(self):
        result = []
        for className, classSym in self.classes.items():
            result.append(f"Třída: {className}, rodič: {classSym.parentName}")
            for selector, methodSym in classSym.methods.items():
                result.append(
                    f"  Metoda: {selector}, počet parametrů: {methodSym.get_param_count()}"
                )
        result.append("Aktuální scopes:")
        for i, scope in enumerate(self.scopes):
            result.append(f"  Scope {i}: {scope}")
        return "\n".join(result)

### konec souboru 'Symtable.py' ###
