#!/usr/bin/env python
"""
Basic Directory Watcher. Monitors any change on the files of a directory.

Copyright (C) 2010  Frederic Boisnard

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

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
    self.files_stats = {}
    QObject.connect(self.watcher, SIGNAL("directoryChanged(const QString &)"), self.dirChanged)
    
  def addPath(self, path):
    qpath = QtCore.QString(path)
    self.watcher.addPath(qpath)    
      
    # limitation : only 1 directory is watched
    self.files_watched = set(os.listdir(self.watcher.directories()[0]))
    for f in self.files_watched:
      self.files_stats[f] = os.stat(f)
    
  def dirChanged(self, path):
    new_files_watched = set(os.listdir(self.watcher.directories()[0]))
    
    # Compare the new state of the files in the directory with the previous one
    #
    # Check 1 : additions
    files_added = new_files_watched - self.files_watched
    if self.options.additions:
      for f in files_added:
        # Display
        if self.options.verbose:
          print("added: %s" % f)      
        else:
          print("%s" % f)
        # Management
        self.files_watched.add(f)
        self.files_stats[f] = os.stat(f)

    # Check 2 : deletions
    files_removed = self.files_watched - new_files_watched 
    if self.options.deletions:
      for f in files_removed:
        # Display
        if self.options.verbose:
          print("removed: %s" % f)
        else:
          print("%s" % f)
        # Management
        self.files_watched.remove(f)
        del self.files_stats[f]
      
    # Check 3 : Modification (file size changed, permissions, ...)
    if self.options.modifications:
      for f in new_files_watched:
        current_stat = os.stat(f)
        if self.files_stats[f] != current_stat:
          # Display
          if self.options.verbose:
            print("modified: %s" % f)
          else:
            print("%s" % f)
          # Management
          self.files_stats[f] = current_stat
  
def main():
  import optparse
  
  # Options and arguments handling
  usage = "usage: %prog [options] dir"
  version="%%prog %s"%VERSION
  
  parser = optparse.OptionParser(usage=usage, version=version)
  parser.add_option("-v", "--verbose", 	action="store_true", dest="verbose", 	default=False, 	help="verbose mode")
  parser.add_option("-a", "--add", 	action="store_true", dest="additions", 	default=False, 	help="additions")
  parser.add_option("-d", "--del", 	action="store_true", dest="deletions", 	default=False, 	help="deletions")
  parser.add_option("-c", "--modif", 	action="store_true", dest="modifications", 	default=False, 	help="modificaitons")
  parser.add_option("-e", "--everything", 	action="store_true", dest="everything", 	default=False, 	help="everything")
  parser.add_option("-r", "--recursive", action="store_true",dest="recursive", 	default=False, 	help="recursive")
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
  
  # If no check is asked, activate 'everything' by default
  if not options.everything \
    and not options.additions \
    and not options.deletions \
    and not options.modifications:
      options.everything = True
      
  # 'everything' option is choosen : activate every checks
  if options.everything:
    options.additions = True
    options.deletions = True
    options.modifications = True
  
  # Creation of the Qt Context
  app = QCoreApplication(sys.argv)
  
  # Creation of the directory watcher
  my_watcher = DirectoryWatcher(options=options)
  my_watcher.addPath(dir_path)

  # Event loop
  sys.exit(app.exec_())
  
if __name__ == "__main__":
  main()
