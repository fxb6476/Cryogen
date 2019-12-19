sudo mkdir imgs
wget https://github.com/ReFirmLabs/binwalk/archive/master.zip
unzip master.zip
(cd binwalk-master && sudo python setup.py uninstall && sudo python setup.py install)
sudo ./binwalk-master/deps.sh
