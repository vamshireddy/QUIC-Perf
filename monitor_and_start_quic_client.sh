bwm-ng -t 100 -o csv -u bits -T rate -C ',' > $2 &
./out/Default/quic_client --host=$1 --port=6121 $3 > /dev/null
echo $?
sleep 2
pkill bwm-ng
echo "Done downloading file"
