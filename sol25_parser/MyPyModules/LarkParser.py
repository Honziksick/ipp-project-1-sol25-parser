"""
********************************************************************************
*                                                                              *
* Název projektu:   Projekt do předmětu IPP 2024/2025 IFJ24:                   *
*                   Úloha 1 - Analyzátor kódu v SOL25 (parse.py)               *
*                                                                              *
* Soubor:           LarkParser.py                                              *
* Autor:            Jan Kalina <xkalinj00>                                     *
*                                                                              *
* Datum:            18.02.2025                                                 *
* Poslední změna:   xx.xx.2025                                                 *
*                                                                              *
********************************************************************************
"""
"""
@file LarkParser.py
@author Jan Kalina \<xkalinj00>

@brief
@details
"""

from lark import Lark, Transformer
from MyPyModules.ASTNodes import ASTNodes as AST

###################################################################################
# Zdroj (manuál): lark-parser.readthedocs.io/en/latest/_static/lark_cheatsheet.pdf
###################################################################################

# Konstanta obsahující definici lexikálních a syntaktických pravidel SOL25
SOL25_GRAMMAR = r"""
    ////////////////////////////////////////////////////////////////////////////
    //                                                                        //
    //            NĚKOLIK SPECIFIK ZÁPISU PARSERU V MODULU "lark"             //
    //                                                                        //
    ////////////////////////////////////////////////////////////////////////////

    // =========================================================================
    // ?NonT: expand    operátor '?' nyvtvoří uzel v AST
    // X*               0 nebo více opakování X
    // X+               1 nebo více opakování X
    // X?               nanejvýš jednou (0 nebo 1 výskyt X), náhrada ε-pravidla
    // (X Y)*           0 nebo více opakování X Y
    // (X Y)+           1 nebo více opakování X Y
    // (X Y)?           nanejvýš jednou (0 nebo 1 výskyt X Y), náhrada ε-pravidla
    // (Keyword | Id)   POZOR, vyhodnocuje se zleva => 'Keyword' má vyšší prioritu
    // =========================================================================


    ////////////////////////////////////////////////////////////////////////////
    //                                                                        //
    //                   TERMINÁLY (tokeny) V JAZYCE SOL25                    //
    //                                                                        //
    ////////////////////////////////////////////////////////////////////////////

    // Klíčová slova
    tClass:         "class"
    tSelf:          "self"
    tSuper:         "super"
    tNil:           "nil"
    tTrue:          "true"
    tFalse:         "false"

    // Speciální znaky
    tColon:         ":"
    tSemicolon:     ";"
    tLeftRoundBr:   "("
    tRightRoundBr:  ")"
    tLeftCurlyBr:   "{"
    tRightCurlyBr:  "}"
    tLeftSquareBr:  "["
    tRightSquareBr: "]"
    tPipe:          "|"
    tDot:           "."

    // Operátory
    tAssignOp:      ":="

    // Identifikátory
    tId:            /[a-z_][A-Za-z0-9_]*/
    tIdSelector:    /[a-z_][A-Za-z0-9_]*:/
    tSelectorId:    /:[a-z_][A-Za-z0-9_]*/
    tCid:           /[A-Z][A-Za-z0-9]*/
    CID:            (BUILT_IN_CLASS | tCid)

    // Literály
    tIntLiteral:    /[+-]?\d+/
    tStringLiteral: /'(\\.|[^'\\])*'/

    // Vestavěné třídy
    BUILT_IN_CLASS: "Object"
                  | "Nil"
                  | "Integer"
                  | "String"
                  | "Block"
                  | "True"
                  | "False"

    // Vestavěné metody
    BUILT_IN_METHOD: "new"
                   | "from:"
                   | "identicalTo:"
                   | "equalTo:"
                   | "asString"
                   | "asInteger"
                   | "isNumber"
                   | "isString"
                   | "isBlock"
                   | "isNil"
                   | "greaterThan:"
                   | "plus:"
                   | "minus:"
                   | "multiplyBy:"
                   | "divBy:"
                   | "timesRepeat:"
                   | ("value:")+
                   | "read"
                   | "print"
                   | "concatenateWith:"
                   | "startsWith:endsBefore:"
                   | "whileTrue:"
                   | "not"
                   | "and:"
                   | "or:"
                   | "ifTrue:ifFalse:"

    ////////////////////////////////////////////////////////////////////////////
    //                                                                        //
    //                   GRAMATICKÁ PRAVIDLA V JAZYCE SOL25                   //
    //                                                                        //
    ////////////////////////////////////////////////////////////////////////////

    // Startovacím pravidlem je "PROGRAM"
    ?START: PROGRAM


    // =============================
    // Základní struktura programu
    // =============================

    // Program -> Class Program | ε
    PROGRAM: (CLASS)*

    // Class -> class <Cid> : <Cid> { Method }
    CLASS: tClass CID tColon CID tLeftCurlyBr METHOD tRightCurlyBr

    // Method -> Selector Block Method | ε
    METHOD: (SELECTOR BLOCK)*


    // ==============================
    // Selektory při definici metod
    // ==============================

    // Selector -> <id> | <id:> SelectorTail
    SELECTOR: tId
            | tIdSelector SELECTOR_TAIL

    // SelectorTail -> <id:> SelectorTail | ε
    SELECTOR_TAIL: (tIdSelector)*


    // =======
    // Bloky
    // =======

    // Block -> [ BlockPar | BlockStat ]
    BLOCK:      tLeftSquareBr BLOCK_PAR tPipe BLOCK_STAT tRightSquareBr

    // BlockPar -> <:id> BlockPar | ε
    BLOCK_PAR:  (tSelectorId)*

    // Selector -> <id> := Expr . BlockStat | ε
    BLOCK_STAT: (tId tAssignOp EXPR tDot)*


    // =========================
    // Výrazy a zasílání zpráv
    // =========================

    // Expr -> ExprBase ExprTail
    EXPR: EXPR_BASE EXPR_TAIL

    // ExprTail -> <id> | ExprSel
    EXPR_TAIL: tId
             | EXPR_SEL

    // ExprSel -> <id:> ExprBase ExprSel | ε
    EXPR_SEL: (tIdSelector EXPR_BASE)*

    // ExprBase -> <int> | <str> | <id> | <Cid> | Block | ( Expr )
    EXPR_BASE: tIntLiteral
             | tStringLiteral
             | tNil
             | tTrue
             | tFalse
             | tSelf
             | tSuper
             | CID
             | BLOCK
             | tLeftRoundBr EXPR tRightRoundBr
             | tId


    ////////////////////////////////////////////////////////////////////////////
    //                                                                        //
    //                 KOMENTÁŘE A BÍLÉ ZNAKY V JAZYCE SOL25                  //
    //                                                                        //
    ////////////////////////////////////////////////////////////////////////////

    // Komentáře
    COMMENT: /"[^"]*"/
    %ignore COMMENT

    // Bílé znaky
    %ignore /[ \n\t\r]+/
"""


#####################################################################
# Zdroj (manuál): lark-parser.readthedocs.io/en/stable/visitors.html
#####################################################################

class LarkTransformer(Transformer):
    def create_AST_program_node(self, children):
        """
        Program -> Class Program | ε
        """
        return AST.ProgramNode(children)

    def class_def(self, children):
        """
        Class -> class <Cid> : <Cid> { Method }
        """
        identifier = children[0]
        fatherIdentifier = children[1]
        methods = children[2]
        return AST.ClassNode(identifier, fatherIdentifier, methods)

    def method_def(self, children):
        """
        Method -> Selector Block Method | ε
        """
        selector = children[0]
        blocks = children[1]
        return AST.MethodNode(selector, [blocks])

    def block_def(self, children):
        """
        Block -> [ BlockPar | BlockStat ]
        """
        parameters = children[0]
        statements = children[1]
        return AST.BlockNode(parameters, statements)

    def assign_stat(self, children):
        """
        Selector -> <id> := Expr . BlockStat | ε
        """
        variable = children[0]
        expression = children[1]
        return AST.AssignNode(variable, expression)

    def var_use(self, token_list):
        # Např. [ "x" ] => VarNode("x")
        return AST.VarNode(str(token_list[0]))

    def literal_int(self, token_list):
        # Např. [ Token(INT,'42') ] => LiteralNode("Integer", 42)
        val = int(token_list[0])
        return AST.LiteralNode("Integer", val)

    def literal_string(self, token_list):
        # Např. "'ahoj'" => LiteralNode("String", "ahoj")
        raw = str(token_list[0])
        content = raw.strip("'")
        return AST.LiteralNode("String", content)

    def send_expr(self, children):
        # [ receiverNode, selectorString, arg1Node, arg2Node, ... ]
        receiver = children[0]
        selector = children[1]
        args = children[2:]
        return AST.SendNode(receiver, selector, args)


class LarkParser:
    def __init__(self):
        self._larkParser = Lark(SOL25_GRAMMAR, parser="lalr", start="start")
        self._ASTBuilder = LarkTransformer()

    def parse(self, SOL25Code):
        try:
            larkParseTree = self._larkParser.parse(SOL25Code)
            ASTRoot = self._ASTBuilder.transform(larkParseTree)
            return ASTRoot

        except Exception as e:
            raise e

### konec souboru 'LarkParser.py' ###
