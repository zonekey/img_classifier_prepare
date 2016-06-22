#include "video_source.h"

class InitFFmpeg
{
public:
	InitFFmpeg()
	{
		av_register_all();
		avcodec_register_all();
		avformat_network_init();
		av_log_set_level(AV_LOG_FATAL);
	}
};

static InitFFmpeg _init_ffmpeg;

FFmpegVideoSource::FFmpegVideoSource()
{
	ctx_ = 0;
	memset(valid_decodere_, 0, sizeof(valid_decodere_));

	frame_ = av_frame_alloc();
	sws_ = 0;
	pic_.data[0] = 0;
	width_ = 0, height_ = 0;

	duration_ = -1.0;
}

double FFmpegVideoSource::duration() const
{
	return duration_;
}

FFmpegVideoSource::~FFmpegVideoSource()
{
	av_frame_free(&frame_);
	if (sws_) {
		sws_freeContext(sws_);
		avpicture_free(&pic_);
	}
}

bool FFmpegVideoSource::check_sws(AVFrame *frame)
{
	if (frame->width != width_ || frame->height != height_) {
		if (sws_) sws_freeContext(sws_);

		sws_ = sws_getContext(frame->width, frame->height, (AVPixelFormat)frame->format,
				frame->width, frame->height, AV_PIX_FMT_BGR24, SWS_FAST_BILINEAR, 
				0, 0, 0);
		if (!sws_) {
			fprintf(stderr, "FATAL: check_sws: can't create sws: %d-%d, %d to BGR24\n",
					frame->width, frame->height, frame->format);
			exit(-1);
		}

		width_ = frame->width, height_ = frame->height;

		if (pic_.data[0]) avpicture_free(&pic_);

		avpicture_alloc(&pic_, (AVPixelFormat)AV_PIX_FMT_BGR24, frame->width, frame->height);
	}

	return true;
}

int FFmpegVideoSource::open(const char *url)
{
	ctx_ = 0;
	int rc = avformat_open_input(&ctx_, url, 0, 0);
	if (rc < 0) {
		fprintf(stderr, "ERR: can't open url '%s'\n", url);
		return -1;
	}

	rc = avformat_find_stream_info(ctx_, 0);
	if (rc < 0) {
		fprintf(stderr, "ERR: avformat_find_stream_info err, code=%d\n", rc);
		avformat_close_input(&ctx_);
		return -2;
	}

	duration_ = ctx_->duration / AV_TIME_BASE;

	// 打开 video decoder ...
	for (size_t i = 0; i < ctx_->nb_streams; i++) {
		AVCodecContext *codec = ctx_->streams[i]->codec;
		if (codec->codec_type == AVMEDIA_TYPE_VIDEO) {
			AVCodec *cc = avcodec_find_decoder(codec->codec_id);
			if (!cc) {
				fprintf(stderr, "ERR: avcodec_find_decoder can't find codec_id: %08x\n", codec->codec_id);
			}
			else {
				rc = avcodec_open2(codec, cc, 0);
				if (rc < 0) {
					fprintf(stderr, "ERR: avcodec_open2: can't open codec_id: %08x\n", codec->codec_id);
				}
				else {
					valid_decodere_[i] = true;
				}
			}
		}
	}

	return 0;
}

void FFmpegVideoSource::close()
{
	if (ctx_) {
		avformat_close_input(&ctx_);
	}
}

cv::Mat FFmpegVideoSource::next_frame(double &stamp, bool &eof)
{
	int n = 50;
	AVPacket pkg;
	eof = false;

	cv::Mat m;

	while (--n > 0) {
		int rc = av_read_frame(ctx_, &pkg);
		if (rc < 0) {
			if (rc == (int)AVERROR_EOF) {
				eof = true;
			}
			else {
				fprintf(stderr, "ERR: av_read_frame ret %d\n", rc);
			}
			return m;
		}
		else {
			if (valid_decodere_[pkg.stream_index]) {
				// valid video frame, decode ...		
				AVStream *stream = ctx_->streams[pkg.stream_index];
				stamp = pkg.pts * stream->time_base.num / stream->time_base.den;
				m = one_video_frame(pkg);
			}

			av_free_packet(&pkg);
		}
	}

	return m;
}

cv::Mat FFmpegVideoSource::one_video_frame(AVPacket &pkg)
{
	cv::Mat frame;

	AVCodecContext *decoder = ctx_->streams[pkg.stream_index]->codec;
	int got;
	int rc = avcodec_decode_video2(decoder, frame_, &got, &pkg); // FIXME: 是否可能多帧?
	if (rc >= 0 && got) {
		if (check_sws(frame_)) {
			sws_scale(sws_, frame_->data, frame_->linesize, 0, frame_->height, pic_.data, pic_.linesize);
			cv::Mat tmp(frame_->height, frame_->width, CV_8UC3, pic_.data[0]);
			frame = tmp.clone();
		}
	}

	return frame;
}

