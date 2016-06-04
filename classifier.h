#ifndef CLASSIFIER_H
#define CLASSIFIER_H

#include <caffe/caffe.hpp>
#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <algorithm>
#include <iosfwd>
#include <memory>
#include <string>
#include <sstream>
#include <utility>
#include <vector>
#include <fstream>
#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>

using namespace caffe;		// NOLINT(build/namespaces)
using std::string;

/* Pair (label, confidence) representing a prediction. */
typedef std::pair < string, float >Prediction;

class Classifier {
 public:
    explicit Classifier(const string & model_file,
           const string & trained_file,
           const string & mean_file, const string & label_file);

    std::vector < Prediction > Classify(const cv::Mat & img, int N = 5);

    int catalog_num() const {
        return labels_.size();
    }

    int catalog_from_label(const std::string & label) const {
        for (size_t i = 0; i < labels_.size(); i++) {
            if (label == labels_[i]) {
                return i;
            }
        } return -1;
    }

    cv::Mat title_from_catalog(int c) const
    {
        return titles_[c];
    }

    std::string label(int c) const
    {
        return labels_[c];
    }

 private:
    void SetMean(const string & mean_file);

    std::vector < float >Predict(const cv::Mat & img);

    void WrapInputLayer(std::vector < cv::Mat > *input_channels);

    void Preprocess(const cv::Mat & img,
            std::vector < cv::Mat > *input_channels);

 private:
    shared_ptr < Net < float > > net_;
    cv::Size input_geometry_;
    int num_channels_;
    cv::Mat mean_;
    std::vector < string > labels_;
    std::vector<cv::Mat> titles_;	// 位图，用于显示 ..
};

#endif // CLASSIFIER_H
