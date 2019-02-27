#!/bin/bash
TEAMS=$(cat teams)
i="8"
for t in $TEAMS
do
	sed -i "s/team$i/$t/g" *.sql
	i=$(expr $i + 1)
done

