FROM ubuntu:22.04

ENV TZ=America/Chicago
ENV DEBIAN_FRONTEND=noninteractive

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt update &&  \
    apt install -y --no-install-recommends libopenjp2-7-dev \
                                              libgdk-pixbuf2.0-dev \
                                                             git \
                                                             cmake \
                                                              make \
                                                              wget \
                                                               g++ \
                                                       libjpeg-dev \
                                                  libopenjp2-7-dev \
                                                  libfreetype6-dev \
                                                  libfontconfig1-dev \
                                                      libtiff5-dev \
                                                      libomp-dev \
                                                      libopenblas-dev \
                                                      python3-watchdog \
                                                      zip \
                                                      unzip \
                                                      libgl1-mesa-glx \
                                                      ffmpeg \
                                                      libsm6

RUN apt update && \
    apt install --no-install-recommends -y build-essential gcc g++ && \
    apt-get install -y openssl && \
    apt-get install -y ca-certificates && \
	apt install --no-install-recommends -y build-essential software-properties-common &&\
	apt-get install -y  python3.9 python3-pip && \
	apt clean && \
	rm -rf /var/lib/apt/lists/*


RUN apt update -y
RUN apt install -y poppler-utils
RUN apt-get -y install libpoppler-cpp-dev

COPY . .

RUN ldconfig
RUN pip3 install --upgrade pip

RUN apt-get install -y python3-dev build-essential

RUN pip3 install --no-cache-dir -r requirements.txt


WORKDIR /

EXPOSE 9002
