"""
********************************************************************************
*                                                                              *
* Název projektu:   Projekt do předmětu IPP 2024/2025 IFJ24:                   *
*                   Úloha 1 - Analyzátor kódu v SOL25 (parse.py)               *
*                                                                              *
* Soubor:           test.py                                                    *
* Autor:            Jan Kalina <xkalinj00>                                     *
*                                                                              *
* Datum:            18.02.2025                                                 *
* Poslední změna:   15.03.2025                                                 *
*                                                                              *
* Popis:            Testovací skript pro analyzátor kódu v SOL25 využívající   *
*                   pytest. Za testy děkuji Markovi z VUT FIT.                 *
*                                                                              *
********************************************************************************
"""

import sys         # path.append()
import io          # StringIO()
import os          # path.dirname(), path.abspath(), path.exists(), path.join(), makedirs()
import pytest      # monkeypatch
import inspect     # stack()
import contextlib  # redirect_stdout()
import xml.etree.ElementTree as ET
import subprocess
import re

# Import skriptu 'parse.py'
currentDirectory = os.path.dirname(os.path.abspath(__file__))
parentDirectory = os.path.abspath(os.path.join(currentDirectory, os.pardir))
sys.path.append(parentDirectory)
import parse  # main()


################################################################################
#                                                                              #
#                                  TEST-UTILS                                  #
#                                                                              #
################################################################################

def run_parse(SOL25Code, monkeypatch):
    monkeypatch.setattr(sys, "stdin", io.StringIO(SOL25Code))
    monkeypatch.setattr(sys, "argv", ["parse.py"])

    outputFolder = os.path.join(currentDirectory, "xml")
    if not os.path.exists(outputFolder):
        os.makedirs(outputFolder)

    caller = inspect.stack()[1].function
    XMLFile = os.path.join(outputFolder, f"{caller}.xml")

    with open(XMLFile, "w") as f_out, contextlib.redirect_stdout(f_out):
        try:
            parse.main()
            monkeypatch.setattr(sys, "argv", [])
        except SystemExit as e:
            if e.code == 0:
                return 0
            else:
                return 42
        except Exception as e:
            return e.errorCode

def run_valid_test(input, expected_output):
    process = subprocess.run(
        ["python3.11", "../parse.py"],
        input=input,
        capture_output=True,
        text=True
        )

    print(process.stdout)

    assert process.returncode == 0

    assert len(process.stderr) == 0
    assert len(process.stdout) != 0

    print(expected_output)
    print(process.stdout)
    assert compare_xml_strings(expected_output, process.stdout)

def normalize_children(children):
    children = sorted(children, key=lambda e: (e.tag, list(e.attrib.items())))
    return children

def compare_xml_elements(elem1, elem2):
    if elem1.tag != elem2.tag:
        return False
    if elem1.attrib != elem2.attrib:
        return False
    if len(elem1) != len(elem2):
        return False

    children1 = normalize_children(list(elem1))
    children2 = normalize_children(list(elem2))

    for child1, child2 in zip(children1, children2):
        if not compare_xml_elements(child1, child2):
            return False
    return True

def compare_xml_strings(xml_string1, xml_string2):
    try:
        elem1 = ET.fromstring(str_to_xml_s(xml_string1))
        elem2 = ET.fromstring(str_to_xml_s(xml_string2))
        return compare_xml_elements(elem1, elem2)
    except ET.ParseError:
        return False

def str_to_xml_s(x):
    return ET.tostring(
        ET.fromstring(
            re.sub(r'&nbsp;', '\\\\n',
                   re.sub(r'\s+=\s+', '=',
                          re.sub(r'<\s+', '<',
                                 re.sub(r'\s+>', '>',
                                        re.sub(r'</\s+', '</',
                                               re.sub(r'\s+\/>', '/>',
                                                      "".join(re.findall(r'<[^<>]*>', x.strip()))
                                                      )))))))).decode('utf-8')

def run_arg_test(args, expected_code):
    args = ["python3.11", "../parse.py"] + args
    process = subprocess.run(
        args,
        capture_output=True,
        text=True
        )

    assert process.returncode == expected_code

    if expected_code == 0:
        assert len(process.stdout) != 0
    else:
        assert len(process.stderr) != 0
################################################################################
#                                                                              #
#                          TESTY LEXIKÁLNÍ SPRÁVNOSTI                          #
#                                                                              #
################################################################################

def test_lex_bad_unclosed_comment1(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|
                "abc
                A_BH_oj := 10.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 21

def test_lex_bad_unclosed_comment2(monkeypatch):
    SOL25Code = """
        class Main : Object {
            "Toto je neuzavretý komentár
            run [| |]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 21

def test_lex_bad_num_literal1(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|
                x := +-12.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 21

def test_lex_bad_num_literal2(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|
                x := -+12.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 21

def test_lex_bad_num_literal3(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|
                x := -.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 21

def test_lex_bad_num_literal4(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|
                x := +-.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 21

def test_lex_bad_num_literal5(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|
                x := -0,10.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 21

def test_lex_bad_str_literal1(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|
                x := '\\a'.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 21

def test_lex_bad_str_literal2(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|
                x := '\\n".
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 21

def test_lex_bad_str_literal3(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|
                x := 'abc.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 21

def test_lex_bad_str_literal4(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|
                x := 'Nesprávny escape: \\x'.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 21

def test_lex_bad_str_literal5(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|
                x := 'Nesprávny escape: \\x
                '.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 21

def test_lex_bad_selector1(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|
                x := a a+: msg.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 21

def test_lex_bad_selector2(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|
                x := a + 1.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 21

def test_lex_bad_id1(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|
                x := a@.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 21

def test_lex_bad_id2(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|
                x := _/a.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 21
################################################################################
#                                                                              #
#                         TESTY SYNTAKTICKÉ SPRÁVNOSTI                         #
#                                                                              #
################################################################################

def test_syntax_bad_missing_colon(monkeypatch):
    SOL25Code = """
        class Main Object {
            run [ | x := 5. ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_syntax_bad_invalid_class_id1(monkeypatch):
    SOL25Code = """
        class main : Object {
            run [ | x := 5. ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_syntax_bad_invalid_class_id2(monkeypatch):
    SOL25Code = """
        class Main : object {
            run [ | x := 5. ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_syntax_bad_unterminated_block(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [ | x := 5.
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_syntax_bad_block_missing_pipe(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [ x := 5. ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_syntax_bad_missing_dot(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [ | x := 5 ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_syntax_bad_unterminated_class(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [ | x := 5. ]
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_syntax_bad_missing_class(monkeypatch):
    SOL25Code = """
        Main : Object {
            run [ | x := 5. ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_syntax_bad_missing_class_id(monkeypatch):
    SOL25Code = """
        class : Object {
            run [ | x := 5. ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_syntax_bad_missing_class_body(monkeypatch):
    SOL25Code = """
        class Main: Object
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_syntax_bad_invalid_parameter1(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [ x := 5. | ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_syntax_bad_invalid_parameter2(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [ x := 5. | y ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_syntax_bad_invalid_parameter3(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [
                :Main |
                x := 5.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_syntax_bad_invalid_parameter4(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [
                Main |
                x := 5.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_syntax_bad_unclosed_parentheses(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [ | x := (5. ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_syntax_bad_invalid_send(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [ | x := 5 timesRepeat:. ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_syntax_bad_selector1(monkeypatch):
    SOL25Code = """
        class Main : Object {
            Integer [ | x := 5.  ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_syntax_bad_selector2(monkeypatch):
    SOL25Code = """
        class Main : Object {
            Irun [ | x := 5.  ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_syntax_bad_selector3(monkeypatch):
    SOL25Code = """
        class Main : Object {
            :run [ | x := 5.  ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_syntax_bad_selector4(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run: a [ | x := 5.  ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_syntax_bad_selector5(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run: a: b [ | x := 5.  ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_syntax_bad_block_param_space(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [ : y |
                x := 5.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_syntax_bad_selector_space1(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|
                x := a add : b.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_syntax_bad_selector_space2(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run :[|
                x := a add: b.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_syntax_bad_selector_space3(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run: a : [|
                x := a add: b.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_syntax_bad_reserved_id_asgn1(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|
                self := 1.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_syntax_bad_reserved_id_asgn2(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|
                super := 1.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_syntax_bad_reserved_id_asgn3(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|
                true := 1.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_syntax_bad_reserved_id_asgn4(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|
                false := 1.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_syntax_bad_reserved_id_asgn5(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|
                nil := 1.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_syntax_bad_reserved_id_asgn6(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|
                class := 1.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_syntax_bad_reserved_id_param1(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|]
            a: [:self|]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_syntax_bad_reserved_id_param2(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|]
            a: [:super|]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_syntax_bad_reserved_id_param3(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|]
            a: [:true|]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_syntax_bad_reserved_id_param4(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|]
            a: [:false|]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_syntax_bad_reserved_id_param5(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|]
            a: [:nil|]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_syntax_bad_reserved_id_param6(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|]
            a: [:class|]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_syntax_bad_reserved_id_sel1(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|x := 1 self.]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_syntax_bad_reserved_id_sel2(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|x := 1 super.]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_syntax_bad_reserved_id_sel3(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|x := 1 true.]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_syntax_bad_reserved_id_sel4(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|x := 1 false.]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_syntax_bad_reserved_id_sel5(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|x := 1 nil.]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_syntax_bad_reserved_id_sel6(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|x := 1 class.]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_syntax_bad_reserved_id_method1(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|]
            self [|]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_syntax_bad_reserved_id_method2(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|]
            super [|]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_syntax_bad_reserved_id_method3(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|]
            false [|]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_syntax_bad_reserved_id_method4(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|]
            nil [|]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_syntax_bad_reserved_id_method5(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|]
            false [|]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_syntax_bad_reserved_id_method6(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|]
            class [|]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22
################################################################################
#                                                                              #
#                         TESTY SÉMANTICKÉ SPRÁVNOSTI                          #
#                                                                              #
################################################################################

def test_seman_bad_no_main1(monkeypatch):
    SOL25Code = """
        class Man1 : Object {
            run [|
                x := 1.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 31

def test_seman_bad_no_main2(monkeypatch):
    SOL25Code = """
        class MyInt : Integer {}
        class Man2 : Object {
            run [|
                x := 1.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 31

def test_seman_bad_no_main3(monkeypatch):
    SOL25Code = """
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 31

def test_seman_bad_no_run1(monkeypatch):
    SOL25Code = """
        class Main : Object {
            ru1 [|
                x := 1.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 31

def test_seman_bad_no_run2(monkeypatch):
    SOL25Code = """
        class Main : Object {
            ru2: [:b|
                x := b.
            ]
            r [|
                x := 1.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 31

def test_seman_bad_no_run3(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run: [:b|
                x := b.
            ]
            r [|
                x := 1.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 31

def test_seman_bad_no_run4(monkeypatch):
    SOL25Code = """
        class Main : Object {}
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 31

def test_seman_bad_undefined_class1(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|
                x := MyInt1 new.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 32

def test_seman_bad_undefined_class2(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|
                x := MyInt2 from: 2.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 32

def test_seman_bad_undefined_class3(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|]
        }
        class MyInt3 : Int4 {}
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 32

def test_seman_bad_undefined_var1(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|
                x := y.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 32

def test_seman_bad_undefined_var2(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|
                x := y.
                y := 1.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 32

def test_seman_bad_undefined_var3(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|
                x := y.
                y := 1.
                z := y.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 32

def test_seman_bad_undefined_var4(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|
                x := 1 plus: y.
                y := 1.
                z := y.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 32

def test_seman_bad_undefined_var5(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|
                x := 1 plus: 1 plus: y.
                y := 1.
                z := y.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 32

def test_seman_bad_run_param(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [:a|
                x := a.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 33

def test_seman_bad_arity1(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [:a|
                x := a.
                y := a plus: 1.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 33

def test_seman_bad_arity2(monkeypatch):
    SOL25Code = """
        class Main : Object {
            abc2: [|]
            run [|
                x := self abc2: 2.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 33

def test_seman_bad_arity3(monkeypatch):
    SOL25Code = """
        class Main : Object {
            p3: [:a :b|]
            run [|
                x := self p3: 2.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 33

def test_seman_bad_arity4(monkeypatch):
    SOL25Code = """
        class Main : Object {
            p4:aa4a: [:a :b :c|]
            run [|
                x := self p4: 2 aa4a: 2.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 33

def test_seman_bad_collision_var1(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|]
            a1: [:x | x := 1.]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 34

def test_seman_bad_collision_var2(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|]
            a2:b2: [:x :x | a := 1.]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 35

def test_seman_bad_class_redef1(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|]
        }
        class A:Integer{}
        class A:Integer{}
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 35

def test_seman_bad_circular_inheritance1(monkeypatch):
    SOL25Code = """
        class A : B {}
        class B : A {}
        class Main : Object {
            run [|]
        }
        """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 35

def test_seman_bad_circular_inheritance2(monkeypatch):
    SOL25Code = """
        class A : B {}
        class Main : Object {
            run [|]
        }
        class B : A {}
        """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 35

def test_seman_bad_circular_inheritance3(monkeypatch):
    SOL25Code = """
        class A : B {}
        class B : C {}
        class C : A {}
        class Main : Object {
            run [|]
        }
        """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 35
################################################################################
#                                                                              #
#                               TESTY XML VÝSTUP                               #
#                                                                              #
################################################################################

def test_xml_ok_minimal1(monkeypatch):
    SOL25Code = """
        class Main:Object{run[|]}
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    exp_output = """
        <?xml version="1.0" encoding="UTF-8"?>
        <program language="SOL25">
            <class name="Main" parent="Object">
                <method selector="run">
                    <block arity="0" />
                </method>
            </class>
        </program>
        """
    run_valid_test(SOL25Code, exp_output)
    assert exitCode == 0

def test_xml_ok_test_minimal2(monkeypatch):
    SOL25Code = """
        class Main:Integer{run[|]}
        """
    exitCode = run_parse(SOL25Code, monkeypatch)
    exp_output = """
        <?xml version="1.0" encoding="UTF-8"?>
        <program language="SOL25">
            <class name="Main" parent="Integer">
                <method selector="run">
                    <block arity="0" />
                </method>
            </class>
        </program>
        """
    run_valid_test(SOL25Code, exp_output)
    assert exitCode == 0

def test_xml_ok_test_almost_minimal1(monkeypatch):
    SOL25Code = """
        class A:Object{}
        class Main:A{run[|]}
        """
    exitCode = run_parse(SOL25Code, monkeypatch)
    exp_output = """
        <?xml version="1.0" encoding="UTF-8"?>
        <program language="SOL25">
            <class name="A" parent="Object" />
            <class name="Main" parent="A">
                <method selector="run">
                    <block arity="0" />
                </method>
            </class>
        </program>
        """
    run_valid_test(SOL25Code, exp_output)
    assert exitCode == 0

def test_xml_ok_test_almost_minimal2(monkeypatch):
    SOL25Code = """
        class A:Object{}
        class B:A{}
        class Main:B{run[|]}
        """
    exitCode = run_parse(SOL25Code, monkeypatch)
    exp_output = """
        <?xml version="1.0" encoding="UTF-8"?>
        <program language="SOL25">
            <class name="A" parent="Object" />
            <class name="B" parent="A" />
            <class name="Main" parent="B">
                <method selector="run">
                    <block arity="0" />
                </method>
            </class>
        </program>
        """
    run_valid_test(SOL25Code, exp_output)
    assert exitCode == 0

def test_xml_ok_description1(monkeypatch):
    SOL25Code = """
        class Main:Object{run[|]} "comment"
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    exp_output = """
        <?xml version="1.0" encoding="UTF-8"?>
        <program language="SOL25" description="comment">
            <class name="Main" parent="Object">
                <method selector="run">
                    <block arity="0" />
                </method>
            </class>
        </program>
        """
    run_valid_test(SOL25Code, exp_output)
    assert exitCode == 0

def test_xml_ok_description2(monkeypatch):
    SOL25Code = """
        class Main:Object{run[|]} "comment\nnewline"
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    exp_output = """
    <?xml version="1.0" encoding="UTF-8"?>
    <program language="SOL25" description="comment&nbsp;newline">
        <class name="Main" parent="Object">
            <method selector="run">
                <block arity="0" />
            </method>
        </class>
    </program>
    """
    run_valid_test(SOL25Code, exp_output)
    assert exitCode == 0

def test_xml_ok_description3(monkeypatch):
    SOL25Code = """
        class Main:Object{run[|]} "comment" "another"
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    exp_output = """
        <?xml version="1.0" encoding="UTF-8"?>
        <program language="SOL25" description="comment">
            <class name="Main" parent="Object">
                <method selector="run">
                    <block arity="0" />
                </method>
            </class>
        </program>
        """
    run_valid_test(SOL25Code, exp_output)
    assert exitCode == 0

def test_xml_ok_description4(monkeypatch):
    SOL25Code = """
        class Main:Object{run[|]} "comment\n\nnewline"
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    exp_output = """
        <?xml version="1.0" encoding="UTF-8"?>
        <program language="SOL25" description="comment&nbsp;&nbsp;newline">
            <class name="Main" parent="Object">
                <method selector="run">
                    <block arity="0" />
                </method>
            </class>
        </program>
        """
    run_valid_test(SOL25Code, exp_output)
    assert exitCode == 0

def test_xml_ok_test_expr1(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|
                x := (((Integer from: ((Integer new))))).
            ]
        }
        """
    exitCode = run_parse(SOL25Code, monkeypatch)
    exp_output = """
        <?xml version="1.0" encoding="UTF-8"?>
        <program language="SOL25">
            <class name="Main" parent="Object">
                <method selector="run">
                    <block arity="0">
                        <assign order="1">
                            <var name="x" />
                            <expr>
                                <send selector="from:">
                                    <expr>
                                        <literal class="class" value="Integer" />
                                    </expr>
                                    <arg order="1">
                                        <expr>
                                            <send selector="new">
                                                <expr>
                                                    <literal class="class" value="Integer" />
                                                </expr>
                                            </send>
                                        </expr>
                                    </arg>
                                </send>
                            </expr>
                        </assign>
                    </block>
                </method>
            </class>
        </program>
        """
    run_valid_test(SOL25Code, exp_output)
    assert exitCode == 0

def test_xml_ok_test_expr2(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|
                x := (((Integer from: ((Integer new))) plus: (Integer new))).
            ]
        }
        """
    exitCode = run_parse(SOL25Code, monkeypatch)
    exp_output = """
        <?xml version="1.0" encoding="UTF-8"?>
        <program language="SOL25">
            <class name="Main" parent="Object">
                <method selector="run">
                    <block arity="0">
                        <assign order="1">
                            <var name="x" />
                            <expr>
                                <send selector="plus:">
                                    <expr>
                                        <send selector="from:">
                                            <expr>
                                                <literal class="class" value="Integer" />
                                            </expr>
                                            <arg order="1">
                                                <expr>
                                                    <send selector="new">
                                                        <expr>
                                                            <literal class="class" value="Integer" />
                                                        </expr>
                                                    </send>
                                                </expr>
                                            </arg>
                                        </send>
                                    </expr>
                                    <arg order="1">
                                        <expr>
                                            <send selector="new">
                                                <expr>
                                                    <literal class="class" value="Integer" />
                                                </expr>
                                            </send>
                                        </expr>
                                    </arg>
                                </send>
                            </expr>
                        </assign>
                    </block>
                </method>
            </class>
        </program>
        """
    run_valid_test(SOL25Code, exp_output)
    assert exitCode == 0

def test_xml_ok_test_expr3(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|
                x := [|
                    x := 2.
                ].
            ]
        }
        """
    exitCode = run_parse(SOL25Code, monkeypatch)
    exp_output = """
        <?xml version="1.0" encoding="UTF-8"?>
        <program language="SOL25">
            <class name="Main" parent="Object">
                <method selector="run">
                    <block arity="0">
                        <assign order="1">
                            <var name="x" />
                            <expr>
                                <block arity="0">
                                    <assign order="1">
                                        <var name="x" />
                                        <expr>
                                            <literal class="Integer" value="2" />
                                        </expr>
                                    </assign>
                                </block>
                            </expr>
                        </assign>
                    </block>
                </method>
            </class>
        </program>
        """
    run_valid_test(SOL25Code, exp_output)
    assert exitCode == 0

def test_xml_ok_test_expr4(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|
                x := ([|
                    x := (2).
                ]).
            ]
        }
        """
    exitCode = run_parse(SOL25Code, monkeypatch)
    exp_output = """
        <?xml version="1.0" encoding="UTF-8"?>
        <program language="SOL25">
            <class name="Main" parent="Object">
                <method selector="run">
                    <block arity="0">
                        <assign order="1">
                            <var name="x" />
                            <expr>
                                <block arity="0">
                                    <assign order="1">
                                        <var name="x" />
                                        <expr>
                                            <literal class="Integer" value="2" />
                                        </expr>
                                    </assign>
                                </block>
                            </expr>
                        </assign>
                    </block>
                </method>
            </class>
        </program>
        """
    run_valid_test(SOL25Code, exp_output)
    assert exitCode == 0

def test_xml_ok_multiple_classes(monkeypatch):
    SOL25Code = """
        class Main : Object {run [|]}
        class Main2 : Object {run [|]}
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    exp_output = """
        <?xml version="1.0" encoding="UTF-8"?>
        <program language="SOL25">
            <class name="Main" parent="Object">
                <method selector="run">
                    <block arity="0" />
                </method>
            </class>
            <class name="Main2" parent="Object">
                <method selector="run">
                    <block arity="0" />
                </method>
            </class>
        </program>
        """
    run_valid_test(SOL25Code, exp_output)
    assert exitCode == 0

def test_xml_ok_multiple_methods(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|]
            run2 [|]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    exp_output = """
        <?xml version="1.0" encoding="UTF-8"?>
        <program language="SOL25">
            <class name="Main" parent="Object">
                <method selector="run">
                    <block arity="0" />
                </method>
                <method selector="run2">
                    <block arity="0" />
                </method>
            </class>
        </program>
        """
    run_valid_test(SOL25Code, exp_output)
    assert exitCode == 0

def test_xml_ok_multiple_parameters(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|]
            self:from:nil: [:x :y :z |]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    exp_output = """
        <?xml version="1.0" encoding="UTF-8"?>
        <program language="SOL25">
            <class name="Main" parent="Object">
                <method selector="run">
                    <block arity="0" />
                </method>
                <method selector="self:from:nil:">
                    <block arity="3">
                        <parameter order="1" name="x" />
                        <parameter order="2" name="y" />
                        <parameter order="3" name="z" />
                    </block>
                </method>
            </class>
        </program>
        """
    run_valid_test(SOL25Code, exp_output)
    assert exitCode == 0

def test_xml_ok_multiple_assign(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|
                x := 10.
                y := 5.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    exp_output = """
        <?xml version="1.0" encoding="UTF-8"?>
        <program language="SOL25">
            <class name="Main" parent="Object">
                <method selector="run">
                    <block arity="0">
                        <assign order="1">
                            <var name="x" />
                            <expr>
                                <literal class="Integer" value="10" />
                            </expr>
                        </assign>
                        <assign order="2">
                            <var name="y" />
                            <expr>
                                <literal class="Integer" value="5" />
                            </expr>
                        </assign>
                    </block>
                </method>
            </class>
        </program>
        """
    run_valid_test(SOL25Code, exp_output)
    assert exitCode == 0

def test_xml_ok_inheritance(monkeypatch):
    SOL25Code = """
        class Str : String {}
        class Main : Object {
            run [|
                x := Str2 read.
            ]
        }
        class Str2 : Str {}
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    exp_output = """
        <?xml version="1.0" encoding="UTF-8"?>
        <program language="SOL25">
            <class name="Str" parent="String" />
            <class name="Main" parent="Object">
                <method selector="run">
                    <block arity="0">
                        <assign order="1">
                            <var name="x" />
                            <expr>
                                <send selector="read">
                                    <expr>
                                        <literal class="class" value="Str2" />
                                    </expr>
                                </send>
                            </expr>
                        </assign>
                    </block>
                </method>
            </class>
            <class name="Str2" parent="Str" />
        </program>
        """
    run_valid_test(SOL25Code, exp_output)
    assert exitCode == 0

def test_xml_ok_literal_integer(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|
                x := 10.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    exp_output = """
        <?xml version="1.0" encoding="UTF-8"?>
        <program language="SOL25">
            <class name="Main" parent="Object">
                <method selector="run">
                    <block arity="0">
                        <assign order="1">
                            <var name="x" />
                            <expr>
                                <literal class="Integer" value="10" />
                            </expr>
                        </assign>
                    </block>
                </method>
            </class>
        </program>
        """
    run_valid_test(SOL25Code, exp_output)
    assert exitCode == 0

def test_xml_ok_literal_nil(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|
                x := nil.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    exp_output = """
        <?xml version="1.0" encoding="UTF-8"?>
        <program language="SOL25">
            <class name="Main" parent="Object">
                <method selector="run">
                    <block arity="0">
                        <assign order="1">
                            <var name="x" />
                            <expr>
                                <literal class="Nil" value="nil" />
                            </expr>
                        </assign>
                    </block>
                </method>
            </class>
        </program>
        """
    run_valid_test(SOL25Code, exp_output)
    assert exitCode == 0

def test_xml_ok_literal_true(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|
                x := true.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    exp_output = """
        <?xml version="1.0" encoding="UTF-8"?>
        <program language="SOL25">
            <class name="Main" parent="Object">
                <method selector="run">
                    <block arity="0">
                        <assign order="1">
                            <var name="x" />
                            <expr>
                                <literal class="True" value="true" />
                            </expr>
                        </assign>
                    </block>
                </method>
            </class>
        </program>
        """
    run_valid_test(SOL25Code, exp_output)
    assert exitCode == 0

def test_xml_ok_literal_false(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|
                x := false.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    exp_output = """
        <?xml version="1.0" encoding="UTF-8"?>
        <program language="SOL25">
            <class name="Main" parent="Object">
                <method selector="run">
                    <block arity="0">
                        <assign order="1">
                            <var name="x" />
                            <expr>
                                <literal class="False" value="false" />
                            </expr>
                        </assign>
                    </block>
                </method>
            </class>
        </program>
        """
    run_valid_test(SOL25Code, exp_output)
    assert exitCode == 0

def test_xml_ok_literal_string(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|
                x := 'a10'.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    exp_output = """
        <?xml version="1.0" encoding="UTF-8"?>
        <program language="SOL25">
            <class name="Main" parent="Object">
                <method selector="run">
                    <block arity="0">
                        <assign order="1">
                            <var name="x" />
                            <expr>
                                <literal class="String" value="a10" />
                            </expr>
                        </assign>
                    </block>
                </method>
            </class>
        </program>
        """
    run_valid_test(SOL25Code, exp_output)
    assert exitCode == 0

def test_xml_ok_literal_string_lt(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|
                x := 'a < 10'.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    exp_output = """
        <?xml version="1.0" encoding="UTF-8"?>
        <program language="SOL25">
            <class name="Main" parent="Object">
                <method selector="run">
                    <block arity="0">
                        <assign order="1">
                            <var name="x" />
                            <expr>
                                <literal class="String" value="a &lt; 10" />
                            </expr>
                        </assign>
                    </block>
                </method>
            </class>
        </program>
        """
    run_valid_test(SOL25Code, exp_output)
    assert exitCode == 0

def test_xml_ok_literal_string_gt(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|
                x := 'a > 10'.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    exp_output = """
        <?xml version="1.0" encoding="UTF-8"?>
        <program language="SOL25">
            <class name="Main" parent="Object">
                <method selector="run">
                    <block arity="0">
                        <assign order="1">
                            <var name="x" />
                            <expr>
                                <literal class="String" value="a &gt; 10" />
                            </expr>
                        </assign>
                    </block>
                </method>
            </class>
        </program>
        """
    run_valid_test(SOL25Code, exp_output)
    assert exitCode == 0

def test_xml_ok_literal_string_amp(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|
                x := 'a & 10'.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    exp_output = """
        <?xml version="1.0" encoding="UTF-8"?>
        <program language="SOL25">
            <class name="Main" parent="Object">
                <method selector="run">
                    <block arity="0">
                        <assign order="1">
                            <var name="x" />
                            <expr>
                                <literal class="String" value="a &amp; 10" />
                            </expr>
                        </assign>
                    </block>
                </method>
            </class>
        </program>
        """
    run_valid_test(SOL25Code, exp_output)
    assert exitCode == 0

def test_xml_ok_literal_string_apos(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|
                x := 'a \\' 10'.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    exp_output = """
        <?xml version="1.0" encoding="UTF-8"?>
        <program language="SOL25">
            <class name="Main" parent="Object">
                <method selector="run">
                    <block arity="0">
                        <assign order="1">
                            <var name="x" />
                            <expr>
                                <literal class="String" value="a \\&apos; 10" />
                            </expr>
                        </assign>
                    </block>
                </method>
            </class>
        </program>
        """
    run_valid_test(SOL25Code, exp_output)
    assert exitCode == 0

def test_xml_ok_literal_string_quot(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|
                x := 'a " 10'.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    exp_output = """
        <?xml version="1.0" encoding="UTF-8"?>
        <program language="SOL25">
            <class name="Main" parent="Object">
                <method selector="run">
                    <block arity="0">
                        <assign order="1">
                            <var name="x" />
                            <expr>
                                <literal class="String" value="a &quot; 10" />
                            </expr>
                        </assign>
                    </block>
                </method>
            </class>
        </program>
        """
    run_valid_test(SOL25Code, exp_output)
    assert exitCode == 0

def test_xml_ok_literal_string_esc_nl(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|
                x := 'a \\n 10'.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    exp_output = """
        <?xml version="1.0" encoding="UTF-8"?>
        <program language="SOL25">
            <class name="Main" parent="Object">
                <method selector="run">
                    <block arity="0">
                        <assign order="1">
                            <var name="x" />
                            <expr>
                                <literal class="String" value="a \\n 10" />
                            </expr>
                        </assign>
                    </block>
                </method>
            </class>
        </program>
        """
    run_valid_test(SOL25Code, exp_output)
    assert exitCode == 0

def test_xml_ok_literal_string_esc_backslash(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|
                x := 'a \\\\ 10'.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    exp_output = """
        <?xml version="1.0" encoding="UTF-8"?>
        <program language="SOL25">
            <class name="Main" parent="Object">
                <method selector="run">
                    <block arity="0">
                        <assign order="1">
                            <var name="x" />
                            <expr>
                                <literal class="String" value="a \\\\ 10" />
                            </expr>
                        </assign>
                    </block>
                </method>
            </class>
        </program>
        """
    run_valid_test(SOL25Code, exp_output)
    assert exitCode == 0

def test_xml_ok_nested_expr(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|
                x := (((1))).
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    exp_output = """
    <?xml version='1.0' encoding='UTF-8'?>
    <program language="SOL25">
        <class name="Main" parent="Object">
            <method selector="run">
                <block arity="0">
                    <assign order="1">
                        <var name="x" />
                        <expr>
                            <literal value="1" class="Integer" />
                        </expr>
                    </assign>
                </block>
            </method>
        </class>
    </program>
    """
    run_valid_test(SOL25Code, exp_output)
    assert exitCode == 0

def test_xml_ok_inheritance_method_call(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [| x := Baf startsWith: 0 endsBefore: 1.]
        }
        class Baf : String {
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    exp_output = """
        <?xml version='1.0' encoding='UTF-8'?>
        <program language="SOL25">
            <class name="Main" parent="Object">
                <method selector="run">
                    <block arity="0">
                        <assign order="1">
                            <var name="x" />
                            <expr>
                                <send selector="startsWith:endsBefore:">
                                    <arg order="1">
                                        <expr>
                                            <literal value="0" class="Integer" />
                                        </expr>
                                    </arg>
                                    <arg order="2">
                                        <expr>
                                            <literal value="1" class="Integer" />
                                        </expr>
                                    </arg>
                                    <expr>
                                        <literal value="Baf" class="class" />
                                    </expr>
                                </send>
                            </expr>
                        </assign>
                    </block>
                </method>
            </class>
            <class name="Baf" parent="String">
            </class>
        </program>
        """
    run_valid_test(SOL25Code, exp_output)
    assert exitCode == 0

def test_xml_ok_literal_class_new(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|
                x := Integer new.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    exp_output = """
        <?xml version="1.0" encoding="UTF-8"?>
        <program language="SOL25">
            <class name="Main" parent="Object">
                <method selector="run">
                    <block arity="0">
                        <assign order="1">
                            <var name="x" />
                            <expr>
                                <send selector ="new">
                                    <expr>
                                        <literal class="class" value="Integer" />
                                    </expr>
                                </send>
                            </expr>
                        </assign>
                    </block>
                </method>
            </class>
        </program>
        """
    run_valid_test(SOL25Code, exp_output)
    assert exitCode == 0

def test_xml_ok_literal_class_from(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|
                x := Integer from: 1.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    exp_output = """
        <?xml version="1.0" encoding="UTF-8"?>
        <program language="SOL25">
            <class name="Main" parent="Object">
                <method selector="run">
                    <block arity="0">
                        <assign order="1">
                            <var name="x" />
                            <expr>
                                <send selector ="from:">
                                    <expr>
                                        <literal class="class" value="Integer" />
                                    </expr>
                                    <arg order="1">
                                        <expr>
                                            <literal class="Integer" value="1" />
                                        </expr>
                                    </arg>
                                </send>
                            </expr>
                        </assign>
                    </block>
                </method>
            </class>
        </program>
        """
    run_valid_test(SOL25Code, exp_output)
    assert exitCode == 0

def test_xml_ok_assign_block(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|
                x := [|].
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    exp_output = """
        <?xml version="1.0" encoding="UTF-8"?>
        <program language="SOL25">
            <class name="Main" parent="Object">
                <method selector="run">
                    <block arity="0">
                        <assign order="1">
                            <var name="x" />
                            <expr>
                                <block arity="0" />
                            </expr>
                        </assign>
                    </block>
                </method>
            </class>
        </program>
        """
    run_valid_test(SOL25Code, exp_output)
    assert exitCode == 0

def test_xml_ok_assign_block_param(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|
                x := [:x|].
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    exp_output = """
        <?xml version="1.0" encoding="UTF-8"?>
        <program language="SOL25">
            <class name="Main" parent="Object">
                <method selector="run">
                    <block arity="0">
                        <assign order="1">
                            <var name="x" />
                            <expr>
                                <block arity="1">
                                    <parameter order="1" name="x" />
                                </block>
                            </expr>
                        </assign>
                    </block>
                </method>
            </class>
        </program>
        """
    run_valid_test(SOL25Code, exp_output)
    assert exitCode == 0

def test_xml_ok_assign_var(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run [|
                y := 1.
                x := y.
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    exp_output = """
        <?xml version="1.0" encoding="UTF-8"?>
        <program language="SOL25">
            <class name="Main" parent="Object">
                <method selector="run">
                    <block arity="0">
                        <assign order="1">
                            <var name="y" />
                            <expr>
                                <literal class="Integer" value="1" />
                            </expr>
                        </assign>
                        <assign order="2">
                            <var name="x" />
                            <expr>
                                <var name="y" />
                            </expr>
                        </assign>
                    </block>
                </method>
            </class>
        </program>
        """
    run_valid_test(SOL25Code, exp_output)
    assert exitCode == 0
'''
def test_xml_ok_example(monkeypatch):
    SOL25Code = """
        class Main : Object {
            run "<- definice metody - bezparametrický selektor run"
            [ |
                x := self compute: 3 and: 2 and: 5.
                x := self plusOne: (self vysl).
                y := x asString .
            ]

            plusOne:
            [ :x |
                r := x plus: 1.
            ]

            compute:and:and:
            [ :x :y :z |
                a := x plus: y.
                _ := self vysl: a.
                _ := (( self vysl) greaterThan: 0)
                ifTrue: [|u := self vysl: 1.]
                ifFalse: [|].
            ]
        }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    exp_output = """
    <?xml version="1.0" encoding="UTF-8"?>
    <program language="SOL25" description="&lt;- definice metody - bezparametrický selektor run">
      <class name="Main" parent="Object">
        <method selector="run">
          <block arity="0">
            <assign order="1">
              <var name="x" />
              <expr>
                <send selector="compute:and:and:">
                  <expr>
                    <var name="self" />
                  </expr>
                  <arg order="1">
                    <expr>
                      <literal class="Integer" value="3" />
                    </expr>
                  </arg>
                  <arg order="2">
                    <expr>
                      <literal class="Integer" value="2" />
                    </expr>
                  </arg>
                  <arg order="3">
                    <expr>
                      <literal class="Integer" value="5" />
                    </expr>
                  </arg>
                </send>
              </expr>
            </assign>
            <assign order="2">
              <var name="x" />
              <expr>
                <send selector="plusOne:">
                  <expr>
                    <var name="self" />
                  </expr>
                  <arg order="1">
                    <expr>
                      <send selector="vysl">
                        <expr>
                          <var name="self" />
                        </expr>
                      </send>
                    </expr>
                  </arg>
                </send>
              </expr>
            </assign>
            <assign order="3">
              <var name="y" />
              <expr>
                <send selector="asString">
                  <expr>
                    <var name="x" />
                  </expr>
                </send>
              </expr>
            </assign>
          </block>
        </method>
        <method selector="plusOne:">
          <block arity="1">
            <parameter order="1" name="x" />
            <assign order="1">
              <var name="r" />
              <expr>
                <send selector="plus:">
                  <expr>
                    <var name="x" />
                  </expr>
                  <arg order="1">
                    <expr>
                      <literal class="Integer" value="1" />
                    </expr>
                  </arg>
                </send>
              </expr>
            </assign>
          </block>
        </method>
        <method selector="compute:and:and:">
          <block arity="3">
            <parameter name="x" order="1" />
            <parameter name="y" order="2" />
            <parameter name="z" order="3" />
            <assign order="1">
              <var name="a" />
              <expr>
                <send selector="plus:">
                  <expr>
                    <var name="x" />
                  </expr>
                  <arg order="1">
                    <expr>
                      <var name="y" />
                    </expr>
                  </arg>
                </send>
              </expr>
            </assign>
            <assign order="2">
              <var name="_" />
              <expr>
                <send selector="vysl:">
                  <expr>
                    <var name="self" />
                  </expr>
                  <arg order="1">
                    <expr>
                      <var name="a" />
                    </expr>
                  </arg>
                </send>
              </expr>
            </assign>
            <assign order="3">
              <var name="_" />
              <expr>
                <send selector="ifTrue:ifFalse:">
                  <expr>
                    <send selector="greaterThan:">
                      <expr>
                        <send selector="vysl">
                          <expr>
                            <var name="self" />
                          </expr>
                        </send>
                      </expr>
                      <arg order="1">
                        <expr>
                          <literal class="Integer" value="0" />
                        </expr>
                      </arg>
                    </send>
                  </expr>
                  <arg order="1">
                    <expr>
                      <block arity="0">
                        <assign order="1">
                          <var name="u" />
                          <expr>
                            <send selector="vysl:">
                              <expr>
                                <var name="self" />
                              </expr>
                              <arg order="1">
                                <expr>
                                  <literal class="Integer" value="1" />
                                </expr>
                              </arg>
                            </send>
                          </expr>
                        </assign>
                      </block>
                    </expr>
                  </arg>
                  <arg order="2">
                    <expr>
                      <block arity="0" />
                    </expr>
                  </arg>
                </send>
              </expr>
            </assign>
          </block>
        </method>
      </class>
    </program>
    """
    run_valid_test(SOL25Code, exp_output)
    assert exitCode == 0
'''
################################################################################
#                                                                              #
#                                OSTATNÍ TESTY                                 #
#                                                                              #
################################################################################

def test_ok_multiple_classes(monkeypatch):
    SOL25Code = """
    class Main:Object {
        run [|
            var1 := 42 .
        ]
        doOther [ | ]
    }
    "This is a comment."
    class Helper:Main {
        assist [ | msg := 'assist\\nDone' . ]
    }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 0

def test_ok_selector_with_parameterization(monkeypatch):
    SOL25Code = """
    class Main:Object {
        run [ | ]
    }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 0

def test_ok_expression_with_parens_and_selector(monkeypatch):
    SOL25Code = """
    class Main:Object {
        run [ | res := (5 plus: 3) . ]
    }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 0

def test_ok_nested_block(monkeypatch):
    SOL25Code = """
    class Main:Object {
        run [ | result :=
            [ |innerMethod :=[ | innerVar := 100 . ] .]
            .
        ]
    }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 0

def test_ok_literals_in_expression(monkeypatch):
    SOL25Code = """
    class Main:Object {
        run [ | a := 123 . b := 'hello\\nworld' . c := nil . d := true . exception := false . f := self . g := super . ]
    }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 0

def test_ok_string_literal_with_valid_escapes(monkeypatch):
    SOL25Code = """
    class Main:Object {
        run [ | msg := 'Hello\\nIt\\'s a \\\\ test' . ]
    }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 0

def test_ok_two_parameters(monkeypatch):
    SOL25Code = """
    "This is the first comment."
    class Main : Object {
        run [ | ]
        x: [ :one :two | r := Integer from: two. ]
    }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 0

def test_bad_empty_program(monkeypatch):
    SOL25Code = ""
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 11

def test_bad_parse_invalid_string_escape(monkeypatch):
    SOL25Code = """
    class Main:Main {
        errorMethod [ | s := 'Bad\\aEscape' . ]
    }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 21

def test_bad_missing_dot_in_block_statement(monkeypatch):
    SOL25Code = """
    class Main:Main {
        incomplete [ var := 10 ]
    }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_bad_missing_closing_bracket(monkeypatch):
    SOL25Code = """
    class Main:Main {
        method [ :p | var := 20 .
    }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_bad_invalid_identifier(monkeypatch):
    SOL25Code = """
    class Main:Main {
        1invalid [ | ]
    }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_bad_extraneous_tokens(monkeypatch):
    SOL25Code = """
    class Main:Main {
        method [ | ]
    } extra_token
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_bad_unbalanced_parentheses(monkeypatch):
    SOL25Code = """
    class Main:Main {
        compute [ | r := (5 plus: 3 . ]
    }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 22

def test_ok_example7(monkeypatch):
    SOL25Code = """
    class Main : Object {
        run "<- definice metody - bezparametrický selektor run"
        [ |
            x := self compute: 3 and: 2 and: 5.
            x := self plusOne: (self vysl).
            y := x asString .
        ]

        plusOne:
        [ :x |
            r := x plus: 1.
        ]

        compute:and:and:
        [ :x :y :z |
            a := x plus: y.
            _ := self vysl: a.
            _ := (( self vysl) greaterThan: 0)
            ifTrue: [|u := self vysl: 1.]
            ifFalse: [|].
        ]
    }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 0

def test_bad_DuplicateMethodDefinition(monkeypatch):
    SOL25Code = """
    class DuplicateMethod : Object {
        foo [| a := 'hello'. ]
        foo [| b := 'bye'. ]
    }

    class Main : Object {
        run [| a := 'servus'. ]
    }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 32

def test_bad_UndeclaredBlockParamUse(monkeypatch):
    SOL25Code = """
    class Main : Object {
        run [|
            b := [| a := x. ].
            _ := b value.
        ]
    }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 32


def test_bad_AccessUndefinedParamInBlock(monkeypatch):
    SOL25Code = """
    class Main : Object {
        run [|
            bl := [ :p | a := q. ].
            _ := bl value: 10.
        ]
    }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 32

def test_bad_ShadowingBlockParam(monkeypatch):
    SOL25Code = """
    class Main : Object {
        run [|
            block := [ :x | x := x plus: 1. y := x. ].
            y := 100.
            _ := block value: 10.
        ]
    }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 34

def test_bad_OverridingWithDifferentArity(monkeypatch):
    SOL25Code = """
    class Parent : Object {
        doStuff: [ :x | a := 'a " 10'. ]
    }

    class Child : Parent {
        doStuff: [ :x:y | a := 'a'. ]
    }

    class Main : Object {
        run [| a := 'a'. ]
    }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 33

def test_bad_OverlappingParamAndLocal(monkeypatch):
    SOL25Code = """
    class Main : Object {
        run [|
            b := [ :val | val := val plus: 1. x := val. ].
            x := 100.
            _ := b value: 10.
        ]
    }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 34


################################################################################
#                                                                              #
#                                 HANKA TESTY                                  #
#                                                                              #
################################################################################

def test_hanka_BlockInput(monkeypatch):
    SOL25Code = """
    class Main : Object {
        run [|
            a := self foo: 4. "a = instance 14"
            b := [ :x | _ := 42. ]. "b = instance Block"
            c := b value: 16. "c = instance 42"
            d := 'ahoj' print.] "d = instance 'ahoj' - print vrací self , viz Vestavěné třídy"

        foo: [ :x |
            "s proměnnou 'u' se nijak dál nepracuje , ale výsledek zaslání
            zprávy 'plus:' bude vrácen jako výsledek volání metody 'foo'"
            u := x plus: 10.
        ]
    }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 0

def test_hanka_Classes(monkeypatch):
    SOL25Code = """
    class MyInt : Integer { }
    class Main : Object {
    run [|
    x := 1. y := 1. z := Integer from: 1.
    u := MyInt from: 1. w := MyInt from: 1.
    a := x equalTo: y. a := x equalTo: z. "obojí true"
    a := x identicalTo: y. "podle implementace"
    a := x identicalTo: z. "podle implementace"
    a := u equalTo: x. a := u equalTo: w. "obojí true"
    a := u identicalTo: x. "false"
    a := u identicalTo: w. "podle implementace"
    ]
    }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 0

def test_hanka_Constructor(monkeypatch):
    SOL25Code = """
    class Factorial : Integer {
    factorial "použití from: pro podtřídu třídy Integer"
    [| r := (self equalTo: 0) ifTrue: [|r := Factorial from: 1.]
    ifFalse: [|r := self multiplyBy:
    ((Factorial from:(self plus: -1)) factorial) . ].
    ]
    }
    class Main : Object {
    run
    [| x := Factorial from: ((String read) asInteger). x := (x factorial) print. ]
    }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 0

def test_hanka_ExpressionsInput(monkeypatch):
    SOL25Code = """
    class Main : Object {
        run [|
        "výraz zaslání zprávy v argumentu je už nutné uzávorkovat"
        a := self attrib: (Integer from: 10).
        "vnořená zaslání zprávy , kde je výsledek užit jako cíl pro další zprávu"
        "gramatika v příloze by následující přijala i bez závorek kolem '10 asString',
        ale testovat to nebudeme"
        b := [| x := ((self attrib) asString) concatenateWith: (10 asString). ].
        ]
    }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 0

def test_hanka_Selector(monkeypatch):
    SOL25Code = """
    class Main : Object {
        run "<- definice metody - bezparametrický selektor run"
        [ |
        "zaslání zprávy 'compute:and:and:' sobě samému - selektor se dvěma arg."
            x := self compute: 3 and: 2 and: 5.
            "zaslání zprávy 'plusOne:' sobě samému - selektor s jedním arg.
            Argumentem je výsledek po zaslání zprávy 'vysl' objektu self."
            x := self plusOne: (self vysl).
            "zaslání zprávy 'asString' objektu x - bezparam. selektor"
            y := x asString.
        ]
        plusOne: "<- definice metody - selektor s jedním parametrem"
        [ :x | r := x plus: 1. ]
            compute:and:and: "<- definice metody - selektor se třemi parametry"
        [ :x :y :z |
        "zaslání zpr. 'plus:' objektu x - selektor s jedním argumentem"
            a := x plus: y.
            "zaslání zpr. 'vysl:' sobě samému - nastaví instanční atribut 'vysl'"
            _ := self vysl: a.
            "zpráva 'vysl' se zašle sobě , výsledkem je ref. na objekt vysl;
            tomuto objektu se pak zašle zpráva 'greaterThan:' s arg. 0."
            _ := ((self vysl) greaterThan: 0)
            "výsledkem je objekt typu True nebo False , kterému se zašle zpráva
            'ifTrue:ifFalse:', argumenty jsou bezparametrické bloky"
            ifTrue: [|u := self vysl: 1.]
            ifFalse: [|].
        ]
    }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 0

def test_hanka_SelfReference(monkeypatch):
    SOL25Code = """
    class Main : Object {
        run [|
            a := A new.
            "instance bloku si zapamatuje , že self odkazuje na tuto instanci Main"
            "blok navíc tuto referenci na konci vrací"
            b := [ :arg | y := self attr: arg. z := self. ].
            "zavoláme metodu 'foo' na instanci A a předáme jí objekt 'b' typu Block"
            c := a foo: b.
            "výsledkem přiřazeným do c je instance třídy Main s instančním atributem
            attr inicializovaným na 1"
        ]
    }
    class A : Object {
        foo: [ :x |
            "blok předaný v x je vyhodnocen a do instance Main je jím vytvořen
            instanční atribut attr s hodnotou 1"
            u := x value: 1.
        ]
    }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 0

def test_hanka_ValidInputShort(monkeypatch):
    SOL25Code = """
    class Main : Object {
    run [|
    "definuje a inicializuje instanční atribut 'value'"
    r := self value: 10.
    "definuje další inst. atribut 'next', inicializuje hodnotou atributu 'value'"
    e := self next: (self value).
    "atribut 'value' již existuje , takže pouze modifikuje hodnotu na nil"
    t := self value: nil.
    ]
    }
    """
    exitCode = run_parse(SOL25Code, monkeypatch)
    assert exitCode == 0

################################################################################
#                                                                              #
#                            ARGUMENT PARSER TESTY                             #
#                                                                              #
################################################################################

def test_arg_ok_help(monkeypatch):
    run_arg_test(['--help'], 0)

def test_arg_ok_help_short(monkeypatch):
    run_arg_test(['-h'], 0)

def test_arg_bad_wrong(monkeypatch):
    run_arg_test(['wrong'], 10)

def test_arg_bad_too_many(monkeypatch):
    run_arg_test(['too', 'many'], 10)

def test_arg_bad_wrong_and_help(monkeypatch):
    run_arg_test(['wrong', '--help'],  10)

def test_arg_bad_help_and_wrong(monkeypatch):
    run_arg_test(['--help', 'wrong'], 10)

def test_arg_bad_help_and_help(monkeypatch):
    run_arg_test(['--help', '--help'], 10)

def test_arg_bad_help_and_short_help(monkeypatch):
    run_arg_test(['--help', '-h'], 10)

def test_arg_bad_short_help_and_help(monkeypatch):
    run_arg_test(['-h', '--help'], 10)

### konec souboru 'test.py' ###
