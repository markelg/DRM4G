import re
import os
import logging
import subprocess

__version__  = '2.4.1'
__author__   = 'Carlos Blanco'
__revision__ = "$Id$"

r = re.compile(r'[:,\s]') # match whitespac, coma or :

def parse(output):
    output = [r.split(line) for line in output.splitlines()]
    # now we have a list of lists, but it may contain empty strings
    for line in output:
        while '' in line:
            line.remove('')
    # turn into dict and return
    return dict([(line[0],line[1:]) for line in output])	

def exec_cmd( cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE, env = os.environ ):
    logging.debug( "Executing command ... " + cmd )
    p      = subprocess.Popen( cmd, shell = True, stdout = stdout,
                               stderr = stderr, env = env )
    output = p.stdout.read().strip() + p.stderr.read().strip()
    code   = p.wait()
    return code, output