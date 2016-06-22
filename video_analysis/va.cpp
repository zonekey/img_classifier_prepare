#include "KVConfig.h"
#include "imga.h"
#include "video_source.h"
#include <iostream>
#include <stdio.h>
#include <vector>
#include <string>
#include <utility>
#include <signal.h>
#include <sstream>

#ifdef USE_OPENCV
typedef struct 
{
	double timestamp;
	std::vector<Prediction> predictions;
} frameinfo; 

void print_info(frameinfo finf, int n)
{
	std::string s;
	for (int i = 0; i < n; i++) {
		std::ostringstream oss;
		oss << finf.predictions[i].first 
			<< " " << finf.predictions[i].second;

		s += oss.str() + " ";
	}
	std::ostringstream oos;
	oos << finf.timestamp;
	std::cout << "BF: " << oos.str() << " " 
		<< s << std::endl;
}

bool is_quit = false;

void sighandler(int signo)
{
	is_quit = true;
	signal(SIGINT, SIG_DFL);
}

int main(int args, char **argv)
{
	if (args == 1 || strncmp(argv[1], "-help", 5) == 0) {
		fprintf(stdout, "usage: %s url ftp", argv[0]);
		exit(0);
	}
 	::google::InitGoogleLogging(argv[0]);
	signal(SIGINT, sighandler);
	std::string deploy = "../models/deploy.prototxt";
	std::string model = "../models/caffenet.caffemodel";
	std::string mean = "../models/mean.binaryproto";
	std::string labels = "../models/labels.txt";
	Classifier imgc = Classifier(deploy, model, mean, labels);
   	FFmpegVideoSource fvs;
	fvs.open(argv[1]);
	int a_time = atoi(argv[2]);
	int tm = 0;
	
	while (!is_quit) {
		double stamp;
		bool eof;
		frameinfo finfo;		
		cv::Mat  img = fvs.next_frame(stamp, eof);
		if (img.rows > 0 && img.cols > 0) {
			if (stamp >= tm) {
				finfo.timestamp = stamp;	
				finfo.predictions = imgc.Classify(img, 3);	
				print_info(finfo, 3);
				tm = tm + a_time;
			}
		}
		else
			is_quit = true;
	}
	fvs.close();
	return 0;
}
#endif
