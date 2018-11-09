FROM ubuntu:18.10
MAINTAINER sk1.project.org@gmail.com
 
RUN apt-get update && apt-get install -y gcc sudo libcairo2-dev liblcms2-dev libmagickwand-dev libpango1.0-dev python-dev python-cairo-dev && apt-get clean
 
CMD ["/vagrant/bbox.py"]