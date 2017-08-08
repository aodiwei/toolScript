#!/bin/sh
echo '**********starting install rely libs ***********'
yum groupinstall 'Development Tools'
yum install zlib-devel bzip2-devel openssl-devel ncurese-devel
echo '**********starting install python3***********'
wget https://www.python.org/ftp/python/3.5.3/Python-3.5.3.tar.xz
tar Jxvf Python-3.5.3.tar.xz
cd Python-3.5.3
./configure --prefix=/usr/local/python3
make && make install
ln -s /usr/local/python3/bin/python3.5 /usr/bin/python3
ln -s /usr/local/python3/bin/pip3 /usr/bin/pip3
yum install ncurses-devel 
pip3 install readline
cd ..
echo '**********starting install htop***********'
wget http://dl.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-10.noarch.rpm
rpm -ihv epel-release-7-10.noarch.rpm
yum install htop