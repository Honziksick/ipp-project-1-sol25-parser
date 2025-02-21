"""
********************************************************************************
*                                                                              *
* Název projektu:   Projekt do předmětu IPP 2024/2025 IFJ24:                   *
*                   Úloha 1 - Analyzátor kódu v SOL25 (parse.py)               *
*                                                                              *
* Soubor:           ASTNodes.py                                                *
* Autor:            Jan Kalina <xkalinj00>                                     *
*                                                                              *
* Datum:            18.02.2025                                                 *
* Poslední změna:   xx.xx.2025                                                 *
*                                                                              *
********************************************************************************
"""
"""
@file ASTNodes.py
@author Jan Kalina \<xkalinj00>

@brief
@details
"""

from typing import Any, List
from MyPyModules.CustomErrors import InternalError

class ASTNodes:
    class ASTAbstractNode:
        def visit_by(self, visitor):
            raise InternalError()

    class ProgramNode(ASTAbstractNode):
        def __init__(self, classes:List["ASTNodes.ClassNode"]):
            self.classNodeList = classes

        def visit_by(self, visitor):
            return visitor.visit_program_node(self)

    class ClassNode(ASTAbstractNode):
        def __init__(self, identifier:str, fatherIdentifier:str, methods:List["ASTNodes.MethodNode"]):
            self.id = identifier
            self.father = fatherIdentifier
            self.methodNodeList = methods

        def visit_by(self, visitor):
            return visitor.visit_class_node(self)

    class MethodNode(ASTAbstractNode):
        def __init__(self, selector:str, block:"ASTNodes.BlockNode"):
            self.selector = selector
            self.blockNode = block

        def visit_by(self, visitor):
            return visitor.visit_method_node(self)

    class BlockNode(ASTAbstractNode):
        def __init__(self, parameters:List[str], statements:List["ASTNodes.ASTAbstractNode"]):
            self.paramNodeList = parameters
            self.statementNodeList = statements

        def visit_by(self, visitor):
            return visitor.visit_block_node(self)

    class VarNode(ASTAbstractNode):
        def __init__(self, identifier:str):
            self.id = identifier

        def visit_by(self, visitor):
            return visitor.visit_var_node(self)

    class LiteralNode(ASTAbstractNode):
        def __init__(self, type:str, value:Any):
            self.literalType = type
            self.literalValue = value

        def visit_by(self, visitor):
            return visitor.visit_literal_node(self)

    class AssignNode(ASTAbstractNode):
        def __init__(self, variable:"ASTNodes.VarNode", expression:"ASTNodes.ExprNode"):
            self.varNode = variable
            self.exprNode = expression

        def visit_by(self, visitor):
            return visitor.visit_assign_node(self)

    class ExprNode(ASTAbstractNode):
        def __init__(self, receiver:"ASTNodes", selector:str, args:List["ASTNodes"]):
            self.receiver = receiver
            self.selector = selector
            self.argNodeList = args

        def visit_by(self, visitor):
            return visitor.visit_expr_node(self)

class ASTNodeVisitor:
    def visit_program_node(self, ASTNode):
        raise InternalError() from NotImplementedError()

    def visit_block_node(self, ASTNode):
        raise InternalError() from NotImplementedError()

    def visit_class_node(self, ASTNode):
        raise InternalError() from NotImplementedError()

    def visit_method_node(self, ASTNode):
        raise InternalError() from NotImplementedError()

    def visit_expr_node(self, ASTNode):
        raise InternalError() from NotImplementedError()

    def visit_assign_node(self, ASTNode):
        raise InternalError() from NotImplementedError()

    def visit_var_node(self, ASTNode):
        raise InternalError() from NotImplementedError()

    def visit_literal_node(self, ASTNode):
        raise InternalError() from NotImplementedError()

### konec souboru 'ASTNodes.py' ###
