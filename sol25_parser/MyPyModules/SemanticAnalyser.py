"""
********************************************************************************
*                                                                              *
* Název projektu:   Projekt do předmětu IPP 2024/2025 IFJ24:                   *
*                   Úloha 1 - Analyzátor kódu v SOL25 (parse.py)               *
*                                                                              *
* Soubor:           SemanticAnalyser.py                                        *
* Autor:            Jan Kalina <xkalinj00>                                     *
*                                                                              *
* Datum:            19.02.2025                                                 *
* Poslední změna:   xx.xx.2025                                                 *
*                                                                              *
********************************************************************************
"""
"""
@file SemanticAnalyser.py
@author Jan Kalina \<xkalinj00>

@brief
@details
"""

from MyPyModules.ASTNodes import ASTNodes, ASTNodeVisitor
from MyPyModules.Symtable import Symtable
from MyPyModules.CustomErrors import (SemanticMainRunError, SemanticUndefinedSymbolError,
                                      SemanticArityError, SemanticVariableCollisionError)

class SemanticAnalyser(ASTNodeVisitor):
    def __init__(self):
        self.symtable = Symtable()
        self.currentClass = None  # Pro udržení kontextu aktuálně analyzované třídy

    def analyse_semantic(self, programNode:ASTNodes.ProgramNode):
        """
        1) Načteme vestavěné třídy & metody
        2) Projdeme AST (user definované třídy, metody)
        3) Zkontrolujeme existenci Main.run
        """
        self.symtable.load_builtin_symbols()
        self.visit_program_node(programNode)
        mainClass = self.symtable.get_class_symbol("Main")
        if mainClass is None:
            raise SemanticMainRunError("Chybí třída 'Main'.")
        runMethod = self.symtable.get_method_symbol("Main", "run")
        if runMethod is None:
            raise SemanticMainRunError("Třída 'Main' nemá metodu 'run'.")

        return self.symtable

    def visit_program_node(self, node:ASTNodes.ProgramNode):
        for classNode in node.classNodeList:
            self.visit_class_node(classNode)

    def visit_class_node(self, node:ASTNodes.ClassNode):
        # Vložíme třídu do symbolové tabulky s uvedením nadtřídy.
        self.symtable.insert_class_symbol(node.id, node.father)
        self.currentClass = node.id
        # Projdeme všechny metody dané třídy.
        for methodNode in node.methodNodeList:
            self.visit_method_node(methodNode)
        self.currentClass = None

    def visit_method_node(self, node:ASTNodes.MethodNode):
        if self.currentClass is None:
            raise SemanticUndefinedSymbolError("Metoda mimo třídu!")
        # Vložíme definici metody do symbolové tabulky; kontrola override se provede uvnitř insert_method_symbol.
        self.symtable.insert_method_symbol(self.currentClass, node.selector, node.blockNode)

        self.symtable.enter_new_scope()
        self.symtable.define_pseudovariable("self", "instance_placeholder")
        currentClassSymbol = self.symtable.get_class_symbol(self.currentClass)
        parentClass = currentClassSymbol.parentName if currentClassSymbol else None
        self.symtable.define_pseudovariable("super", ("instance_placeholder", parentClass))

        # Kontrola arity – očekávaný počet parametrů získáme např. z bloku.
        currentArity = len(getattr(node.blockNode, 'paramNodeList', []))
        expectedArity = (node.blockNode.get_parameter_count()
                          if hasattr(node.blockNode, 'get_parameter_count')
                          else currentArity)
        if expectedArity != currentArity:
            raise SemanticArityError(
                f"Metoda '{node.selector}' v třídě '{self.currentClass}' má špatnou aritu. "
                f"Očekává se {expectedArity}, dostalo se {node.arity}."
            )
        # Analyzujeme tělo metody (blok)
        node.blockNode.visit_by(self)
        self.symtable.exit_current_scope()


    def visit_block_node(self, node:ASTNodes.BlockNode):
        # Vstup do nového lokálního rozsahu.
        self.symtable.enter_new_scope()
        # Zpracujeme formální parametry bloku (pokud existují).
        for param in node.paramNodeList:
            if self.symtable.is_defined_in_current_scope(param):
                raise SemanticVariableCollisionError(
                    f"Kolize formálního parametru: {param}"
                )  # chyba 34
            self.symtable.define_parameter(param)
        # Projdeme všechny příkazy (přiřazení apod.) v bloku.
        for statement in node.statementNodeList:
            statement.visit_by(self)
        self.symtable.exit_current_scope()

    def visit_assign_node(self, node:ASTNodes.AssignNode):
        # Kontrola: nelze přiřadit do formálního parametru.
        variableId = node.varNode.id
        if self.symtable.is_formal_parameter(variableId):
            raise SemanticVariableCollisionError(
                f"Není povoleno přiřazení do formálního parametru: {variableId}"
            )
        # Pokud proměnná ještě není definována v aktuálním rozsahu, definujeme ji.
        if not self.symtable.is_defined(variableId):
            self.symtable.define_variable(variableId)
        # Analyzujeme cílový uzel (proměnnou) i výraz přiřazení.
        node.varNode.visit_by(self)
        node.exprNode.visit_by(self)

    def visit_expr_node(self, node:ASTNodes.ExprNode):
        """
        Zpracuje zaslání zprávy (message send) v jazyce SOL25.
        node.receiver = str - buď jméno třídy (např. 'String') nebo jméno proměnné (např. 'x').
        node.selector = 'new', 'from:', 'plus:', ...
        node.argNodeList = list argumentů (AST uzlů).
        """
        if hasattr(node.receiver, "id"):
            receiverId = node.receiver.id
        elif hasattr(node.receiver, "literalType"):
            receiverId = node.receiver.literalType
        else:
            receiverId = str(node.receiver)

        # 1) Navštívíme argumenty (aby se i v nich provedla sémantická kontrola).
        for arg in node.argNodeList:
            arg.visit_by(self)

        # 2) Rozhodneme, zda je to volání **třídní** metody nebo **instanční** metody.
        if receiverId and receiverId[0].isupper():
            # => TŘÍDNÍ METODA
            #   Např. "String from:"
            #   Musíme zkontrolovat, že třída existuje a má danou metodu.
            classSymbol = self.symtable.get_class_symbol(receiverId)
            if classSymbol is None:
                # Chybí definice třídy
                raise SemanticUndefinedSymbolError(
                    f"Nedefinovaná třída '{receiverId}' při volání metody '{node.selector}'."
                )

            # Najdeme metodu
            methodSymbol = self.symtable.get_method_symbol(receiverId, node.selector)
            if methodSymbol is None:
                # Metoda neexistuje
                raise SemanticUndefinedSymbolError(
                    f"Třída '{receiverId}' nezná třídní metodu '{node.selector}'. (chyba 32)"
                )

            # Zkontrolujeme aritu: kolik argumentů => len(node.argNodeList)
            expectedParamCount = methodSymbol.get_param_count()
            actualParamCount = len(node.argNodeList)
            if expectedParamCount != -1 and expectedParamCount != actualParamCount:
                # (pokud by sis zavedl variadiku pro Block)
                raise SemanticArityError(
                    f"Třídní metoda '{node.selector}' v '{receiverId}' očekává {expectedParamCount} argumentů, "
                    f"ale bylo jich předáno {actualParamCount}."
                )

        else:
            # => INSTANČNÍ METODA
            #  a) Ověříme, zda proměnná existuje:
            if not self.symtable.is_defined(receiverId):
                raise SemanticUndefinedSymbolError(
                    f"Proměnná '{receiverId}' není definována (chyba 32)!"
            )

    def visit_var_node(self, node:ASTNodes.VarNode):
        # Pokud proměnná nebyla definována v aktuálním (nebo nějakém nadřazeném) rozsahu,
        if not self.symtable.is_defined(node.id):
            raise SemanticUndefinedSymbolError(f"Proměnná '{node.id}' není definována.")

    def visit_literal_node(self, node:ASTNodes.LiteralNode):
        pass

### konec souboru 'SemanticAnalyser.py' ###
