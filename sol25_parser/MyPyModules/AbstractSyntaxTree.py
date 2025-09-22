"""
********************************************************************************
* Název projektu:   Projekt do předmětu IPP 2024/2025:                         *
*                   Úloha 1 - Analyzátor kódu v SOL25 (parse.py)               *
*                                                                              *
* Soubor:           AbstractSyntaxTree.py                                      *
* Autor:            Jan Kalina <xkalinj00>                                     *
*                                                                              *
* Datum:            18.02.2025                                                 *
* Poslední změna:   22.02.2025                                                 *
*                                                                              *
* Popis:            Tento soubor obsahuje definice uzlů abstraktního           *
*                   syntaktického stromu (AST) pro jazyk SOL25 a obecných      *
*                   návštěvníka pro zpracování těchto uzlů.                    *
********************************************************************************
"""

# Import modulů standardní knihovny
from typing import Any, List

# Import vlastních modulů
from MyPyModules.CustomErrors import InternalError


class ASTNodes:
    """
    Třída `ASTNodes` obsahuje vnořené třídy reprezentující různé typy uzlů
    abstraktního syntaktického stromu (AST) pro jazyk SOL25.

    Vnořené třídy:
        - ASTAbstractNode: Abstraktní třída pro všechny uzly AST.
        - ProgramNode:     Třída reprezentující uzel programu v AST.
        - ClassNode:       Třída reprezentující uzel třídy v AST.
        - MethodNode:      Třída reprezentující uzel metody v AST.
        - BlockNode:       Třída reprezentující uzel bloku v AST.
        - IdentifierNode:  Třída reprezentující uzel proměnné v AST.
        - LiteralNode:     Třída reprezentující uzel literálu v AST.
        - AssignNode:      Třída reprezentující uzel přiřazení v AST.
        - ExpressionNode:  Třída reprezentující uzel výrazu v AST.
    """

    class ASTAbstractNode:
        """
        Abstraktní třída pro všechny uzly AST.

        Metody:
            - visit_by(visitor:ASTNodeVisitor): Metoda pro návštěvu uzlu návštěvníkem.
        """

        def visit_by(self, visitor):
            """
            Metoda pro návštěvu uzlu návštěvníkem.

            Parametry:
                - visitor (ASTNodeVisitor): Návštěvník uzlu.

            Výjimky:
                - InternalError: Pokud není metoda implementována v podtřídě.
            """
            raise InternalError()

    class ProgramNode(ASTAbstractNode):
        """
        Třída reprezentující uzel programu v AST.

        Atributy:
            - classNodeList (ASTNodes.ClassNode): Seznam uzlů tříd.

        Metody:
            - __init__(classes:ASTNodes.ClassNode)
            - visit_by(visitor:ASTNodeVisitor)
        """

        def __init__(self, classes: List["ASTNodes.ClassNode"]):
            """
            Inicializuje uzel programu.

            Parametry:
                - classes (ASTNodes.ClassNode): Seznam uzlů tříd.
            """
            self.classNodeList = classes

        def visit_by(self, visitor):
            return visitor.visit_program_node(self)

    class ClassNode(ASTAbstractNode):
        """
        Třída reprezentující uzel třídy v AST.

        Atributy:
            - identifier (str): Identifikátor třídy.
            - parentIdentifier (str): Identifikátor nadřazené třídy.
            - methodNodeList (ASTNodes.MethodNode): Seznam uzlů metod.

        Metody:
            - __init__(identifier:str, parentIdentifier:str, methods:ASTNodes.MethodNode)
            - visit_by(visitor:ASTNodeVisitor)
        """

        def __init__(self, identifier: str, parentIdentifier: str, methods: List["ASTNodes.MethodNode"]):
            """
            Inicializuje uzel třídy.

            Parametry:
                - identifier (str): Identifikátor třídy.
                - parentIdentifier (str): Identifikátor nadřazené třídy.
                - methods (ASTNodes.MethodNode): Seznam uzlů metod.
            """
            self.identifier = identifier
            self.perentIdentifier = parentIdentifier
            self.methodNodeList = methods

        def visit_by(self, visitor):
            return visitor.visit_class_node(self)

    class MethodNode(ASTAbstractNode):
        """
        Třída reprezentující uzel metody v AST.
        """

        def __init__(self, selector: str, blockNode: "ASTNodes.BlockNode"):
            """
            Inicializuje uzel metody.

            Parametry:
                - selector (str): Selektor metody.
                - blockNode (ASTNodes.BlockNode): Blok uzlů metody.
            """
            self.selector = selector
            self.blockNode = blockNode

        def visit_by(self, visitor):
            return visitor.visit_method_node(self)

    class BlockNode(ASTAbstractNode):
        """
        Třída reprezentující uzel bloku v AST.
        """

        def __init__(self, parameters: List[str], statements: List["ASTNodes"]):
            """
            Inicializuje uzel bloku.

            Parametry:
                - parameters (str): Seznam parametrů bloku.
                - statements (ASTNodes.ASTAbstractNode): Seznam uzlů příkazů.
            """
            self.parameterNodeList = parameters
            self.statementNodeList = statements

        def visit_by(self, visitor):
            return visitor.visit_block_node(self)

    class IdentifierNode(ASTAbstractNode):
        """
        Třída reprezentující uzel proměnné v AST.
        """

        def __init__(self, identifier: str):
            """
            Inicializuje uzel proměnné.

            Parametry:
                - identifier (str): Identifikátor proměnné.
            """
            self.identifier = identifier

        def visit_by(self, visitor):
            return visitor.visit_identifier_node(self)

    class LiteralNode(ASTAbstractNode):
        """
        Třída reprezentující uzel literálu v AST.
        """

        def __init__(self, literalType: str, literalValue: Any):
            """
            Inicializuje uzel literálu.

            Parametry:
                - type (str): Typ literálu.
                - value (Any): Hodnota literálu.
            """
            self.literalType = literalType
            self.literalValue = literalValue

        def visit_by(self, visitor):
            return visitor.visit_literal_node(self)

    class AssignNode(ASTAbstractNode):
        """
        Třída reprezentující uzel přiřazení v AST.
        """

        def __init__(self, identifier: "ASTNodes.IdentifierNode", expression: "ASTNodes.ExpressionNode"):
            """
            Inicializuje uzel přiřazení.

            Parametry:
                - identifier (ASTNodes.IdentifierNode): Uzl proměnné.
                - expression (ASTNodes.ExpressionNode): Uzl výrazu.
            """
            self.identifierNode = identifier
            self.exprNode = expression

        def visit_by(self, visitor):
            return visitor.visit_assign_node(self)

    class ExpressionNode(ASTAbstractNode):
        """
        Třída reprezentující uzel výrazu v AST.
        """

        def __init__(self, receiver: "ASTNodes", selector: str, args: List["ASTNodes"]):
            """
            Inicializuje uzel výrazu.

            Parametry:
                - receiver (ASTNodes): Příjemce výrazu.
                - selector (str): Selektor výrazu.
                - args (ASTNodes): Seznam argumentů výrazu.
            """
            self.receiver = receiver
            self.selector = selector
            self.argNodeList = args

        def visit_by(self, visitor):
            return visitor.visit_expression_node(self)


class ASTNodeVisitor:
    """
    Třída `ASTNodeVisitor` definuje rozhraní pro návštěvníky uzlů AST.
    """

    def visit_program_node(self, ASTNode):
        """
        Návštěvník uzlu programu.

        Parametry:
            - ASTNode (ASTNodes.ProgramNode): Uzel programu.

        Výjimky:
            - InternalError: Pokud není metoda implementována.
        """
        raise InternalError("Method 'visit_program_node' isn't implemented.") \
            from NotImplementedError()

    def visit_block_node(self, ASTNode):
        """
        Návštěvník uzlu bloku.

        Parametry:
            - ASTNode (ASTNodes.BlockNode): Uzel bloku.

        Výjimky:
            - InternalError: Pokud není metoda implementována.
        """
        raise InternalError("Method 'visit_block_node' isn't implemented.") \
            from NotImplementedError()

    def visit_class_node(self, ASTNode):
        """
        Návštěvník uzlu třídy.

        Parametry:
            - ASTNode (ASTNodes.ClassNode): Uzel třídy.

        Výjimky:
            - InternalError: Pokud není metoda implementována.
        """
        raise InternalError("Method 'visit_class_node' isn't implemented.") \
            from NotImplementedError()

    def visit_method_node(self, ASTNode):
        """
        Návštěvník uzlu metody.

        Parametry:
            - ASTNode (ASTNodes.MethodNode): Uzel metody.

        Výjimky:
            - InternalError: Pokud není metoda implementována.
        """
        raise InternalError("Method 'visit_method_node' isn't implemented.") \
            from NotImplementedError()

    def visit_expression_node(self, ASTNode):
        """
        Návštěvník uzlu výrazu.

        Parametry:
            - ASTNode (ASTNodes.ExpressionNode): Uzel výrazu.

        Výjimky:
            - InternalError: Pokud není metoda implementována.
        """
        raise InternalError("Method 'visit_expression_node' isn't implemented.") \
            from NotImplementedError()

    def visit_assign_node(self, ASTNode):
        """
        Návštěvník uzlu přiřazení.

        Parametry:
            - ASTNode (ASTNodes.AssignNode): Uzel přiřazení.

        Výjimky:
            - InternalError: Pokud není metoda implementována.
        """
        raise InternalError("Method 'visit_assign_node' isn't implemented.") \
            from NotImplementedError()

    def visit_identifier_node(self, ASTNode):
        """
        Návštěvník uzlu proměnné.

        Parametry:
            - ASTNode (ASTNodes.IdentifierNode): Uzel proměnné.

        Výjimky:
            - InternalError: Pokud není metoda implementována.
        """
        raise InternalError("Method 'visit_identifier_node' isn't implemented.") \
            from NotImplementedError()

    def visit_literal_node(self, ASTNode):
        """
        Návštěvník uzlu literálu.

        Parametry:
            - ASTNode (ASTNodes.LiteralNode): Uzel literálu.

        Výjimky:
            - InternalError: Pokud není metoda implementována.
        """
        raise InternalError("Method 'visit_literal_node' isn't implemented.") \
            from NotImplementedError()

### konec souboru 'AbstractSyntaxTree.py' ###
