#ifndef CATKIN_WS_STARTLIGHTPANEL_H
#define CATKIN_WS_STARTLIGHTPANEL_H

#include <ros/ros.h>
#include <rr_msgs/race_reset.h>
#include <rviz/panel.h>
#include <QPushButton>
#include <QVBoxLayout>
#include <QtWidgets/QLabel>
#include <std_msgs/Bool.h>
#include <QtGui/QPaintEvent>

namespace rr_rviz_plugins {

    class StartlightPanel : public rviz::Panel {
    Q_OBJECT
    public:
        explicit StartlightPanel(QWidget *parent = nullptr);

    protected:
        ros::NodeHandle nh;
        ros::Subscriber start_detector;

    private slots:
        static void startlightCallback(std_msgs::Bool msg);
        void paintEvent(QPaintEvent *e) override;
    };

}  // namespace rr_rviz_plugins

#endif //CATKIN_WS_STARTLIGHTPANEL_H