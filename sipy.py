"""!
SiPy: Statistics in Python

Date created: 9th September 2022

License: GNU General Public License version 3 for academic or 
not-for-profit use only

SiPy package is free software: you can redistribute it and/or 
modify it under the terms of the GNU General Public License as 
published by the Free Software Foundation, either version 3 of the 
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""
import datetime
import os
import subprocess
import sys
import traceback
import warnings
warnings.filterwarnings("ignore")

import numpy
import pandas as pd

import data_wrangler as dw
import libsipy
import sipy_info


class SiPy_Shell(object):
    """!
    Command-line shell for SiPy.
    """
    def __init__(self):
        """!
        Initialization method.
        """
        self.count = 1
        self.data = {}
        self.environment = {"cwd": os.getcwd(),
                            "prompt": ">>>",
                            "separator": ","}
        self.history = {}
        self.modules = [m for m in dir(libsipy) 
                        if m not in ['__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__path__', '__spec__']]
        self.result = {}
        self.session = {}
    
    def formatExceptionInfo(self, maxTBlevel=10):
        """!
        Method to gather information about an exception raised. It is used to readout the exception messages and type of exception. This method takes a parameter, maxTBlevel, which is set to 10, which defines the maximum level of tracebacks to recall.
        
        This method is obtained from http://www.linuxjournal.com/article.php?sid=5821
        """
        cla, exc, trbk = sys.exc_info()
        excName = cla.__name__
        try: excArgs = exc.__dict__["args"]
        except KeyError: excArgs = "<no args>"
        excTb = traceback.format_tb(trbk, maxTBlevel)
        return (excName, excArgs, excTb)
        
    def header(self):
        """!
        Prints header, which is displayed at the start of the shell.
        """
        print(sipy_info.header)
        return None
        
    def do_copyright(self):
        """!
        Prints copyright statement.
        """
        print(sipy_info.copyright)
        return sipy_info.copyright
    
    def do_credits(self):
        """!
        Prints list of credits for SiPy development.
        """
        print(sipy_info.credits)
        print(sipy_info.citations)
        return sipy_info.credits + sipy_info.citations
        
    def do_license(self):
        """!
        Prints license statement.
        """
        print("")
        license = open("LICENSE", "r").readlines()
        license = [x[:-1] for x in license]
        for line in license: print(line)
        print("")
        return license
        
    def intercept_processor(self, statement):
        """!
        Method to intercept non-bytecode statements and channel to the appropriate handlers.
        
        @param statement String: command-line statement
        """
        if statement == "copyright": return self.do_copyright()
        if statement == "credits": return self.do_credits()
        if statement == "exit": return "exit"
        if statement == "license": return self.do_license()
        if statement == "quit": return "exit"
        
    def error_message(self, code, msg):
        """!
        Generic error code/message printer to display error/warning messages.
        
        @param code String: error/warning code to display
        @param msg String: error/warning message to display
        """
        print("%s: %s" % (str(code), str(msg)))

    def do_let(self, operand):
        """!
        Assign a value or list of values to a variable.

        Commands: 
            let <variable_name> be number <value>
            let <variable_name> be list <comma-separated values>
            let <variable_name> be frame <data descriptor>
        """
        variable_name = operand[0]
        data_type = operand[2]
        if data_type.lower() in ["numeric", "number", "num", "integer", "int", "float", "value"]:
            data_values = operand[3]
            self.data[variable_name] = float(data_values)
            retR = "%s = %s" % (variable_name, str(data_values))
        elif data_type.lower() in ["list", "series", "tuple", "vector"]:
            data_values = "".join(operand[3:])
            data_values = [float(x) for x in data_values.split(self.environment["separator"])]
            self.data[variable_name] = pd.Series(data_values)
            retR = "%s = %s" % (variable_name, str(data_values))
        elif data_type.lower() in ["dataframe", "df", "frame", "table"]:
            data_values = operand[3:]
            source_descriptors = [x.split(":") for x in data_values]
            source_data = {}
            for d in source_descriptors: 
                source_data[d[0]] = self.data[d[1]]
            self.data[variable_name] = pd.concat(source_data, axis=1)
            retR = "%s = %s" % (variable_name, str(data_values))
        print(retR)
        return retR

    def do_mean(self, operand):
        """!
        Calculating various means (arithmetic mean, geometric mean, harmonic mean) of the values.

        Commands: 
            mean {arithmetic} <variable_name>

        Reference: 
            - https://github.com/mauriceling/mauriceling.github.io/wiki/Arithmetic-mean
        """
        variable_name = operand[1]
        data_values = self.data[variable_name]
        if operand[0].lower() in ["arithmetic", "amean", "average", "avg", "mean"]:
            result = libsipy.base.arithmeticMean(data_values)
            retR = "Arimethic mean = %s" % result
        else: 
            retR = "Unknown sub-operation: %s" % operand[0].lower()
        print(retR)
        return retR

    def do_normality(self, operand):
        """!
        Perform normality test(s) on the values.

        Commands: 
            normality {kurtosis} <variable_name>

        References: 
            - Kurtosis test: Anscombe FJ, Glynn WJ. 1983. Distribution of the kurtosis statistic b2 for normal samples. Biometrika 70, 227-234. (https://github.com/mauriceling/mauriceling.github.io/wiki/Kurtosis-test)

        """
        variable_name = operand[1]
        data_values = self.data[variable_name]
        if operand[0].lower() == "kurtosis":
            result = libsipy.base.kurtosisNormalityTest(data_values)
            if type(result[0]) is numpy.ndarray:
                retR = "Z-score, p-value \n"
                temp = [[str(result[0][i]), str(result[1][i])]
                        for i in range(len(result[0]))]
                temp = [", ".join(x) for x in temp]
                retR = retR + " \n".join(temp)
            else:
                retR = "Z-score = %f; p-value = %f" % (result[0], result[1])
        else: 
            retR = "Unknown sub-operation: %s" % operand[0].lower()
        print(retR)
        return retR

    def do_read(self, operand):
        """!
        Read external data files into SiPy.

        Commands: 
            read excel <variable_name> be <file_name> <sheet_name>
        """
        variable_name = operand[1]
        if operand[0].lower() == "excel":
            df = pd.read_excel(operand[4], sheet_name=operand[5])
            self.data[variable_name] = df

    def do_show(self, operand):
        """!
        Show various status of the SiPy.

        Commands: 
            show {data|history|environment|modules}
            show item <history number>
        """
        if operand[0].lower() in ["data", "d"]:
            for x in self.data: 
                retR = self.data
                print("%s: %s" % (str(x), str(self.data[x])))
        elif operand[0].lower() in ["history", "hist", "h"]:
            for x in self.history: 
                retR = self.history
                print("%s: %s" % (str(x), str(self.history[x])))
        elif operand[0].lower() in ["environment", "env", "e"]:
            for x in self.environment: 
                retR = self.environment
                print("%s: %s" % (str(x), str(self.environment[x])))
        elif operand[0].lower() in ["item", "i"]:
            item = str(int(operand[1]))
            retR = ["Command: %s" % (str(self.history[item])),
                    "Result: %s" % (str(self.result[item]))]
            print(retR[0])
            print(retR[1])
            retR = "\n".join(retR)
        elif operand[0].lower() in ["modules", "mod", "m"]:
            print("List of Available Modules:")
            retR = self.modules
            for module in self.modules: print(module)
        elif operand[0].lower() in ["result", "r"]:
            retR = self.result
            for x in self.result:
                print("%s: %s" % (str(x), str(self.result[x])))
        else: 
            retR = "Unknown sub-operation: %s" % operand[0].lower()
        return retR

    def command_processor(self, operator, operand):
        """
        Method to channel bytecodes operand(s), if any, into the respective bytecode processors.
        
        @param operator String: bytecode operator
        @param operand list: bytecode operand(s), if any
        """
        if operator == "let": return self.do_let(operand)
        elif operator == "mean": return self.do_mean(operand)
        elif operator == "normality": return self.do_normality(operand)
        elif operator == "read": return self.do_read(operand)
        elif operator == "show": return self.do_show(operand)
        else: print("Unknown command / operation: %s" % operator)

    def interpret(self, statement):
        """!
        Method to process an input statement by either sending it to SiPy_Shell.intercept_processor() or SiPy_Shell.command_processor().
        
        @param statement String: command-line statement
        """
        try:
            self.history[str(self.count)] = statement
            if statement.lower() in ["copyright", "copyright;", "credits", "credits;", "exit", "exit;",
                                     "license", "license;", "quit", "quit;"]:
                 retR = self.intercept_processor(statement)
                 if retR == "exit": return "exit"
            else:
                statement = statement.strip()
                statement = [x.strip() for x in statement.split()]
                operator = statement[0].lower()
                operand = statement[1:]
                retR = self.command_processor(operator, operand)
            self.result[str(self.count)] = retR
            self.count = self.count + 1
        except:
            error_message = list(self.formatExceptionInfo())
            for line in error_message:
                if (type(line) == list):
                    for l in line: 
                        print(l)

    def cmdLoop(self):
        """!
        Command-line loop executor. This runs the shell like a command-line interpreter and calls SiPy_Shell.interpret() method to process the statement/command from the command-line.
        
        @return: session dictionary
        """
        self.header()
        while True:
            statement = input("SiPy: %s %s " % (str(self.count), self.environment["prompt"])).strip() 
            if statement == "exit": return 0
            elif statement.startswith("#"): continue
            else: self.interpret(statement)
            print("")
        return self.session

    def cmdScript(self, script):
        """!
        Script executor. This method is used to execute a script file that is passed into SiPy and calls SiPy_Shell.interpret() method to process the ordered list of commands in script.
        
        @param script: ordered list of commands in script to execute.
        @return: session dictionary
        """
        for statement in script:
            statement = statement.strip()
            print('Command #%s: %s' % (str(self.count), statement))
            if statement == 'exit': return 0
            self.interpret(statement)
        return self.session


if __name__ == "__main__":
    shell = SiPy_Shell()
    if len(sys.argv) == 1:
        shell.cmdLoop()
        sys.exit()
    if len(sys.argv) == 2:
        scriptfile = os.path.abspath(sys.argv[1])
        shell.cmdScript(script)
        sys.exit()