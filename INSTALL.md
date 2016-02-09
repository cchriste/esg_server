ViSUS Visualization Project
===============================================

| Copyright (c) 2016 University of Utah
| Scientific Computing and Imaging Institute
| 72 S Central Campus Drive, Room 3750
| Salt Lake City, UT 84112
						    
| For information about this project see: 
| http://www.pascucci.org/visus/
| or contact: pascucci@sci.utah.edu

--------------------------------------
Prerequisites 
--------------------------------------

download and install cmake (http://www.cmake.org/cmake/resources/software.html)

Get source code from::

	https://github.com/sci-visus/nvisusio

--------------------------------------
Windows 32bit compilation
--------------------------------------

Run cmake-gui and::

	"Where is the source code" 	    c:/path/to/nvisusio
	"WHere to build the binaries"   c:/path/to/nvisusio/build/win32
	Click "Configure" (probably two times). Choose "Visual Studio"/
	Click "Generate"
	Open the project build\win32\visus.sln and "Build all"

--------------------------------------
Windows 64bit compilation
--------------------------------------

Run cmake-gui and::

	"Where is the source code" 	c:/path/to/nvisusio
	"WHere to build the binaries"   c:/path/to/nvisusio/build/win64
	Click "Configure". Choose "Visual Studio 10 64bit"
	Click "Generate"
	Open the project build/win64/visus.sln and "Build all"


--------------------------------------
Linux compilation
--------------------------------------

Note: you need to install the package uuid-dev

For example in Ubuntu:

  sudo apt-get install uuid-dev

From shell::

	cd <path/to/nvisusio>
	mkdir -p build/linux 
	cd build/linux
	cmake ../../ -DCMAKE_BUILD_TYPE=Release
	make

--------------------------------------
MacOsx compilation
--------------------------------------

From a terminal::

	cd <path/to/nvisusio>
	mkdir -p build/macosx
	cd build/macosx
	# for OSX 10.6
	cmake -GXcode ../../
	# for OSX 10.5 
	cmake -GXcode -DCMAKE_OSX_DEPLOYMENT_TARGET="10.5" ../../    
	
Then::
	
	Open the XCode project in build/macosx/Visus.xcode  
	Run	
	 
--------------------------------------
IOS compilation
--------------------------------------

IMPORTANT: project dependencies do not work!
every time you modify some code you need to touch the executable file
For example "touch visuscpp/executable/visusviewer.cpp) to force REALLY the re-linking

From a terminal::

	cd <path/to/nvisusio>
	mkdir -p build/ios
	cd build/ios	
	cmake -GXcode -DVISUS_IOS=1 ../..

Then::

	Open the XCode project in build/ios/Visus.xcode 
	Select visusviewer/iPhone|iPad device
	Run

Note: if you upgraded to IOS 7.0 or 7.1 you may need to run this command:

sudo ln -sf /Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/SDKs/iPhoneOS7.1.sdk/System/Library/Frameworks/IOKit.framework/Versions/A/IOKit /Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/SDKs/iPhoneOS7.1.sdk/System/Library/Frameworks/IOKit.framework/IOKit


--------------------------------------
mod_visus compilation
--------------------------------------

	see visuscpp/executable/mod_visus/README
	
	
--------------------------------------
Generate dependency graph
--------------------------------------

From a shell::

	cmake --graphviz=../../docs/etc/visus-dependecy-graph.dot ../../  
	dot -Tgif -o ../../docs/etc/visus-dependecy-graph.gif ../../docs/etc/visus-dependecy-graph.dot
	eog ../../docs/visus-dependecy-graph.gif
	
--------------------------------------
Using the ViSUS Framework in an external application 
--------------------------------------

Please see docs/examples/external_nvisusio.
