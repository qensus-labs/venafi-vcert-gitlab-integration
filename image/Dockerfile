FROM python:3.8

ADD . /build
RUN cd /build && \
    python3 setup.py install && \
    cd / && \
    rm -rf /build
