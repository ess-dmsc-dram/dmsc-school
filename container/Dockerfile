FROM jupyter/base-notebook:4d70cf8da953


USER root

# get McCode debian packages: release release 3.3
RUN  wget http://packages.mccode.org/debian/dists/stable/main/binary-amd64/mcstas-3.3-deb64.deb \
&&   wget http://packages.mccode.org/debian/dists/stable/main/binary-amd64/mcstas-comps-3.3-deb64.deb \
&&   wget http://packages.mccode.org/debian/dists/stable/main/binary-amd64/mcstas-manuals-3.3-deb64.deb \
&&   wget http://packages.mccode.org/debian/dists/stable/main/binary-amd64/mcstas-tools-matlab-mcplot-3.3-deb64.deb \
&&   wget http://packages.mccode.org/debian/dists/stable/main/binary-amd64/mcstas-tools-perl-cmdline-3.3-deb64.deb \
&&   wget http://packages.mccode.org/debian/dists/stable/main/binary-amd64/mcstas-tools-python-mccodelib-3.3-deb64.deb \
&&   wget http://packages.mccode.org/debian/dists/stable/main/binary-amd64/mcstas-tools-python-mcdisplay-pyqtgraph-3.3-deb64.deb \
&&   wget http://packages.mccode.org/debian/dists/stable/main/binary-amd64/mcstas-tools-python-mcdisplay-webgl-3.3-deb64.deb \
&&   wget http://packages.mccode.org/debian/dists/stable/main/binary-amd64/mcstas-tools-python-mcdoc-3.3-deb64.deb \
&&   wget http://packages.mccode.org/debian/dists/stable/main/binary-amd64/mcstas-tools-python-mcgui-3.3-deb64.deb \
&&   wget http://packages.mccode.org/debian/dists/stable/main/binary-amd64/mcstas-tools-python-mcplot-matplotlib-3.3-deb64.deb \
&&   wget http://packages.mccode.org/debian/dists/stable/main/binary-amd64/mcstas-tools-python-mcplot-pyqtgraph-3.3-deb64.deb \
&&   wget http://packages.mccode.org/debian/dists/stable/main/binary-amd64/mcstas-tools-python-mcrun-3.3-deb64.deb \
&&   wget http://packages.mccode.org/debian/dists/stable/main/binary-amd64/mcstas-ncrystal-3.3-deb64.deb \
&&   wget http://packages.mccode.org/debian/dists/stable/main/binary-amd64/mcstas-tools-python-mcresplot-3.3-deb64.deb \
&&   wget http://packages.mccode.org/debian/dists/stable/main/binary-amd64/mcstas-tools-python-mcdisplay-mantid-3.3-deb64.deb \
&&   wget http://packages.mccode.org/debian/dists/stable/main/binary-amd64/mcstas-mcpl-3.3-deb64.deb \
&&   apt update && apt install -y software-properties-common && add-apt-repository ppa:mozillateam/ppa \
&& echo 'Package: *' > /etc/apt/preferences.d/mozilla-firefox \
&& echo Pin: release o=LP-PPA-mozillateam >> /etc/apt/preferences.d/mozilla-firefox \
&& echo Pin-Priority: 1001 >> /etc/apt/preferences.d/mozilla-firefox \
&& apt-get install -y dbus-x11 \
   xfce4 \
   xfce4-panel \
   xfce4-session \
   xfce4-settings \
   xorg \
   xubuntu-icon-theme \
   view3dscene \
   python3-pyqt5 \
   xdg-utils \
   gedit \
   gedit-plugins \
   evince \
   gnuplot \
   octave \
   libopenmpi-dev \
   libnexus1 \
   libnexus-dev \
   git \
   firefox

# install McStas, and make sure we use the python from the system for it, and let conda-based Python modules be used from with McStas
RUN apt install -y ./*.deb && rm *.deb && ln -s /opt/conda /usr/share/mcstas/3.3/miniconda3


# Remove light-locker to prevent screen lock
RUN wget 'https://sourceforge.net/projects/turbovnc/files/2.2.5/turbovnc_2.2.5_amd64.deb/download' -O turbovnc_2.2.5_amd64.deb && \
   apt-get install -y -q ./turbovnc_2.2.5_amd64.deb && \
   apt-get remove -y -q light-locker xfce4-screensaver && \
   rm ./turbovnc_2.2.5_amd64.deb && \
   ln -s /opt/TurboVNC/bin/* /usr/local/bin/

# apt-get may result in root-owned directories/files under $HOME
RUN chown -R $NB_UID:$NB_GID $HOME

ADD . /opt/install
RUN fix-permissions /opt/install

USER $NB_USER

RUN cd /opt/install && \
   mamba env update -n base --file environment.yml && \
   mamba init

COPY McStasScript/configuration.yaml  /opt/conda/lib/python3.10/site-packages/mcstasscript/

