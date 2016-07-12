bin_PROGRAMS = va
va_SOURCES = va.cpp \
			 imga.cpp \
			video_source.cpp 
va_CXXFLAGS = ${avcodec_CFLAGS} ${avformat_CFLGAGS} ${avutil_CFLAGS} ${swscale_CFLAGS} \
			  -I/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.8.sdk/System/Library/Frameworks/Accelerate.framework/Versions/A/Frameworks/vecLib.framework/Versions/A/Headers \
			-DUSE_OPENCV \
			  -DCPU_ONLY \
			  @OPENCV_CFLAGS@
va_LDADD = -L/opt/local/lib -lcaffe -lboost_system -lglog \
		   ${avcodec_LIBS} ${avformat_LIBS} ${avutil_LIBS} ${swscale_LIBS} \
		   @OPENCV_LIBS@
