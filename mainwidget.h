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
#include <QDir>

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
    void undo();
    void but_skipped();
    void but_confused();

    void but_subject_selected();
    void but_regions_selected();
    void but_actions_selected();
    void but_objects_selected();
    void but_prev();    //

private:
    Ui::MainWidget *ui;

    /// 输入文件列表
    std::deque<QString> img_fnames_;

    /// 用于支持 undo
    std::stack<QString> undo_list_;

    QString subject_, region_, action_, object_;    // 当前选择 ..

    /// 来自配置文件的分类 ...
    std::vector<std::pair<QString, QString> > subjects_, regions_, actions_, objects_;
    std::vector<QRadioButton*> but_regions_, but_actions_, but_subjects_, but_objects_;

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

    void enable_buts();

    void show_buttons();    // 根据当前状态，显示按钮 ...

    // 显示
    void show_image(const QPixmap *img);
    void show_curr();
    void show_info();

    // 从原始名字转化为分类后的名字
    QString cataloged_filename(const QString &fname, const QString &subdir)
    {
        if (region_.isEmpty() || action_.isEmpty() || subject_.isEmpty()) {
            throw new std::exception();
        }

        int pos = fname.lastIndexOf('/');
        if (pos > 0) {
            QString fs = IMG_PATH;
            fs += '/';
            fs += subdir;
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

    void all_selected();
};

#endif // MAINWIDGET_H
