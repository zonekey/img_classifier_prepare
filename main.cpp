#include "mainwidget.h"
#include <QApplication>

#include <caffe/caffe.hpp>

int main(int argc, char *argv[])
{
    ::google::InitGoogleLogging(argv[0]);
    QApplication a(argc, argv);
    MainWidget w;
    w.show();

    return a.exec();
}
