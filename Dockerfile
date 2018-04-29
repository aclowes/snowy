FROM quay.io/aclowes/yawn-gke

RUN git clone https://github.com/aclowes/snowy.git
RUN pip install -r snowy/requirements.txt

