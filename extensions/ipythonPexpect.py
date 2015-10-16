# ipythonPexpect netcat variant

"""Handle a pexpect.py session with an external program."""

# Adam Lyon   lyon at fnal.gov   March 2013

#------------
# Fermilab Software Legal Information (BSD License)
# Copyright (c) 2013, FERMI NATIONAL ACCELERATOR LABORATORY
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this list of conditions and the following
#  disclaimer.
#
# Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
#  disclaimer in the documentation and/or other materials provided with the distribution.
#
# Neither the name of the FERMI NATIONAL ACCELERATOR LABORATORY, nor the names of its contributors may be used to endorse
#  or promote products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#------------

# THIS IS AN IPYTHON EXTENSION MODULE
# Load with %load_ext ipythonPexpect

import sys
import os

import pexpect

from IPython.testing.skipdoctest import skip_doctest
from IPython.core.magic import (Magics, magics_class, cell_magic, line_magic, line_cell_magic)
from IPython.core.magic_arguments import (argument, magic_arguments, parse_argstring)
from IPython.core.error import UsageError
from IPython.display import Image

__version__ = '0.0.1'

print "%ipythonPexpect? for help"

# Strip quotes if necessary
def stripQuotes(s):
  if s[0] == '"' or s[0] == "'":
    q = s[0]
    if s[-1] == q:
      return s[1:-1]
  return s

# The PexpectMagics class
@magics_class
class PexpectMagics(Magics):
  """A set of magics for interacting with an external command-line application with pexpect."""

  def __init__(self, shell):
    super(PexpectMagics, self).__init__(shell)

    # Hang on to our instance of a pexpect child
    #   (maybe one day have a dictionary of these things)
    self._shell = shell
    self._child = None
    self._expectSearch = None
    self._prompt = None
    self._name = None
    self._isDefault = False
  
    self._shell.pexpect_locked = False

  #--Magics follow ------------------------------
  
  #-- For help--
  @line_magic
  def ipythonPexpect(self, line):
    """
    ipythonPexpect uses pexpect to control an application from within an IPython notebook.
      
    Magics (add ? to each for additional help):
      
    %pexpect_spawn - Spawn an application under control of pexpect

        Pre-defined commands for certain applications
        %pexpect_spawn_bash    - Spawn a bash shell
        %pexpect_spawn_pytyhon - Spawn a python shell
        %pexpect_spawn_R       - Spawn the R statistics analysis program
        %pexpect_spawn_root    - Spawn the CERN ROOT data analysis program
      
    %%P - Send a command to the application
      
    %pexpect_lock - Every subsequent executed IPython cell will go to the 
                    application, even without %%P in the cell
      
    %pexpect_unlock - Return execution to IPython
      
    %pexpect_next_prompt - If something messes up, try to get pexpect to find the
                           next prompt (useful if you had to interrupt pexpect or it timed out)
      
    %pexpect_close - Close and terminate the application
      
    %pexpect_clear_testing - If you had set a testing flag, turn it off
      
    """
    print "%ipythonPexpect? for help"
  
  # Arguments for spawning
  @skip_doctest
  @magic_arguments()
  @argument(
      '-p', '--prompt', type=unicode,
      help='Pexpect Regex for the main application prompt [mandatory]'
    )

  @argument(
      '-c', '--continuation', type=unicode,
      help='Pexpect Regex for the continuation prompt [optional]'
    )
  
  @argument(
      '-i', '--init', type=str,
      help='Initialization command, if necessary'
    )

  @argument(
      '-t', '--timeout', type=int,
      help='Timeout (in s) for expect'
  )
  
  @argument(
      '-w', '--searchWindow', type=int,
      help='Search window size'
  )

  @argument(
      '-e', '--executeCommand', type=str,
         help='The command to run including arguments (if dash options use quotes)'
    )
  
  @argument(
      '-x', '--logfortest',
      help='Log output to file for testing regular expressions (output goes to pexpect.log)',
      action='store_true',
      default=False
  )
      
  @line_magic
  def pexpect_spawn(self, line):
    '''
      Line-level magic that spawns a pexpect session
      
      You can send an initalization string to set the prompt.
      
      The prompt should start with \r\n
      
      For example (you can also use the pre-defined commands for the examples below),
      
      Bash: (Set the prompt to a known quantity)
      %pexpect_spawn -i 'PS1="bash> "' -p '\\r\\nbash> ' -c '\\r\\n> ' -e /usr/bin/env bash
      
      R:
      %pexpect_spawn -p "\\r\\n> " -c "\\r\\n[+] " -e R
      
      CERN Root:
      %pexpect_spawn -p "\\r\\nroot [[]\\d+[]] " -c "\\r\\n> " -e "root -l"
    '''
    
    args = parse_argstring(self.pexpect_spawn, line)

    # Make sure we have a prompt
    if getattr(args, 'prompt') is None:
      raise UsageError("You did not supply -p or --prompt")

    if getattr(args, 'executeCommand') is None:
      raise UsageError("You did not supply -e or --executeCommand")
        
    continuation = None
    if getattr(args, 'continuation') is not None:
      continuation = stripQuotes(args.continuation)
        
    timeout = None
    if getattr(args, 'timeout') is not None:
      timeout = args.timeout
  
    searchwindowsize = None
    if getattr(args, 'searchWindow') is not None:
      searchwindowsize = args.searchWindow
        
    initCommand = None
    if getattr(args, 'init') is not None:
      initCommand = stripQuotes(args.init)
        
    self.spawn(stripQuotes(args.executeCommand), stripQuotes(args.prompt), continuation, initCommand,
               timeout, searchwindowsize, args.logfortest)
  
  #--------------------------------
  def spawn(self, command, prompt, continuation=None, initCommand=None, timeout=None, searchwindowsize=None,
            logfortest=False):
    
    # If we already have a child, close it
    if self._child:
      self._child.close(True)
      self._child = None
      print 'Closing old connection'
    
    self._testing = False

    # Determine the prompt
    self._expectSearch = prompt
    if continuation:
      self._expectSearch = [prompt, continuation ]
        
    #print self._expectSearch

    if logfortest:
      print 'In testing mode. Logging all output to pexpect.log. No output will appear in the cell'
      
    # Set for dumb terminal to get rid of ANSI cruft
    os.environ['TERM'] = 'dumb'

    # Let's spawn
    self._child = pexpect.spawn(command)
  
    # Turn on read logging
    if logfortest:
        # If we are testing, send everything to log file
        self._child.logfile = open('pexpect.log', 'w')
        self._testing = True
    else:
      self._child.logfile_read = sys.stdout
        
    # Set timeout and windowsize
    if timeout:
      self._child.timeout = timeout
      
    if searchwindowsize:
      self._child.searchwindowsize = searchwindowsize

    # Run the init command
    if initCommand:
      # Run the command, discarding output
      self._child.sendline(initCommand)
      self._child.readline()
    
    print 'Opened connection to %s' % command
   
    self._child.expect( prompt,timeout=5 )  # Get the prompt
    self._prompt = self._child.after.lstrip()
    self._name = command

  #--------------------------------
  @line_magic
  def pexpect_spawn_bash(self, line):
    """Spawn a bash shell"""
    self.spawn("/usr/bin/env bash", "bash> ", "\r\n> ", "PS1='bash> '")

  #--------------------------------
  @line_magic
  def pexpect_spawn_python(self, line):
    """Spawn a python shell"""
    self.spawn("/usr/bin/env python", "\r\n>>> ", "\r\n\.\.\. ")

  #--------------------------------
  @line_magic
  def pexpect_spawn_R(self, line):
    """Spawn an R session"""
    self.spawn("R", "\r\n> ", "\r\n[+] ")
    
  #--------------------------------
  # Spawn Root
  # Note that you must have a .rootrc file with
  #
  #   
  @line_magic
  def pexpect_spawn_root(self, line):
    """Spawn a Root session"""
    
    rootrc = """Rint.TypeColor:           default
Rint.BracketColor:        default
Rint.BadBracketColor:     default
Rint.TabColor:            default
Rint.PromptColor:         default
Rint.ReverseColor:        default
"""
    
    # Check for .rootrc
    if os.path.exists("./.rootrc"):
      print 'A .rootrc file is automatically written to turn off root prompt syntax coloring.'
      print 'But it cannot be written because one already exists. Continuing assuming'
      print '.rootrc turns off syntax coloring.'
      print '------'
    else:
      # Write rootrc
      open('./.rootrc', 'w').write(rootrc)
        
    # Even then syntax coloring is turned off, the prompt still has the "decolor"
    # ansi command (it can appear multiple times).
    self.spawn("root -b", '\r\n(\x1b\[[;\d]*[A-Za-z])*root \[\d+\] ', "\r\n(\x1b\[[;\d]*[A-Za-z])*end with '}', '@':abort > ")


  #--------------------------------
  @line_magic
  def pexpect_get_child(self, line):
    """Return the pexpect child object (for debugging)"""
    return self._child

  #--------------------------------
  @skip_doctest
  @magic_arguments()
  @argument(
    '-t', '--timeout', type=int,
    help='Timeout (in s) for this command'
    )
  
  @argument(
    '-w', '--searchWindow', type=int,
    help='Search window size for this command'
    )

  @argument(
    '-p', '--prompt', type=str,
    help='New Pexpect Regex for the main application prompt [mandatory]'
    )
  
  @argument(
    '-c', '--continuation', type=str,
    help='New Pexpect Regex for the continuation prompt [optional]'
    )
  
  @argument(
     '-e', '--evalLast',
     help='Return the output of the last command to python along with displaying (evaluate)',
     action='store_true',
     default=False
    )
      
  @argument(
      '-f', '--figure', type=str,
      help='Load a PNG figure with the given file name (must be in the current iPython directory)'
    )
  
  @argument(
      '-x', '--logfortest',
      help='Log output to file for testing regular expressions (output goes to pexpect.log)',
      action='store_true',
      default=False
    )

  @argument(
    'code',
    nargs='*',
    )
  
  @line_cell_magic
  def P(self, line, cell=None):
    '''
    Send line or cell to the application and print the output
    '''
    
    if not self._child:
      raise UsageError("No connection")

    args = parse_argstring(self.P, line)
        
    code = None

    if cell is None and args.code is None:
      # Un, no command
      raise UsageError("No command given")
      
    if cell is None and args.code is not None:
      code = " ".join(args.code)

    if cell is not None and args.code is None:
      code = cell

    if cell is not None and args.code is not None:
      code1 = " ".join(args.code)
      code = code1 + cell

    if code == None:
      raise UsageError("Somehow code is not set")
        
    timeout = -1
    if getattr(args, 'timeout') is not None:
      timeout=args.timeout

    searchwindowsize = -1
    if getattr(args, 'searchWindow') is not None:
      searchwindowsize=args.searchWindow
    
    # Determine the prompt search
    if getattr(args, 'prompt') is not None:
      self._expectSearch = stripQuotes( args.prompt )
    
    if getattr(args, 'continuation') is not None:
      self._expectSearch = [self._expectSearch, stripQuotes( args.continuation ) ]

    codeLines = [ x.rstrip() for x in code.split("\n") ]

    # Print the prompt (output is automatically printed from logfile_read)
    sys.stdout.write( self._prompt )
  
    if args.logfortest:
      if not self._testing:
        self._child.logfile_read = None
        self._child.logfile=open('pexpect.log', 'w')
        self._testing = True
        print 'In testing mode. Logging all output to pexpect.log. No output will appear in the cell'

    index = 0
    debug = False
    # Send each line one at a time
    for line in codeLines:
	got_prompt=False
        if debug:
            print "Sending line:",line
        self._child.sendline(line)
        try:
            if debug:
                print "Waiting for prompt..."
            index = self._child.expect(self._expectSearch, timeout=0.5, searchwindowsize=searchwindowsize)
            self._prompt = self._child.after.lstrip()
            got_prompt=True
            if debug:
                print "Got prompt:",self._prompt,"index:",index
            
        except KeyboardInterrupt:
            print 'Ctrl^C'
        except pexpect.TIMEOUT:
            if debug:
                print "Prompt timeout"
            pass


    if index == 0 and not got_prompt:
        try:
            if debug:
                print "Waiting for final prompt..."
            index = self._child.expect(self._expectSearch, timeout=timeout, searchwindowsize=searchwindowsize)
            self._prompt = self._child.after.lstrip()
        except KeyboardInterrupt:
            print 'Ctrl^C while waiting for bash prompt...'
        except pexpect.TIMEOUT:
            if debug:
                print "Pexpect waiting for input"

    # Load the figure if desired
    if getattr(args, 'figure') is not None:
      return Image(data=open(args.figure).read(), format="png")

    if args.evalLast:
      # Strip out the first line
      lines = [x.strip() for x in self._child.before.split("\n") ]
      if len(lines) > 1:
        return '\n'.join(lines[1:])
  

  #--------------------------------
  @skip_doctest
  @magic_arguments()
  @argument(
            '-t', '--timeout', type=int,
            help='Timeout (in s) for this command'
            )
  
  @argument(
            '-w', '--searchWindow', type=int,
            help='Search window size for this command'
            )
  
  @line_magic
  def pexpect_next_prompt(self, line):
    '''
      Use pexpect_next_prompt to clear a timeout or other problem
    '''
    
    if not self._child:
      raise UsageError("No connection")
    
    args = parse_argstring(self.P, line)

    timeout = -1
    if getattr(args, 'timeout') is not None:
      timeout=args.timeout
    
    searchwindowsize = -1
    if getattr(args, 'searchWindow') is not None:
      searchwindowsize=args.searchWindow

    try:
        index = self._child.expect( self._expectSearch, timeout=timeout, searchwindowsize=searchwindowsize)
    except KeyboardInterrupt:
        print 'Ctrl^C'

    self._prompt = self._child.after.lstrip()

  #--------------------------------
  @line_magic
  def pexpect_close(self, line):
    '''
      Close the connection and quit the application
    '''
    if not self._child:
      raise UsageError("No connection")

    self._child.close(True)
    self._child = None
    print 'Closed connection to %s' % self._name

  #--------------------------------
  @line_magic
  def pexpect_lock(self, line):
    '''
      Lock the notebook to send EVERY executed cell through pexpect
      
      Do %pexpect_unlock to unlock
    '''
    if not self._child:
      raise UsageError("No connection")

    self._shell.pexpect_locked = True

    print 'WARNING: All future cell execution will be processed through pexpect!'
    print 'To return to IPython, issue %pexpect_unlock'

  #--------------------------------
  @line_magic
  def pexpect_unlock(self, line):
    '''
      Unlock the notebook to return to regular IPython
    '''

    if not self._child:
      raise UsageError("No connection")

    self._shell.pexpect_locked = False
    
    print 'Notebook will use IPython'

  #---------------------------
  @line_magic
  def pexpect_clear_testing(self, line):
    if not self._child:
      raise UsageError("No connection")
    if not self._testing:
      raise UsageError("Not testing")
    self._testing = False
    self._child.logfile=None
    self._child.logfle_read = sys.stdout
    print 'Testing cleared'

    
# Let's rewrite InteractiveShell.run_cell to do automatic processing with pexpect,
# if desired
from IPython.core.interactiveshell import InteractiveShell

# Let's copy the original "run_cell" method (we do this only once so we can reload)
if not getattr(InteractiveShell, "run_cell_a", False):
  InteractiveShell.run_cell_a = InteractiveShell.run_cell

# Now rewrite run_cell
def run_cell_new(self, raw_cell, store_history=False, silent=False, shell_futures=True):
  
  # Are we locked in pexpect?
  if getattr(self, "pexpect_locked", False):
  
    # Don't alter cells that start with %%P or with %pexpect_unlock
    if raw_cell[:3] == '%%P' or raw_cell[:15] == '%pexpect_unlock':
      pass
    else:
      # We're going to add a %%P to the top
      raw_cell = "%%P\n" + raw_cell

  self.run_cell_a(raw_cell, store_history, silent, shell_futures)

# And assign it
InteractiveShell.run_cell = run_cell_new

# Register this extension
def load_ipython_extension(ipython):
  pexpectMagics = PexpectMagics(ipython)
  ipython.register_magics(pexpectMagics)

