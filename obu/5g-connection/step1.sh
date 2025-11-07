#!/bin/bash                                                                     
                                                                                
sudo mmcli --modem=any --enable                                                   
sudo mmcli -m any --simple-connect='apn=embedded-systems'                         
sudo mmcli --modem=any                                                            
sudo mmcli --modem=any --bearer=0    