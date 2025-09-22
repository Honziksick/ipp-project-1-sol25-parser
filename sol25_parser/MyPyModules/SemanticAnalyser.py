"""
********************************************************************************
* Název projektu:   Projekt do předmětu IPP 2024/2025:                         *
*                   Úloha 1 - Analyzátor kódu v SOL25 (parse.py)               *
*                                                                              *
* Soubor:           SemanticAnalyser.py                                        *
* Autor:            Jan Kalina <xkalinj00>                                     *
*                                                                              *
* Datum:            19.02.2025                                                 *
* Poslední změna:   24.02.2025                                                 *
*                                                                              *
* Popis:            Tento soubor implementuje sémantický analyzátor pro jazyk  *
*                   SOL25. Analyzátor prochází abstraktní syntaktický strom    *
*                   (AST) a kontroluje sémantické chyby (např. nedefinované    *
*                   symboly, kolize proměnných, nesprávný počet parametrů      *
*                   metod a další).                                            *
********************************************************************************
"""

# Import vlastních modulů
from MyPyModules.AbstractSyntaxTree import ASTNodes, ASTNodeVisitor
from MyPyModules.CustomErrors import (
    SemanticArityError, SemanticMainRunError, SemanticOtherError,
    SemanticUndefinedSymbolError, SemanticVariableCollisionError)
from MyPyModules.Symtable import Symtable


class SemanticAnalyser(ASTNodeVisitor):
    """
    Třída `SemanticAnalyser` provádí sémantickou analýzu AST.

    Atributy:
        - _symtable: Instance tabulky symbolů.
        - _currentClass: Kontext aktuálně analyzované třídy.

    Metody:
        - __init__: Inicializuje sémantický analyzátor a tabulku symbolů.
        - analyse_semantic: Spustí rekurzivní sémantickou analýzu programu.
        - visit_program_node: Návštěvník uzlu programu.
        - visit_class_node: Návštěvník uzlu třídy.
        - visit_method_node: Návštěvník uzlu metody.
        - visit_block_node: Návštěvník uzlu bloku.
        - visit_assign_node: Návštěvník uzlu přiřazení.
        - visit_expression_node: Návštěvník uzlu výrazu.
        - visit_identifier_node: Návštěvník uzlu proměnné.
        - visit_literal_node: Návštěvník uzlu literálu.
        - _handle_class_method: Zpracuje volání třídní metody.
        - _handle_instance_method: Zpracuje volání instanční metody.
        - _check_combined_selector: Zkontroluje složený selektor metod.
        - _get_expected_param_count: Získá očekávaný počet parametrů pro složený selektor.
    """

    def __init__(self):
        """
        Inicializuje sémantický analyzátor a tabulku symbolů.
        """
        self._symtable = Symtable()
        self._currentClass = None

    def analyse_semantic(self, programNode: ASTNodes.ProgramNode):
        """
        Spustí rekurzivní sémantickou analýzu programu od kořene AST.

        Parametry:
            - programNode (ASTNodes.ProgramNode): Kořenový uzel AST (programu).

        Výjimky:
            - SemanticMainRunError: Pokud chybí třída 'Main' nebo metoda 'run'.
        """
        # Načteme vestavěné třídy a metody
        self._symtable.classManager.load_builtin_symbols()

        # Projdeme abstraktní syntaktický strom (AST)
        self.visit_program_node(programNode)

        # Kontrola existence povinné třídy 'Main' a metody 'run'
        mainClass = self._symtable.classManager.get_class_symbol("Main")
        if mainClass is None:
            raise SemanticMainRunError("Class 'Main' is missing.")

        runMethod = self._symtable.classManager.get_method_symbol("Main", "run")
        if runMethod is None:
            raise SemanticMainRunError("Class 'Main' is missing method 'run'.")

        # Kontrola cyklické dědičnosti
        self.check_cyclic_inheritance()

    def visit_program_node(self, node: ASTNodes.ProgramNode):
        """
        Návštěvník uzlu programu.

        Parametry:
            - node (ASTNodes.ProgramNode): Uzel reprezentující celý program.
        """
        for classNode in node.classNodeList:
            self._symtable.classManager.set_class_as_defined(classNode)

        # Projedeme všechny třídy jednu po druhé
        for classNode in node.classNodeList:
            self.visit_class_node(classNode)
        self._symtable.classManager.are_all_classes_defined()

    def visit_class_node(self, node: ASTNodes.ClassNode):
        """
        Návštěvník uzlu třídy.

        Parametry:
            - node (ASTNodes.ClassNode): Uzel třídy.
        """
        # Vložíme procházenou třídu do tabulky symbolů a aktualizujeme kontext analýzy
        self._currentClass = node.identifier

        # Projedeme všechny metody analyzované třídy
        for methodNode in node.methodNodeList:
            self.visit_method_node(methodNode)

        # Resetujeme kontext analýzy kvůli detekci metod mimo třídy
        self._currentClass = None

    def visit_method_node(self, node: ASTNodes.MethodNode):
        """
        Návštěvník uzlu metody.

        Parametry:
            - node (ASTNodes.MethodNode): Uzel metody.

        Výjimky:
            - SemanticUndefinedSymbolError: Pokud je metoda definována mimo třídu.
            - SemanticArityError: Pokud metoda 'run' má parametry.
                                  Pokud override metody mění počet parametrů.
        """
        # Kontrola chybného výskytu metody mimo třídu
        if self._currentClass is None:
            raise SemanticUndefinedSymbolError(f"Method {node.selector} is defined out of class.")

        # Kontrola, že metoda 'run' je bezparametrická
        if node.selector == "run" and len(getattr(node.blockNode, 'parameterNodeList', [])) > 0:
            raise SemanticArityError(f"Method 'run' must have no parameters.")

        # Kontrola override, zda se nemění počet parametrů
        classSymbol = self._symtable.classManager.get_class_symbol(self._currentClass)
        if classSymbol and classSymbol.parentIdentifier:
            parentMethod = self._symtable.classManager.get_method_symbol(
                classSymbol.parentIdentifier, node.selector
                )
            if parentMethod is not None:
                paramCount = len(node.blockNode.parameterNodeList)
                if parentMethod.get_param_count() != paramCount:
                    raise SemanticArityError(
                        f"Override of method '{node.selector}' in class '{self._currentClass}' "
                        f"has incorrect arity. Original method has arity '{parentMethod.get_param_count()}'; "
                        f"new method has arity '{paramCount}'."
                        )

        # Vložíme definici metody do tabulky symbolů.
        # (Pozn. případná kontrola korektnosti override (arity) se provede uvnitř tabulky symbolů.)
        self._symtable.classManager.insert_method_symbol(self._currentClass, node.selector, node.blockNode)

        # Analýza metody => vstup do nového lokálního rozsahu platnosti (rámce).
        self._symtable.scopeManager.enter_new_scope()

        # Vložení a nastavení pseudoproměnných 'self' a 'super' do lokálního rámce.
        self._symtable.scopeManager.define_pseudovariable("self", "instance_placeholder")
        _currentClassSymbol = self._symtable.classManager.get_class_symbol(self._currentClass)
        parentClass = _currentClassSymbol.parentIdentifier if _currentClassSymbol else None
        self._symtable.scopeManager.define_pseudovariable("super", ("instance_placeholder", parentClass))

        # Analýza těla (bloku) metody
        node.blockNode.visit_by(self)

        # Konec analýzy metody => výstup z lokálního rámce
        self._symtable.scopeManager.exit_current_scope()

    def visit_block_node(self, node: ASTNodes.BlockNode):
        """
        Návštěvník uzlu bloku.

        Parametry:
            - node (ASTNodes.BlockNode): Uzel bloku.

        Výjimky:
            - SemanticVariableCollisionError: Pokud dojde ke kolizi formálních parametrů.
        """
        # Analýza bloku => vstup do nového lokálního rozsahu platnosti (rámce).
        self._symtable.scopeManager.enter_new_scope()

        # Zpracujeme formální parametry bloku (pokud existují).
        for parameter in node.parameterNodeList:
            # Kontrola kolize formálního parametru s jiným symbolem
            # (Pozn. pseudoproměnné 'self' a 'super' jsou ošetřeny v tabulce symbolů.)
            if self._symtable.scopeManager.is_defined(parameter):
                if self._symtable.scopeManager.is_formal_parameter(parameter):
                    raise SemanticOtherError(
                        f"Trying to redefine formal parameter '{parameter}'."
                        )
                else:
                    raise SemanticVariableCollisionError(
                        f"Collision of formal parameter '{parameter}'."
                        )
            # Definice formálního parametru v lokálním rámci
            self._symtable.scopeManager.define_formal_parameter(parameter)

        # Projdeme všechny příkazy v těle bloku
        for statement in node.statementNodeList:
            statement.visit_by(self)

        # Konec analýzy bloku => výstup z lokálního rámce
        self._symtable.scopeManager.exit_current_scope()

    def visit_assign_node(self, node: ASTNodes.AssignNode):
        """
        Návštěvník uzlu přiřazení.

        Parametry:
            - node (ASTNodes.AssignNode): Uzel přiřazení.

        Výjimky:
            - SemanticOtherError: Při pokusu o přiřazení do formálního parametru.
            - SemanticVariableCollisionError: Pokud dojde ke kolizi formálních parametrů.
        """
        # Kontrola kolize přiřazení do formálního parametru
        identifier = node.identifierNode.identifier
        if self._symtable.scopeManager.is_formal_parameter(identifier):
            raise SemanticVariableCollisionError(
                f"Assignment to formal parameter ({identifier}) is not allowed."
                )
        # Pokud proměnná nebyla definována v aktuálním (či nadřazeném) rozsahu, definujeme ji.
        if not self._symtable.scopeManager.is_defined(identifier):
            self._symtable.scopeManager.define_variable(identifier)

        # Analyzujeme přiřazení
        node.identifierNode.visit_by(self)  # L-hodnota
        node.exprNode.visit_by(self)  # R-hodnota

    def visit_expression_node(self, node: ASTNodes.ExpressionNode):
        """
        Návštěvník uzlu výrazu.

        Parametry:
            - node (ASTNodes.ExpressionNode): Uzel výrazu.

        Výjimky:
            - SemanticOtherError: Pokud je volána metoda na nedefinovanou
                                  třídu nebo proměnnou.
            - SemanticArityError: Pokud počet argumentů metody neodpovídá
                                  očekávanému počtu.
        """
        # Projdeme všechny podvýrazy
        if isinstance(node.receiver, ASTNodes.LiteralNode):
            self.visit_literal_node(node.receiver)  # literál
            receiverId = node.receiver.literalType
        elif isinstance(node.receiver, ASTNodes.IdentifierNode):
            self.visit_identifier_node(node.receiver)  # třída, proměnná
            receiverId = node.receiver.identifier
        elif isinstance(node.receiver, ASTNodes.BlockNode):
            self.visit_block_node(node.receiver)  # blokový literál
            return
        elif isinstance(node.receiver, ASTNodes.ExpressionNode):
            self.visit_expression_node(node.receiver)  # odeslání zprávy
            return
        else:
            receiverId = str(node.receiver)  # jiný typ uzlu (např. 'self', 'super')

        # Projdeme všechny argumenty, které se předávají metodě
        for arg in node.argNodeList:
            arg.visit_by(self)

        # Analýza třídních a instančních metod
        if node.selector:
            if receiverId and receiverId[0].isupper():
                self._handle_class_method(node, receiverId)
            else:
                self._handle_instance_method(node, receiverId)

    def visit_identifier_node(self, node: ASTNodes.IdentifierNode):
        """
        Návštěvník uzlu proměnné nebo třídy.

        Parametry:
            - node (ASTNodes.IdentifierNode): Uzel proměnné nebo třídy.

        Výjimky:
            - SemanticUndefinedSymbolError: Pokud proměnná nebo třída
                                            není definována.
        """
        identifier = node.identifier
        # Rozlišení mezi proměnnou a třídou
        if identifier[0].isupper():
            # Kontrola existence třídy
            if not self._symtable.classManager.get_class_symbol(identifier):
                raise SemanticUndefinedSymbolError(
                    f"Class '{identifier}' is not defined."
                    )
        else:
            # Kontrola existence proměnné
            if not self._symtable.scopeManager.is_defined(identifier):
                raise SemanticUndefinedSymbolError(
                    f"Variable '{identifier}' is not defined."
                    )

    def visit_literal_node(self, node: ASTNodes.LiteralNode):
        """
        Návštěvník uzlu literálu.

        Parametry:
            - node (ASTNodes.LiteralNode): Uzel literálu.
        """
        pass  # Literály mají zřejmou hodnotu, není třeba nic kontrolovat

    def _handle_class_method(self, node, receiverId):
        """
        Zpracuje volání třídní metody.

        Parametry:
            - node (ASTNodes.ExpressionNode): Uzel výrazu.
            - receiverId (str): Identifikátor třídy.

        Výjimky:
            - SemanticUndefinedSymbolError: Pokud třída nemá danou metodu.
            - SemanticArityError: Nesoulad v počtu argumentů.
        """
        methodSymbol = self._symtable.classManager.get_method_symbol(receiverId, node.selector)

        # Pokud jde o složený selektor
        if methodSymbol is None and ":" in node.selector:
            self._check_combined_selector(node, receiverId)
            return

        # Kontrola, zda třída obsahuje metodu
        if methodSymbol is None:
            raise SemanticUndefinedSymbolError(
                f"Class '{receiverId}' doesn't know any class method '{node.selector}'."
                )

        # Kontrola správného arity bezparametrické metody
        actualParamCount = len(node.argNodeList)
        expectedParamCount = methodSymbol.get_param_count()
        if expectedParamCount != actualParamCount:
            raise SemanticArityError(
                f"Class method '{node.selector}' of class '{receiverId}' expects "
                f"{expectedParamCount} arguments, but was given {actualParamCount}."
                )

    def _handle_instance_method(self, node: ASTNodes.MethodNode, receiverId: str):
        """
        Zpracuje volání instanční metody.

        Parametry:
            - node (ASTNodes.Metody): Uzel metody.
            - receiverId (str): Identifikátor proměnné.

        Výjimky:
            - SemanticUndefinedSymbolError: Pokud proměnná není definována.
            - SemanticArityError: Nesoulad v počtu argumentů.
        """
        # Pokud je to 'self', kontrolujeme existenci metody v aktuální třídě
        if receiverId == "self":
            methodSymbol = self._symtable.classManager.get_method_symbol(
                self._currentClass, node.selector
                )
            if methodSymbol is not None:
                actualParamCount = len(node.argNodeList)
                expectedParamCount = methodSymbol.get_param_count()
                if actualParamCount != expectedParamCount:
                    raise SemanticArityError(
                        f"Instance method '{node.selector}' of class '{self._currentClass}'"
                        f"expects {expectedParamCount} arguments, but was given "
                        f"{actualParamCount}."
                        )
        # Pro obecnou proměnnou kontrolujeme jen, jestli je definovaná.
        else:
            if not self._symtable.scopeManager.is_defined(receiverId):
                raise SemanticUndefinedSymbolError(
                    f"Variable '{receiverId}' is not defined."
                    )

    def _check_combined_selector(self, node, receiverId: str):
        """
        Zkontroluje složený selektor metod.

        Parametry:
            - node (ASTNodes.ExpressionNode): Uzel výrazu.
            - receiverId (str): Identifikátor třídy.

        Výjimky:
            - SemanticUndefinedSymbolError: Pokud složený selektor není správně
                                            uspořádán nebo metoda neexistuje.
            - SemanticArityError: Pokud počet argumentů metody neodpovídá
                                  očekávanému počtu.
        """
        # Rozdělíme složený selektor na dílčí části
        splitSelector = node.selector.split(":")

        # Kontrola, že za "startsWith:" následuje "endsBefore:" a že za "ifTrue:" následuje "ifFalse:"
        for i, part in enumerate(splitSelector):
            # Pozor na zkratkové vyhodnocování v podmínkách
            if part == "startsWith" and (i + 1 >= len(splitSelector) or splitSelector[i + 1] != "endsBefore"):
                raise SemanticUndefinedSymbolError(
                    f"Method 'startsWith:' must be followed by 'endsBefore:'."
                    )
            if part == "ifTrue" and (i + 1 >= len(splitSelector) or splitSelector[i + 1] != "ifFalse"):
                raise SemanticUndefinedSymbolError(
                    f"Method 'ifTrue:' must be followed by 'ifFalse:'."
                    )

        # Zkontrolujeme, zda součet arit všech dílčích částí sedí s počtem předaných argumentů
        expectedParamCount = self._get_expected_param_count(splitSelector, receiverId)
        actualParamCount = len(node.argNodeList)
        if expectedParamCount != actualParamCount:
            raise SemanticArityError(
                f"Combined method call '{node.selector}' of class '{receiverId}' "
                f"expects {expectedParamCount} arguments, but got {actualParamCount}."
                )

    def _get_expected_param_count(self, splitSelector, receiverId):
        """
        Získá očekávaný počet parametrů pro složený selektor.

        Parametry:
            - splitSelector (list): Seznam dílčích selektorů.
            - receiverId (str): Identifikátor třídy.

        Návratová hodnota:
            - int: Očekávaný počet parametrů.

        Výjimky:
            - SemanticUndefinedSymbolError: Pokud třída neobsahuje metodu.
        """
        expectedParamCount = 0
        for part in splitSelector:
            part += ":"
            partSymbol = self._symtable.classManager.get_method_symbol(receiverId, part)
            if partSymbol is not None:
                expectedParamCount += partSymbol.get_param_count()
        return expectedParamCount

    def check_cyclic_inheritance(self):
        """
        Zkontroluje cyklickou dědičnost mezi třídami.

        Výjimky:
            - SemanticOtherError: Pokud je detekována cyklická dědičnost.
        """
        visited = set()

        # Projdeme všechny třídy a zkontrolujeme cyklickou dědičnost
        for classSymbol in self._symtable.classManager.get_all_class_symbols():
            classIdentifier = classSymbol.identifier
            # Dokud nedojdeme ke kořeni dědičnosti
            while classIdentifier:
                # Pokud jsme už tuto třídu navštívili, máme cyklickou dědičnost
                if classIdentifier in visited:
                    raise SemanticOtherError(
                        f"Cyclic inheritance detected for class '{classIdentifier}'."
                        )
                # Jinak přidáme třídu do navštívených tříd a pokračujeme v průchodu
                visited.add(classIdentifier)
                parentClass = self._symtable.classManager.get_class_symbol(classIdentifier).parentIdentifier
                classIdentifier = parentClass
            # Vyprázdníme navštívené třídy pro další iteraci
            visited.clear()

### konec souboru 'SemanticAnalyser.py' ###
