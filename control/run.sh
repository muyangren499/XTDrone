#!/bin/bash
python leader.py &
uav_num=2
while(( $uav_num<= 9 )) 
do
    python follower.py $uav_num &
    #echo $uav_num
    let "uav_num++"
done