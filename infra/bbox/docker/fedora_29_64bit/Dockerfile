FROM fedora:29
MAINTAINER sk1.project.org@gmail.com

RUN yum -y update && yum clean all
RUN yum -y install gcc rpmdevtools cairo-devel lcms2-devel ImageMagick-devel pango-devel python2-devel python2-cairo-devel && yum clean all
 
CMD ["/vagrant/bbox.py"]