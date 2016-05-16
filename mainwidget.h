#ifndef MAINWIDGET_H
#define MAINWIDGET_H

#include <QWidget>
#include <deque>
#include <stack>
#include <string>
#include <vector>
#include <QPixmap>
#include <sstream>
#include <QPushButton>
#include <QRadioButton>

#define IMG_PATH "./image.d"
#define CFG_PATH "./cfg.d"
#define CATALOG_FNAME CFG_PATH "/catalogs.txt"

namespace Ui {
class MainWidget;
}

class MainWidget : public QWidget
{
    Q_OBJECT

public:
    explicit MainWidget(QWidget *parent = 0);
    ~MainWidget();

private slots:
    void but_who_selected();
    void but_where_selected();
    void but_what_selected();
    void undo();
    void but_skipped();

private:
    Ui::MainWidget *ui;

    QString where_, what_, who_;    // 根据这三个构造子目录名字 ...

    /// 输入文件列表
    std::deque<QString> img_fnames_;

    /// 用于支持 undo
    std::stack<QString> undo_list_;

    /// 类别
    std::vector<std::pair<QString, QString> > catalogs_, catalogs2_;
    std::vector<QRadioButton*> but_wheres_, but_whats_, but_whos_;

    void load_image_fnames();
    std::vector<std::pair<QString, QString> > load_catalogs(const char *fname);
    virtual void paintEvent(QPaintEvent *pd);

    // 下一张照片，当前照片位于 img_fnames_.front()
    QPixmap *next_image();

    QPixmap curr_image_;    // 正在显示的图像 ...

    void enable_buts(std::vector<QRadioButton*> buts, bool enable)
    {
        for (size_t i = 0; i < buts.size(); i++) {
            buts[i]->setEnabled(enable);
            buts[i]->setAutoExclusive(false);
            buts[i]->setChecked(false);
            buts[i]->setAutoExclusive(true);
        }
    }

    // 显示
    void show_image(const QPixmap *img);
    void show_curr();
    void show_info();

    // 从原始名字转化为分类后的名字
    QString cataloged_fname(const QString &fname)
    {
        if (where_.isEmpty() || what_.isEmpty() || who_.isEmpty()) {
            throw new std::exception();
        }

        int pos = fname.lastIndexOf('/');
        if (pos > 0) {
            QString fs = IMG_PATH;
            fs += '/';
            fs += where_;
            fs += '-';
            fs += what_;
            fs += '-';
            fs += who_;
            fs += '/';
            fs += fname.right(fname.length() - pos - 1);
            return fs;
        }
        else {
            throw new std::exception();
        }
    }

    QString cataloged_fname(const QString &catalog, const QString &fname)
    {
        int pos = fname.lastIndexOf('/');
        if (pos > 0) {
            QString fs = IMG_PATH;
            fs += '/';
            fs += catalog;
            fs += '/';
            fs += fname.right(fname.length() - pos - 1);
            return fs;
        }
        else {
            throw new std::exception();
            return "";
        }
    }

    QString origin_fname(const QString &cataloged_fname)
    {
        int pos = cataloged_fname.lastIndexOf("/");
        if (pos > 0) {
            QString fs = IMG_PATH;
            fs += '/';
            QString n = cataloged_fname.right(cataloged_fname.length() - pos - 1);
            fs += n;
            return fs;
        }
        else {
            throw new std::exception();
            return "";
        }
    }
};

#endif // MAINWIDGET_H
