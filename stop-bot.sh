#!/bin/bash
PID=`cat bot.pid` || PID="-1"
if [ $PID -gt 0 ]
then
	echo "Found process with PID $PID"
	sudo kill $PID
	sleep 10
	if ps -p $PID > /dev/null
	then
		echo "Killing process $PID failed..."
	else
		echo "Process $PID killed successfully, removing bot.pid file..."
		sudo rm bot.pid
	fi
fi
