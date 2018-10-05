#ifndef RR_COMMON_KINEMATIC_BICYCLE_MODEL_H
#define RR_COMMON_KINEMATIC_BICYCLE_MODEL_H

#include <tuple>

#include "planner_types.h"

namespace rr {

class BicycleModel {
 public:
  BicycleModel(double wheel_base, double max_lateral_accel, double distance_increment, double max_speed,
               const std::vector<double>& segment_distances);

  BicycleModel() = default;

  /*
   * RollOutPath: roll out a trajectory through the world.
   * Params:
   * control - vector with a steering value for each path segment
   */
  std::vector<PathPoint> RollOutPath(const std::vector<double>& control);

 private:
  /*
   * SteeringToSpeed: Calculate a desired speed from a steering angle based on 
   * a maximum acceptable lateral acceleration. See 
   * https://www.desmos.com/calculator/7nh83g8afj
   * Params:
   * steer_angle - proposed steering value to publish
   */
  double SteeringToSpeed(double steer_angle);

  /*
   * StepKinematics: calculate one distance-step of "simulated"
   * vehicle motion. Bicycle-model steering trig happens here.
   * Params:
   * steer_angle - steering angle in radians centered at 0
   * pose - initial (x,y,theta)
   */
  Pose StepKinematics(const Pose& pose, double steer_angle);


  double wheel_base_;
  double max_lateral_accel_;
  std::vector<double> segment_distances_;
  double distance_increment_;
  double max_speed_;
};

}  // namespace rr

#endif  // RR_COMMON_KINEMATIC_BICYCLE_MODEL_H
