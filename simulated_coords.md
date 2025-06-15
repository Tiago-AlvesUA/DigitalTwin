### How to add simulated coordinates to a machine on IT

- First, create a csv with coordinates of the trajectory wanted in My Maps (Google);

- Some changes must be done to the .csv file. Each coordinate point must be on a new line; A comma is needed to separate lat and lon; Latitude must come first and longitude second.

- Configurate /etc/it2s/gnss.toml to "simulate".

- Copy this file to the repo folder "it2s-itss-management/simulations" and change its name to input.csv.
(scp trajeto.csv it2s-admin@192.168.94.86:~
scp trajeto.csv it2s-admin@192.168.94.47:~/it2s-itss-management/simulations)

- In the same folder run Rscript ./interpolate.R

- Finally copy the generated interpolated.csv file to /var/lib/it2s.
(sudo mv interpolated.csv /var/lib/it2s/)

sudo systemctl restart it2s-gnssd
sudo it2s-itss restart