#-------------------------------------------------
#
# Project created by QtCreator 2016-01-26T19:33:38
#
#-------------------------------------------------

QT       += core gui

CONFIG += c++11

greaterThan(QT_MAJOR_VERSION, 4): QT += widgets

TARGET = classifier
TEMPLATE = app

SDK_ROOT = c:/Users/sunkw/work/sdk

DEFINES += CPU_ONLY=1 _MBCS
win32:INCLUDEPATH += $$SDK_ROOT/include

win32:LIBS += -L$$SDK_ROOT/lib -llibcaffe -lopencv_world300 -llibgflags -llibglog -llibprotobuf -ladvapi32

SOURCES += main.cpp\
        mainwidget.cpp \
    kvconfig.cpp \
    classifier.cpp \
    predicator.cpp \
    register_all.cpp

HEADERS  += mainwidget.h \
    kvconfig.h \
    classifier.h \
    predicator.h

FORMS    += mainwidget.ui
