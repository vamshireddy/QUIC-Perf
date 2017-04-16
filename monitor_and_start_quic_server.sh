bwm-ng -t 100 -o csv -u bits -T rate -C ',' > $2 &
./out/Default/quic_server --quic_response_cache_dir=$1 --certificate_file=net/tools/quic/certs/out/leaf_cert.pem   --key_file=net/tools/quic/certs/out/leaf_cert.pkcs8 
echo $?
