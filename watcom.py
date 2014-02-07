# Copyright (c) 2013-2014 The SCons Foundation
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
#Required for the linker, and static/dynamic archivers.
def _watstr_linksrc(x):
    res = []
    for f in x:
    	    res.append(str(f))
    return tuple(res)


def generate(env, **kw):
	#Get environment for the WATCOM compiler from the OS.
	env['ENV']['WATCOM'] = os.environ['WATCOM']
	env['ENV']['INCLUDE'] = os.environ['INCLUDE']
	env['ENV']['EDPATH'] = os.environ['EDPATH']
	env['ENV']['WIPFC'] = os.environ['WIPFC']
	#env['ENV']['WHTMLHELP'] = os.environ['WHTMLHELP']
	env.AppendENVPath('PATH', env['ENV']['WATCOM'] + '/BINNT') #Windows NT
	env.AppendENVPath('PATH', env['ENV']['WATCOM'] + '/BINW') #Windows 9x
	env.AppendENVPath('PATH', env['ENV']['WATCOM'] + '/binl') #Linux
	#OS/2 eventually- I mainly can't add this because I have no OS/2 system
	#with which to test.
	
	#Generate default builders- this is generic for now until I can otherwise
	#improve.
	static_obj, shared_obj = SCons.Tool.createObjBuilders(env)
	
	#Future Improvement- since WATCOM can run on multiple platforms- change
	#supported suffixes et. al depending on env['HOST_OS'].
	#For now, assume Windows host (Capital .C is C file, not C++)
	#Also, look at SCons.Util.case_sensitive_suffixes('.c', '.C')
	for suffix in ['.c', '.C']:
		static_obj.add_action(suffix, SCons.Defaults.CAction)
		shared_obj.add_action(suffix, SCons.Defaults.ShCAction)
		static_obj.add_emitter(suffix, SCons.Defaults.StaticObjectEmitter)
		shared_obj.add_emitter(suffix, SCons.Defaults.SharedObjectEmitter)
	for suffix in ['.cpp', '.CPP']:
		static_obj.add_action(suffix, SCons.Defaults.CXXAction)
		shared_obj.add_action(suffix, SCons.Defaults.ShCXXAction)
		static_obj.add_emitter(suffix, SCons.Defaults.StaticObjectEmitter)
		shared_obj.add_emitter(suffix, SCons.Defaults.SharedObjectEmitter)
	for suffix in ['.asm', '.ASM']:
		static_obj.add_action(suffix, SCons.Defaults.ASAction)
		shared_obj.add_action(suffix, SCons.Defaults.ASAction)
		static_obj.add_emitter(suffix, SCons.Defaults.StaticObjectEmitter)
		shared_obj.add_emitter(suffix, SCons.Defaults.SharedObjectEmitter)	
		
	#WATCOM supports a number of actions that are implemented in SCons	
	SCons.Tool.createStaticLibBuilder(env)
	SCons.Tool.createSharedLibBuilder(env)
	SCons.Tool.createProgBuilder(env)	
	
	#Set tool-specific information
	env['USE386'] = False
	env['WATSTR_LINK'] = _watstr_linksrc
	env['WATSTR_AR'] = _watstr_linksrc
	env['MEMMODEL16'] = 'c'
	env['MEMMODEL32'] = 'f'
	env['USEWASM'] = True
	
	#Deprecated- do not use directly.
	env['MEMMODEL'] = "${USE386==True and MEMMODEL32 or MEMMODEL16}"
	
	#C/C++ Compilers, Preprocessor, and General Command Line Decorators.
	#Watcom Compilers come in 2 flavors- one for 8088 targets, and one for 386 targets.
	#The 386-compilers have '386' appended to them... i.e. wpp vs wpp386
	env['CC'] = "wcc${USE386==True and '386' or ''}"
	env['CXX'] = "wpp${USE386==True and '386' or ''}"
	#env['CCFLAGS'] = '-0 -c -m' + env['MEMMODEL'] + ' -onatx -ol -oh -oi -s -ecc -ze -zq -zu'
	env['CCFLAGS'] = SCons.Util.CLVar('-zq -m${MEMMODEL}')
	env['CFLAGS'] = SCons.Util.CLVar('')
	env['CXXFLAGS'] = SCons.Util.CLVar('') #Suppress /TP
	
	#Precompiled header support will be added later
	env['_CCCOMCOM']  = '$CPPFLAGS $_CPPDEFFLAGS $_CPPINCFLAGS $CCPCHFLAGS $CCPDBFLAGS'
	env['CCCOM'] = '$CC -fo=$TARGET $CFLAGS $CCFLAGS $_CCCOMCOM $SOURCES'
	env['CXXCOM'] = '$CXX -fo=$TARGET $CXXFLAGS $CCFLAGS $_CCCOMCOM $SOURCES'
	env['CPPDEFPREFIX'] = '-d'
	env['CPPDEFSUFFIX'] = ''
	env['INCPREFIX'] = '-i='
	env['INCSUFFIX'] = ''
	
	#Assembler- Does not automatically set 386 or 8088 mode.
	#Check for jwasm- use that if it exists.
	#First check WATCOM paths, then OS paths
	jwasm_path=env.WhereIs('jwasm') or SCons.Util.WhereIs('jwasm')
	if jwasm_path:
		#This seems to be required, as opposed to SCons platform-independent
		#dir functions to split filenames and paths... why?
		dir = os.path.dirname(jwasm_path)
		env.PrependENVPath('PATH', dir)
		env['USEWASM'] = False
		
	env['AS']="${USEWASM==True and 'wasm' or 'jwasm'}"
	env['ASFLAGS'] = SCons.Util.CLVar('-q -m${MEMMODEL}')
	env['ASPPFLAGS'] = SCons.Util.CLVar('-q -m${MEMMODEL}') 	#-q and -Fo 
	#appears to be undocumented aliases for -zq, or operate quietly, and 
	#-Fo= and fo=, or File Output. These are compatible with jwasm.
	
	
	#Possible future improvement? Make command lines compatible with chosen
	#assembler. Check to see that appending flags still works however!
	#Makes it so initally generated command lines won't mix syntaxes... doesn't
	#prevent user from appending mixed incompatible command line options however!
	#I simply feel a bit uncomfortable using the undocumented aliases.
	#env['WASMFLAGS'] = '-zq -m${MEMMODEL}'
	#env['WASMCOM']  = '$AS -fo=$TARGET $ASFLAGS $CPPFLAGS $_CPPDEFFLAGS $_CPPINCFLAGS $SOURCES'
	#env['WASMPPCOM']  = '$CC -fo=$TARGET $ASPPFLAGS $CPPFLAGS $_CPPDEFFLAGS $_CPPINCFLAGS $SOURCES'
	#env['JWASMFLAGS'] = '-q -m${MEMMODEL}'
	#env['JWASMCOM']  = '$AS -Fo$TARGET $ASFLAGS $CPPFLAGS $_CPPDEFFLAGS $_CPPINCFLAGS $SOURCES'
	#env['JWASMPPCOM']   = '$CC -Fo$TARGET $ASPPFLAGS $CPPFLAGS $_CPPDEFFLAGS $_CPPINCFLAGS $SOURCES'
	#env['ASFLAGS']="${USEWASM==True and WASMFLAGS or JWASMFLAGS}"
	#env['ASPPFLAGS']="${USEWASM==True and WASMPPFLAGS or JWASMPPFLAGS}"
	#env['ASCOM']="${USEWASM==True and WASMCOM or JWASMCOM}"
	#env['ASPPCOM']="${USEWASM==True and WASMPPCOM or JWASMPPCOM}"
	
	#MASM/WASM has it's own macro language, so the C preprocessor doesn't do
	#much here. WATCOM DOES have a (broken) POSIX interface, howver.
	env['ASCOM'] = '$AS -Fo$TARGET $ASFLAGS $CPPFLAGS $_CPPDEFFLAGS $_CPPINCFLAGS $SOURCES'
	env['ASPPCOM']   = '$CC -Fo$TARGET $ASPPFLAGS $CPPFLAGS $_CPPDEFFLAGS $_CPPINCFLAGS $SOURCES'

	#Linker- To fix: Resources require the "resource" directive, but all other
	#SCons builders treat them are regular object files automatically handled
	#by the linker.
	env['LINK'] = 'wlink'
	env['LINKPREFIX'] = 'file '
	env['LINKSUFFIX'] = ''
	env['_LINKSOURCES'] = '$(${_concat(LINKPREFIX, ' \
		'SOURCES, ' \
		'LINKSUFFIX, __env__, WATSTR_LINK)}$)'
	env['LINKCOM'] = "$LINK name '$TARGET' $LINKFLAGS $_LIBDIRFLAGS $_LIBFLAGS $_LINKSOURCES"

	env['LINKFLAGS'] = SCons.Util.CLVar('option quiet')
	env['LIBDIRPREFIX'] = 'libpath '
	env['LIBDIRSUFFIX'] = ''
	env['LIBLINKPREFIX'] = 'library '
	env['LIBLINKSUFFIX'] = ''

	#Librarian
	env['AR'] = 'wlib'
	env['ARFLAGS'] = SCons.Util.CLVar('-q')
	env['ARPREFIX'] = '+'
	env['ARSUFFIX'] = ''
	env['ARCOM'] = '$AR $ARFLAGS $TARGET $_ARSOURCES'
	env['_ARSOURCES'] = '$(${_concat(ARPREFIX, ' \
		'SOURCES, ' \
		'ARSUFFIX, __env__, WATSTR_AR)}$)'
	env['LIBPREFIX'] = ''
	env['LIBSUFFIX'] = '.lib'
	
	#For UNIX targets... may require using TARGET_OS or WATTARGET_OS
	#env['LIBPREFIX']   = 'lib'
	#env['LIBSUFFIX']   = '.a'
	
	
	#Resource Compiler
	env['RC'] = 'wrc'
	env['RCFLAGS'] = SCons.Util.CLVar('-q -r')
        env['RCSUFFIXES']=['.rc','.rc2']
        env['RCCOM'] = '$RC $_CPPDEFFLAGS $_CPPINCFLAGS $RCFLAGS -fo=$TARGET $SOURCES'
	
	#Internal option used when the shared and static object compilers differ.
	env['STATIC_AND_SHARED_OBJECTS_ARE_THE_SAME'] = 1
	
	
def exists(env):
	return check_for_watcom()
	
def check_for_watcom():
	try:
		return env['WATCOM']
	except KeyError:
		return None
	
