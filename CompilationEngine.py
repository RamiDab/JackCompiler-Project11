"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
from JackTokenizer import JackTokenizer
from SymbolTable import SymbolTable
from VMWriter import VMWriter


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """
    CONVERT_KIND = {
        'ARG': 'ARG',
        'STATIC': 'STATIC',
        'VAR': 'LOCAL',
        'FIELD': 'THIS'
    }
    ARITHMETIC = {
        '+': 'ADD',
        '-': 'SUB',
        '=': 'EQ',
        '>': 'GT',
        '<': 'LT',
        '&': 'AND',
        '|': 'OR'
    }

    ARITHMETIC_UNARY = {
        '-': 'NEG',
        '~': 'NOT',
        '^': 'SHIFTLEFT',
        '#': 'SHIFTRIGHT'
    }

    def __init__(self, input_stream: typing.TextIO, output_stream) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        # Your code goes here!
        # Note that you can write to output_stream like so:
        # output_stream.write("Hello world! \n")
        tokenizer = JackTokenizer(input_stream)
        self.all_tokens = []
        self.index = -1
        while tokenizer.has_more_tokens():
            tokenizer.advance()
            self.all_tokens.append((tokenizer.current_value, tokenizer.current_type))
        self.size = len(self.all_tokens)
        self.table = SymbolTable()
        self.vm = VMWriter(output_stream)
        self.clas_name = ""
        self.subroutine_name = ""
        self.subroutine_kind = ""
        self.num_args = 0
        self.func_name = ""
        self.while_index = -1
        self.if_index = -1

    def compile_class(self) -> None:
        """Compiles a complete class."""
        # Your code goes here!
        if self.index < self.size:
            self.index += 1
            self.index += 1
            self.clas_name = self.all_tokens[self.index][0]
            self.index += 1
            while self.all_tokens[self.index + 1][0] == "static" or self.all_tokens[self.index + 1][0] == "field":
                self.compile_class_var_dec()
            while self.all_tokens[self.index + 1][0] == "constructor" or self.all_tokens[self.index + 1][
                0] == "function" or \
                    self.all_tokens[self.index + 1][0] == "method":
                self.compile_subroutine()

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        # Your code goes here!
        self.index += 1
        kind = self.all_tokens[self.index][0]
        self.index += 1
        type_of = self.all_tokens[self.index][0]
        self.index += 1
        name = self.all_tokens[self.index][0]
        self.table.define(name, type_of, kind.upper())
        while self.all_tokens[self.index + 1][0] != ";":
            self.index += 1
            self.index += 1
            name = self.all_tokens[self.index][0]
            self.table.define(name, type_of, kind.upper())
        self.index += 1

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        # Your code goes here!
        self.table.start_subroutine()
        self.index += 1
        self.subroutine_kind = self.all_tokens[self.index][0]
        if self.subroutine_kind == "method":
            self.table.define("this", self.clas_name, "ARG")
        self.index += 1  # return type
        self.index += 1
        self.subroutine_name = self.all_tokens[self.index][0]
        self.index += 1
        self.compile_parameter_list()
        self.index += 1  # )
        self.index += 1  # {
        self.compile_subroutine_body()

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        # Your code goes here!
        if self.all_tokens[self.index + 1][0] != ")":
            self.index += 1
            type_of = self.all_tokens[self.index][0]
            self.index += 1
            self.table.define(self.all_tokens[self.index][0], type_of, "ARG")
        while self.all_tokens[self.index + 1][0] != ")":
            self.index += 1
            self.index += 1
            type_of = self.all_tokens[self.index][0]
            self.index += 1
            self.table.define(self.all_tokens[self.index][0], type_of, "ARG")

    def compile_subroutine_body(self) -> None:
        while self.all_tokens[self.index + 1][0] == "var":
            self.compile_var_dec()
        func_name = "{}.{}".format(self.clas_name, self.subroutine_name)
        num_locals = self.table.var_count("VAR")
        self.vm.write_function(func_name, num_locals)
        if self.subroutine_kind == "constructor":
            num_fields = self.table.var_count('FIELD')
            self.vm.write_push('CONST', num_fields)
            self.vm.write_call('Memory.alloc', 1)
            self.vm.write_pop('POINTER', 0)
        elif self.subroutine_kind == 'method':
            self.vm.write_push('ARG', 0)
            self.vm.write_pop('POINTER', 0)
        self.compile_statements()
        self.index += 1

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        self.index += 1
        self.index += 1
        type_of = self.all_tokens[self.index][0]
        self.index += 1
        name = self.all_tokens[self.index][0]
        self.table.define(name, type_of, "VAR")
        while self.all_tokens[self.index + 1][0] != ";":
            self.index += 1
            self.index += 1
            name = self.all_tokens[self.index][0]
            self.table.define(name, type_of, "VAR")
        self.index += 1

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        # Your code goes here!
        lst = ["let", "do", "if", "while", "return"]
        while self.all_tokens[self.index + 1][0] in lst:
            self.index += 1
            token = self.all_tokens[self.index][0]
            if token == "let":
                self.compile_let()
            elif token == "do":
                self.compile_do()
            elif token == "if":
                self.compile_if()
            elif token == "return":
                self.compile_return()
            elif token == "while":
                self.compile_while()

    def compile_do(self) -> None:
        """Compiles a do statement."""
        # Your code goes here!
        self.subroutine_call()
        self.vm.write_pop("TEMP", 0)
        self.index += 1

    def subroutine_call(self):
        self.index += 1
        identifier = self.all_tokens[self.index][0]
        self.func_name = identifier
        self.num_args = 0
        if self.all_tokens[self.index + 1][0] == ".":
            self.index += 1
            self.index += 1
            sub_name = self.all_tokens[self.index][0]
            type_of = self.table.type_of(identifier)
            if type_of != "None":
                self.num_args += 1
                var_kind = self.table.kind_of(identifier)
                var_index = self.table.index_of(identifier)
                self.func_name = "{}.{}".format(type_of, sub_name)
                self.vm.write_push(self.CONVERT_KIND[var_kind.upper()], var_index)
            else:
                class_name = identifier
                self.func_name = "{}.{}".format(class_name, sub_name)
        elif self.all_tokens[self.index + 1][0] == "(":
            sub_name = self.all_tokens[self.index][0]
            self.func_name = "{}.{}".format(self.clas_name, sub_name)
            self.num_args += 1
            self.vm.write_push("POINTER", 0)
        self.index += 1
        self.compile_expression_list()
        self.index += 1
        self.vm.write_call(self.func_name, self.num_args)

    def compile_let(self) -> None:
        """Compiles a let statement."""
        # Your code goes here!
        self.index += 1
        var_name = self.all_tokens[self.index][0]
        index_of = self.table.index_of(var_name)
        if self.table.kind_of(var_name) == "argument":
            kind = "ARG"
        else:
            kind = self.CONVERT_KIND[self.table.kind_of(var_name).upper()]
        if self.all_tokens[self.index + 1][0] == "[":
            self.index += 1
            self.compile_expression()
            self.index += 1
            self.vm.write_push(kind, index_of)
            self.vm.write_arithmetic("ADD")
            self.vm.write_pop("TEMP", 0)
            self.index += 1
            self.compile_expression()
            self.index += 1
            self.vm.write_push("TEMP", 0)
            self.vm.write_pop("POINTER", 1)
            self.vm.write_pop("THAT", 0)
        else:
            self.index += 1
            self.compile_expression()
            self.index += 1
            self.vm.write_pop(kind, index_of)



    def compile_while(self) -> None:
        """Compiles a while statement."""
        # Your code goes here!
        self.while_index += 1
        while_index = self.while_index
        self.vm.write_label("WHILE{}".format(while_index))
        self.index += 1
        self.compile_expression()
        self.vm.write_arithmetic("NOT")
        self.index += 1
        self.index += 1
        self.vm.write_if("WHILE_END{}".format(while_index))
        self.compile_statements()
        self.vm.write_goto("WHILE{}".format(while_index))
        self.vm.write_label("WHILE_END{}".format(while_index))
        self.index += 1

    def compile_return(self) -> None:
        """Compiles a return statement."""
        # Your code goes here!
        if self.all_tokens[self.index + 1][0] != ";":
            self.compile_expression()
        else:
            self.vm.write_push("CONST", 0)
        self.vm.write_return()
        self.index += 1

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        # Your code goes here!
        self.if_index += 1
        if_index = self.if_index
        self.index += 1
        self.compile_expression()
        self.index += 1
        self.index += 1
        self.vm.write_if("IF_TRUE{}".format(if_index))
        self.vm.write_goto("IF_FALSE{}".format(if_index))
        self.vm.write_label("IF_TRUE{}".format(if_index))
        self.compile_statements()
        self.vm.write_goto("IF_END{}".format(if_index))
        self.index += 1
        self.vm.write_label("IF_FALSE{}".format(if_index))
        if self.all_tokens[self.index + 1][0] == "else":
            self.index += 1
            self.index += 1
            self.compile_statements()
            self.index += 1
        self.vm.write_label("IF_END{}".format(if_index))

    def compile_expression(self) -> None:
        """Compiles an expression."""
        # Your code goes here!
        self.compile_term()
        op_lst = ["+", "-", "*", "/", "&", "|", "<", ">", "="]
        while self.all_tokens[self.index + 1][0] in op_lst:
            self.index += 1
            op = self.all_tokens[self.index][0]
            self.compile_term()
            if op in self.ARITHMETIC.keys():
                self.vm.write_arithmetic(self.ARITHMETIC[op])
            elif op == '*':
                self.vm.write_call('Math.multiply', 2)
            elif op == '/':
                self.vm.write_call('Math.divide', 2)

    def compile_term(self) -> None:
        """Compiles a term. 
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        # Your code goes here!

        if self.all_tokens[self.index + 1][0] == "~" or self.all_tokens[self.index + 1][0] == "-" \
                or self.all_tokens[self.index + 1][0] == "^" or self.all_tokens[self.index + 1][0] == "#":
            self.index += 1
            unary_op = self.all_tokens[self.index][0]
            self.compile_term()
            self.vm.write_arithmetic(self.ARITHMETIC_UNARY[unary_op])
        elif self.all_tokens[self.index + 1][0] == "(":
            self.index += 1
            self.compile_expression()
            self.index += 1
        elif self.all_tokens[self.index + 1][1] == "INT_CONST":
            self.index += 1
            self.vm.write_push("CONST", self.all_tokens[self.index][0])
        elif self.all_tokens[self.index + 1][1] == "STRING_CONST":
            self.index += 1
            string = self.all_tokens[self.index][0]  # stringConstant

            self.vm.write_push("CONST", len(string))
            self.vm.write_call("String.new", 1)

            for char in string:
                self.vm.write_push('CONST', ord(char))
                self.vm.write_call("String.appendChar", 2)
        elif self.all_tokens[self.index + 1][1] == "KEYWORD":
            self.index += 1
            keyword = self.all_tokens[self.index][0]  # keywordConstant

            if keyword == "this":
                self.vm.write_push("POINTER", 0)
            else:
                self.vm.write_push("CONST", 0)
                if keyword == "true":
                    self.vm.write_arithmetic("NOT")
        else:
            if self.all_tokens[self.index + 2][0] == "[":
                self.index += 1
                var_name = self.all_tokens[self.index][0]
                self.index += 1
                self.compile_expression()
                self.index += 1
                if self.table.kind_of(var_name) == "argument":
                    kind = "ARG"
                else:
                    kind = self.CONVERT_KIND[self.table.kind_of(var_name).upper()]
                array_i = self.table.index_of(var_name)
                self.vm.write_push(kind, array_i)
                self.vm.write_arithmetic("ADD")
                self.vm.write_pop("POINTER", 1)
                self.vm.write_push("THAT", 0)
            elif self.all_tokens[self.index + 2][0] == "(" or self.all_tokens[self.index + 2][0] == ".":
                self.subroutine_call()
            else:
                self.index += 1
                var = self.all_tokens[self.index][0]
                if self.table.kind_of(var) == "argument":
                    var_kind = "ARG"
                else:
                    var_kind = self.CONVERT_KIND[self.table.kind_of(var).upper()]
                var_index = self.table.index_of(var)
                self.vm.write_push(var_kind, var_index)

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        # Your code goes here!
        if ")" != self.all_tokens[self.index + 1][0]:
            self.num_args += 1
            self.compile_expression()
        while ')' != self.all_tokens[self.index + 1][0]:
            self.num_args += 1
            self.index += 1
            self.compile_expression()
