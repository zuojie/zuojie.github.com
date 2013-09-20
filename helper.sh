#!/bin/sh
var=$1
var=${var//-/ } 
i=0
for v in $var
do
	((i++))
	if [ $i -eq 1 ]; then
		year=$v
	elif [ $i -eq 2 ]; then
		month=$v
	elif [ $i -eq 3 ]; then
		day=$v
	elif [ $i -eq 4 ]; then
		filen=$v
	fi
done
echo $year"/"$month"/"$day"/"$filen
echo $filen
