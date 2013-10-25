# Copyright (c) 2013 The SCons Foundation
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.



"""This is the WATCOM SCons tool file (for DOS). This fine-tunes the build process and general
compiler options. I strongly advise leaving this alone unless you know what you're doing.
Perhaps the only problem with SCons is that WATCOM is not supported out of the box.
I am heavily considering submitting a patch to add it."""


#If you didn't heed the above, some notes:
"""Variables with a leading underscore are internal variables to my understanding...
but I based this tool file on already existing tools.""" 

"""It's worth noting that you can create a tools file without ever referring to 
the SCons API, but such behavior assumes that the default tools have already been loaded. 
If I submit this as a patch to SCons, for example, I have to create default actions
for my builders."""

import os
#import SCons.Defaults
#import SCons.Tool
import SCons.Util

#http://four.pairlist.net/pipermail/scons-users/2013-August/001639.html
#This is required to bypass certain limitations of SCons __concat function.
def _watstr(x):
    res = []
    for f in x:
        res.append(str(f))
    return tuple(res)
   
#Watcom Compilers come in 2 flavors- one for 8088 targets, and one for 386 targets.
#The 386-compilers have '386' appended to them... i.e. wpp vs wpp386
class string386:
	def __init__(self, Use386 = False):
		self.use386 = Use386
		
	def __str__():
		if self.use386:
			return '386'
		else:
			return ''


def generate(env, **kw):
	#Get environment for the WATCOM compiler from the OS.
	env['ENV']['WATCOM'] = os.environ['WATCOM']
	env['ENV']['INCLUDE'] = os.environ['INCLUDE']
	env['ENV']['EDPATH'] = os.environ['EDPATH']
	env['ENV']['WIPFC'] = os.environ['WIPFC']
	env['ENV']['WHTMLHELP'] = os.environ['WHTMLHELP']
	env.AppendENVPath('PATH', env['ENV']['WATCOM'] + '/BINNT')
	env.AppendENVPath('PATH', env['ENV']['WATCOM'] + '/BINW')
	
	#Set DOS-specific information
	env['MEMMODEL'] = 'c'
	env['USE386'] = False
	
	#Then set up the compiler tools themselves.
	env['CC'] = 'wcc'
	#env['CCFLAGS'] = '-0 -c -m' + env['MEMMODEL'] + ' -onatx -ol -oh -oi -s -ecc -ze -zq -zu'
	env['CCFLAGS'] = SCons.Util.CLVar('-zq -m${MEMMODEL}')
	env['CCCOM'] = '$CC -fo=$TARGET $CFLAGS $CCFLAGS $_CCCOMCOM $SOURCES'
	env['CPPDEFPREFIX'] = '-d'
	env['INCPREFIX'] = '-i='
	env['AR'] = 'wlib'
	env['AS'] = 'wasm'
	env['ASFLAGS'] = SCons.Util.CLVar('-zq -m${MEMMODEL}')
	
	#MASM has it's own macro language
	env['ASCOM'] = '$AS -fo=$TARGET $ASFLAGS $CPPFLAGS $_CPPDEFFLAGS $_CPPINCFLAGS $SOURCES'
	env['ASPPCOM']   = '$CC -fo=$TARGET $ASPPFLAGS $CPPFLAGS $_CPPDEFFLAGS $_CPPINCFLAGS $SOURCES'

	env['LINK'] = 'wlink'
	env['LINKPREFIX'] = 'file '
	env['LINKSUFFIX'] = ''
	env['WATSTR'] = _watstr
	env['_LINKSOURCES'] = '$(${_concat(LINKPREFIX, SOURCES, LINKSUFFIX, __env__, WATSTR)}$)'
	env['LINKCOM'] = "$LINK name '$TARGET' $LINKFLAGS $_LIBDIRFLAGS $_LIBFLAGS $_LINKSOURCES"

	env['LINKFLAGS'] = SCons.Util.CLVar('option quiet')
	env['LIBDIRPREFIX'] = 'libpath '
	env['LIBDIRSUFFIX'] = ''
	env['LIBLINKPREFIX'] = 'library '
	env['LIBLINKSUFFIX'] = ''

	
	env['RC'] = 'wrc'
	env['RCFLAGS'] = SCons.Util.CLVar('-q -r')
        env['RCSUFFIXES']=['.rc','.rc2']
        env['RCCOM'] = '$RC $_CPPDEFFLAGS $_CPPINCFLAGS $RCFLAGS -fo=$TARGET $SOURCES'
	
	#Depends on if using 386 or not- 8088 not likely to be using DLLs
	env['STATIC_AND_SHARED_OBJECTS_ARE_THE_SAME'] = 1
	
	#A newer old configuration :P
	#env['ASPPCOM']   = '$CC -fo=$TARGET $ASPPFLAGS $CPPFLAGS $_CPPDEFFLAGS $_CPPINCFLAGS $SOURCES'
	#$(LIB) $(LIBFLAGS) $(LIBNAME) +$(OBJS)
	#env['LINK'] = 'wcl'
	#env['LINKFLAGS'] = SCons.Util.CLVar('-zq')
	#env['LIBDIRPREFIX'] = '-"libpath '
	#env['LIBDIRSUFFIX'] = '"'
	#env['LIBLINKPREFIX'] = '-"library '
	#env['LIBLINKSUFFIX'] = '"'
	#  ${TEMPFILE("$LINK $LINKFLAGS /OUT:$TARGET.windows $_LIBDIRFLAGS $_LIBFLAGS $_PDB $SOURCES.windows")}
	#env['LINKCOM'] = '$LINK -fe=$TARGET $LINKFLAGS $_LIBDIRFLAGS $_LIBFLAGS $SOURCES'
	
	
	#Old configuration
	#env['CC'] = 'wcc'
	#env['CCFLAGS'] = '-za -os -bt=dos'
	#env['CCCOM'] = '$CC -fo=$TARGET $CFLAGS $CCFLAGS $_CCCOMCOM $SOURCES'
	#env['INCPREFIX'] = '-i='
	#env['AR'] = 'wlib'
	#env['LINK'] = 'wlink'
	#env['LINKFLAGS'] = 'system dos'
	#env['LIBDIRPREFIX'] = 'libpath '
	#env['LIBLINKPREFIX'] = 'library '
	#  ${TEMPFILE("$LINK $LINKFLAGS /OUT:$TARGET.windows $_LIBDIRFLAGS $_LIBFLAGS $_PDB $SOURCES.windows")}
	#env['LINKCOM'] = '$LINK $LINKFLAGS $_LIBDIRFLAGS $_LIBFLAGS file{$SOURCES} name $TARGET'
	
def exists(env):
	return check_for_watcom()
	
def check_for_watcom():
	try:
		return env['WATCOM']
	except KeyError:
		return None
	
