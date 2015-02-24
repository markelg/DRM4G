"""
Start DRM4G daemon deleting all the jobs available on DRM4G.
    
Usage: 
    drm4g clear [ --dbg ] 
   
Options:
   --dbg    Debug mode.
"""
__version__  = '2.3.0'
__author__   = 'Carlos Blanco'
__revision__ = "$Id$"

import logging
from time                 import sleep
from drm4g.commands       import Daemon, logger

def run( arg ) :
    try:
        if arg[ '--dbg' ] :
            logger.setLevel(logging.DEBUG)
        daemon = Daemon()
        daemon.stop()
        sleep( 2.0 )
        daemon.clear()
    except Exception , err :
        logger.error( str( err ) )
