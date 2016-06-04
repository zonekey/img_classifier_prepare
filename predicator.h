#ifndef PREDICATOR_H
#define PREDICATOR_H

#include <QThread>
#include <opencv2/opencv.hpp>
#include "classifier.h"

struct ResultItem
{
    std::string title;  // 显示 ..
    float ratio;        //
};

class Predicator : public QThread
{
public:
    Predicator();

    bool pred(const cv::Mat &orig, cv::Mat &show, std::vector<ResultItem> &results);

private:
    void run();
};

#endif // PREDICATOR_H
