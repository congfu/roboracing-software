#ifndef PROJECT_RESETPANEL_H
#define PROJECT_RESETPANEL_H

#include <ros/ros.h>
#include <rviz/panel.h>
#include <QPushButton>
#include <rr_platform/race_reset.h>

/*
 * All of our panels need to be under the rr_rviz_plugins namespace.
 */
namespace rr_rviz_plugins {

class ResetPanel : public rviz::Panel {
Q_OBJECT
public:
    ResetPanel(QWidget *parent = 0);

protected:
    QPushButton *reset_btn;
    ros::NodeHandle nh;
    ros::Publisher reset_pub = nh.advertise<rr_platform::race_reset>("/reset_detected", 0);

private slots:
    void resetCallback();
};

}

#endif
