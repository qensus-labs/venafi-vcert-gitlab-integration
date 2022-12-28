FROM python:3.9

ADD . /build
# We run 'pip install --use-feature=2020-resolver' because vcert 0.11 requires
# 'cryptography<=3.3.2' in order to maintain Python 2.7 compatibility.
# Without 'pip install --use-feature=2020-resolver', setup.py installs
# 'cryptography>3.3.2' and then aborts with an error complaining that
# 'cryptography<=3.3.2' is not satisfied.
RUN cd /build && \
    pip install -r requirements.txt --use-feature=2020-resolver && \
    python3 setup.py install && \
    cd / && \
    venafi-vcert-version && \
    rm -rf /build
