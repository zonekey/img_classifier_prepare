bin_PROGRAMS = va
va_SOURCES = va.cpp \
			 imga.cpp \
			video_source.cpp 
va_CXXFLAGS = -I/opt/local/include \
			  -I/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.8.sdk/System/Library/Frameworks/Accelerate.framework/Versions/A/Frameworks/vecLib.framework/Versions/A/Headers \
			-DUSE_OPENCV \
			  -DCPU_ONLY \
			  @OPENCV_CFLAGS@
va_LDADD = -L/opt/local/lib -lcaffe -lswscale -lavcodec -lavformat -lavutil -lboost_system-mt -lglog \
		   @OPENCV_LIBS@
