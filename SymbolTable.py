"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class SymbolTable:
    """A symbol table that associates names with information needed for Jack
    compilation: type, kind and running index. The symbol table has two nested
    scopes (class/subroutine).
    """

    def __init__(self) -> None:
        """Creates a new empty symbol table."""
        # Your code goes here!
        self.class_table = {}
        self.subroutine_table = {}
        self.static_counter = 0
        self.field_counter = 0
        self.arg_counter = 0
        self.var_counter = 0

    def start_subroutine(self) -> None:
        """Starts a new subroutine scope (i.e., resets the subroutine's 
        symbol table).
        """
        # Your code goes here!
        self.subroutine_table = {}
        self.arg_counter = 0
        self.var_counter = 0

    def define(self, name: str, type: str, kind: str) -> None:
        """Defines a new identifier of a given name, type and kind and assigns 
        it a running index. "STATIC" and "FIELD" identifiers have a class scope, 
        while "ARG" and "VAR" identifiers have a subroutine scope.

        Args:
            name (str): the name of the new identifier.
            type (str): the type of the new identifier.
            kind (str): the kind of the new identifier, can be:
            "STATIC", "FIELD", "ARG", "VAR".
        """
        # Your code goes here!
        if kind == "STATIC" or kind == "FIELD":
            if kind == "STATIC":
                self.class_table[name] = (type, kind.lower(), self.static_counter)
                self.static_counter += 1
            if kind == "FIELD":
                self.class_table[name] = (type, kind.lower(), self.field_counter)
                self.field_counter += 1
        elif kind == "VAR" or kind == "ARG":
            if kind == "VAR":
                self.subroutine_table[name] = (type, kind.lower(), self.var_counter)
                self.var_counter += 1
            if kind == "ARG":
                self.subroutine_table[name] = (type, "argument", self.arg_counter)
                self.arg_counter += 1

    def var_count(self, kind: str) -> int:
        """
        Args:
            kind (str): can be "STATIC", "FIELD", "ARG", "VAR".

        Returns:
            int: the number of variables of the given kind already defined in 
            the current scope.
        """
        # Your code goes here!
        if kind == "VAR":
            return self.var_counter
        if kind == "ARG":
            return self.arg_counter
        if kind == "FIELD":
            return self.field_counter
        if kind == "STATIC":
            return self.static_counter

    def kind_of(self, name: str) -> str:
        """
        Args:
            name (str): name of an identifier.

        Returns:
            str: the kind of the named identifier in the current scope, or None
            if the identifier is unknown in the current scope.
        """
        # Your code goes here!
        if name in self.subroutine_table.keys():
            return self.subroutine_table[name][1]
        if name in self.class_table.keys():
            return self.class_table[name][1]
        return 'None'

    def type_of(self, name: str) -> str:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            str: the type of the named identifier in the current scope.
        """
        # Your code goes here!
        if name in self.subroutine_table.keys():
            return self.subroutine_table[name][0]
        if name in self.class_table.keys():
            return self.class_table[name][0]
        return "None"

    def index_of(self, name: str) -> int:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            int: the index assigned to the named identifier.
        """
        # Your code goes here!
        if name in self.subroutine_table.keys():
            return self.subroutine_table[name][2]
        if name in self.class_table.keys():
            return self.class_table[name][2]
