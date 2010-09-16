#!/usr/bin/env python

import sys
import os
import signal
import PyQt4

from PyQt4 import QtCore
from PyQt4.QtCore import *

VERSION = 0.1

signal.signal(signal.SIGINT, signal.SIG_DFL)

class DirectoryWatcher():
  def __init__(self, parent = None, options = None):
    self.path = ""
    self.watcher = QtCore.QFileSystemWatcher()
    self.options = options
    self.files_watched = None
    QObject.connect(self.watcher, SIGNAL("directoryChanged(const QString &)"), self.dirChanged)
    
  def addPath(self, path):
    qpath = QtCore.QString(path)
    self.watcher.addPath(qpath)    
    
    # limitation : only 1 directory is watched
    self.files_watched = set(os.listdir(self.watcher.directories()[0]))
    
  def dirChanged(self, path):
    new_files_watched = set(os.listdir(self.watcher.directories()[0]))
    
    # Compare the new state of the files in the directory with the previous one
    
    files_removed = self.files_watched - new_files_watched 
    for f in files_removed:
      print("removed: %s" % f)
      
    files_added = new_files_watched - self.files_watched
    for f in files_added:
      print("added: %s" % f)      
    
    if len(files_added) == 0 and len(files_removed) == 0:
      print("other change")
      
    # Update the state of the watched files
    self.files_watched = new_files_watched
  
def main():
  import optparse
  
  # Options and arguments handling
  usage = "usage: %prog [options] dir"
  version="%%prog %s"%VERSION
  
  parser = optparse.OptionParser(usage=usage, version=version)
  parser.add_option("-v", "--verbose", 	action="store_true", dest="verbose", 	default=False, 	help="verbose mode")
  parser.add_option("-a", "--add", 	action="store_true", dest="add", 	default=True, 	help="additions")
  parser.add_option("-d", "--del", 	action="store_true", dest="delete", 	default=True, 	help="deletions")
  parser.add_option("-c", "--change", 	action="store_true", dest="change", 	default=True, 	help="changes")
  parser.add_option("-p", "--permissions", action="store_true", dest="permissions", default=True, help="permissions")
  parser.add_option("-r", "--recursive", action="store_true",dest="recursive", 	default=True, 	help="recursive")
  # Add : e for everything
  # Add : l for long
  # Add : t for time
  # Add : i for ignore
  
  (options, args) = parser.parse_args()
  
  # Check the arguments  
  if len(args) != 1:
      parser.error("incorrect number of arguments")
      return 1
      
  # Check that the 1st argument is a directory
  dir_path = args[0]
  if not os.path.isdir(dir_path):
      sys.stdout.write("Error: '%s' is not a directory\n" % dir_path)
      return 1
        
  # Creation of the Qt Context
  app = QCoreApplication(sys.argv)
  
  # Creation of the directory watcher
  my_watcher = DirectoryWatcher(options=options)
  my_watcher.addPath(dir_path)

  # Event loop
  sys.exit(app.exec_())
  
if __name__ == "__main__":
  main()
