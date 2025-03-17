"""!
SiPy: Statistics in Python (GUI Version)

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
import FreeSimpleGUI as sg

import libsipy
import sipy_info
import sipy_plugins
from sipy_pm import PluginManager


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
        if os.path.exists(os.path.abspath("portable_R\\bin\\Rscript.exe")):
            rscript_exe = os.path.abspath("portable_R\\bin\\Rscript.exe")
        else: rscript_exe = None
        self.environment = {"cwd": os.getcwd(),
                            "plugin_directory": "sipy_plugins",
                            "plugin_system": True,
                            "prompt": ">>>",
                            "rscript_exe": rscript_exe,
                            "separator": ",",
                            "sipy_directory": os.getcwd(),
                            "verbosity": 0}
        self.history = {}
        self.modules = [m for m in dir(libsipy) 
                        if m not in ['__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__path__', '__spec__']]
        self.result = {}
        # Plugin Manager Initialization
        self.sipy_pm = PluginManager()
        try:
            self.available_plugins = [p[:-3] for p in os.listdir(os.sep.join([self.environment["sipy_directory"], self.environment["plugin_directory"]]))
                                      if p.endswith(".py")]
            self.available_plugins = [p for p in self.available_plugins
                                      if p not in ["__init__", "base_plugin", "sample_plugin"]]
        except:
            self.available_plugins = None
            self.environment["plugin_directory"] = ""
            self.environment["plugin_system"] = False
    
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
    
    def do_citation(self):
        """!
        Prints citation information.
        """
        print(sipy_info.citations)
        return sipy_info.citations

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
        return sipy_info.credits
        
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
        if statement == "citation": return self.do_citation()
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

    def do_anova(self, operand, kwargs):
        """!
        Performs comparison of means for 2 or more samples.

        Commands: 
            anova 1way {list|series|tuple|vector} <variable name 1> <variable name 2> ... <variable name N>
            anova 1way {list|series|tuple|vector} data=<variable name 1>,<variable name 2>, ... ,<variable name N>

            anova 1way {dataframe|df|frame|table} wide <variable name>
            anova 1way {dataframe|df|frame|table} wide data=<variable name>

            anova rm {dataframe|df|frame|table} wide <variable name>
            anova rm {dataframe|df|frame|table} wide data=<variable name>

            #anova kruskal {list|series|tuple|vector} <variable name 1> <variable name 2> ... <variable name N>
            #anova kruskal {dataframe|df|frame|table} wide <variable name>

        @return: String containing results of command execution
        """
        data_type = operand[1].lower()
        if operand[0].lower() == "1way":
            if data_type in ["list", "series", "tuple", "vector"]:
                if "data" not in kwargs:
                    """
                    anova 1way {list|series|tuple|vector} <variable name 1> <variable name 2> ... <variable name N>
                    
                    Example:
                    let X1 be list 1,2,3,4,5,6
                    let X2 be list 2,3,4,5,6,7
                    let X3 be list 3,4,5,6,7,8
                    anova 1way list X1 X2 X3
                    """
                    data_values = [self.data[operand[i]] for i in range(2, len(operand))]
                else:
                    """
                    anova 1way {list|series|tuple|vector} data=<variable name 1>,<variable name 2>, ... ,<variable name N>
                    
                    Example:
                    let X1 be list 1,2,3,4,5,6
                    let X2 be list 2,3,4,5,6,7
                    let X3 be list 3,4,5,6,7,8
                    anova 1way list data=X1,X2,X3
                    """
                    data_list = kwargs["data"].split(self.environment["separator"])
                    data_values = [self.data[x.strip()] for x in data_list]
                result = libsipy.base.anova1way(data_values)
                retR = "F = %.3f; p-value = %s" % (result.statistic, result.pvalue)
            elif data_type in ["dataframe", "df", "frame", "table"] and operand[2].lower() == "wide":
                if "data" not in kwargs:
                    """
                    anova 1way {dataframe|df|frame|table} wide <variable name>

                    Example:
                    let X1 be list 1,2,3,4,5,6
                    let X2 be list 2,3,4,5,6,7
                    let z be dataframe X1:X1 X2:X2
                    anova 1way dataframe wide z
                    """
                    data_values = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns="all", rtype="list")
                else:
                    """
                    anova 1way {dataframe|df|frame|table} wide data=<variable name>

                    Example:
                    let X1 be list 1,2,3,4,5,6
                    let X2 be list 2,3,4,5,6,7
                    let z be dataframe X1:X1 X2:X2
                    anova 1way dataframe wide data=z
                    """
                    data_values = libsipy.data_wrangler.df_extract(df=self.data[kwargs["data"]], columns="all", rtype="list")
                result = libsipy.base.anova1way(data_values)
                retR = "F = %.3f; p-value = %s" % (result.statistic, result.pvalue)
        # elif operand[0].lower() in ["kruskal"]:
        #     if data_type in ["list", "series", "tuple", "vector"]:
        #         # anova 1way {list|series|tuple|vector} <variable name 1> <variable name 2> ... <variable name N>
        #         data_values = [self.data[operand[i]] for i in range(2, len(operand))]
        #         result = libsipy.base.anovakruskal(data_values)
        #         retR = "F = %.3f; p-value = %s" % (result.statistic, result.pvalue)
        #     elif data_type in ["dataframe", "df", "frame", "table"] and operand[2].lower() == "wide":
        #         # anova 1way {dataframe|df|frame|table} wide <variable name>
        #         data_values = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns="all", rtype="list")
        #         result = libsipy.base.anovakruskal(data_values)
        #         retR = "F = %.3f; p-value = %s" % (result.statistic, result.pvalue)
        elif operand[0].lower() in ["rm", "repeated-measure"]:
            if data_type in ["dataframe", "df", "frame", "table"] and operand[2].lower() == "wide":
                if "data" not in kwargs:
                    """
                    anova rm {dataframe|df|frame|table} wide <variable name>

                    Example:
                    let X1 be list 1,2,3,4,5,6
                    let X2 be list 2,3,4,5,6,7
                    let z be dataframe X1:X1 X2:X2
                    anova rm dataframe wide z
                    """
                    data_values = self.data[operand[3]]
                else:
                    """
                    anova rm {dataframe|df|frame|table} wide data=<variable name>

                    Example:
                    let X1 be list 1,2,3,4,5,6
                    let X2 be list 2,3,4,5,6,7
                    let z be dataframe X1:X1 X2:X2
                    anova rm dataframe wide data=z
                    """
                    data_values = self.data[kwargs["data"]]
                retR = libsipy.base.anovaRM_wide(data_values)
        else: 
            retR = "Unknown sub-operation: %s" % operand[0].lower()
        print(retR)
        return retR
    
    def do_compute_effsize(self, operand, kwargs):
        """!
        Calculates effect size between 2 sets of observations.

        Commands:
            compute_effsize none {list|series|tuple|vector} <variable name A> <variable name B>
            compute_effsize none {list|series|tuple|vector} data=<variable name A>,<variable name B>
            compute_effsize none {dataframe|df|frame|table} wide <variable name> <series name A> <series name B>
            compute_effsize none {dataframe|df|frame|table} wide data=<variable name>.<series name A>,<variable name>.<series name B>

            compute_effsize cohen {list|series|tuple|vector} <variable name A> <variable name B>
            compute_effsize cohen {list|series|tuple|vector} data=<variable name A>,<variable name B>
            compute_effsize cohen {dataframe|df|frame|table} wide <variable name> <series name A> <series name B>
            compute_effsize cohen {dataframe|df|frame|table} wide data=<variable name>.<series name A>,<variable name>.<series name B>

            compute_effsize hedges {list|series|tuple|vector} <variable name A> <variable name B>
            compute_effsize hedges {list|series|tuple|vector} data=<variable name A>,<variable name B>
            compute_effsize hedges {dataframe|df|frame|table} wide <variable name> <series name A> <series name B>
            compute_effsize hedges {dataframe|df|frame|table} wide data=<variable name>.<series name A>,<variable name>.<series name B>
            
            compute_effsize r {list|series|tuple|vector} <variable name A> <variable name B>
            compute_effsize r {list|series|tuple|vector} data=<variable name A>,<variable name B>
            compute_effsize r {dataframe|df|frame|table} wide <variable name> <series name A> <series name B>
            compute_effsize r {dataframe|df|frame|table} wide data=<variable name>.<series name A>,<variable name>.<series name B>
            
            ####not working compute_effsize pointbiserialr {list|series|tuple|vector} <variable name A> <variable name B>
            compute_effsize pointbiserialr {dataframe|df|frame|table} wide <variable name> <series name A> <series name B>####
            
            compute_effsize eta-square {list|series|tuple|vector} <variable name A> <variable name B>
            compute_effsize eta-square {list|series|tuple|vector} data=<variable name A>,<variable name B>
            compute_effsize eta-square {dataframe|df|frame|table} wide <variable name> <series name A> <series name B>
            compute_effsize eta-square {dataframe|df|frame|table} wide data=<variable name>.<series name A>,<variable name>.<series name B>
            
            compute_effsize odds-ratio {list|series|tuple|vector} <variable name A> <variable name B>
            compute_effsize odds-ratio {list|series|tuple|vector} data=<variable name A>,<variable name B>
            compute_effsize odds-ratio {dataframe|df|frame|table} wide <variable name> <series name A> <series name B>
            compute_effsize odds-ratio {dataframe|df|frame|table} wide data=<variable name>.<series name A>,<variable name>.<series name B>
            
            compute_effsize AUC {list|series|tuple|vector} <variable name A> <variable name B>
            compute_effsize AUC {list|series|tuple|vector} data=<variable name A>,<variable name B>
            compute_effsize AUC {dataframe|df|frame|table} wide <variable name> <series name A> <series name B>
            compute_effsize AUC {dataframe|df|frame|table} wide data=<variable name>.<series name A>,<variable name>.<series name B>
            
            compute_effsize CLES {list|series|tuple|vector} <variable name A> <variable name B>
            compute_effsize CLES {list|series|tuple|vector} data=<variable name A>,<variable name B>
            compute_effsize CLES {dataframe|df|frame|table} wide <variable name> <series name A> <series name B>
            compute_effsize CLES {dataframe|df|frame|table} wide data=<variable name>.<series name A>,<variable name>.<series name B>

        @return: String containing results of command execution
        """
        data_type = operand[1].lower()
        if operand[0].lower() in ["none"]:
            if data_type in ["list", "series", "tuple", "vector"]:
                if "data" not in kwargs:
                    """
                    compute_effsize none {list|series|tuple|vector} <variable name A> <variable name B>

                    Example:
                    let x be list 2,3,4,5,6,7,8,9
                    let y be list 3,4,5,6,7,8,9,10
                    compute_effsize none list x y
                    """
                    data_valuesA = self.data[operand[2]]
                    data_valuesB = self.data[operand[3]]
                else:
                    """
                    compute_effsize none {list|series|tuple|vector} data=<variable name A>,<variable name B>

                    Example:
                    let x be list 2,3,4,5,6,7,8,9
                    let y be list 3,4,5,6,7,8,9,10
                    compute_effsize none list data=x,y
                    """
                    datavar = [x.strip() for x in kwargs["data"].split(self.environment["separator"])]
                    data_valuesA = self.data[datavar[0]]
                    data_valuesB = self.data[datavar[1]]
                retR = libsipy.base.compute_effsize_none(data_valuesA, data_valuesB)
            elif data_type in ["dataframe", "df", "frame", "table"] and operand[2].lower() == "wide":
                if "data" not in kwargs:
                    """
                    compute_effsize none {dataframe|df|frame|table} wide <variable name> <series name A> <series name B>

                    Example:
                    let x be list 1,2,3,4,5
                    let y be list 2,3,4,5,6
                    let z be dataframe x:x y:y
                    compute_effsize none dataframe wide z x y
                    """
                    data_valuesA = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns=operand[4], rtype="list")
                    data_valuesB = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns=operand[5], rtype="list")
                else:
                    """
                    compute_effsize none {dataframe|df|frame|table} wide data=<variable name>.<series name A>,<variable name>.<series name B>

                    Example:
                    let x be list 1,2,3,4,5
                    let y be list 2,3,4,5,6
                    let z be dataframe x:x y:y
                    compute_effsize none dataframe wide data=z.x,z.y
                    """
                    datavar = [x.strip() for x in kwargs["data"].split(self.environment["separator"])]
                    dA = [x.strip() for x in datavar[0].split(".")]
                    dB = [x.strip() for x in datavar[1].split(".")]
                    data_valuesA = libsipy.data_wrangler.df_extract(df=self.data[dA[0]], columns=dA[1], rtype="list")
                    data_valuesB = libsipy.data_wrangler.df_extract(df=self.data[dB[0]], columns=dB[1], rtype="list")
                retR = libsipy.base.compute_effsize_none(data_valuesA, data_valuesB)
        elif operand[0].lower() in ["cohen", "d"]:
            if data_type in ["list", "series", "tuple", "vector"]:
                if "data" not in kwargs:
                    """
                    compute_effsize cohen {list|series|tuple|vector} <variable name A> <variable name B>

                    Example:
                    let x be list 2,3,4,5,6,7,8,9
                    let y be list 3,4,5,6,7,8,9,10
                    compute_effsize cohen list x y
                    """
                    data_valuesA = self.data[operand[2]]
                    data_valuesB = self.data[operand[3]]
                else:
                    """
                    compute_effsize cohen {list|series|tuple|vector} data=<variable name A>,<variable name B>

                    Example:
                    let x be list 2,3,4,5,6,7,8,9
                    let y be list 3,4,5,6,7,8,9,10
                    compute_effsize cohen list data=x,y
                    """
                    datavar = [x.strip() for x in kwargs["data"].split(self.environment["separator"])]
                    data_valuesA = self.data[datavar[0]]
                    data_valuesB = self.data[datavar[1]]
                retR = libsipy.base.compute_effsize_cohen(data_valuesA, data_valuesB)
            elif data_type in ["dataframe", "df", "frame", "table"] and operand[2].lower() == "wide":
                if "data" not in kwargs:
                    """
                    compute_effsize cohen {dataframe|df|frame|table} wide <variable name> <series name A> <series name B>

                    Example:
                    let x be list 1,2,3,4,5
                    let y be list 2,3,4,5,6
                    let z be dataframe x:x y:y
                    compute_effsize cohen dataframe wide z x y
                    """
                    data_valuesA = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns=operand[4], rtype="list")
                    data_valuesB = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns=operand[5], rtype="list")
                else:
                    """
                    compute_effsize cohen {dataframe|df|frame|table} wide data=<variable name>.<series name A>,<variable name>.<series name B>

                    Example:
                    let x be list 1,2,3,4,5
                    let y be list 2,3,4,5,6
                    let z be dataframe x:x y:y
                    compute_effsize cohen dataframe wide data=z.x,z.y
                    """
                    datavar = [x.strip() for x in kwargs["data"].split(self.environment["separator"])]
                    dA = [x.strip() for x in datavar[0].split(".")]
                    dB = [x.strip() for x in datavar[1].split(".")]
                    data_valuesA = libsipy.data_wrangler.df_extract(df=self.data[dA[0]], columns=dA[1], rtype="list")
                    data_valuesB = libsipy.data_wrangler.df_extract(df=self.data[dB[0]], columns=dB[1], rtype="list")
                retR = libsipy.base.compute_effsize_cohen(data_valuesA, data_valuesB)  
        elif operand[0].lower() in ["hedges", "g"]:
            if data_type in ["list", "series", "tuple", "vector"]:
                if "data" not in kwargs:
                    """
                    compute_effsize hedges {list|series|tuple|vector} <variable name A> <variable name B>

                    Example:
                    let x be list 2,3,4,5,6,7,8,9
                    let y be list 3,4,5,6,7,8,9,10
                    compute_effsize hedges list x y
                    """
                    data_valuesA = self.data[operand[2]]
                    data_valuesB = self.data[operand[3]]
                else:
                    """
                    compute_effsize hedges {list|series|tuple|vector} data=<variable name A>,<variable name B>
                    
                    Example:
                    let x be list 2,3,4,5,6,7,8,9
                    let y be list 3,4,5,6,7,8,9,10
                    compute_effsize hedges list data=x,y
                    """
                    datavar = [x.strip() for x in kwargs["data"].split(self.environment["separator"])]
                    data_valuesA = self.data[datavar[0]]
                    data_valuesB = self.data[datavar[1]]
                retR = libsipy.base.compute_effsize_hedges(data_valuesA, data_valuesB)
            elif data_type in ["dataframe", "df", "frame", "table"] and operand[2].lower() == "wide":
                if "data" not in kwargs:
                    """
                    compute_effsize hedges {dataframe|df|frame|table} wide <variable name> <series name A> <series name B>

                    Example:
                    let x be list 1,2,3,4,5
                    let y be list 2,3,4,5,6
                    let z be dataframe x:x y:y
                    compute_effsize hedges dataframe wide z x y
                    """
                    data_valuesA = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns=operand[4], rtype="list")
                    data_valuesB = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns=operand[5], rtype="list")
                else:
                    """
                    compute_effsize hedges {dataframe|df|frame|table} wide data=<variable name>.<series name A>,<variable name>.<series name B>

                    Example:
                    let x be list 1,2,3,4,5
                    let y be list 2,3,4,5,6
                    let z be dataframe x:x y:y
                    compute_effsize hedges dataframe wide data=z.x,z.y
                    """
                    datavar = [x.strip() for x in kwargs["data"].split(self.environment["separator"])]
                    dA = [x.strip() for x in datavar[0].split(".")]
                    dB = [x.strip() for x in datavar[1].split(".")]
                    data_valuesA = libsipy.data_wrangler.df_extract(df=self.data[dA[0]], columns=dA[1], rtype="list")
                    data_valuesB = libsipy.data_wrangler.df_extract(df=self.data[dB[0]], columns=dB[1], rtype="list")
                retR = libsipy.base.compute_effsize_hedges(data_valuesA, data_valuesB)              
        elif operand[0].lower() in ["pearson", "r"]:
            if data_type in ["list", "series", "tuple", "vector"]:
                if "data" not in kwargs:
                    """
                    compute_effsize r {list|series|tuple|vector} <variable name A> <variable name B>

                    Example:
                    let x be list 2,3,4,5,6,7,8,9
                    let y be list 3,4,5,6,7,8,9,10
                    compute_effsize r list x y
                    """
                    data_valuesA = self.data[operand[2]]
                    data_valuesB = self.data[operand[3]]
                else:
                    """
                    compute_effsize r {list|series|tuple|vector} data=<variable name A>,<variable name B>
                    
                    Example:
                    let x be list 2,3,4,5,6,7,8,9
                    let y be list 3,4,5,6,7,8,9,10
                    compute_effsize r list data=x,y
                    """
                    datavar = [x.strip() for x in kwargs["data"].split(self.environment["separator"])]
                    data_valuesA = self.data[datavar[0]]
                    data_valuesB = self.data[datavar[1]]
                retR = libsipy.base.compute_effsize_r(data_valuesA, data_valuesB)
            elif data_type in ["dataframe", "df", "frame", "table"] and operand[2].lower() == "wide":
                if "data" not in kwargs:
                    """
                    compute_effsize r {dataframe|df|frame|table} wide <variable name> <series name A> <series name B>

                    Example:
                    let x be list 1,2,3,4,5
                    let y be list 2,3,4,5,6
                    let z be dataframe x:x y:y
                    compute_effsize r dataframe wide z x y
                    """
                    data_valuesA = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns=operand[4], rtype="list")
                    data_valuesB = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns=operand[5], rtype="list")
                else:
                    """
                    compute_effsize r {dataframe|df|frame|table} wide data=<variable name>.<series name A>,<variable name>.<series name B>

                    Example:
                    let x be list 1,2,3,4,5
                    let y be list 2,3,4,5,6
                    let z be dataframe x:x y:y
                    compute_effsize r dataframe wide data=z.x,z.y
                    """
                    datavar = [x.strip() for x in kwargs["data"].split(self.environment["separator"])]
                    dA = [x.strip() for x in datavar[0].split(".")]
                    dB = [x.strip() for x in datavar[1].split(".")]
                    data_valuesA = libsipy.data_wrangler.df_extract(df=self.data[dA[0]], columns=dA[1], rtype="list")
                    data_valuesB = libsipy.data_wrangler.df_extract(df=self.data[dB[0]], columns=dB[1], rtype="list")
                retR = libsipy.base.compute_effsize_r(data_valuesA, data_valuesB)  
        # elif operand[0].lower() in ["pointbiserialr"]:
        #     if data_type in ["list", "series", "tuple", "vector"]:
        #         # compute_effsize pointbiserialr {list|series|tuple|vector} <variable name A> <variable name B>
        #         data_valuesA = self.data[operand[2]]
        #         data_valuesB = self.data[operand[3]]
        #         retR = libsipy.base.compute_effsize_pointbiserialr(data_valuesA, data_valuesB)
        #     elif data_type in ["dataframe", "df", "frame", "table"] and operand[2].lower() == "wide":
        #         # compute_effsize pointbiserialr {dataframe|df|frame|table} wide <variable name> <series name A> <series name B>
        #         data_valuesA = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns=operand[4], rtype="list")
        #         data_valuesB = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns=operand[5], rtype="list")
        #         retR = libsipy.base.compute_effsize_pointbiserialr(data_valuesA, data_valuesB)              
        elif operand[0].lower() in ["eta-square"]:
            if data_type in ["list", "series", "tuple", "vector"]:
                if "data" not in kwargs:
                    """
                    compute_effsize eta-square {list|series|tuple|vector} <variable name A> <variable name B>

                    Example:
                    let x be list 2,3,4,5,6,7,8,9
                    let y be list 3,4,5,6,7,8,9,10
                    compute_effsize eta-square list x y
                    """
                    data_valuesA = self.data[operand[2]]
                    data_valuesB = self.data[operand[3]]
                else:
                    """
                    compute_effsize eta-square {list|series|tuple|vector} data=<variable name A>,<variable name B>

                    Example:
                    let x be list 2,3,4,5,6,7,8,9
                    let y be list 3,4,5,6,7,8,9,10
                    compute_effsize eta-square list data=x,y
                    """
                    datavar = [x.strip() for x in kwargs["data"].split(self.environment["separator"])]
                    data_valuesA = self.data[datavar[0]]
                    data_valuesB = self.data[datavar[1]]
                retR = libsipy.base.compute_effsize_etasquare(data_valuesA, data_valuesB)
            elif data_type in ["dataframe", "df", "frame", "table"] and operand[2].lower() == "wide":
                if "data" not in kwargs:
                    """
                    compute_effsize eta-square {dataframe|df|frame|table} wide <variable name> <series name A> <series name B>

                    Example:
                    let x be list 1,2,3,4,5
                    let y be list 2,3,4,5,6
                    let z be dataframe x:x y:y
                    compute_effsize eta-square dataframe wide z x y
                    """
                    data_valuesA = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns=operand[4], rtype="list")
                    data_valuesB = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns=operand[5], rtype="list")
                else:
                    """
                    compute_effsize eta-square {dataframe|df|frame|table} data=wide <variable name>.<series name A>,<variable name>.<series name B>

                    Example:
                    let x be list 1,2,3,4,5
                    let y be list 2,3,4,5,6
                    let z be dataframe x:x y:y
                    compute_effsize eta-square dataframe wide data=z.x,z.y
                    """
                    datavar = [x.strip() for x in kwargs["data"].split(self.environment["separator"])]
                    dA = [x.strip() for x in datavar[0].split(".")]
                    dB = [x.strip() for x in datavar[1].split(".")]
                    data_valuesA = libsipy.data_wrangler.df_extract(df=self.data[dA[0]], columns=dA[1], rtype="list")
                    data_valuesB = libsipy.data_wrangler.df_extract(df=self.data[dB[0]], columns=dB[1], rtype="list")
                retR = libsipy.base.compute_effsize_etasquare(data_valuesA, data_valuesB)              
        elif operand[0].lower() in ["odds-ratio", "or"]:
            if data_type in ["list", "series", "tuple", "vector"]:
                if "data" not in kwargs:
                    """
                    compute_effsize odds-ratio {list|series|tuple|vector} <variable name A> <variable name B>

                    Example:
                    let x be list 2,3,4,5,6,7,8,9
                    let y be list 3,4,5,6,7,8,9,10
                    compute_effsize odds-ratio list x y
                    """
                    data_valuesA = self.data[operand[2]]
                    data_valuesB = self.data[operand[3]]
                else:
                    """
                    compute_effsize odds-ratio {list|series|tuple|vector} data=<variable name A>,<variable name B>

                    Example:
                    let x be list 2,3,4,5,6,7,8,9
                    let y be list 3,4,5,6,7,8,9,10
                    compute_effsize odds-ratio list data=x,y
                    """
                    datavar = [x.strip() for x in kwargs["data"].split(self.environment["separator"])]
                    data_valuesA = self.data[datavar[0]]
                    data_valuesB = self.data[datavar[1]]
                retR = libsipy.base.compute_effsize_oddsratio(data_valuesA, data_valuesB)
            elif data_type in ["dataframe", "df", "frame", "table"] and operand[2].lower() == "wide":
                if "data" not in kwargs:
                    """
                    compute_effsize odds-ratio {dataframe|df|frame|table} wide <variable name> <series name A> <series name B>

                    Example:
                    let x be list 1,2,3,4,5
                    let y be list 2,3,4,5,6
                    let z be dataframe x:x y:y
                    compute_effsize odds-ratio dataframe wide z x y
                    """
                    data_valuesA = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns=operand[4], rtype="list")
                    data_valuesB = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns=operand[5], rtype="list")
                else:
                    """
                    compute_effsize odds-ratio {dataframe|df|frame|table} wide data=<variable name>.<series name A>,<variable name>.<series name B>

                    Example:
                    let x be list 1,2,3,4,5
                    let y be list 2,3,4,5,6
                    let z be dataframe x:x y:y
                    compute_effsize odds-ratio dataframe wide data=z.x,z.y
                    """
                    datavar = [x.strip() for x in kwargs["data"].split(self.environment["separator"])]
                    dA = [x.strip() for x in datavar[0].split(".")]
                    dB = [x.strip() for x in datavar[1].split(".")]
                    data_valuesA = libsipy.data_wrangler.df_extract(df=self.data[dA[0]], columns=dA[1], rtype="list")
                    data_valuesB = libsipy.data_wrangler.df_extract(df=self.data[dB[0]], columns=dB[1], rtype="list")
                retR = libsipy.base.compute_effsize_oddsratio(data_valuesA, data_valuesB)              
        elif operand[0].lower() in ["AUC", "auc"]:
            if data_type in ["list", "series", "tuple", "vector"]:
                if "data" not in kwargs:
                    """
                    compute_effsize AUC {list|series|tuple|vector} <variable name A> <variable name B>

                    Example:
                    let x be list 2,3,4,5,6,7,8,9
                    let y be list 3,4,5,6,7,8,9,10
                    compute_effsize auc list x y
                    """
                    data_valuesA = self.data[operand[2]]
                    data_valuesB = self.data[operand[3]]
                else:
                    """
                    compute_effsize AUC {list|series|tuple|vector} data=<variable name A>,<variable name B>

                    Example:
                    let x be list 2,3,4,5,6,7,8,9
                    let y be list 3,4,5,6,7,8,9,10
                    compute_effsize auc list data=x,y
                    """
                    datavar = [x.strip() for x in kwargs["data"].split(self.environment["separator"])]
                    data_valuesA = self.data[datavar[0]]
                    data_valuesB = self.data[datavar[1]]
                retR = libsipy.base.compute_effsize_AUC(data_valuesA, data_valuesB)
            elif data_type in ["dataframe", "df", "frame", "table"] and operand[2].lower() == "wide":
                if "data" not in kwargs:
                    """
                    compute_effsize AUC {dataframe|df|frame|table} wide <variable name> <series name A> <series name B>"

                    Example:
                    let x be list 1,2,3,4,5
                    let y be list 2,3,4,5,6
                    let z be dataframe x:x y:y
                    compute_effsize auc dataframe wide z x y
                    """
                    data_valuesA = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns=operand[4], rtype="list")
                    data_valuesB = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns=operand[5], rtype="list")
                else:
                    """
                    compute_effsize AUC {dataframe|df|frame|table} wide data=<variable name>.<series name A>,<variable name>.<series name B>

                    Example:
                    let x be list 1,2,3,4,5
                    let y be list 2,3,4,5,6
                    let z be dataframe x:x y:y
                    compute_effsize auc dataframe wide data=z.x,z.y
                    """
                    datavar = [x.strip() for x in kwargs["data"].split(self.environment["separator"])]
                    dA = [x.strip() for x in datavar[0].split(".")]
                    dB = [x.strip() for x in datavar[1].split(".")]
                    data_valuesA = libsipy.data_wrangler.df_extract(df=self.data[dA[0]], columns=dA[1], rtype="list")
                    data_valuesB = libsipy.data_wrangler.df_extract(df=self.data[dB[0]], columns=dB[1], rtype="list")
                retR = libsipy.base.compute_effsize_AUC(data_valuesA, data_valuesB)              
        elif operand[0].lower() in ["CLES", "cles"]:
            if data_type in ["list", "series", "tuple", "vector"]:
                if "data" not in kwargs:
                    """
                    compute_effsize CLES {list|series|tuple|vector} <variable name A> <variable name B>

                    Example:
                    let x be list 2,3,4,5,6,7,8,9
                    let y be list 3,4,5,6,7,8,9,10
                    compute_effsize cles list x y
                    """
                    data_valuesA = self.data[operand[2]]
                    data_valuesB = self.data[operand[3]]
                else:
                    """
                    compute_effsize CLES {list|series|tuple|vector} data=<variable name A>,<variable name B>

                    Example:
                    let x be list 2,3,4,5,6,7,8,9
                    let y be list 3,4,5,6,7,8,9,10
                    compute_effsize cles list data=x,y
                    """
                    datavar = [x.strip() for x in kwargs["data"].split(self.environment["separator"])]
                    data_valuesA = self.data[datavar[0]]
                    data_valuesB = self.data[datavar[1]]
                retR = libsipy.base.compute_effsize_CLES(data_valuesA, data_valuesB)
            elif data_type in ["dataframe", "df", "frame", "table"] and operand[2].lower() == "wide":
                if "data" not in kwargs:
                    """
                    compute_effsize CLES {dataframe|df|frame|table} wide <variable name> <series name A> <series name B>

                    Example:
                    let x be list 1,2,3,4,5
                    let y be list 2,3,4,5,6
                    let z be dataframe x:x y:y
                    compute_effsize cles dataframe wide z x y
                    """
                    data_valuesA = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns=operand[4], rtype="list")
                    data_valuesB = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns=operand[5], rtype="list")
                else:
                    """
                    compute_effsize CLES {dataframe|df|frame|table} wide data=<variable name>.<series name A>,<variable name>.<series name B>

                    Example:
                    let x be list 1,2,3,4,5
                    let y be list 2,3,4,5,6
                    let z be dataframe x:x y:y
                    compute_effsize cles dataframe wide data=z.x,z.y
                    """
                    datavar = [x.strip() for x in kwargs["data"].split(self.environment["separator"])]
                    dA = [x.strip() for x in datavar[0].split(".")]
                    dB = [x.strip() for x in datavar[1].split(".")]
                    data_valuesA = libsipy.data_wrangler.df_extract(df=self.data[dA[0]], columns=dA[1], rtype="list")
                    data_valuesB = libsipy.data_wrangler.df_extract(df=self.data[dB[0]], columns=dB[1], rtype="list")
                retR = libsipy.base.compute_effsize_CLES(data_valuesA, data_valuesB)                                 
        else: 
            retR = "Unknown sub-operation: %s" % operand[0].lower()
        print(retR)
        return retR

    def do_correlate(self, operand, kwargs):
        """!
        Performs correlation on values.

        Commands:
            correlate pearson {list|series|tuple|vector} <variable name A> <variable name B>
            correlate pearson {dataframe|df|frame|table} wide <variable name> <series name A> <series name B>
            correlate spearman {list|series|tuple|vector} <variable name A> <variable name B>
            correlate spearman {dataframe|df|frame|table} wide <variable name> <series name A> <series name B>
            correlate kendall {list|series|tuple|vector} <variable name A> <variable name B>
            correlate kendall {dataframe|df|frame|table} wide <variable name> <series name A> <series name B>
            
            ####### not working ##### correlate bicor {list|series|tuple|vector} <variable name A> <variable name B>
            
            correlate bicor {dataframe|df|frame|table} wide <variable name> <series name A> <series name B>
            correlate percbend {list|series|tuple|vector} <variable name A> <variable name B>
            correlate percbend {dataframe|df|frame|table} wide <variable name> <series name A> <series name B>
           
            ####### warning ####### correlate skipped {list|series|tuple|vector} <variable name A> <variable name B>
            ####### warning ####### correlate skipped {dataframe|df|frame|table} wide <variable name> <series name A> <series name B>
            
            ##### shepherd not working #####

            correlate kendall {list|series|tuple|vector} <variable name A> <variable name B>
            correlate kendall {dataframe|df|frame|table} wide <variable name> <series name A> <series name B>
            correlate distance {list|series|tuple|vector} <variable name A> <variable name B>
            correlate distance {dataframe|df|frame|table} wide <variable name> <series name A> <series name B>
             
            ##### not working correlate cv1 {list|series|tuple|vector} <variable name A> <variable name B>
            correlate cv1 {dataframe|df|frame|table} wide <variable name> <series name A> <series name B>
            correlate cv2 {list|series|tuple|vector} <variable name A> <variable name B>
            correlate cv2 {dataframe|df|frame|table} wide <variable name> <series name A> <series name B>####

        @return: String containing results of command execution
        """
        data_type = operand[1].lower()
        if operand[0].lower() in ["pearson", "r"]:
            if data_type in ["list", "series", "tuple", "vector"]:
                # correlate pearson {list|series|tuple|vector} <variable name A> <variable name B>
                data_valuesA = self.data[operand[2]]
                data_valuesB = self.data[operand[3]]
                retR = libsipy.base.correlatePearson(data_valuesA, data_valuesB)
            elif data_type in ["dataframe", "df", "frame", "table"] and operand[2].lower() == "wide":
                # correlate pearson {dataframe|df|frame|table} wide <variable name> <series name A> <series name B>
                data_valuesA = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns=operand[4], rtype="list")
                data_valuesB = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns=operand[5], rtype="list")
                retR = libsipy.base.correlatePearson(data_valuesA, data_valuesB)
        elif operand[0].lower() in ["spearman"]:
            if data_type in ["list", "series", "tuple", "vector"]:
                # correlate spearman {list|series|tuple|vector} <variable name A> <variable name B>
                data_valuesA = self.data[operand[2]]
                data_valuesB = self.data[operand[3]]
                retR = libsipy.base.correlateSpearman(data_valuesA, data_valuesB)
            elif data_type in ["dataframe", "df", "frame", "table"] and operand[2].lower() == "wide":
                # correlate spearman {dataframe|df|frame|table} wide <variable name> <series name A> <series name B>
                data_valuesA = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns=operand[4], rtype="list")
                data_valuesB = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns=operand[5], rtype="list")
                retR = libsipy.base.correlateSpearman(data_valuesA, data_valuesB)
        elif operand[0].lower() in ["kendall"]:
            if data_type in ["list", "series", "tuple", "vector"]:
                # correlate kendall {list|series|tuple|vector} <variable name A> <variable name B>
                data_valuesA = self.data[operand[2]]
                data_valuesB = self.data[operand[3]]
                retR = libsipy.base.correlateKendall(data_valuesA, data_valuesB)
            elif data_type in ["dataframe", "df", "frame", "table"] and operand[2].lower() == "wide":
                # correlate kendall {dataframe|df|frame|table} wide <variable name> <series name A> <series name B>
                data_valuesA = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns=operand[4], rtype="list")
                data_valuesB = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns=operand[5], rtype="list")
                retR = libsipy.base.correlateKendall(data_valuesA, data_valuesB)
        elif operand[0].lower() in ["bicor"]:
            if data_type in ["list", "series", "tuple", "vector"]:
                # correlate bicor {list|series|tuple|vector} <variable name A> <variable name B>
                data_valuesA = self.data[operand[2]]
                data_valuesB = self.data[operand[3]]
                retR = libsipy.base.correlateBicor(data_valuesA, data_valuesB)
            elif data_type in ["dataframe", "df", "frame", "table"] and operand[2].lower() == "wide":
                # correlate bicor {dataframe|df|frame|table} wide <variable name> <series name A> <series name B>
                data_valuesA = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns=operand[4], rtype="list")
                data_valuesB = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns=operand[5], rtype="list")
                retR = libsipy.base.correlateBicor(data_valuesA, data_valuesB)
        elif operand[0].lower() in ["percbend"]:
            if data_type in ["list", "series", "tuple", "vector"]:
                # correlate percbend {list|series|tuple|vector} <variable name A> <variable name B>
                data_valuesA = self.data[operand[2]]
                data_valuesB = self.data[operand[3]]
                retR = libsipy.base.correlatePercbend(data_valuesA, data_valuesB)
            elif data_type in ["dataframe", "df", "frame", "table"] and operand[2].lower() == "wide":
                # correlate percbend {dataframe|df|frame|table} wide <variable name> <series name A> <series name B>
                data_valuesA = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns=operand[4], rtype="list")
                data_valuesB = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns=operand[5], rtype="list")
                retR = libsipy.base.correlatePercbend(data_valuesA, data_valuesB)
        elif operand[0].lower() in ["skipped"]:
            if data_type in ["list", "series", "tuple", "vector"]:
                # correlate skipped {list|series|tuple|vector} <variable name A> <variable name B>
                data_valuesA = self.data[operand[2]]
                data_valuesB = self.data[operand[3]]
                retR = libsipy.base.correlateSkipped(data_valuesA, data_valuesB)
            elif data_type in ["dataframe", "df", "frame", "table"] and operand[2].lower() == "wide":
                # correlate skipped {dataframe|df|frame|table} wide <variable name> <series name A> <series name B>
                data_valuesA = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns=operand[4], rtype="list")
                data_valuesB = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns=operand[5], rtype="list")
                retR = libsipy.base.correlateSkipped(data_valuesA, data_valuesB)
        # elif operand[0].lower() in ["shepherd"]:
        #     if data_type in ["list", "series", "tuple", "vector"]:
        #         # correlate skipped {list|series|tuple|vector} <variable name A> <variable name B>
        #         data_valuesA = self.data[operand[2]]
        #         data_valuesB = self.data[operand[3]]
        #         retR = libsipy.base.correlateShepherd(data_valuesA, data_valuesB)
        #     elif data_type in ["dataframe", "df", "frame", "table"] and operand[2].lower() == "wide":
        #         # correlate skipped {dataframe|df|frame|table} wide <variable name> <series name A> <series name B>
        #         data_valuesA = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns=operand[4], rtype="list")
        #         data_valuesB = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns=operand[5], rtype="list")
        #         retR = libsipy.base.correlateShepherd(data_valuesA, data_valuesB)
        elif operand[0].lower() in ["distance"]:
            if data_type in ["list", "series", "tuple", "vector"]:
                # correlate distance {list|series|tuple|vector} <variable name A> <variable name B>
                data_valuesA = self.data[operand[2]]
                data_valuesB = self.data[operand[3]]
                retR = libsipy.base.correlateDistance(data_valuesA, data_valuesB)
            elif data_type in ["dataframe", "df", "frame", "table"] and operand[2].lower() == "wide":
                # correlate distance {dataframe|df|frame|table} wide <variable name> <series name A> <series name B>
                data_valuesA = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns=operand[4], rtype="list")
                data_valuesB = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns=operand[5], rtype="list")
                retR = libsipy.base.correlateDistance(data_valuesA, data_valuesB)
        elif operand[0].lower() in ["2cv"]:
            if data_type in ["list", "series", "tuple", "vector"]:
                # correlate skipped {list|series|tuple|vector} <variable name A> <variable name B>
                data_valuesA = self.data[operand[2]]
                data_valuesB = self.data[operand[3]]
                retR = libsipy.base.correlate2cv(data_valuesA, data_valuesB)
            elif data_type in ["dataframe", "df", "frame", "table"] and operand[2].lower() == "wide":
                # correlate skipped {dataframe|df|frame|table} wide <variable name> <series name A> <series name B>
                data_valuesA = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns=operand[4], rtype="list")
                data_valuesB = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns=operand[5], rtype="list")
                retR = libsipy.base.correlate2cv(data_valuesA, data_valuesB)
        elif operand[0].lower() in ["1cv"]:
            if data_type in ["list", "series", "tuple", "vector"]:
                # correlate skipped {list|series|tuple|vector} <variable name A> <variable name B>
                data_valuesA = self.data[operand[2]]
                data_valuesB = self.data[operand[3]]
                retR = libsipy.base.correlate1cv(data_valuesA, data_valuesB)
            elif data_type in ["dataframe", "df", "frame", "table"] and operand[2].lower() == "wide":
                # correlate skipped {dataframe|df|frame|table} wide <variable name> <series name A> <series name B>
                data_valuesA = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns=operand[4], rtype="list")
                data_valuesB = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns=operand[5], rtype="list")
                retR = libsipy.base.correlate1cv(data_valuesA, data_valuesB)
        else: 
            retR = "Unknown sub-operation: %s" % operand[0].lower()
        print(retR.to_string())
        return retR
    
    def do_describe(self, operand, kwargs):
        """!
        Calculating various descriptions (standard deviation, variance, standarad error) of the values.

        Commands: 
            describe {kurtosis|kurt} <variable_name>
            describe {skew|sk} <variable_name>
            describe {stdev|stdev.s|s|sd} <variable_name>
            describe se <variable_name>
            describe {var|var.s} <variable_name>

        @return: String containing results of command execution
        """
        variable_name = operand[1]
        data_values = self.data[variable_name]
        if operand[0].lower() in ["kurtosis" , "kurt"]:
            # describe {kurtosis|kurt} <variable_name>
            result = libsipy.base.kurtosis(data_values)
            retR = "Kurtosis = %s" % result
        elif operand[0].lower() in ["skew" , "sk"]:
            # describe {skew|sk} <variable_name>
            result = libsipy.base.skew(data_values)
            retR = "Skew = %s" % result
        elif operand[0].lower() in ["stdev", "stdev.s", "s", "sd"]:
            # describe {stdev|stdev.s|s|sd} <variable_name>
            result = libsipy.base.standardDeviation(data_values)
            retR = "Standard deviation = %s" % result
        elif operand[0].lower() in ["se"]:
            # describe se <variable_name>
            result = libsipy.base.standardError(data_values)
            retR = "Standard error = %s" % result
        elif operand[0].lower() in ["var", "var.s"]:
            # describe {var|var.s} <variable_name>
            result = libsipy.base.variance(data_values)
            retR = "Variance = %s" % result
        else: 
            retR = "Unknown sub-operation: %s" % operand[0].lower()
        print(retR)
        return retR

    def do_let(self, operand, kwargs):
        """!
        Assign a value or list of values to a variable.

        Commands: 
            let <variable_name> be {numeric|number|num|integer|int|float|value} <value>
            let <variable_name> be {list|series|tuple|vector} <comma-separated values>
            let <variable_name> be {dataframe|df|frame|table} <data descriptor>
            let <new_variable_name> from {dataframe|df|frame|table} <existing_variable_name> <series name>
            let <new_variable_name> melt <existing_variable_name> factor_name=<name of new factor> value_name=<name of value>

        @return: String containing results of command execution
        """
        variable_name = operand[0]
        if operand[1].lower() == "be":
            data_type = operand[2]
            if data_type.lower() in ["numeric", "number", "num", "integer", "int", "float", "value"]:
                # let <variable_name> be {numeric|number|num|integer|int|float|value} <value>
                data_values = operand[3]
                self.data[variable_name] = float(data_values)
                retR = "%s = %s" % (variable_name, str(data_values))
            elif data_type.lower() in ["list", "clist", "series", "tuple", "vector"]:
                # let <variable_name> be {list|clist|series|tuple|vector} <comma-separated values>
                data_values = "".join(operand[3:])
                data_values = [float(x) for x in data_values.split(self.environment["separator"])]
                self.data[variable_name] = pd.Series(data_values)
                retR = "%s = %s" % (variable_name, str(data_values))
            elif data_type.lower() in ["dlist"]:
                # let <variable_name> be dlist <comma-separated values>
                data_values = "".join(operand[3:])
                data_values = [int(x) for x in data_values.split(self.environment["separator"])]
                self.data[variable_name] = pd.Series(data_values)
                retR = "%s = %s" % (variable_name, str(data_values))
            elif data_type.lower() in ["slist"]:
                # let <variable_name> be slist <comma-separated values>
                data_values = "".join(operand[3:])
                data_values = [str(x) for x in data_values.split(self.environment["separator"])]
                self.data[variable_name] = pd.Series(data_values)
                retR = "%s = %s" % (variable_name, str(data_values))
            elif data_type.lower() in ["dataframe", "df", "frame", "table"]:
                # let <variable_name> be {dataframe|df|frame|table} <data descriptor>
                data_values = operand[3:]
                source_descriptors = [x.split(":") for x in data_values]
                source_data = {}
                for d in source_descriptors: 
                    source_data[d[0]] = self.data[d[1]]
                self.data[variable_name] = pd.concat(source_data, axis=1)
                retR = "%s = %s" % (variable_name, str(data_values))
        elif operand[1].lower() == "from" and operand[2].lower() in ["dataframe", "df", "frame", "table"]:
            if len(operand) == 5:
                # let <new_variable_name> from {dataframe|df|frame|table} <existing_variable_name> <series name>
                data_values = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns=operand[4], rtype="list")
                self.data[variable_name] = data_values
                retR = "%s from %s.%s; %s = %s" % (variable_name, operand[3], operand[4], variable_name, str(data_values))
        elif operand[1].lower() == "melt":
            # let <new_variable_name> melt <existing_variable_name> factor_name=<name of new factor> value_name=<name of value>
            if "retained_factors" in kwargs:
                id_vars = [str(f.strip()) for f in kwargs["retained_factors"].split(self.environment["separator"])]
                id_vars = ["ID"]
            else:
                id_vars = []
            data_values = libsipy.data_wrangler.df_melt(df=self.data[operand[2]], id_vars=id_vars, var_name=kwargs["factor_name"], value_name=kwargs["value_name"])
            self.data[variable_name] = data_values
            retR = "%s melted into %s" % (operand[2], variable_name)
        print(retR)
        return retR

    def do_mean(self, operand, kwargs):
        """!
        Calculating various means (arithmetic mean, geometric mean, harmonic mean) of the values.

        Commands: 
            mean {arithmetic|amean|average|avg|mean} <variable_name>
            mean {geometric|gmean|geo} <variable_name>
            mean {harmonic|hmean|harm} <variable_name>

        @return: String containing results of command execution
        """
        variable_name = operand[1]
        data_values = self.data[variable_name]
        if operand[0].lower() in ["arithmetic", "amean", "average", "avg", "mean"]:
            # mean {arithmetic|amean|average|avg|mean} <variable_name>
            result = libsipy.base.arithmeticMean(data_values)
            retR = "Arimethic mean = %s" % result
        elif operand[0].lower() in ["geometric", "gmean", "geo"]:
            # mean {geometric|gmean|geo} <variable_name>
            result = libsipy.base.geometricMean(data_values)
            retR = "Geometric mean = %s" % result
        elif operand[0].lower() in ["harmonic", "hmean", "harm"]:
            # mean {harmonic|hmean|harm} <variable_name>
            result = libsipy.base.harmonicMean(data_values)
            retR = "Harmonic mean = %s" % result
        else: 
            retR = "Unknown sub-operation: %s" % operand[0].lower()
        print(retR)
        return retR

    def do_normality(self, operand, kwargs):
        """!
        Perform normality test(s) on the values.

        Commands: 
            normality kurtosis <variable_name>
            normality {jarquebera|jb} <variable_name>
            normality {shapirowilk|sw} <variable_name>
            normality {skewtest|sk} <variable_name>

            normality kurtosis data=<variable_name>
            normality {jarquebera|jb} data=<variable_name>
            normality {shapirowilk|sw} data=<variable_name>
            normality {skewtest|sk} data=<variable_name>

        @return: String containing results of command execution
        """
        if "data" in kwargs:
            data_values = self.data[kwargs["data"]]
        else:
            variable_name = operand[1]
            data_values = self.data[variable_name]
        if operand[0].lower() == "kurtosis":
            """
            normality kurtosis <variable_name>
            normality kurtosis data=<variable_name>

            Example (list):
            let x be list 2,3,4,5,6,7,8,9
            normality kurtosis x
            normality kurtosis data=x

            Example (dataframe):
            let X1 be list 1,2,3,4,5,6
            let X2 be list 2,3,4,5,6,7
            let X3 be list 3,4,5,6,7,8
            let z be dataframe X1:X1 X2:X2 X3:X3
            normality kurtosis z
            normality kurtosis data=z
            """
            result = libsipy.base.kurtosisNormalityTest(data_values)
            retR = "Z-score = %s; p-value = %s" % (str(result[0]), str(result[1]))
        elif operand[0].lower() in ["jb" , "jarquebera" , "jarqueBera"]:
            """
            normality {jarquebera|jb} <variable_name>
            normality {jarquebera|jb} data=<variable_name>

            Example (list):
            let x be list 2,3,4,5,6,7,8,9
            normality jarquebera x
            normality jarquebera data=x

            Example (dataframe):
            let X1 be list 1,2,3,4,5,6
            let X2 be list 2,3,4,5,6,7
            let X3 be list 3,4,5,6,7,8
            let z be dataframe X1:X1 X2:X2 X3:X3
            normality jarquebera z
            normality jarquebera data=z
            """
            result = libsipy.base.jarqueBeraNormalityTest(data_values)
            retR = "Statistic = %s; p-value = %s" % (str(result[0]), str(result[1]))
        elif operand[0].lower() in ["shapirowilk" , "sw" , "shapiroWilk"]:
            """
            normality {shapirowilk|sw} <variable_name>
            normality {shapirowilk|sw} data=<variable_name>

            Example (list):
            let x be list 2,3,4,5,6,7,8,9
            normality shapirowilk x
            normality shapirowilk data=x

            Example (dataframe):
            let X1 be list 1,2,3,4,5,6
            let X2 be list 2,3,4,5,6,7
            let X3 be list 3,4,5,6,7,8
            let z be dataframe X1:X1 X2:X2 X3:X3
            normality shapirowilk z
            normality shapirowilk data=z
            """
            result = libsipy.base.shapiroWilkNormalityTest(data_values)
            retR = "Statistic = %s; p-value = %s" % (str(result[0]), str(result[1]))
        elif operand[0].lower() in ["skewtest" , "sk"]:
            """
            normality {skewtest|sk} <variable_name>
            normality {skewtest|sk} data=<variable_name>

            Example (list):
            let x be list 2,3,4,5,6,7,8,9
            normality skewtest x
            normality skewtest data=x

            Example (dataframe):
            let X1 be list 1,2,3,4,5,6
            let X2 be list 2,3,4,5,6,7
            let X3 be list 3,4,5,6,7,8
            let z be dataframe X1:X1 X2:X2 X3:X3
            normality skewtest z
            normality skewtest data=z
            """
            try:
                result = libsipy.base.skewNormalityTest(data_values)
            except ValueError:
                # caters for data frame variable
                data_values = libsipy.data_wrangler.df_extract(data_values, columns="all", rtype="list")
                data_values = libsipy.data_wrangler.flatten(data_values)
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

    def do_read(self, operand, kwargs):
        """!
        Read external data files into SiPy.

        Commands: 
            read excel <variable_name> from <file_name> <sheet_name>

        @return: String containing results of command execution
        """
        variable_name = operand[1]
        if operand[0].lower() == "excel":
            # read excel <variable_name> from <file_name> <sheet_name>
            df = pd.read_excel(operand[3], sheet_name=operand[4])
            self.data[variable_name] = df
            retR = "Read Excel: %s.%s into %s" % (operand[3], operand[4], operand[1])
        else: 
            retR = "Unknown sub-operation: %s" % operand[0].lower()
        print(retR)
        return retR

    def do_regression(self, operand, kwargs):
        """!
        Performs regression(s).

        Commands:
            regress linear <dependent variable name> <independent variable name> [False for intercept=0]
            regress linear y=<dependent variable name> x=<independent variable name> intercept=<intercept flag>
            regress logistic <dependent variable name> <independent variable name>
            regress logistic y=<dependent variable name> x=<independent variable name>

        @return: String containing results of command execution
        """
        if operand[0].lower() in ["linear", "lin"]:
            if "data" not in kwargs:
                # regress linear <dependent variable name> <independent variable name> [False for intercept=0]
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
            else:
                # regress linear y=<dependent variable name> x=<independent variable name> intercept=<intercept flag>
                y = self.data[kwargs["y"]]
                X = self.data[kwargs["x"]]
                if ("intercept" in kwargs):
                    add_intercept = True
                else:
                    add_intercept = False
            retR = libsipy.base.regressionLinear(X, y, add_intercept)
        elif operand[0].lower() in ["logistic", "log"]:
            if "data" not in kwargs:
                # regress logistic <dependent variable name> <independent variable name>
                y = self.data[operand[1]]
                X = self.data[operand[2]]
            else:
                # regress logistic y=<dependent variable name> x=<independent variable name>
                y = self.data[kwargs["y"]]
                X = self.data[kwargs["x"]]
            retR = libsipy.base.regressionLogistic(X, y)
        else: 
            retR = "Unknown sub-operation: %s" % operand[0].lower()
        print(retR.to_string())
        return retR

    def do_R_regression(self, operand, kwargs):
        """!
        Performs R-based regression(s).

        Commands: 
            rregress {decision_tree|dt} data=<dataframe> y=<dependent variable> x=<independent variable 1>,<independent variable 2>, ..., <independent variable n>
            rregress {elasticnet|elastic|enet} data=<dataframe> y=<dependent variable> x=<independent variable 1>,<independent variable 2>, ..., <independent variable n>
            rregress {gradient_boosting|gb} data=<dataframe> y=<dependent variable> x=<independent variable 1>,<independent variable 2>, ..., <independent variable n>
            rregress hurdle data=<dataframe> y=<dependent variable> x=<independent variable 1>,<independent variable 2>, ..., <independent variable n>
            rregress lasso data=<dataframe> y=<dependent variable> x=<independent variable 1>,<independent variable 2>, ..., <independent variable n>
            rregress {lm|linear|lin} data=<dataframe> y=<dependent variable> x=<independent variable 1>,<independent variable 2>, ..., <independent variable n>
            rregress {negbinom|negbi|nb data=<dataframe> y=<dependent variable> x=<independent variable 1>,<independent variable 2>, ..., <independent variable n>
            rregress poisson data=<dataframe> y=<dependent variable> x=<independent variable 1>,<independent variable 2>, ..., <independent variable n>
            rregress probit data=<dataframe> y=<dependent variable> x=<independent variable 1>,<independent variable 2>, ..., <independent variable n>
            rregress {randomforest|rf} data=<dataframe> y=<dependent variable> x=<independent variable 1>,<independent variable 2>, ..., <independent variable n>
            rregress svm data=<dataframe> y=<dependent variable> x=<independent variable 1>,<independent variable 2>, ..., <independent variable n>
            rregress svr data=<dataframe> y=<dependent variable> x=<independent variable 1>,<independent variable 2>, ..., <independent variable n>
            rregress zeroinfl data=<dataframe> y=<dependent variable> x=<independent variable 1>,<independent variable 2>, ..., <independent variable n>

        @return: String containing results of command execution
        """
        df = self.data[kwargs["data"]]
        dependent_variable = kwargs["y"]
        independent_variables = [x.strip() for x in kwargs["x"].split(self.environment["separator"])]
        if operand[0].lower() in ["decision_tree", "dt"]:
            """
            rregress {decision_tree|dt} data=<dataframe> y=<dependent variable> x=<independent variable 1>,<independent variable 2>, ..., <independent variable n>

            Example: 
            let yN be clist 1.2, 2.3, 3.1, 4.8, 5.6, 6.2, 7.9, 8.4, 9.7, 10.5
            let yB be dlist 1, 0, 1, 0, 1, 0, 1, 1, 0, 1
            let yC be slist A, B, C, A, B, C, A, B, C, A
            let x1 be clist 2, 3, 5, 7, 11, 13, 17, 19, 23, 29
            let x2 be clist 1, 4, 9, 16, 25, 36, 49, 64, 81, 100
            let x3 be clist 5, 8, 6, 10, 12, 14, 18, 20, 24, 30
            let x4 be clist 3.1, 5.2, 2.7, 8.6, 9.1, 4.4, 7.8, 6.5, 10.2, 11.3
            let x5 be clist 100, 90, 80, 70, 60, 50, 40, 30, 20, 10
            let df be dataframe yN:yN yB:yB x1:x1 x2:x2 x3:x3 x4:x4 x5:x5
            rregress decision_tree data=df y=yN x=x1,x2,x3,x4,x5
            """
            retR = libsipy.r_wrap.regression(df, dependent_variable, independent_variables, "decision_tree", None)
            retR = "\n".join(retR)
        elif operand[0].lower() in ["elasticnet", "elastic", "enet"]:
            """
            rregress {elasticnet|elastic|enet} data=<dataframe> y=<dependent variable> x=<independent variable 1>,<independent variable 2>, ..., <independent variable n>

            Example: 
            let yN be clist 1.2, 2.3, 3.1, 4.8, 5.6, 6.2, 7.9, 8.4, 9.7, 10.5
            let yB be dlist 1, 0, 1, 0, 1, 0, 1, 1, 0, 1
            let yC be slist A, B, C, A, B, C, A, B, C, A
            let x1 be clist 2, 3, 5, 7, 11, 13, 17, 19, 23, 29
            let x2 be clist 1, 4, 9, 16, 25, 36, 49, 64, 81, 100
            let x3 be clist 5, 8, 6, 10, 12, 14, 18, 20, 24, 30
            let x4 be clist 3.1, 5.2, 2.7, 8.6, 9.1, 4.4, 7.8, 6.5, 10.2, 11.3
            let x5 be clist 100, 90, 80, 70, 60, 50, 40, 30, 20, 10
            let df be dataframe yN:yN yB:yB yC:yC x1:x1 x2:x2 x3:x3 x4:x4 x5:x5
            rregress elasticnet data=df y=yN x=x1,x2,x3,x4,x5
            """
            retR = libsipy.r_wrap.regression(df, dependent_variable, independent_variables, "elasticnet", None)
            retR = "\n".join(retR)
        elif operand[0].lower() in ["gradient_boosting", "gb"]:
            """
            rregress {gradient_boosting|gb} data=<dataframe> y=<dependent variable> x=<independent variable 1>,<independent variable 2>, ..., <independent variable n>

            Example: 
            let yN be clist 1.2, 2.3, 3.1, 4.8, 5.6, 6.2, 7.9, 8.4, 9.7, 10.5
            let yB be dlist 1, 0, 1, 0, 1, 0, 1, 1, 0, 1
            let yC be slist A, B, C, A, B, C, A, B, C, A
            let x1 be clist 2, 3, 5, 7, 11, 13, 17, 19, 23, 29
            let x2 be clist 1, 4, 9, 16, 25, 36, 49, 64, 81, 100
            let x3 be clist 5, 8, 6, 10, 12, 14, 18, 20, 24, 30
            let x4 be clist 3.1, 5.2, 2.7, 8.6, 9.1, 4.4, 7.8, 6.5, 10.2, 11.3
            let x5 be clist 100, 90, 80, 70, 60, 50, 40, 30, 20, 10
            let df be dataframe yN:yN yB:yB yC:yC x1:x1 x2:x2 x3:x3 x4:x4 x5:x5
            rregress gradient_boosting data=df y=yN x=x1,x2,x3,x4,x5
            """
            retR = libsipy.r_wrap.regression(df, dependent_variable, independent_variables, "gradient_boosting", None)
            retR = "\n".join(retR)
        elif operand[0].lower() in ["hurdle"]:
            """
            rregress hurdle data=<dataframe> y=<dependent variable> x=<independent variable 1>,<independent variable 2>, ..., <independent variable n>

            Example: 
            let yN be clist 1.2, 2.3, 3.1, 4.8, 5.6, 6.2, 7.9, 8.4, 9.7, 10.5
            let yB be dlist 1, 0, 1, 0, 1, 0, 1, 1, 0, 1
            let yC be slist A, B, C, A, B, C, A, B, C, A
            let x1 be clist 2, 3, 5, 7, 11, 13, 17, 19, 23, 29
            let x2 be clist 1, 4, 9, 16, 25, 36, 49, 64, 81, 100
            let x3 be clist 5, 8, 6, 10, 12, 14, 18, 20, 24, 30
            let x4 be clist 3.1, 5.2, 2.7, 8.6, 9.1, 4.4, 7.8, 6.5, 10.2, 11.3
            let x5 be clist 100, 90, 80, 70, 60, 50, 40, 30, 20, 10
            let df be dataframe yN:yN yB:yB yC:yC x1:x1 x2:x2 x3:x3 x4:x4 x5:x5
            rregress hurdle data=df y=yB x=x1,x2,x3,x4,x5
            """
            retR = libsipy.r_wrap.regression(df, dependent_variable, independent_variables, "hurdle", None)
            retR = "\n".join(retR)
        elif operand[0].lower() in ["lasso"]:
            """
            rregress lasso data=<dataframe> y=<dependent variable> x=<independent variable 1>,<independent variable 2>, ..., <independent variable n>

            Example: 
            let yN be clist 1.2, 2.3, 3.1, 4.8, 5.6, 6.2, 7.9, 8.4, 9.7, 10.5
            let yB be dlist 1, 0, 1, 0, 1, 0, 1, 1, 0, 1
            let yC be slist A, B, C, A, B, C, A, B, C, A
            let x1 be clist 2, 3, 5, 7, 11, 13, 17, 19, 23, 29
            let x2 be clist 1, 4, 9, 16, 25, 36, 49, 64, 81, 100
            let x3 be clist 5, 8, 6, 10, 12, 14, 18, 20, 24, 30
            let x4 be clist 3.1, 5.2, 2.7, 8.6, 9.1, 4.4, 7.8, 6.5, 10.2, 11.3
            let x5 be clist 100, 90, 80, 70, 60, 50, 40, 30, 20, 10
            let df be dataframe yN:yN yB:yB yC:yC x1:x1 x2:x2 x3:x3 x4:x4 x5:x5
            rregress lasso data=df y=yN x=x1,x2,x3,x4,x5
            """
            retR = libsipy.r_wrap.regression(df, dependent_variable, independent_variables, "lasso", None)
            retR = "\n".join(retR)
        elif operand[0].lower() in ["lm", "linear", "lin"]:
            """
            rregress {lm|linear|lin} data=<dataframe> y=<dependent variable> x=<independent variable 1>,<independent variable 2>, ..., <independent variable n>

            Example: 
            let yN be clist 1.2, 2.3, 3.1, 4.8, 5.6, 6.2, 7.9, 8.4, 9.7, 10.5
            let yB be dlist 1, 0, 1, 0, 1, 0, 1, 1, 0, 1
            let yC be slist A, B, C, A, B, C, A, B, C, A
            let x1 be clist 2, 3, 5, 7, 11, 13, 17, 19, 23, 29
            let x2 be clist 1, 4, 9, 16, 25, 36, 49, 64, 81, 100
            let x3 be clist 5, 8, 6, 10, 12, 14, 18, 20, 24, 30
            let x4 be clist 3.1, 5.2, 2.7, 8.6, 9.1, 4.4, 7.8, 6.5, 10.2, 11.3
            let x5 be clist 100, 90, 80, 70, 60, 50, 40, 30, 20, 10
            let df be dataframe yN:yN yB:yB yC:yC x1:x1 x2:x2 x3:x3 x4:x4 x5:x5
            rregress lm data=df y=yN x=x1,x2,x3,x4,x5
            """
            retR = libsipy.r_wrap.regression(df, dependent_variable, independent_variables, "lm", None)
            retR = "\n".join(retR)
        elif operand[0].lower() in ["negbinom", "negbi", "nb"]:
            """
            rregress {negbinom|negbi|nb} data=<dataframe> y=<dependent variable> x=<independent variable 1>,<independent variable 2>, ..., <independent variable n>

            Example: 
            let yN be clist 1.2, 2.3, 3.1, 4.8, 5.6, 6.2, 7.9, 8.4, 9.7, 10.5
            let yB be dlist 1, 0, 1, 0, 1, 0, 1, 1, 0, 1
            let yC be slist A, B, C, A, B, C, A, B, C, A
            let x1 be clist 2, 3, 5, 7, 11, 13, 17, 19, 23, 29
            let x2 be clist 1, 4, 9, 16, 25, 36, 49, 64, 81, 100
            let x3 be clist 5, 8, 6, 10, 12, 14, 18, 20, 24, 30
            let x4 be clist 3.1, 5.2, 2.7, 8.6, 9.1, 4.4, 7.8, 6.5, 10.2, 11.3
            let x5 be clist 100, 90, 80, 70, 60, 50, 40, 30, 20, 10
            let df be dataframe yN:yN yB:yB yC:yC x1:x1 x2:x2 x3:x3 x4:x4 x5:x5
            rregress negbinom data=df y=yB x=x1,x2,x3,x4,x5
            """
            retR = libsipy.r_wrap.regression(df, dependent_variable, independent_variables, "negbinom", None)
            retR = "\n".join(retR)
        elif operand[0].lower() in ["poisson"]:
            """
            rregress poisson data=<dataframe> y=<dependent variable> x=<independent variable 1>,<independent variable 2>, ..., <independent variable n>

            Example: 
            let yN be clist 1.2, 2.3, 3.1, 4.8, 5.6, 6.2, 7.9, 8.4, 9.7, 10.5
            let yB be dlist 1, 0, 1, 0, 1, 0, 1, 1, 0, 1
            let yC be slist A, B, C, A, B, C, A, B, C, A
            let x1 be clist 2, 3, 5, 7, 11, 13, 17, 19, 23, 29
            let x2 be clist 1, 4, 9, 16, 25, 36, 49, 64, 81, 100
            let x3 be clist 5, 8, 6, 10, 12, 14, 18, 20, 24, 30
            let x4 be clist 3.1, 5.2, 2.7, 8.6, 9.1, 4.4, 7.8, 6.5, 10.2, 11.3
            let x5 be clist 100, 90, 80, 70, 60, 50, 40, 30, 20, 10
            let df be dataframe yN:yN yB:yB yC:yC x1:x1 x2:x2 x3:x3 x4:x4 x5:x5
            rregress poisson data=df y=yB x=x1,x2,x3,x4,x5
            """
            retR = libsipy.r_wrap.regression(df, dependent_variable, independent_variables, "poisson", None)
            retR = "\n".join(retR)
        elif operand[0].lower() in ["probit"]:
            """
            rregress probit data=<dataframe> y=<dependent variable> x=<independent variable 1>,<independent variable 2>, ..., <independent variable n>

            Example: 
            let yN be clist 1.2, 2.3, 3.1, 4.8, 5.6, 6.2, 7.9, 8.4, 9.7, 10.5
            let yB be dlist 1, 0, 1, 0, 1, 0, 1, 1, 0, 1
            let yC be slist A, B, C, A, B, C, A, B, C, A
            let x1 be clist 2, 3, 5, 7, 11, 13, 17, 19, 23, 29
            let x2 be clist 1, 4, 9, 16, 25, 36, 49, 64, 81, 100
            let x3 be clist 5, 8, 6, 10, 12, 14, 18, 20, 24, 30
            let x4 be clist 3.1, 5.2, 2.7, 8.6, 9.1, 4.4, 7.8, 6.5, 10.2, 11.3
            let x5 be clist 100, 90, 80, 70, 60, 50, 40, 30, 20, 10
            let df be dataframe yN:yN yB:yB yC:yC x1:x1 x2:x2 x3:x3 x4:x4 x5:x5
            rregress probit data=df y=yB x=x1,x2,x3,x4,x5
            """
            retR = libsipy.r_wrap.regression(df, dependent_variable, independent_variables, "probit_regression", None)
            retR = "\n".join(retR)
        elif operand[0].lower() in ["randomforest", "rf"]:
            """
            rregress {randomforest|rf} data=<dataframe> y=<dependent variable> x=<independent variable 1>,<independent variable 2>, ..., <independent variable n>

            Example: 
            let yN be clist 1.2, 2.3, 3.1, 4.8, 5.6, 6.2, 7.9, 8.4, 9.7, 10.5
            let yB be dlist 1, 0, 1, 0, 1, 0, 1, 1, 0, 1
            let yC be slist A, B, C, A, B, C, A, B, C, A
            let x1 be clist 2, 3, 5, 7, 11, 13, 17, 19, 23, 29
            let x2 be clist 1, 4, 9, 16, 25, 36, 49, 64, 81, 100
            let x3 be clist 5, 8, 6, 10, 12, 14, 18, 20, 24, 30
            let x4 be clist 3.1, 5.2, 2.7, 8.6, 9.1, 4.4, 7.8, 6.5, 10.2, 11.3
            let x5 be clist 100, 90, 80, 70, 60, 50, 40, 30, 20, 10
            let df be dataframe yN:yN yB:yB yC:yC x1:x1 x2:x2 x3:x3 x4:x4 x5:x5
            rregress randomforest data=df y=yN x=x1,x2,x3,x4,x5
            """
            retR = libsipy.r_wrap.regression(df, dependent_variable, independent_variables, "randomforest", None)
            retR = "\n".join(retR)
        elif operand[0].lower() in ["svm"]:
            """
            rregress svm data=<dataframe> y=<dependent variable> x=<independent variable 1>,<independent variable 2>, ..., <independent variable n>

            Example: 
            let yN be clist 1.2, 2.3, 3.1, 4.8, 5.6, 6.2, 7.9, 8.4, 9.7, 10.5
            let yB be dlist 1, 0, 1, 0, 1, 0, 1, 1, 0, 1
            let yC be slist A, B, C, A, B, C, A, B, C, A
            let x1 be clist 2, 3, 5, 7, 11, 13, 17, 19, 23, 29
            let x2 be clist 1, 4, 9, 16, 25, 36, 49, 64, 81, 100
            let x3 be clist 5, 8, 6, 10, 12, 14, 18, 20, 24, 30
            let x4 be clist 3.1, 5.2, 2.7, 8.6, 9.1, 4.4, 7.8, 6.5, 10.2, 11.3
            let x5 be clist 100, 90, 80, 70, 60, 50, 40, 30, 20, 10
            let df be dataframe yN:yN yB:yB yC:yC x1:x1 x2:x2 x3:x3 x4:x4 x5:x5
            rregress svm data=df y=yN x=x1,x2,x3,x4,x5
            """
            retR = libsipy.r_wrap.regression(df, dependent_variable, independent_variables, "svm", None)
            retR = "\n".join(retR)
        elif operand[0].lower() in ["svr"]:
            """
            rregress svr data=<dataframe> y=<dependent variable> x=<independent variable 1>,<independent variable 2>, ..., <independent variable n>

            Example: 
            let yN be clist 1.2, 2.3, 3.1, 4.8, 5.6, 6.2, 7.9, 8.4, 9.7, 10.5
            let yB be dlist 1, 0, 1, 0, 1, 0, 1, 1, 0, 1
            let yC be slist A, B, C, A, B, C, A, B, C, A
            let x1 be clist 2, 3, 5, 7, 11, 13, 17, 19, 23, 29
            let x2 be clist 1, 4, 9, 16, 25, 36, 49, 64, 81, 100
            let x3 be clist 5, 8, 6, 10, 12, 14, 18, 20, 24, 30
            let x4 be clist 3.1, 5.2, 2.7, 8.6, 9.1, 4.4, 7.8, 6.5, 10.2, 11.3
            let x5 be clist 100, 90, 80, 70, 60, 50, 40, 30, 20, 10
            let df be dataframe yN:yN yB:yB yC:yC x1:x1 x2:x2 x3:x3 x4:x4 x5:x5
            rregress svr data=df y=yN x=x1,x2,x3,x4,x5
            """
            retR = libsipy.r_wrap.regression(df, dependent_variable, independent_variables, "svr", None)
            retR = "\n".join(retR)
        elif operand[0].lower() in ["zeroinfl"]:
            """
            rregress zeroinfl data=<dataframe> y=<dependent variable> x=<independent variable 1>,<independent variable 2>, ..., <independent variable n>

            Example: 
            let yN be clist 1.2, 2.3, 3.1, 4.8, 5.6, 6.2, 7.9, 8.4, 9.7, 10.5
            let yB be dlist 1, 0, 1, 0, 1, 0, 1, 1, 0, 1
            let yC be slist A, B, C, A, B, C, A, B, C, A
            let x1 be clist 2, 3, 5, 7, 11, 13, 17, 19, 23, 29
            let x2 be clist 1, 4, 9, 16, 25, 36, 49, 64, 81, 100
            let x3 be clist 5, 8, 6, 10, 12, 14, 18, 20, 24, 30
            let x4 be clist 3.1, 5.2, 2.7, 8.6, 9.1, 4.4, 7.8, 6.5, 10.2, 11.3
            let x5 be clist 100, 90, 80, 70, 60, 50, 40, 30, 20, 10
            let df be dataframe yN:yN yB:yB yC:yC x1:x1 x2:x2 x3:x3 x4:x4 x5:x5
            rregress zeroinfl data=df y=yB x=x1,x2,x3,x4,x5
            """
            retR = libsipy.r_wrap.regression(df, dependent_variable, independent_variables, "zeroinfl", None)
            retR = "\n".join(retR)
        else: 
            retR = "Unknown sub-operation: %s" % operand[0].lower()
        print(retR)
        return retR

    def do_script(self, operand, kwargs):
        """!
        Performs scripting platform operations

        Commands: 
            script execute <file path to script>
            script execute file=<file path to script>
            script merge <file path to script> <merged output file name>
            script merge file=<file path to script> output=<merged output file name>
            script read <file path to script>
            script read file=<file path to script>

        @return: String containing results of command execution
        """
        option = operand[0].lower()
        if option.lower() in ["execute"]:
            if "data" not in kwargs:
                scriptfile = operand[1].strip()
            else:
                scriptfile = kwargs["file"]
            print(scriptfile)
            retR = self.runScript(scriptfile, "script_execute")
        elif option.lower() in ["merge"]:
            if "data" not in kwargs:
                scriptfile = operand[1].strip()
                outputfile = operand[2].strip()
            else:
                scriptfile = kwargs["file"]
                outputfile = kwargs["output"]
            print(scriptfile)
            retR = self.runScript(scriptfile, "script_merge")
            f = open(outputfile, "w")
            for line in retR: f.write(line + "\n")
            f.close()
        elif option.lower() in ["read"]:
            if "data" not in kwargs:
                scriptfile = operand[1].strip()
            else:
                scriptfile = kwargs["file"]
            print(scriptfile)
            retR = self.runScript(scriptfile, "script_read")
        else: 
            retR = "Unknown sub-operation: %s" % operand[0].lower()
        # print(retR)
        return retR

    def do_set(self, operand, kwargs):
        """!
        Set / change various status of the SiPy.

        Commands: 
            set current_directory <new current directory>
            set prompt <new prompt>
            set separator <new separator>

        @return: String containing results of command execution
        """
        if operand[0].lower() in ["current_directory", "cwd"]:
            # set current_directory <new current directory>
            old = self.environment["cwd"]
            self.environment["cwd"] = operand[1]
            retR = "set cwd from %s to %s" % (old, operand[1])
        elif operand[0].lower() in ["prompt"]:
            # set prompt <new prompt>
            old = self.environment["prompt"]
            self.environment["prompt"] = operand[1]
            retR = "set prompt from %s to %s" % (old, operand[1])
        elif operand[0].lower() in ["separator", "sep"]:
            # set seperator <new separator>
            old = self.environment["separator"]
            self.environment["separator"] = operand[1]
            retR = "set separator from %s to %s" % (old, operand[1])
        else: 
            retR = "Unknown sub-operation: %s" % operand[0].lower()
        print(retR)
        return retR

    def do_show(self, operand, kwargs):
        """!
        Show various status of the SiPy.

        Commands: 
            show data [variable name]
            show {available_plugins|environment|history|modules}
            show item <history number>
            show result

        @return: String containing results of command execution
        """
        if operand[0].lower() in ["available_plugins", "aplug", "a"]:
            # show available_plugins
            print("List of Available Plugins:")
            retR = self.available_plugins
            for plugin in self.available_plugins: print(plugin)
        elif operand[0].lower() in ["data", "d"]:
            # show data [variable name]
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
            # show history
            for x in self.history: 
                retR = self.history
                print("%s: %s" % (str(x), str(self.history[x])))
        elif operand[0].lower() in ["environment", "env", "e"]:
            # # show environment
            for x in self.environment: 
                retR = self.environment
                print("%s: %s" % (str(x), str(self.environment[x])))
        elif operand[0].lower() in ["item", "i"]:
            # show item <history number>
            item = str(int(operand[1]))
            retR = ["Command: %s" % (str(self.history[item])),
                    "Result: %s" % (str(self.result[item]))]
            print(retR[0])
            print(retR[1])
            retR = "\n".join(retR)
        elif operand[0].lower() in ["modules", "mod", "m"]:
            # show modules
            print("List of Available Modules:")
            retR = self.modules
            for module in self.modules: print(module)
        elif operand[0].lower() in ["result", "r"]:
            # show result
            retR = self.result
            for x in self.result:
                print("%s: %s" % (str(x), str(self.result[x])))
        else: 
            retR = "Unknown sub-operation: %s" % operand[0].lower()
        return retR

    def do_systest(self, operand, kwargs):
        """!
        Test SiPy system.

        Commands: 
            systest plugin_system

        @return: String containing results of command execution
        """
        if operand[0].lower() in ["plugin_system"]:
            # systest plugin_system
            self.sipy_pm.load_plugin(self.environment["plugin_directory"], "sample_plugin")
            self.sipy_pm.execute_plugin("sample_plugin", 1, 2, 3, operation="print", name="Alice", age=30)
            self.sipy_pm.unload_plugin("sample_plugin")  # Unload the plugin
            retR = "Plugin system tested"
        else: 
            retR = "Unknown sub-operation: %s" % operand[0].lower()
        print(retR)
        return retR

    def do_ttest(self, operand, kwargs):
        """!
        Performs Student's t-test(s) on values.

        Commands:
            ttest 1s {list|series|tuple|vector} <variable name> <population mean>
            ttest 1s {list|series|tuple|vector} data=<variable name> mu=<population mean>
            ttest 1s {dataframe|df|frame|table} wide <variable name> <series name> <population mean>
            ttest 1s {dataframe|df|frame|table} wide data=<variable name>.<series name> mu=<population mean>
            
            ttest 2se {list|series|tuple|vector} <variable name A> <variable name B>
            ttest 2se {list|series|tuple|vector} data=<variable name A>,<variable name B>
            ttest 2se {dataframe|df|frame|table} wide <variable name> <series name A> <series name B>
            ttest 2se {dataframe|df|frame|table} wide data=<variable name>.<series name A>,<variable name>.<series name B>
            
            ttest 2su {list|series|tuple|vector} <variable name A> <variable name B>
            ttest 2su {list|series|tuple|vector} data=<variable name A>,<variable name B>
            ttest 2su {dataframe|df|frame|table} wide <variable name> <series name A> <series name B>
            ttest 2su {dataframe|df|frame|table} wide data=<variable name>.<series name A>,<variable name>.<series name B>
            
            ttest mwu {list|series|tuple|vector} <variable name A> <variable name B>
            ttest mwu {list|series|tuple|vector} data=<variable name A>,<variable name B>
            ttest mwu {dataframe|df|frame|table} wide <variable name> <series name A> <series name B>
            ttest mwu {dataframe|df|frame|table} wide data=<variable name>.<series name A>,<variable name>.<series name B>
            
            ttest paired {list|series|tuple|vector} <variable name A> <variable name B>
            ttest paired {list|series|tuple|vector} data=<variable name A>,<variable name B>
            ttest paired {dataframe|df|frame|table} wide <variable name> <series name A> <series name B>
            ttest paired {dataframe|df|frame|table} wide data=<variable name>.<series name A>,<variable name>.<series name B>

            ttest tost {list|series|tuple|vector} <variable name A> <variable name B>
            ttest tost {list|series|tuple|vector} data=<variable name A>,<variable name B>
            ttest tost {dataframe|df|frame|table} wide <variable name> <series name A> <series name B>
            ttest tost {dataframe|df|frame|table} wide data=<variable name>.<series name A>,<variable name>.<series name B>

            ttest wilcoxon {list|series|tuple|vector} <variable name A> <variable name B>
            ttest wilcoxon {list|series|tuple|vector} data=<variable name A>,<variable name B>
            ttest wilcoxon {dataframe|df|frame|table} wide <variable name> <series name A> <series name B>
            ttest wilcoxon {dataframe|df|frame|table} wide data=<variable name>.<series name A>,<variable name>.<series name B>

        @return: String containing results of command execution
        """
        data_type = operand[1].lower()
        if operand[0].lower() in ["1s", "1sample"]:
            if data_type in ["list", "series", "tuple", "vector"]:
                if "data" not in kwargs:
                    """
                    ttest 1s {list|series|tuple|vector} <variable name> <population mean>

                    Example:
                    let x be list 2,3,4,5,6,7,8,9
                    ttest 1s list x 4
                    """
                    data_values = self.data[operand[2]]
                    mu = float(operand[3])
                else: 
                    """
                    ttest 1s {list|series|tuple|vector} data=<variable name> mu=<population mean>

                    Example:
                    let x be list 2,3,4,5,6,7,8,9
                    ttest 1s list data=x mu=4
                    """
                    data_values = self.data[kwargs["data"]]
                    mu = kwargs["mu"]
                retR = libsipy.base.tTest1Sample(data_values, mu)
            elif data_type in ["dataframe", "df", "frame", "table"] and operand[2].lower() == "wide":
                if "data" not in kwargs:
                    """
                    ttest 1s {dataframe|df|frame|table} wide <variable name> <series name> <population mean>

                    Example:
                    let x be list 1,2,3,4,5
                    let y be list 2,3,4,5,6
                    let z be dataframe x:x y:y
                    ttest 1s dataframe wide z x 5
                    """
                    data_values = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns=operand[4], rtype="list")
                    mu = float(operand[5])
                else:
                    """
                    ttest 1s {dataframe|df|frame|table} wide data=<variable name>.<series name> mu=<population mean>

                    Example:
                    let x be list 1,2,3,4,5
                    let y be list 2,3,4,5,6
                    let z be dataframe x:x y:y
                    ttest 1s dataframe wide data=z.x mu=5
                    """
                    d = [x.strip() for x in kwargs["data"].split(".")]
                    data_values = libsipy.data_wrangler.df_extract(df=self.data[d[0]], columns=d[1], rtype="list")
                    mu = kwargs["mu"]
                retR = libsipy.base.tTest1Sample(data_values, mu)
        elif operand[0].lower() in ["2se", "2sample_equal"]:
            if data_type in ["list", "series", "tuple", "vector"]:
                if "data" not in kwargs:
                    """
                    ttest 2se {list|series|tuple|vector} <variable name A> <variable name B>

                    Example:
                    let x be list 2,3,4,5,6,7,8,9
                    let y be list 3,4,5,6,7,8,9,10
                    ttest 2se list x y
                    """
                    data_valuesA = self.data[operand[2]]
                    data_valuesB = self.data[operand[3]]
                else:
                    """
                    ttest 2se {list|series|tuple|vector} data=<variable name A><variable name B>

                    Example:
                    let x be list 2,3,4,5,6,7,8,9
                    let y be list 3,4,5,6,7,8,9,10
                    ttest 2se list data=x,y
                    """
                    datavar = [x.strip() for x in kwargs["data"].split(self.environment["separator"])]
                    data_valuesA = self.data[datavar[0]]
                    data_valuesB = self.data[datavar[1]]
                retR = libsipy.base.tTest2SampleEqual(data_valuesA, data_valuesB)
            elif data_type in ["dataframe", "df", "frame", "table"] and operand[2].lower() == "wide":
                if "data" not in kwargs:
                    """
                    ttest 2se {dataframe|df|frame|table} wide <variable name> <series name A> <series name B>

                    Example:
                    let x be list 1,2,3,4,5
                    let y be list 2,3,4,5,6
                    let z be dataframe x:x y:y
                    ttest 2se dataframe wide z x y
                    """
                    data_valuesA = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns=operand[4], rtype="list")
                    data_valuesB = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns=operand[5], rtype="list")
                else:
                    """
                    ttest 2se {dataframe|df|frame|table} wide data=<variable name>.<series name A>,<variable name>.<series name B>

                    Example:
                    let x be list 1,2,3,4,5
                    let y be list 2,3,4,5,6
                    let z be dataframe x:x y:y
                    ttest 2se dataframe wide data=z.x,z.y
                    """
                    datavar = [x.strip() for x in kwargs["data"].split(self.environment["separator"])]
                    dA = [x.strip() for x in datavar[0].split(".")]
                    dB = [x.strip() for x in datavar[1].split(".")]
                    data_valuesA = libsipy.data_wrangler.df_extract(df=self.data[dA[0]], columns=dA[1], rtype="list")
                    data_valuesB = libsipy.data_wrangler.df_extract(df=self.data[dB[0]], columns=dB[1], rtype="list")
                retR = libsipy.base.tTest2SampleEqual(data_valuesA, data_valuesB)
        elif operand[0].lower() in ["2su", "2sample_unequal"]:
            if data_type in ["list", "series", "tuple", "vector"]:
                if "data" not in kwargs:
                    """
                    ttest 2su {list|series|tuple|vector} <variable name A> <variable name B>

                    Example:
                    let x be list 2,3,4,5,6,7,8,9
                    let y be list 3,4,5,6,7,8,9,10
                    ttest 2su list x y
                    """
                    data_valuesA = self.data[operand[2]]
                    data_valuesB = self.data[operand[3]]
                else:
                    """
                    ttest 2su {list|series|tuple|vector} data=<variable name A>,<variable name B>

                    Example:
                    let x be list 2,3,4,5,6,7,8,9
                    let y be list 3,4,5,6,7,8,9,10
                    ttest 2su list data=x,y
                    """
                    datavar = [x.strip() for x in kwargs["data"].split(self.environment["separator"])]
                    data_valuesA = self.data[datavar[0]]
                    data_valuesB = self.data[datavar[1]]
                retR = libsipy.base.tTest2SampleUnequal(data_valuesA, data_valuesB)
            elif data_type in ["dataframe", "df", "frame", "table"] and operand[2].lower() == "wide":
                if "data" not in kwargs:
                    """
                    ttest 2su {dataframe|df|frame|table} wide <variable name> <series name A> <series name B>

                    Example:
                    
                    let x be list 1,2,3,4,5
                    let y be list 2,3,4,5,6
                    let z be dataframe x:x y:y
                    ttest 2su dataframe wide z x y
                    """
                    data_valuesA = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns=operand[4], rtype="list")
                    data_valuesB = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns=operand[5], rtype="list")
                else:
                    """
                    ttest 2su {dataframe|df|frame|table} wide data=<variable name>.<series name A>,<variable name>.<series name B>

                    Example:
                    let x be list 1,2,3,4,5
                    let y be list 2,3,4,5,6
                    let z be dataframe x:x y:y
                    ttest 2su dataframe wide data=z.x,z.y
                    """
                    datavar = [x.strip() for x in kwargs["data"].split(self.environment["separator"])]
                    dA = [x.strip() for x in datavar[0].split(".")]
                    dB = [x.strip() for x in datavar[1].split(".")]
                    data_valuesA = libsipy.data_wrangler.df_extract(df=self.data[dA[0]], columns=dA[1], rtype="list")
                    data_valuesB = libsipy.data_wrangler.df_extract(df=self.data[dB[0]], columns=dB[1], rtype="list")
                retR = libsipy.base.tTest2SampleUnequal(data_valuesA, data_valuesB)
        elif operand[0].lower() in ["mwu", "mannwhitney"]:
            if data_type in ["list", "series", "tuple", "vector"]:
                if "data" not in kwargs:
                    """
                    ttest mwu {list|series|tuple|vector} <variable name A> <variable name B>
                    
                    Example:
                    let x be list 2,3,4,5,6,7,8,9
                    let y be list 3,4,5,6,7,8,9,10
                    ttest mwu list x y
                    """
                    data_valuesA = self.data[operand[2]]
                    data_valuesB = self.data[operand[3]]
                else:
                    """
                    ttest mwu {list|series|tuple|vector} data=<variable name A>,<variable name B>

                    Example:
                    let x be list 2,3,4,5,6,7,8,9
                    let y be list 3,4,5,6,7,8,9,10
                    ttest mwu list data=x,y
                    """
                    datavar = [x.strip() for x in kwargs["data"].split(self.environment["separator"])]
                    data_valuesA = self.data[datavar[0]]
                    data_valuesB = self.data[datavar[1]]
                retR = libsipy.base.mannWhitneyU(data_valuesA, data_valuesB)
            elif data_type in ["dataframe", "df", "frame", "table"] and operand[2].lower() == "wide":
                if "data" not in kwargs:
                    """
                    ttest mwu {dataframe|df|frame|table} wide <variable name> <series name A> <series name B>

                    Example:
                    let x be list 1,2,3,4,5
                    let y be list 2,3,4,5,6
                    let z be dataframe x:x y:y
                    ttest mwu dataframe wide z x y
                    """
                    data_valuesA = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns=operand[4], rtype="list")
                    data_valuesB = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns=operand[5], rtype="list")
                else:
                    """
                    ttest mwu {dataframe|df|frame|table} wide data=<variable name>.<series name A>,<variable name>.<series name B>

                    Example:
                    let x be list 1,2,3,4,5
                    let y be list 2,3,4,5,6
                    let z be dataframe x:x y:y
                    ttest mwu dataframe wide data=z.x,z.y
                    """
                    datavar = [x.strip() for x in kwargs["data"].split(self.environment["separator"])]
                    dA = [x.strip() for x in datavar[0].split(".")]
                    dB = [x.strip() for x in datavar[1].split(".")]
                    data_valuesA = libsipy.data_wrangler.df_extract(df=self.data[dA[0]], columns=dA[1], rtype="list")
                    data_valuesB = libsipy.data_wrangler.df_extract(df=self.data[dB[0]], columns=dB[1], rtype="list")
                retR = libsipy.base.mannWhitneyU(data_valuesA, data_valuesB)
        elif operand[0].lower() in ["paired", "dependent"]:
            if data_type in ["list", "series", "tuple", "vector"]:
                if "data" not in kwargs:
                    """
                    ttest paired {list|series|tuple|vector} <variable name A> <variable name B>

                    Example:
                    let x be list 2,3,4,5,6,7,8,9
                    let y be list 3,4,5,6,7,8,9,10
                    ttest paired list x y
                    """
                    data_valuesA = self.data[operand[2]]
                    data_valuesB = self.data[operand[3]]
                else:
                    """
                    ttest paired {list|series|tuple|vector} data=<variable name A>,<variable name B>

                    Example:
                    let x be list 2,3,4,5,6,7,8,9
                    let y be list 3,4,5,6,7,8,9,10
                    ttest paired list data=x,y
                    """
                    datavar = [x.strip() for x in kwargs["data"].split(self.environment["separator"])]
                    data_valuesA = self.data[datavar[0]]
                    data_valuesB = self.data[datavar[1]]
                retR = libsipy.base.tTest2SamplePaired(data_valuesA, data_valuesB)
            elif data_type in ["dataframe", "df", "frame", "table"] and operand[2].lower() == "wide":
                if "data" not in kwargs:
                    """
                    ttest paired {dataframe|df|frame|table} wide <variable name> <series name A> <series name B>

                    Example:
                    let x be list 1,2,3,4,5
                    let y be list 2,3,4,5,6
                    let z be dataframe x:x y:y
                    ttest paired dataframe wide z x y
                    """
                    data_valuesA = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns=operand[4], rtype="list")
                    data_valuesB = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns=operand[5], rtype="list")
                else:
                    """
                    ttest paired {dataframe|df|frame|table} wide data=<variable name>.<series name A>,<variable name>.<series name B>

                    Example:
                    let x be list 1,2,3,4,5
                    let y be list 2,3,4,5,6
                    let z be dataframe x:x y:y
                    ttest paired dataframe wide data=z.x,z.y
                    """
                    datavar = [x.strip() for x in kwargs["data"].split(self.environment["separator"])]
                    dA = [x.strip() for x in datavar[0].split(".")]
                    dB = [x.strip() for x in datavar[1].split(".")]
                    data_valuesA = libsipy.data_wrangler.df_extract(df=self.data[dA[0]], columns=dA[1], rtype="list")
                    data_valuesB = libsipy.data_wrangler.df_extract(df=self.data[dB[0]], columns=dB[1], rtype="list")
                retR = libsipy.base.tTest2SamplePaired(data_valuesA, data_valuesB)
        elif operand[0].lower() in ["tost"]:
            if data_type in ["list", "series", "tuple", "vector"]:
                if "data" not in kwargs:
                    """
                    ttest tost {list|series|tuple|vector} <variable name A> <variable name B>

                    Example:
                    let x be list 2,3,4,5,6,7,8,9
                    let y be list 3,4,5,6,7,8,9,10
                    ttest tost list x y
                    """
                    data_valuesA = self.data[operand[2]]
                    data_valuesB = self.data[operand[3]]
                else:
                    """
                    ttest tost {list|series|tuple|vector} data=<variable name A>,<variable name B>

                    Example:
                    let x be list 2,3,4,5,6,7,8,9
                    let y be list 3,4,5,6,7,8,9,10
                    ttest tost list data=x,y
                    """
                    datavar = [x.strip() for x in kwargs["data"].split(self.environment["separator"])]
                    data_valuesA = self.data[datavar[0]]
                    data_valuesB = self.data[datavar[1]]
                retR = libsipy.base.TOST(data_valuesA, data_valuesB)
            elif data_type in ["dataframe", "df", "frame", "table"] and operand[2].lower() == "wide":
                if "data" not in kwargs:
                    """
                    ttest tost {dataframe|df|frame|table} wide <variable name> <series name A> <series name B>

                    Example:
                    let x be list 1,2,3,4,5
                    let y be list 2,3,4,5,6
                    let z be dataframe x:x y:y
                    ttest tost dataframe wide z x y
                    """
                    data_valuesA = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns=operand[4], rtype="list")
                    data_valuesB = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns=operand[5], rtype="list")
                else:
                    """
                    ttest tost {dataframe|df|frame|table} wide data=<variable name>.<series name A>,<variable name>.<series name B>

                    Example:
                    let x be list 1,2,3,4,5
                    let y be list 2,3,4,5,6
                    let z be dataframe x:x y:y
                    ttest tost dataframe wide data=z.x,z.y
                    """
                    datavar = [x.strip() for x in kwargs["data"].split(self.environment["separator"])]
                    dA = [x.strip() for x in datavar[0].split(".")]
                    dB = [x.strip() for x in datavar[1].split(".")]
                    data_valuesA = libsipy.data_wrangler.df_extract(df=self.data[dA[0]], columns=dA[1], rtype="list")
                    data_valuesB = libsipy.data_wrangler.df_extract(df=self.data[dB[0]], columns=dB[1], rtype="list")
                retR = libsipy.base.TOST(data_valuesA, data_valuesB)
        elif operand[0].lower() in ["wilcoxon"]:
            if data_type in ["list", "series", "tuple", "vector"]:
                if "data" not in kwargs:
                    """
                    ttest wilcoxon {list|series|tuple|vector} <variable name A> <variable name B>

                    Example:
                    let x be list 2,3,4,5,6,7,8,9
                    let y be list 3,4,5,6,7,8,9,10
                    ttest wilcoxon list x y
                    """
                    data_valuesA = self.data[operand[2]]
                    data_valuesB = self.data[operand[3]]
                else:
                    """
                    ttest wilcoxon {list|series|tuple|vector} data=<variable name A>,<variable name B>

                    Example:
                    let x be list 2,3,4,5,6,7,8,9
                    let y be list 3,4,5,6,7,8,9,10
                    ttest wilcoxon list data=x,y
                    """
                    datavar = [x.strip() for x in kwargs["data"].split(self.environment["separator"])]
                    data_valuesA = self.data[datavar[0]]
                    data_valuesB = self.data[datavar[1]]
                retR = libsipy.base.wilcoxon(data_valuesA, data_valuesB)
            elif data_type in ["dataframe", "df", "frame", "table"] and operand[2].lower() == "wide":
                if "data" not in kwargs:
                    """
                    ttest wilcoxon {dataframe|df|frame|table} wide <variable name> <series name A> <series name B>

                    Example:
                    let x be list 1,2,3,4,5
                    let y be list 2,3,4,5,6
                    let z be dataframe x:x y:y
                    ttest wilcoxon dataframe wide z x y
                    """
                    data_valuesA = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns=operand[4], rtype="list")
                    data_valuesB = libsipy.data_wrangler.df_extract(df=self.data[operand[3]], columns=operand[5], rtype="list")
                else:
                    """
                    ttest wilcoxon {dataframe|df|frame|table} wide data=<variable name>.<series name A>,<variable name>.<series name B>

                    Example:
                    let x be list 1,2,3,4,5
                    let y be list 2,3,4,5,6
                    let z be dataframe x:x y:y
                    ttest wilcoxon dataframe wide data=z.x,z.y
                    """
                    datavar = [x.strip() for x in kwargs["data"].split(self.environment["separator"])]
                    dA = [x.strip() for x in datavar[0].split(".")]
                    dB = [x.strip() for x in datavar[1].split(".")]
                    data_valuesA = libsipy.data_wrangler.df_extract(df=self.data[dA[0]], columns=dA[1], rtype="list")
                    data_valuesB = libsipy.data_wrangler.df_extract(df=self.data[dB[0]], columns=dB[1], rtype="list")
                retR = libsipy.base.wilcoxon(data_valuesA, data_valuesB)
        else: 
            retR = "Unknown sub-operation: %s" % operand[0].lower()
        print(retR.to_string())
        return retR

    def do_variance(self, operand, kwargs):
        """!
        Performs test for equality of variances of samples.

        Commands:
            variance bartlett {list|series|tuple|vector} <variable name 1> <variable name 2> ... <variable name N>
            variance bartlett {list|series|tuple|vector} data=<variable name 1>;<variable name 2>; ... ;<variable name N>
            variance bartlett {dataframe|df|frame|table} wide <variable name>
            variance bartlett {dataframe|df|frame|table} wide data=<variable name>
            
            variance fligner {list|series|tuple|vector} <variable name 1> <variable name 2> ... <variable name N>
            variance fligner {list|series|tuple|vector} data=<variable name 1>;<variable name 2>; ... ;<variable name N>
            variance fligner {dataframe|df|frame|table} wide <variable name>
            variance fligner {dataframe|df|frame|table} wide data=<variable name>

            variance levene {list|series|tuple|vector} <variable name 1> <variable name 2> ... <variable name N>
            variance levene {list|series|tuple|vector} data=<variable name 1>;<variable name 2>; ... ;<variable name N>
            variance levene {dataframe|df|frame|table} wide <variable name>
            variance levene {dataframe|df|frame|table} wide data=<variable name>

        @return: String containing results of command execution
        """
        data_type = operand[1].lower()
        if operand[0].lower() in ["bartlett"]:
            if data_type in ["list", "series", "tuple", "vector"]:
                if "data" not in kwargs:
                    # variance bartlett {list|series|tuple|vector} <variable name 1> <variable name 2> ... <variable name N>
                    data_values = [self.data[operand[i]] for i in range(2, len(operand))]
                else:
                    # variance bartlett {list|series|tuple|vector} data=<variable name 1>;<variable name 2>; ... ;<variable name N>
                    varNs = [x.strip() for x in kwargs["data"].split(";")]
                    data_values = [self.data[var] for var in varNs]
                result = libsipy.base.BartlettTest(data_values)
                retR = "Statistic = %.3f; p-value = %s" % (result.statistic, result.pvalue)
            elif data_type in ["dataframe", "df", "frame", "table"] and operand[2].lower() == "wide":
                if "data" not in kwargs:
                    # variance bartlett {dataframe|df|frame|table} wide <variable name>
                    data_values = libsipy.data_wrangler.df_extract(self.data[operand[3]], columns="all", rtype="list")
                else:
                    # variance bartlett {dataframe|df|frame|table} wide data=<variable name>
                    data_values = libsipy.data_wrangler.df_extract(self.data[kwargs["data"]], columns="all", rtype="list")
                result = libsipy.base.BartlettTest(data_values)
                retR = "Statistic = %.3f; p-value = %s" % (result.statistic, result.pvalue)
        elif operand[0].lower() in ["fligner"]:
            if data_type in ["list", "series", "tuple", "vector"]:
                if "data" not in kwargs:
                    # variance fligner {list|series|tuple|vector} <variable name 1> <variable name 2> ... <variable name N>
                    data_values = [self.data[operand[i]] for i in range(2, len(operand))]
                else:
                    # variance fligner {list|series|tuple|vector} data=<variable name 1>;<variable name 2>; ... ;<variable name N>
                    varNs = [x.strip() for x in kwargs["data"].split(";")]
                    data_values = [self.data[var] for var in varNs]
                result = libsipy.base.FlignerTest(data_values)
                retR = "Statistic = %.3f; p-value = %s" % (result.statistic, result.pvalue)
            elif data_type in ["dataframe", "df", "frame", "table"] and operand[2].lower() == "wide":
                if "data" not in kwargs:
                    # variance fligner {dataframe|df|frame|table} wide <variable name>
                    data_values = libsipy.data_wrangler.df_extract(self.data[operand[3]], columns="all", rtype="list")
                else:
                    # variance fligner {dataframe|df|frame|table} wide data=<variable name>
                    data_values = libsipy.data_wrangler.df_extract(self.data[kwargs["data"]], columns="all", rtype="list")
                result = libsipy.base.FlignerTest(data_values)
                retR = "Statistic = %.3f; p-value = %s" % (result.statistic, result.pvalue)
        elif operand[0].lower() in ["levene"]:
            if data_type in ["list", "series", "tuple", "vector"]:
                if "data" not in kwargs:
                    # variance levene {list|series|tuple|vector} <variable name 1> <variable name 2> ... <variable name N>
                    data_values = [self.data[operand[i]] for i in range(2, len(operand))]
                else:
                    # variance levene {list|series|tuple|vector} data=<variable name 1>;<variable name 2>; ... ;<variable name N>
                    varNs = [x.strip() for x in kwargs["data"].split(";")]
                    data_values = [self.data[var] for var in varNs]
                result = libsipy.base.LeveneTest(data_values)
                retR = "Statistic = %.3f; p-value = %s" % (result.statistic, result.pvalue)
            elif data_type in ["dataframe", "df", "frame", "table"] and operand[2].lower() == "wide":
                if "data" not in kwargs:
                    # variance levene {dataframe|df|frame|table} wide <variable name>
                    data_values = libsipy.data_wrangler.df_extract(self.data[operand[3]], columns="all", rtype="list")
                else:
                    # variance levene {dataframe|df|frame|table} wide data=<variable name>
                    data_values = libsipy.data_wrangler.df_extract(self.data[kwargs["data"]], columns="all", rtype="list")
                result = libsipy.base.LeveneTest(data_values)
                retR = "Statistic = %.3f; p-value = %s" % (result.statistic, result.pvalue)
        else: 
            retR = "Unknown sub-operation: %s" % operand[0].lower()
        print(retR)
        return retR

    def command_processor(self, operator, operand, kwargs):
        """
        Method to channel bytecodes operand(s) and keyward arguments, if any, into the respective bytecode processors.
        
        @param operator String: bytecode operator
        @param operand list: bytecode operand(s), if any
        @param kwargs Dictionary: bytecode operand(s) as keyword arguments, if any
        @return: String containing results of command execution
        """
        if operator == "anova": return self.do_anova(operand, kwargs)
        elif operator == "compute_effsize": return self.do_compute_effsize(operand, kwargs)
        elif operator == "correlate": return self.do_correlate(operand, kwargs)
        elif operator == "describe": return self.do_describe(operand, kwargs)
        elif operator == "let": return self.do_let(operand, kwargs)
        elif operator == "mean": return self.do_mean(operand, kwargs)
        elif operator == "normality": return self.do_normality(operand, kwargs)
        elif operator == "read": return self.do_read(operand, kwargs)
        elif operator == "regress": return self.do_regression(operand, kwargs)
        elif operator == "rregress": return self.do_R_regression(operand, kwargs)
        elif operator == "script": return self.do_script(operand, kwargs)
        elif operator == "set": return self.do_set(operand, kwargs)
        elif operator == "show": return self.do_show(operand, kwargs)
        elif operator == "systest": return self.do_systest(operand, kwargs)
        elif operator == "ttest": return self.do_ttest(operand, kwargs)
        elif operator == "variance": return self.do_variance(operand, kwargs)
        elif operator == "try": 
            print("Operator = %s" % str(operand[0]))
            print("Operand(s) = %s" % str(operand[1:]))
            print("Keyword Argument(s) = %s" % str(kwargs))
        else: print("Unknown command / operation: %s" % operator)

    def interpret(self, statement):
        """!
        Method to process an input statement by either sending it to SiPy_Shell.intercept_processor() or SiPy_Shell.command_processor().
        
        @param statement String: command-line statement
        @return: String containing results of command execution
        """
        def dictionize(operand):
            op_list = []
            op_dict = {}
            for op in operand:
                op = op.strip()
                if "=" not in op: op_list.append(op)
                else:
                    op = [x.strip() for x in op.split("=")]
                    op_dict[op[0]] = op[1]
            return (op_list, op_dict)
        try:
            self.history[str(self.count)] = statement
            if statement.lower() in ["citation", "citation;", "copyright", "copyright;", "credits", "credits;", "exit", "exit;", "license", "license;", "quit", "quit;"]:
                 retR = self.intercept_processor(statement)
                 if retR == "exit": return "exit"
            else:
                statement = statement.strip()
                statement = [x.strip() for x in statement.split()]
                operator = statement[0].lower()
                (operand, kwargs) = dictionize(statement[1:])
                retR = self.command_processor(operator, operand, kwargs)
            self.result[str(self.count)] = retR
            self.count = self.count + 1
            return retR
        except:
            error_message = list(self.formatExceptionInfo())
            for line in error_message:
                if (type(line) == list):
                    for l in line: 
                        print(l)

    def cmdLoop(self):
        """!
        Command-line loop executor. This runs the shell like a command-line interpreter and calls SiPy_Shell.interpret() method to process the statement/command from the command-line.
        """
        self.header()
        while True:
            statement = input("SiPy: %s %s " % (str(self.count), self.environment["prompt"])).strip() 
            if len(statement) == 0: pass
            elif statement == "exit": return 0
            elif statement.startswith("#"): continue
            else: _ = self.interpret(statement)
            print("")

    def cmdScript(self, script):
        """!
        Script executor. This method is used to execute a script file that is passed into SiPy and calls SiPy_Shell.interpret() method to process the ordered list of commands in script.
        
        @param script List: ordered list of commands in script to execute.
        """
        for statement in script:
            statement = statement.strip()
            print('Command #%s: %s' % (str(self.count), statement))
            if statement == 'exit': return 0
            _ = self.interpret(statement)

    def runScript(self, scriptfile, operation="script_execute"):
        """!
        Function to execute script file written in SiPy language.
        
        @param scriptfile String: absolute path to SiPy script file
        @param operation String: type of operation. Allowable types are "script_execute" (execute the script), and "script_merge" (merge the scripts without execution)
        """
        def process_script(scriptfile):
            if operation == "script_execute":
                print("")
                print("Reading script file: %s" % scriptfile)
                print("")
            script = open(scriptfile, "r").readlines()
            script = [x.strip() for x in script]
            script = ["# Start script file: %s" % scriptfile] + script + ["# End script file: %s" % scriptfile]
            for i in range(len(script)):
                script[i] = script[i].strip()
                if script[i].startswith("@include"):
                    f = script[i].split()[1].strip()
                    f = os.sep.join([dirname, f])
                    script[i] = process_script(f)
            return script
        def flatten(container):
            for i in container:
                if isinstance(i, list) or isinstance(i, tuple):
                    for j in flatten(i):
                        yield j
                else:
                    yield i
        if operation == "script_execute":
            dirname = os.path.dirname(scriptfile)
            print("")
            print("Executing script file: %s" % scriptfile)
            print("")
            fullscript = process_script(scriptfile)
            fullscript = list(flatten(fullscript))
            fullscript = [x for x in fullscript if x != ""]
            fullscript = [x for x in fullscript 
                          if not x.strip().startswith('#')]
            self.cmdScript(fullscript)
            return fullscript
        elif operation == "script_merge":
            dirname = os.path.dirname(scriptfile)
            fullscript = process_script(scriptfile)
            fullscript = list(flatten(fullscript))
            for line in fullscript: print(line)
            return fullscript
        elif operation == "script_read":
            dirname = os.path.dirname(scriptfile)
            print("")
            print("Reading script file: %s" % scriptfile)
            print("")
            script = open(scriptfile, "r").readlines()
            script = [x.strip() for x in script]
            for line in script: print(line)
            return script

    def do_template(self, operand, kwargs):
        """!
        Performs xxx

        Commands: 
            operator operand[0] operand[1] operand[2] operand[3] ... operand[N]

        @return: String containing results of command execution
        """
        option = operand[0].lower()
        data_type = operand[1].lower()
        if option.lower() in ["option"]:
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

    def basic_gui(self):
        """!
        Basic GUI for SiPy using FreeSimpleGUI.
        """
        sg.theme("DarkGreen3")
        layout = [[sg.Text("Output Window", size=(40, 1))],
                  [sg.Multiline(size=(100, 20), 
                                font=("Courier 10"), 
                                default_text=sipy_info.header + "\n", 
                                autoscroll=True, 
                                disabled=True,
                                reroute_stdout=True)],
                  [sg.Text("Enter Command:"), sg.Multiline(size=(70, 3), 
                                                        font=("Courier 10"), 
                                                        enter_submits=True, 
                                                        key="statement", 
                                                        do_not_clear=False),
                   sg.Button("SEND", button_color=(sg.YELLOWS[0], sg.BLUES[0]), bind_return_key=True),
                   sg.Button('EXIT', button_color=(sg.YELLOWS[0], sg.GREENS[0]))]]
        window_header = "SiPy: Statistics in Python [Release %s (%s)]" % (sipy_info.release_number, sipy_info.release_code_name)
        window = sg.Window(window_header, layout, 
                           font=("Helvetica 12"), 
                           icon="images/sipy_icon.ico", 
                           default_button_element_size=(8,1), 
                           use_default_focus=False, 
                           resizable=True)
        while True:
            event, value = window.read()
            if event in (sg.WIN_CLOSED, "EXIT"): break
            elif event == "SEND":
                statement = value["statement"].rstrip()
                if statement.lower() == "exit": break
                elif statement.startswith("#"): 
                    print("SiPy: %s %s %s" % (str(self.count), self.environment["prompt"], statement), flush=True)
                    print("")
                elif not statement.startswith("#") and statement != "": 
                    print("SiPy: %s %s %s" % (str(self.count), self.environment["prompt"], statement), flush=True)
                    self.interpret(statement)
                    print("")
        window.close()

if __name__ == "__main__":
    shell = SiPy_Shell()
    if len(sys.argv) == 1:
        shell.basic_gui()
        sys.exit()
    elif len(sys.argv) == 2 and sys.argv[1].lower() == "shell":
        shell.cmdLoop()
        sys.exit()
    elif (len(sys.argv) == 3) and (sys.argv[1].lower() == "script_execute"):
        scriptfile = os.path.abspath(sys.argv[2])
        shell.runScript(scriptfile, "script_execute")
        sys.exit()
    elif (len(sys.argv) == 3) and (sys.argv[1].lower() == "script_merge"):
        scriptfile = os.path.abspath(sys.argv[2])
        shell.runScript(scriptfile, "script_merge")
        sys.exit()
    elif (len(sys.argv) == 3) and (sys.argv[1].lower() == "script_read"):
        scriptfile = os.path.abspath(sys.argv[2])
        shell.runScript(scriptfile, "script_read")
        sys.exit()