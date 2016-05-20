#include "mainwidget.h"
#include "ui_mainwidget.h"
#include <stdio.h>
#include <QDir>
#include <sstream>
#include <QString>
#include <QFile>
#include <QIODevice>
#include <QTextStream>
#include <QPushButton>
#include <QRadioButton>
#include <QPainter>
#include <algorithm>
#include <assert.h>

#ifdef WIN32
#   define snprintf _snprintf
#endif

MainWidget::MainWidget(QWidget *parent) :
    QWidget(parent),
    ui(new Ui::MainWidget)
{
    ui->setupUi(this);

    load_image_fnames();

    QObject::connect(ui->button_undo, SIGNAL(clicked(void)), this, SLOT(undo()));

#ifdef Q_OS_WIN32
#   define WHERE "./cfg.d/where.txt"
#else
#   define WHERE "./cfg.d/where.utf8.txt"
#endif

    catalogs_ = load_catalogs(WHERE);
    for (size_t i = 0; i < catalogs_.size(); i++) {
        QString title(catalogs_[i].first), note(catalogs_[i].second);
        QRadioButton *but = new QRadioButton(title);
        but->setToolTip(note);
        ui->verticalLayout_where->addWidget(but);
        but_wheres_.push_back(but);
        QObject::connect(but, SIGNAL(clicked(void)), this, SLOT(but_where_selected(void)));
    }

#ifdef Q_OS_WIN32
#   define WHAT "./cfg.d/what.txt"
#else
#   define WHAT "./cfg.d/what.utf8.txt"
#endif

    catalogs2_ = load_catalogs(WHAT);
    for (size_t i = 0; i < catalogs2_.size(); i++) {
        QString title(catalogs2_[i].first), note(catalogs2_[i].second);
        QRadioButton *but = new QRadioButton(title);
        but->setToolTip(note);
        ui->verticalLayout_what->addWidget(but);
        but_whats_.push_back(but);

        QObject::connect(but, SIGNAL(clicked(void)), this, SLOT(but_what_selected()));
    }

#ifdef Q_OS_WIN32
#   define WHO "./cfg.d/who.txt"
#else
#   define WHO "./cfg.d/who.utf8.txt"
#endif

    std::vector<std::pair<QString, QString> > catalogs3 = load_catalogs(WHO);
    for (size_t i = 0; i < catalogs3.size(); i++) {
        QString title(catalogs3[i].first), note(catalogs3[i].second);
        QRadioButton *but = new QRadioButton(title);
        but->setToolTip(note);
        ui->verticalLayout_who->addWidget(but);
        but_whos_.push_back(but);

        QObject::connect(but, SIGNAL(clicked(void)), this, SLOT(but_who_selected(void)));
    }

    enable_buts(but_wheres_, true);
    enable_buts(but_whats_, false);
    enable_buts(but_whos_, false);

    ui->button_undo->setEnabled(false);

    QObject::connect(ui->pushButton_skip, SIGNAL(clicked()), this, SLOT(but_skipped()));

    QPixmap *img = next_image();
    if (img) {
        show_image(img);
        delete img;
    }

    show_info();
}

MainWidget::~MainWidget()
{
    delete ui;
}

void MainWidget::paintEvent(QPaintEvent *pd)
{
    if (!curr_image_.isNull()) {
        QPainter p(this);
        QImage img = curr_image_.toImage();
        p.drawImage(ui->widget_show->rect(), img);
    }
}

std::vector<std::pair<QString, QString> > MainWidget::load_catalogs(const char *fname)
{
    std::vector<std::pair<QString, QString> > catalogs;

    QFile file(fname);
    if (file.open(QIODevice::ReadOnly | QIODevice::Text)) {
        QTextStream ts(&file);

        while (!ts.atEnd()) {
            QString line = ts.readLine().simplified();
            if (line.count() > 2) {
                QString catalog = line;
                QString note;
                int pos = line.indexOf(':');    // 后面作为注释 ...
                if (pos > 0) {
                    catalog = line.left(pos);
                    note = line.right(line.length() - pos);
                }

                catalogs.push_back(std::pair<QString, QString>(catalog, note));
            }
        }

        file.close();
    }

    return catalogs;
}

void MainWidget::load_image_fnames()
{
    QDir dir(IMG_PATH);
    QStringList filters;
    filters << "*.jpg" << "*.JPG" << "*.png" << "*.PNG";
    dir.setNameFilters(filters);

    QStringList list = dir.entryList();
    QStringList::const_iterator it;
    for (it = list.begin(); it != list.end(); ++it) {
        QString fname = IMG_PATH;
        fname += '/';
        fname += *it;

        img_fnames_.push_back(fname);
    }

    std::random_shuffle(img_fnames_.begin(), img_fnames_.end());

    fprintf(stderr, "%lu images fname loaded!\n", img_fnames_.size());
}

void MainWidget::show_image(const QPixmap *img)
{
    curr_image_ = *img;
    ui->widget_show->update();
}

QPixmap *MainWidget::next_image()
{
    while (!img_fnames_.empty()) {
        QString fname = img_fnames_.front();
        QPixmap *img = new QPixmap(fname);
        if (img->isNull()) {
            fprintf(stderr, "WRN: '%s' can't load!\n", fname.toLocal8Bit().constData());
            img_fnames_.pop_front();
            continue;
        }

        return img;
    }

    fprintf(stderr, "INFO: NO more images!\n");
    return 0;
}

void MainWidget::show_curr()
{
    QPixmap *img = next_image();
    if (img) {
        show_image(img);
        delete img;
    }
}

void MainWidget::but_skipped()
{
    QString src_fname = img_fnames_.front();
    QString dst_fname = cataloged_fname("skipped", src_fname);

    // FIXME: 应该检查目录是否存在，如果不存在，则创建 ...
    QDir curr(IMG_PATH);
    QString subdirname = "skipped";
    curr.mkdir(subdirname);

    QFile::rename(src_fname, dst_fname);

    img_fnames_.pop_front();

    show_curr();
    show_info();

    enable_buts(but_wheres_, true);
    enable_buts(but_whats_, false);
    enable_buts(but_whos_, false);
}

void MainWidget::but_where_selected()
{
    QRadioButton *but = (QRadioButton*)sender();
    where_ = but->text();
    enable_buts(but_whats_, true);

    ui->button_undo->setEnabled(false);
}

void MainWidget::but_what_selected()
{
    QRadioButton *but = (QRadioButton*)sender();
    what_ = but->text();

    /** FIXME: 如果what_为“集体xxx”，则自动选择 who_ 为多人，然后下一张.
     *         如果 what_ 为“无”，则自动选择 who_ 为“无人”，然后下一张 .
     */
    if (what_.indexOf("集体") == 0) {
        who_ = "多人";
        all_selected();
        return;
    }

    if (what_.indexOf("无人") == 0) {
        who_ = "无人";
        all_selected();
        return;
    }

    enable_buts(but_whos_, true);

    ui->button_undo->setEnabled(false);
}

void MainWidget::all_selected()
{
    {
        /** 将当前文件移动到 catalog 对应的子目录中.
         *  从 img_fnames_.front() 删除，保存到 undo_list_ 中，用于支持undo
         */
        QString src_fname = img_fnames_.front();
        QString dst_fname = cataloged_fname(src_fname);

        // FIXME: 应该检查目录是否存在，如果不存在，则创建 ...
        QDir curr(IMG_PATH);
        QString subdirname = where_ + '-' + what_ + '-' + who_;
        curr.mkdir(subdirname);

        QFile::rename(src_fname, dst_fname);

        undo_list_.push(dst_fname);
        img_fnames_.pop_front();

        show_curr();
        show_info();

        enable_buts(but_wheres_, true);
        enable_buts(but_whats_, false);
        enable_buts(but_whos_, false);

        ui->button_undo->setEnabled(true);
    }
}

void MainWidget::but_who_selected()
{
    if (img_fnames_.empty()) {
        return; // TODO: 应该禁用按钮 ...
    }

    QRadioButton *but = (QRadioButton*)sender();
    who_ = but->text();

    all_selected();
}

void MainWidget::undo()
{
    if (undo_list_.empty()) {
        return;
    }

    QString src_fname = undo_list_.top();
    QString dst_fname = origin_fname(src_fname);
    QFile::rename(src_fname, dst_fname);

    undo_list_.pop();
    img_fnames_.push_front(dst_fname);

    show_curr();
    show_info();
}

void MainWidget::show_info()
{
    char buf[128];
    snprintf(buf, sizeof(buf), "剩余: %u", img_fnames_.size());
    setWindowTitle(buf);
}
