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
#include <QTextCodec>
#include <QSizePolicy>
#include <QKeyEvent>
#include <QDebug>

#ifdef WIN32
#   define snprintf _snprintf
#   define TC "GBK"
#else
#   define TC "utf-8"
#endif

MainWidget::MainWidget(QWidget *parent) :
    QWidget(parent),
    ui(new Ui::MainWidget)
{
    ui->setupUi(this);

    load_image_fnames();

    ui->groupBox_subjects->setSizePolicy(QSizePolicy::Preferred, QSizePolicy::Minimum);
    ui->groupBox_regions->setSizePolicy(QSizePolicy::Preferred, QSizePolicy::Minimum);
    ui->groupBox_actions->setSizePolicy(QSizePolicy::Preferred, QSizePolicy::Minimum);
    ui->groupBox_objects->setSizePolicy(QSizePolicy::Preferred, QSizePolicy::Minimum);


#ifdef Q_OS_WIN32
#   define WHO "./cfg.d/subject.txt"
#else
#   define WHO "./cfg.d/subject.utf8.txt"
#endif

    subjects_ = load_catalogs(WHO);
    ui->groupBox_subjects->setLayout(new QVBoxLayout);
    for (size_t i = 0; i < subjects_.size(); i++) {
        QString text = QString("%1 (%2)").arg(subjects_[i].first).arg(i >= 10 ? (char)(i + 'a' - 10) : (char)(i + '0'));
        QString note(subjects_[i].second);
        QRadioButton *but = new QRadioButton(text);
        but->setProperty("title", subjects_[i].first);
        but->setToolTip(note);
        but_subjects_.push_back(but);
        ui->groupBox_subjects->layout()->addWidget(but);
        QObject::connect(but, SIGNAL(clicked()), this, SLOT(but_subject_selected()));
    }

#ifdef Q_OS_WIN32
#   define WHERE "./cfg.d/region.txt"
#else
#   define WHERE "./cfg.d/region.utf8.txt"
#endif

    regions_ = load_catalogs(WHERE);
    ui->groupBox_regions->setLayout(new QVBoxLayout);
    for (size_t i = 0; i < regions_.size(); i++) {
        QString text = QString("%1 (%2)").arg(regions_[i].first).arg(i >= 10 ? (char)(i + 'a' - 10) : (char)(i + '0'));
        QRadioButton *but = new QRadioButton(text);
        but->setProperty("title", regions_[i].first);
        but->setToolTip(regions_[i].second);
        but_regions_.push_back(but);
        ui->groupBox_regions->layout()->addWidget(but);
        QObject::connect(but, SIGNAL(clicked()), this, SLOT(but_regions_selected()));
    }

#ifdef Q_OS_WIN32
#   define WHAT "./cfg.d/action.txt"
#else
#   define WHAT "./cfg.d/action.utf8.txt"
#endif

    actions_ = load_catalogs(WHAT);
    ui->groupBox_actions->setLayout(new QVBoxLayout);
    for (size_t i = 0; i < actions_.size(); i++) {
        QString text = QString("%1 (%2)").arg(actions_[i].first).arg(i >= 10 ? (char)(i + 'a' - 10) : (char)(i + '0'));
        QRadioButton *but = new QRadioButton(text);
        but->setProperty("title", actions_[i].first);
        but->setToolTip(actions_[i].second);
        but_actions_.push_back(but);
        ui->groupBox_actions->layout()->addWidget(but);
        QObject::connect(but, SIGNAL(clicked()), this, SLOT(but_actions_selected()));
    }

#ifdef Q_OS_WIN32
#   define OBJECTS "./cfg.d/object.txt"
#else
#   define OBJECTS "./cfg.d/object.utf8.txt"
#endif

    objects_ = load_catalogs(OBJECTS);
    ui->groupBox_objects->setLayout(new QVBoxLayout);
    for (size_t i = 0; i < objects_.size(); i++) {
        QString text = QString("%1 (%2)").arg(objects_[i].first).arg(i >= 10 ? (char)(i + 'a' - 10) : (char)(i + '0'));
        QRadioButton *but = new QRadioButton(text);
        but->setToolTip(objects_[i].second);
        but->setProperty("title", objects_[i].first);
        but_objects_.push_back(but);
        ui->groupBox_objects->layout()->addWidget(but);
        QObject::connect(but, SIGNAL(clicked()), this, SLOT(but_objects_selected()));
    }

    buts_curr_ = &but_subjects_;

    QObject::connect(ui->pushButton_cancel, SIGNAL(clicked()), this, SLOT(undo()));
    QObject::connect(ui->pushButton_prev, SIGNAL(clicked()), this, SLOT(but_prev()));
    QObject::connect(ui->pushButton_confused, SIGNAL(clicked()), this, SLOT(but_confused()));
    QObject::connect(ui->pushButton_skip, SIGNAL(clicked()), this, SLOT(but_skipped()));

    enable_buts();
    show_buttons();

    QPixmap *img = next_image();
    if (img) {
        show_image(img);
        delete img;
    }

    show_info();

    qApp->installEventFilter(this);
}

MainWidget::~MainWidget()
{
    delete ui;
}

bool MainWidget::eventFilter(QObject *obj, QEvent *evt)
{
    if (evt->type() == QEvent::KeyPress) {
        if (obj == this) {
            QKeyEvent *keyevt = (QKeyEvent*)evt;
            int key = keyevt->key();

            int idx = -1;
            if (key >= Qt::Key_0 && key <= Qt::Key_9) {
                idx = key - '0';
            }
            else if (key >= Qt::Key_A && key <= Qt::Key_Z) {
                idx = key - 'A' + 10;
            }
            else if (key == Qt::Key_Escape) {
                idx = -2;
            }

            qDebug() << idx;

            if (idx >= 0 && idx < buts_curr_->size()) {
                // 模拟发出click，相当于选中类别 ..
                if (((*buts_curr_)[idx])->isEnabled()) {
                    QPointF lpos(1, 1);
                    QMouseEvent *sk = new QMouseEvent(QEvent::MouseButtonPress, lpos, Qt::LeftButton,
                                                      Qt::LeftButton, Qt::NoModifier);
                    QCoreApplication::postEvent((*buts_curr_)[idx], sk);
                    sk = new QMouseEvent(QEvent::MouseButtonRelease, lpos, Qt::LeftButton, Qt::LeftButton, Qt::NoModifier);
                    QCoreApplication::postEvent((*buts_curr_)[idx], sk);
                }
            }
            else if (idx == -2) {
                // 模拟 prev
                QPointF lpos(1, 1);
                QMouseEvent *sk = new QMouseEvent(QEvent::MouseButtonPress, lpos, Qt::LeftButton,
                                                  Qt::LeftButton, Qt::NoModifier);
                QCoreApplication::postEvent(ui->pushButton_prev, sk);
                sk = new QMouseEvent(QEvent::MouseButtonRelease, lpos, Qt::LeftButton, Qt::LeftButton, Qt::NoModifier);
                QCoreApplication::postEvent(ui->pushButton_prev, sk);
            }
        }
    }

    return QObject::eventFilter(obj, evt);
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
            if (line.count() >= 2) {
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
    else {
        // 没有了，需要清空 ...

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

    enable_buts();
    show_buttons();
}

void MainWidget::but_prev()
{
    // TODO:
    if (!object_.isEmpty()) {
        object_.clear();
    }
    else if (!action_.isEmpty()) {
        action_.clear();
    }
    else if (!region_.isEmpty()) {
        region_.clear();
    }
    else {
        subject_.clear();
    }

    show_buttons();
    enable_buts();
}

void MainWidget::but_confused()
{
    QString src_fname = img_fnames_.front();
    QString dst_fname = cataloged_fname("confused", src_fname);

    // FIXME: 应该检查目录是否存在，如果不存在，则创建 ...
    QDir curr(IMG_PATH);
    QString subdirname = "confused";
    curr.mkdir(subdirname);

    QFile::rename(src_fname, dst_fname);

    img_fnames_.pop_front();

    show_curr();
    show_info();

    enable_buts();
    show_buttons();
}

void MainWidget::all_selected()
{
    /** 将当前文件移动到 catalog 对应的子目录中.
     *  从 img_fnames_.front() 删除，保存到 undo_list_ 中，用于支持undo
     */
    QString subdirname = subject_ + '-' + region_ + '-' + action_ + '-' + object_;
    QString src_fname = img_fnames_.front();
    QString dst_fname = cataloged_filename(src_fname, subdirname);

    // FIXME: 应该检查目录是否存在，如果不存在，则创建 ...
    QDir curr(IMG_PATH);
    curr.mkdir(subdirname);

    QFile::rename(src_fname, dst_fname);

    undo_list_.push(dst_fname);
    img_fnames_.pop_front();

    show_curr();
    show_info();

    subject_.clear();
    region_.clear();
    action_.clear();
    object_.clear();
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

    enable_buts();
    show_buttons();
}

///
void MainWidget::but_subject_selected()
{
    QPushButton *but = (QPushButton*)sender();
    subject_ = but->property("title").toString();
    show_buttons();
}

void MainWidget::but_regions_selected()
{
    QPushButton *but = (QPushButton*)sender();
    region_ = but->property("title").toString();

    // NOTE: 如果 subject_ == "无人"，则自动填充 action_ = "无", object_ = "无"，并完成
    if (subject_ == subjects_[0].first) {
        action_ = actions_[0].first;    // FIXME: 要求 action.txt, object.txt 的第一行必须是“无人”的对应 ...
        object_ = objects_[0].first;
        all_selected();
    }

    show_buttons();
}

void MainWidget::but_actions_selected()
{
    QPushButton *but = (QPushButton*)sender();
    action_ = but->property("title").toString();
    show_buttons();
}

void MainWidget::but_objects_selected()
{
    QPushButton *but = (QPushButton*)sender();
    object_ = but->property("title").toString();

    all_selected();

    show_buttons();
}

void MainWidget::show_info()
{
    char buf[128];
    snprintf(buf, sizeof(buf), "剩余: %u", img_fnames_.size());
    setWindowTitle(QTextCodec::codecForName(TC)->toUnicode(buf));
}

void MainWidget::show_buttons()
{
    if (subject_.isEmpty()) {
        ui->groupBox_subjects->show();
        ui->groupBox_regions->hide();
        ui->groupBox_actions->hide();
        ui->groupBox_objects->hide();

        buts_curr_ = &but_subjects_;
    }
    else if (region_.isEmpty()) {
        ui->groupBox_subjects->hide();
        ui->groupBox_regions->show();
        ui->groupBox_actions->hide();
        ui->groupBox_objects->hide();

        buts_curr_ = &but_regions_;
    }
    else if (action_.isEmpty()) {
        ui->groupBox_subjects->hide();
        ui->groupBox_regions->hide();
        ui->groupBox_actions->show();
        ui->groupBox_objects->hide();

        buts_curr_ = &but_actions_;
    }
    else {
        ui->groupBox_subjects->hide();
        ui->groupBox_regions->hide();
        ui->groupBox_actions->hide();
        ui->groupBox_objects->show();

        buts_curr_ = &but_objects_;
    }

    enable_buts();
}

void MainWidget::enable_buts()
{
    enable_buts(but_subjects_, !img_fnames_.empty());
    ui->pushButton_cancel->setEnabled(!undo_list_.empty());
    ui->pushButton_prev->setEnabled(!subject_.isEmpty());
}
