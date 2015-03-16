FROM centos:6

MAINTAINER lee youngchan <y2y0c4@gmail.com>

#install packages
RUN yum -y update
RUN yum -y groupinstall "Development Tools"
RUN yum -y install gcc
RUN yum -y install java-1.7.0-openjdk java-1.7.0-openjdk-devel
RUN yum -y install wget
RUN yum -y install net-tools nfs-utils openssl-devel
RUN yum -y install abrt abrt-*

#setting MariaDB.repo
RUN echo "[mariadb]">> /etc/yum.repos.d/MariaDB.repo&&echo "name=MariaDB" >> /etc/yum.repos.d/MariaDB.repo &&echo "baseurl=http://yum.mariadb.org/10.0/centos6-amd64" >> /etc/yum.repos.d/MariaDB.repo &&echo "gpgkey=https://yum.mariadb.org/RPM-GPG-KEY-MariaDB" >> /etc/yum.repos.d/MariaDB.repo &&echo "gpgcheck=1" >> /etc/yum.repos.d/MariaDB.repo 

RUN yum -y install MariaDB-server MariaDB-client
RUN mkdir /gradeserver
RUN yum -y install tar

#install python2.7. &pip
RUN wget https://www.python.org/ftp/python/2.7.9/Python-2.7.9.tgz && tar xvfz Python-2.7.9.tgz && ./Python-2.7.9/configure && make && make altinstall && mv /usr/bin/python /usr/bin/python_old && cp /usr/local/bin/python2.7 /usr/bin/python
RUN wget http://pypi.python.org/packages/2.7/s/setuptools/setuptools-0.6c11-py2.7.egg
RUN sh setuptools-0.6c11-py2.7.egg
RUN /usr/local/bin/easy_install pip

#etc
RUN pip install Celery
RUN pip install redis
RUN mysql -uroot -h192.168.0.122 -prhflwma GradeServer_DB
RUN pip install sqlalchemy
RUN /usr/local/bin/easy_install mysql-connector-python

RUN cp /usr/bin/yum /usr/bin/yum_old && sed -i 's/\/usr\/bin\/python/\/usr\/bin\/python2.6/g' /usr/bin/yum
RUN wget https://www.python.org/ftp/python/3.4.2/Python-3.4.2.tgz && tar xvfz Python-3.4.2.tgz 
RUN cd Python-3.4.2; ./configure ; make ; make install
# RUN make 
# RUN make install

#add program

#etc
ADD route_CFunction.tar.gz /root/
RUN cd /root/route_CFunction; python setup.py build; python setup.py install

ADD gradeprogram_01.tar.gz /

ADD aaa.py /



