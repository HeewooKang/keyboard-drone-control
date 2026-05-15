# keyboard-drone-control

Keyboard-based drone control simulation using ROS 2, MAVROS, PX4 SITL, and Gazebo.

This project controls a PX4 Iris drone in Gazebo using keyboard inputs through ROS 2 and MAVROS.

---

## Project Overview

This project implements a keyboard-based drone control pipeline for a simulated PX4 Iris drone.

The keyboard controller publishes velocity commands to MAVROS, and MAVROS sends those commands to PX4 in OFFBOARD mode.  
PX4 then controls the Iris drone inside Gazebo.

---

## Tech Stack

- Python
- ROS 2 Humble
- MAVROS
- PX4 SITL
- Gazebo
- pygame

---

## Control Pipeline

```text
Keyboard Input
      ↓
Python Keyboard Controller
      ↓
/mavros/setpoint_velocity/cmd_vel
      ↓
MAVROS
      ↓
PX4 OFFBOARD Mode
      ↓
Gazebo Iris Drone
```

---

## How to Run

The overall execution order is:

1. Start PX4 SITL with Gazebo
2. Start MAVROS
3. Set MAVROS velocity coordinate frame
4. Run the Python keyboard controller
5. Switch PX4 to OFFBOARD mode
6. Arm the drone
7. Check local position feedback

---

## Terminal 1: Start Gazebo Iris Drone

```bash
cd ~/PX4-Autopilot
make px4_sitl gazebo
```

This command starts PX4 SITL and launches the Gazebo Iris drone simulation.

---

## Terminal 2: Start MAVROS

```bash
source /opt/ros/humble/setup.bash
ros2 launch mavros px4.launch fcu_url:=udp://:14540@127.0.0.1:14557
```

MAVROS connects ROS 2 and PX4 through UDP communication.

---

## Terminal 3: Set Coordinate Frame

```bash
source /opt/ros/humble/setup.bash
ros2 param set /mavros/setpoint_velocity mav_frame BODY_NED
```

This sets the MAVROS velocity command frame to `BODY_NED`.

In `BODY_NED` mode, velocity commands are interpreted based on the drone's body direction.

---

## Terminal 4: Run Python Keyboard Controller

```bash
cd ~/Desktop/study/keyboard_drone
python3 keyboard_drone.py
```

This runs the keyboard control Python script.

The script publishes velocity commands to:

```bash
/mavros/setpoint_velocity/cmd_vel
```

Message type:

```bash
geometry_msgs/msg/TwistStamped
```

---

## Terminal 5: Set PX4 OFFBOARD Mode and Arm

```bash
source /opt/ros/humble/setup.bash
ros2 service call /mavros/set_mode mavros_msgs/srv/SetMode "{custom_mode: 'OFFBOARD'}"
ros2 service call /mavros/cmd/arming mavros_msgs/srv/CommandBool "{value: true}"
```

OFFBOARD mode allows PX4 to receive external control commands from ROS 2.

The drone must be armed after switching to OFFBOARD mode.

---

## Terminal 6: Check Drone Position

```bash
source /opt/ros/humble/setup.bash
ros2 topic echo /mavros/local_position/pose
```

This command prints the current local position and orientation of the drone.

---

## Full Execution Summary

The commands below summarize the execution flow. Some commands must be executed in separate terminals.

```bash
# 1. Start Gazebo Iris Drone
cd ~/PX4-Autopilot
make px4_sitl gazebo

# 2. Start MAVROS
source /opt/ros/humble/setup.bash
ros2 launch mavros px4.launch fcu_url:=udp://:14540@127.0.0.1:14557

# 3. Set coordinate frame
source /opt/ros/humble/setup.bash
ros2 param set /mavros/setpoint_velocity mav_frame BODY_NED

# 4. Run Python keyboard controller
cd ~/Desktop/study/keyboard_drone
python3 keyboard_drone.py

# 5. Set PX4 OFFBOARD mode
source /opt/ros/humble/setup.bash
ros2 service call /mavros/set_mode mavros_msgs/srv/SetMode "{custom_mode: 'OFFBOARD'}"

# 6. Arm the drone
ros2 service call /mavros/cmd/arming mavros_msgs/srv/CommandBool "{value: true}"

# 7. Check local position
ros2 topic echo /mavros/local_position/pose
```

---

## Notes

- PX4 and Gazebo must be running before starting MAVROS.
- The Python keyboard controller should be running before switching to OFFBOARD mode.
- The drone will not move unless PX4 is in OFFBOARD mode and armed.
- The coordinate frame is set to `BODY_NED`, so movement commands are based on the drone's body direction.

---

## Future Improvements

- Add smoother acceleration and deceleration
- Add position feedback control
- Add waypoint following
- Add autonomous path tracking
- Integrate with A* path planning
