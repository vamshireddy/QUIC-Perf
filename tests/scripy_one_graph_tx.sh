export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
python util/plot_rate.py --tx \
        --title $3 \
        --legend 'QUIC' 'TCP'\
        --maxy $4 \
        --xlabel 'Time (s)' \
        --ylabel 'Throughput (Mbps)' \
        -i 'h.*-eth0' \
        -f $1\
        -o $2
