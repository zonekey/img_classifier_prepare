#                                               -*- Autoconf -*-
# Process this file with autoconf to produce a configure script.

AC_PREREQ([2.69])
AC_INIT([FULL-PACKAGE-NAME], [VERSION], [BUG-REPORT-ADDRESS])
AM_INIT_AUTOMAKE([1.12 foreign no-define])
AC_CONFIG_SRCDIR([va.cpp])
AC_CONFIG_HEADERS([config.h])

# Checks for programs.
AC_PROG_CXX
AC_PROG_CC

# Checks for libraries.

# Checks for header files.

# Checks for typedefs, structures, and compiler characteristics.
AC_CHECK_HEADER_STDBOOL
AC_TYPE_SIZE_T

# Checks for library functions.
AC_CHECK_FUNCS([memset])
PKG_CHECK_MODULES(OPENCV,opencv)
PKG_CHECK_MODULES(avcodec, libavcodec)
PKG_CHECK_MODULES(avformat, libavformat)
PKG_CHECK_MODULES(avutil, libavutil)
PKG_CHECK_MODULES(swscale, libswscale)

AC_CONFIG_FILES([Makefile])
AC_OUTPUT
