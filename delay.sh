#!/bin/bash

interface=enp0s3
ip=(104.24.96.159 195.128.101.122)
delay=100ms

sudo tc qdisc add dev $interface root handle 1: prio
for i in ${ip[@]}
do
    sudo tc filter add dev $interface parent 1:0 protocol ip prio 1 u32 match ip dst $i flowid 2:1
    echo set filter for $i
done
sudo tc qdisc add dev $interface parent 1:1 handle 2: netem delay $delay