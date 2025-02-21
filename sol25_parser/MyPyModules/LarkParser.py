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

import re
from lark import Lark, Transformer, UnexpectedCharacters, UnexpectedToken, visitors
from MyPyModules.CustomErrors import LexicalError, SyntaxError
from MyPyModules.ASTNodes import ASTNodes as AST

################################################################################
#                                                                              #
#                NĚKOLIK SPECIFIK ZÁPISU PARSERU V MODULU "lark"               #
#                  Zdroj (manuál): lark-parser.readthedocs.io                  #
#                                                                              #
################################################################################
# ==============================================================================
# Konvence: gramatika je definována jako hodnota KONSTANTY
#         : Terminály (tokeny) se zapisují velkými písmeny (v lark.Lark)
#         : NEterminály se zapisují písmeny písmeny (v lark.Lark)
#         : metody v lark.Transformer musí být pojmenovány stejně jako
#           neterminál na levé straně pravidla, popř. terminál
#         : u pravidla s více různými možnými pravými stranami oddělujeme
#           pravé strany promocí '|'
#         : uvnitř konstanty s gramatikou lze psát jednořádkové komentář
#           uvzoené pomocí '//'
#         : vyhazuje dva typy vyjímek 'UnexpectedCharacters' a 'UnexpectedToken'
# ==============================================================================
# _TERMINAL: ...   hodnota tokenu se neuloží do ParseTree díky prefixu '_'
# ?non_term: ...   operátor '?' nevloží uzel pro toto pravidlo do ParseTree
# X*               0 nebo více opakování X
# X+               1 nebo více opakování X
# X?               nanejvýš jednou (0 nebo 1 výskyt X), náhrada ε-pravidla
# (X Y)*           0 nebo více opakování X Y
# (X Y)+           1 nebo více opakování X Y
# (X Y)?           nanejvýš jednou (0 nebo 1 výskyt X Y), náhrada ε-pravidla
# (Keyword | Id)   POZOR, vyhodnocuje se zleva => 'Keyword' má vyšší prioritu
# %ignore cokoliv  změní význam 'cokoliv' na bílý znak a při parsování odignoruje
# ==============================================================================

# Konstanta obsahující definici lexikálních a syntaktických pravidel SOL25
SOL25_GRAMMAR = r"""
    ////////////////////////////////////////////////////////////////////////////
    //                                                                        //
    //                   TERMINÁLY (tokeny) V JAZYCE SOL25                    //
    //                                                                        //
    ////////////////////////////////////////////////////////////////////////////

    // Klíčová slova
    _CLASS: "class"
    SELF:  "self"
    SUPER: "super"
    NIL:   "nil"
    TRUE:  "true"
    FALSE: "false"

    // Speciální znaky
    _COLON:                ":"
    _SEMICOLON:            ";"
    _LEFT_ROUND_BRACKET:   "("
    _RIGHT_ROUND_BRACKET:  ")"
    _LEFT_CURLY_BRACKET:   "{"
    _RIGHT_CURLY_BRACKET:  "}"
    _LEFT_SQUARE_BRACKET:  "["
    _RIGHT_SQUARE_BRACKET: "]"
    _PIPE:                 "|"
    _DOT:                  "."

    // Operátory
    _WALRUS: ":="

    // Literály
    INT_LITERAL:    /[+-]?\d+/
    STRING_LITERAL: /'(\\(?:[n'\\])|[^'\\])*'/

    // Identifikátory
    ID:          /[a-z_][A-Za-z0-9_]*/
    ID_SELECTOR: /[a-z_][A-Za-z0-9_]*:/
    SELECTOR_ID: /:[a-zA-Z_][A-Za-z0-9_]*/
    CID:         /[A-Z][A-Za-z0-9]*/

    ////////////////////////////////////////////////////////////////////////////
    //                                                                        //
    //                   GRAMATICKÁ PRAVIDLA V JAZYCE SOL25                   //
    //                                                                        //
    ////////////////////////////////////////////////////////////////////////////

    // Startovacím pravidlem je "program"
    ?start: program


    // =============================
    // Základní struktura programu
    // =============================

    // Program -> Class Program | ε
    program: (class_definition)*

    // Class -> class <Cid> : <Cid> { Method }
    class_definition: _CLASS CID _COLON CID _LEFT_CURLY_BRACKET method_definition _RIGHT_CURLY_BRACKET

    // Method -> Selector Block Method | ε
    method_definition: (selector block)*


    // ==============================
    // Selektory při definici metod
    // ==============================

    // Selector -> <id> | <id:> SelectorTail
    selector: ID
            | ID_SELECTOR selector_tail

    // SelectorTail -> <id:> SelectorTail | ε
    selector_tail: (ID_SELECTOR)*


    // =======
    // Bloky
    // =======

    // Block -> [ BlockPar | BlockStat ]
    block: _LEFT_SQUARE_BRACKET block_parameter _PIPE block_statement _RIGHT_SQUARE_BRACKET

    // BlockPar -> <:id> BlockPar | ε
    block_parameter: (SELECTOR_ID)*

    // BlockStat -> <id> := Expr . BlockStat | ε
    block_statement: (ID _WALRUS expression _DOT)*


    // =========================
    // Výrazy a zasílání zpráv
    // =========================

    // Expr -> ExprBase ExprTail
    expression: expression_base expression_tail

    // ExprTail -> <id> | ExprSel
    expression_tail: ID
                   | expression_selector

    // ExprSel -> <id:> ExprBase ExprSel | ε
    expression_selector: (ID_SELECTOR expression_base)*

    // ExprBase -> <int> | <str> | <id> | <Cid> | Block | ( Expr )
    expression_base: INT_LITERAL
                   | STRING_LITERAL
                   | NIL
                   | TRUE
                   | FALSE
                   | SELF
                   | SUPER
                   | CID
                   | block
                   | _LEFT_ROUND_BRACKET expression _RIGHT_ROUND_BRACKET
                   | ID


    ////////////////////////////////////////////////////////////////////////////
    //                                                                        //
    //                 KOMENTÁŘE A BÍLÉ ZNAKY V JAZYCE SOL25                  //
    //                                                                        //
    ////////////////////////////////////////////////////////////////////////////

    // Komentáře
    COMMENT: /"[^"]*"/
    %ignore COMMENT

    // Bílé znaky
    %import common.WS
    %ignore WS
"""


#####################################################################
# Zdroj (manuál): lark-parser.readthedocs.io/en/stable/visitors.html
#####################################################################

class LarkTransformer(Transformer):
    def program(self, args):
        """
        Program -> Class Program | ε
        """
        return AST.ProgramNode(args)

    def class_definition(self, args):
        """
        Class -> class <Cid> : <Cid> { Method }
        """
        classIdentifier = str(args[0])
        classFather = str(args[1])
        classMethodList = args[2] if len(args) > 2 else []

        # Pokud metoda v pravidle vrací seznam, zajistíme, že máme list
        #if not isinstance(classMethodList, list):
        #    classMethodList = [classMethodList]

        return AST.ClassNode(classIdentifier, classFather, classMethodList)

    def method_definition(self, args):
        """
        Method -> Selector Block Method | ε
        """
        # args je seznam s následnými tokeny: [selector, block, selector, block, ...]
        methodList = []

        for i in range(0, len(args), 2):
            methodSelector = args[i]
            methodBlock = args[i+1]
            methodList.append(AST.MethodNode(methodSelector, methodBlock))
        return methodList

    def selector(self, args):
        """
        Selector -> <id> | <id:> SelectorTail
        """
        # Bezparametrický selektor - args[0] se vrací jako string <id>
        if len(args) == 1:
            return str(args[0])

        # Parametrický selektor - args[0] (řetězec) <id:>, args[1] SelectorTail (seznam)
        else:
            selectorHead = str(args[0])
            selectorTail = "".join(args[1])  # selector_tail vrací seznam selectorů
            return selectorHead + selectorTail

    def selector_tail(self, args):
        """
        SelectorTail -> <id:> SelectorTail | ε
        """
        return [str(selector) for selector in args]

    def block(self, args):
        """
        Block -> [ BlockPar | BlockStat ]
        """
        blockParameterList = args[0] if len(args) > 0 else []
        blockStatementList = args[1] if len(args) > 1 else []
        return AST.BlockNode(blockParameterList, blockStatementList)

    def block_parameter(self, args):
        """
        BlockPar -> <:id> BlockPar | ε
        """
        return [str(selector) for selector in args]

    def block_statement(self, args):
        """
        BlockStat -> <id> := Expr . BlockStat | ε
        """
        blockStatementList = []
        for i in range(0, len(args) - 1, 2):
            assignToVariable = args[i]
            expression = args[i + 1]
            variableNode = AST.VarNode(str(assignToVariable))
            assignNode = AST.AssignNode(variableNode, expression)
            blockStatementList.append(assignNode)
        return blockStatementList

    def expression(self, args):
        """
        Expr -> ExprBase ExprTail
        """
        expressionBase = args[0]
        if len(args) == 1:
            return expressionBase
        else:
            expressionTail = args[1]

            # Buď je expressionTail jednoduché volání metody bez argumentů
            if isinstance(expressionTail, str):
                return AST.ExprNode(expressionBase, expressionTail, [])

            # Nebo je expressionTail seznam ve tvaru [ID_SELECTOR, expression_base, ...]
            elif isinstance(expressionTail, list):
                currBase = expressionBase
                for i in range(0, len(expressionTail), 2):
                    sel = expressionTail[i]
                    arg = expressionTail[i+1]
                    currBase = AST.ExprNode(currBase, sel, [arg])
                return currBase

            # Pro neučekávané hodnoty (ani str, ani list)
            else:
                return expressionBase

    def expression_tail(self, args):
        """
        ExprTail -> <id> | ExprSel
        """
        return args[0]

    def expression_selector(self, args):
        """
        ExprSel -> <id:> ExprBase ExprSel | ε
        """
        # Vrací list, kde každá dvojice je [selector, expression_base]
        expressionSelector = []

        for i in range(0, len(args), 2):
            expressionSelector.append(str(args[i]))
            expressionSelector.append(args[i+1])

        return expressionSelector

    def expression_base(self, args):
        """
        ExprBase -> <int> | <str> | <id> | <Cid> | Block | ( Expr )
        """
        if isinstance(args[0], str):
            return AST.VarNode(args[0])
        return args[0]

    # --- Tokenové transformace ---
    def INT_LITERAL(self, token):
        """
        Vytvoří uzel AST pro literál typu Integer
        """
        return AST.LiteralNode("Integer", int(token))

    def STRING_LITERAL(self, token):
        """
        Vytvoří uzel AST pro literál typu String
        """
        identifier = str(token)
        return AST.LiteralNode("String", identifier.strip("'"))

    def NIL(self, token):
        """
        Vytvoří uzel AST pro literál typu Nil
        """
        return AST.LiteralNode("Nil", None)

    def TRUE(self, token):
        """
        Vytvoří uzel AST pro literál typu bool s hodnotou 'true'
        """
        return AST.LiteralNode("Bool", True)

    def FALSE(self, token):
        """
        Vytvoří uzel AST pro literál typu bool s hodnotou 'false'
        """
        return AST.LiteralNode("Bool", False)

    def SELF(self, token):
        """

        """
        return AST.VarNode("self")

    def SUPER(self, token):
        """

        """
        return AST.VarNode("super")

    def ID(self, token):
        """
        Vrátí identifikátor <id> a zkontroluje, že odpovídá regexu: [a-z_][A-Za-z0-9_]*
        """
        identifier = str(token)
        pattern = r'^[a-z_][A-Za-z0-9_]*$'
        if not re.fullmatch(pattern, identifier):
            raise LexicalError(f"Neplatný identifikátor <id> '{identifier}'")
        return identifier

    def ID_SELECTOR(self, token):
        """
        Vrátí identifikátor z původního tokenu <id:> a zkontroluje, že odpovídá
        regexu: [a-z_][A-Za-z0-9_]*:
        """
        identifier = str(token)
        pattern = r'^[a-z_][A-Za-z0-9_]*:$'
        if not re.fullmatch(pattern, identifier):
            raise LexicalError(f"Neplatný identifikátor <id:> '{identifier}'")
        return identifier

    def SELECTOR_ID(self, token):
        """
        Vrátí identifikátor z původního tokenu <:id> a zkontroluje, že odpovídá
        regexu: :[a-z_][A-Za-z0-9_]*
        """
        identifier = str(token)
        pattern = r'^:[a-z_][A-Za-z0-9_]*$'
        if not re.fullmatch(pattern, identifier):
            raise LexicalError(f"Neplatný identifikátor <:id> '{identifier}'")
        return identifier[1:]

    def CID(self, token):
        """
        Vrátí identifikátor třidy <Cid> a zkontroluje, že odpovídá
        regexu: [A-Z][A-Za-z0-9]*
        """
        identifier = str(token)
        pattern = r'^[A-Z][A-Za-z0-9]*$'
        if not re.fullmatch(pattern, identifier):
            raise LexicalError(f"Neplatný identifikátor třídy <Cid> '{identifier}'")
        return identifier

class LarkParser:
    def __init__(self):
        self._larkParser = Lark(SOL25_GRAMMAR, parser="lalr", start="start", debug=True)
        self._ASTBuilder = LarkTransformer()

    def parse_code(self, SOL25Code):
        try:
            larkParseTree = self._larkParser.parse(SOL25Code)
        except UnexpectedCharacters as e:
            raise LexicalError() from e
        except UnexpectedToken as e:
            raise SyntaxError() from e
        except Exception:
            raise

        try:
            ASTRoot = self._ASTBuilder.transform(larkParseTree)
            return ASTRoot
        except visitors.VisitError as e:
            raise LexicalError(str(e.orig_exc.errorDetail)) from e
        except Exception:
            raise

### konec souboru 'LarkParser.py' ###
