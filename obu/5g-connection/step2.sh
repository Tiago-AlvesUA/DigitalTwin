iface="wwan0"                                                                   
                                                                                
ip=$(mmcli -b 0 | awk '/address:/{print $3}')                                   
echo "IP: $ip"                                                                  
                                                                                
prefix=$(mmcli -b 0 | awk '/prefix:/{print $3}')                                
echo "Prefix: $prefix"                                                          
                                                                                
gw=$(mmcli -b 0 | awk '/gateway:/{print $3}')                                   
echo "GW: $gw"                                                                  
                                                                                
ns=$(mmcli -b 0 | awk '/dns:/{print $3}' | sed 's/,$//')                        
echo "NS: $ns"                                                                  
                                                                                
ip link set $iface up                                                           
ip addr add $ip/$prefix dev $iface                                              
ip link set dev $iface arp off                                                  
ip link set dev $iface mtu 1500                                                 
ip route add default via $gw dev wwan0 metric 200                               
systemctl restart systemd-resolved                                              
sh -c "echo 'nameserver $ns' >> /etc/resolv.conf"  