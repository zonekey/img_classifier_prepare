#pragma once

extern "C" {
#	include <libavformat/avformat.h>
#	include <libavcodec/avcodec.h>
#	include <libswscale/swscale.h>
}

#include <opencv2/opencv.hpp>
#include <cc++/thread.h>
#include <cc++/socket.h>

class FFmpegVideoSource
{
	AVFormatContext *ctx_;
	bool valid_decodere_[32];
	AVFrame *frame_;
	SwsContext *sws_;	// 
	AVPicture pic_;		//
	int width_, height_;
	double duration_;

public:
	FFmpegVideoSource();
	~FFmpegVideoSource();

	int open(const char *url);
	void close();

	cv::Mat next_frame(double &stamp, bool &eof);

	double duration() const;

private:
	cv::Mat one_video_frame(AVPacket &pkg);
	bool check_sws(AVFrame *frame);
};

