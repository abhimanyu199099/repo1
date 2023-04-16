import rospy
from std_msgs.msg import String
from sensor_msgs.msg import Imu

'''basic approach - we take imu data inputs from the sensor, of linear acceleration in x, y and z axes
and angular acceleration about them. this will be in put in a subscriber node. then, we take the data
from the subcriber node and increment the linear and angular acceleration at a constant rate.
then we publish it to the publisher.'''

''' also checked out using odom and twist packages for the same, but couldnt really get the hang of it
so i just divided the total increment by the time and my publishing rate'''

''' setup of the imu sensor'''
import os # Miscellaneous operating system interface
import zmq # Asynchronous messaging framework
import time # Time access and conversions
import sys # System-specific parameters and functions
from matrix_io.proto.malos.v1 import driver_pb2 # MATRIX Protocol Buffer driver library
from matrix_io.proto.malos.v1 import sense_pb2 # MATRIX Protocol Buffer sensor library
from multiprocessing import Process # Allow for multiple processes at once
from zmq.eventloop import ioloop # Asynchronous events through ZMQ
matrix_ip = '127.0.0.1' # Local device ip
imu_port = 20013 # Driver Base port
# Handy functions for connecting to the keep-Alive, Data Update, & Error port 
from utils import driver_keep_alive, register_data_callback, register_error_callback


def config_socket():
    # Define zmq socket
    context = zmq.Context()
    # Create a Pusher socket
    socket = context.socket(zmq.PUSH)
    # Connect Pusher to configuration socket
    socket.connect('tcp://{0}:{1}'.format(matrix_ip, imu_port))

    # Create a new driver config
    driver_config_proto = driver_pb2.DriverConfig()
    # Delay between updates in seconds
    driver_config_proto.delay_between_updates = 0.05
    # Timeout after last ping
    driver_config_proto.timeout_after_last_ping = 6.0

    # Send driver configuration through ZMQ socket
    socket.send(driver_config_proto.SerializeToString())

def imu_error_callback(error):
    # Log error
    print('{0}'.format(error))

''' taking the data inputs from the imu'''
def callback(data):
    # Extract data
    data = sense_pb2.Imu().FromString(data[0])
    # Log data 
    print('{0}'.format(data))

def listener():

    rospy.init_node('listener', anonymous=True)
    # subscriber is taking imu data inputs from the callback function
    rospy.Subscriber("this is the imu data coming in", String, callback)

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

if __name__ == '__main__':
    listener()

linacx = Imu.linear_acceleration.x
linacy = Imu.linear_acceleration.y
linacz = Imu.linear_acceleration.z

angacx = Imu.angular_acceleration.x
angacy = Imu.angular_acceleration.y
angacz = Imu.angular_acceleration.z


def talker():
    pub = rospy.Publisher('chatter', String, queue_size=50)
    rospy.init_node('talker', anonymous=True)
    rate = rospy.Rate(50) 
    while not rospy.is_shutdown():
        hello_str = "hello world %s" % rospy.get_time()

        # loop of sorts, it will increment at 50hz till we get the req values at the 10s mark
        lininc = 0.005
        anginc = 0.02

        linacx += lininc
        angacz += anginc
        
        newdata = Float64MultiArray() #imu data is published this way

        d = [[linacx, linacy, linacz], [angacx, angacy, angacz]]

        newdata.data = d

        rospy.loginfo(hello_str)
        pub.publish(hello_str)
        pub.publish(newdata)
        rate.sleep()

        # need to add code to make it stop incrementing after the 10s mark, using the clock

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
