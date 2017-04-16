bwm-ng -t 200 -o csv -u bits -T rate -C ',' > $3 &
curl $1/$2.html > /dev/null
echo $?
sleep 2
pkill bwm-ng
echo "Done downloading file"
