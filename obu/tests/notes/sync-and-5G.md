#### TODO: Check verificar na OBU de versão atualizada se os comandos correm melhor (comparação da OBU com Ubuntu 20 à advantech que te Ubuntu 22)

## Verificar sincronização temporal correta:
- ssh raspberry
- ver status do serviço ptpd
- Ctrl R e procurar por comando source (acho que é do chrony): ver valores NMEA e PPS
- exit
- ver serviço ptpd
- alterar o nome da interface 5G em ptpd.conf se necessário
- ver logs do ptpd, e ver qualquer cena de clock aquired from master ou assim... (/var/logs/ptpd.log)

## Setup 5G na OBU advantech-dt

```#Open AT terminal
minicom -D /dev/ttyUSB2

#Reset to factory settings
at&f0
at+cfun=1,1

# Disable autoconnect to avoid NoEffect error
sudo qmicli -p -d /dev/cdc-wdm0 --wds-set-autoconnect-settings=disabled

#Please let the customer check the response of the AT+QMBNCFG="AutoSel" command:
#- if it is 1, let them run AT+QMBNCFG="AutoSel",0 and reset the module
#- if it is 0, no need to change anything with this command

# Set profile to ROW_Commercial
AT+QMBNCFG="select","ROW_Commercial"

# Reset the module
AT+CFUN=1,1```
