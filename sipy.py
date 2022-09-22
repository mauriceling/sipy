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
        
    def do_variance(self, operand):
        data_type = operand[1].lower()
        if operand[0].lower() in ["bartlett"]:
            if data_type in ["list", "series", "tuple", "vector"]:
                data_values = [self.data[operand[i]] for i in range(2, len(operand))]
                result = libsipy.base.BartlettTest(data_values)
                retR = "F = %.3f; p-value = %s" % (result.statistic, result.pvalue)
            elif data_type in ["dataframe", "df", "frame", "table"]:
                pass
        else: 
            retR = "Unknown sub-operation: %s" % operand[0].lower()
        print(retR)
        return retR

    def do_anova(self, operand):
        data_type = operand[1].lower()
        if operand[0].lower() in ["1way"]:
            if data_type in ["list", "series", "tuple", "vector"]:
                data_values = [self.data[operand[i]] for i in range(2, len(operand))]
                result = libsipy.base.anova1way(data_values)
                retR = "F = %.3f; p-value = %s" % (result.statistic, result.pvalue)
            elif data_type in ["dataframe", "df", "frame", "table"]:
                pass
        else: 
            retR = "Unknown sub-operation: %s" % operand[0].lower()
        print(retR)
        return retR
    
    def do_describe(self, operand):
        """!
        Calculating various descriptions(standard deviation, variance, standarad error) of the values.

        Commands: 
            describe {} <variable_name>

        Reference: 
            - 
        """
        variable_name = operand[1]
        data_values = self.data[variable_name]
        if operand[0].lower() in ["kurtosis" , "kurt"]:
            result = libsipy.base.kurtosis(data_values)
            retR = "Kurtosis = %s" % result
        elif operand[0].lower() in ["skew" , "sk"]:
            result = libsipy.base.skew(data_values)
            retR = "Skew = %s" % result
        elif operand[0].lower() in ["stdev", "stdev.s", "s", "sd"]:
            result = libsipy.base.standardDeviation(data_values)
            retR = "Standard deviation = %s" % result
        elif operand[0].lower() in ["se"]:
            result = libsipy.base.standardError(data_values)
            retR = "Standard error = %s" % result
        elif operand[0].lower() in ["var", "var.s"]:
            result = libsipy.base.variance(data_values)
            retR = "Variance = %s" % result
        else: 
            retR = "Unknown sub-operation: %s" % operand[0].lower()
        print(retR)
        return retR

    def do_let(self, operand):
        """!
        Assign a value or list of values to a variable.

        Commands: 
            let <variable_name> be number <value>
            let <variable_name> be list <comma-separated values>
            let <variable_name> be frame <data descriptor>
        """
        variable_name = operand[0]
        if operand[1].lower() == "be":
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
        elif operand[1].lower() == "from":
            pass
        print(retR)
        return retR

    def do_mean(self, operand):
        """!
        Calculating various means (arithmetic mean, geometric mean, harmonic mean) of the values.

        Commands: 
            mean {arithmetic|geometric|harmonic} <variable_name>

        Reference: 
            - https://github.com/mauriceling/mauriceling.github.io/wiki/Arithmetic-mean
        """
        variable_name = operand[1]
        data_values = self.data[variable_name]
        if operand[0].lower() in ["arithmetic", "amean", "average", "avg", "mean"]:
            result = libsipy.base.arithmeticMean(data_values)
            retR = "Arimethic mean = %s" % result
        elif operand[0].lower() in ["geometric", "gmean", "geo"]:
            result = libsipy.base.geometricMean(data_values)
            retR = "Geometric mean = %s" % result
        elif operand[0].lower() in ["harmonic", "hmean", "harm"]:
            result = libsipy.base.harmonicMean(data_values)
            retR = "Harmonic mean = %s" % result
        else: 
            retR = "Unknown sub-operation: %s" % operand[0].lower()
        print(retR)
        return retR

    def do_normality(self, operand):
        """!
        Perform normality test(s) on the values.

        Commands: 
            normality {kurtosis} <variable_name>
        """
        variable_name = operand[1]
        data_values = self.data[variable_name]
        if operand[0].lower() == "kurtosis":
            result = libsipy.base.kurtosisNormalityTest(data_values)
            retR = "Z-score = %f; p-value = %f" % (result[0], result[1])
        elif operand[0].lower() in ["jb" , "jarquebera" , "jarqueBera"]:
            result = libsipy.base.jarqueBeraNormalityTest(data_values)
            retR = "Z-score = %f; p-value = %f" % (result[0], result[1])
        elif operand[0].lower() in ["shapirowilk" , "sw" , "shapiroWilk"]:
            result = libsipy.base.shapiroWilkNormalityTest(data_values)
            retR = "Z-score = %f; p-value = %f" % (result[0], result[1])
        elif operand[0].lower() in ["skewtest" , "sk"]:
            result = libsipy.base.skewNormalityTest(data_values)
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
            read excel <variable_name> from <file_name> <sheet_name>
        """
        variable_name = operand[1]
        if operand[0].lower() == "excel":
            df = pd.read_excel(operand[3], sheet_name=operand[4])
            self.data[variable_name] = df
            retR = "Read Excel: %s.%s into %s" % (operand[3], operand[4], operand[1])
        else: 
            retR = "Unknown sub-operation: %s" % operand[0].lower()
        print(retR)
        return retR

    def do_regression(self, operand):
        """!
        Performs regression(s).

        Commands:
            regress linear <dependent variable name> <independent variable name> [False for intercept=0]
            regress logistic <dependent variable name> <independent variable name>
        """
        if operand[0].lower() in ["linear", "lin"]:
            try: 
                if operand[3] in [True, "True", "TRUE", "true", "T", "t", "Yes", "YES", "Y", "y"]:
                    add_intercept = True
                elif operand[3] in [False, "False", "FALSE", "false", "F", "f", "No", "NO", "N", "n"]:
                    add_intercept = False
                else:
                    add_intercept = True
            except IndexError: add_intercept = True
            y = self.data[operand[1]]
            X = self.data[operand[2]]
            retR = libsipy.base.regressionLinear(X, y, add_intercept)
        elif operand[0].lower() in ["logistic", "log"]:
            y = self.data[operand[1]]
            X = self.data[operand[2]]
            retR = libsipy.base.regressionLogistic(X, y)
        else: 
            retR = "Unknown sub-operation: %s" % operand[0].lower()
        print(retR)
        return retR

    def do_show(self, operand):
        """!
        Show various status of the SiPy.

        Commands: 
            show data [variable name]
            show {history|environment|modules}
            show item <history number>
        """
        if operand[0].lower() in ["data", "d"]:
            if len(operand) == 1: 
                # show data
                for x in self.data: 
                    retR = self.data
                    print("%s: %s" % (str(x), str(self.data[x])))
            else: 
                # show data <variable name>
                item = str(operand[1])
                retR = {item: self.data[item]}
                print("%s: %s" % (item, str(retR[item])))
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

    def do_ttest(self, operand):
        """!
        Performs Student's t-test(s) on values.

        Commands:
            ttest 1s {list|series|tuple|vector} <variable name> <population mean>
            ttest 2se {list|series|tuple|vector} <variable name A> <variable name B>
            ttest 2su {list|series|tuple|vector} <variable name A> <variable name B>
            ttest paired {list|series|tuple|vector} <variable name A> <variable name B>
        """
        data_type = operand[1].lower()
        if operand[0].lower() in ["1s", "1sample"]:
            data_values = self.data[operand[2]]
            mu = float(operand[3])
            if data_type in ["list", "series", "tuple", "vector"]:
                retR = libsipy.base.tTest1Sample(data_values, mu)
            elif data_type in ["dataframe", "df", "frame", "table"]:
                pass
        elif operand[0].lower() in ["2se", "2sample_equal"]:
            data_valuesA = self.data[operand[2]]
            data_valuesB = self.data[operand[3]]
            if data_type in ["list", "series", "tuple", "vector"]:
                retR = libsipy.base.tTest2SampleEqual(data_valuesA, data_valuesB)
        elif operand[0].lower() in ["2su", "2sample_unequal"]:
            data_valuesA = self.data[operand[2]]
            data_valuesB = self.data[operand[3]]
            if data_type in ["list", "series", "tuple", "vector"]:
                retR = libsipy.base.tTest2SampleUnequal(data_valuesA, data_valuesB)
        elif operand[0].lower() in ["paired", "dependent"]:
            data_valuesA = self.data[operand[2]]
            data_valuesB = self.data[operand[3]]
            if data_type in ["list", "series", "tuple", "vector"]:
                retR = libsipy.base.tTest2SamplePaired(data_valuesA, data_valuesB )
        else: 
            retR = "Unknown sub-operation: %s" % operand[0].lower()
        print(retR)
        return retR

    def command_processor(self, operator, operand):
        """
        Method to channel bytecodes operand(s), if any, into the respective bytecode processors.
        
        @param operator String: bytecode operator
        @param operand list: bytecode operand(s), if any
        """
        if operator == "describe": return self.do_describe(operand)
        elif operator == "let": return self.do_let(operand)
        elif operator == "mean": return self.do_mean(operand)
        elif operator == "normality": return self.do_normality(operand)
        elif operator == "read": return self.do_read(operand)
        elif operator == "regress": return self.do_regression(operand)
        elif operator == "show": return self.do_show(operand)
        elif operator == "ttest": return self.do_ttest(operand)
        elif operator == "anova": return self.do_anova(operand)
        elif operator == "variance": return self.do_variance(operand)
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