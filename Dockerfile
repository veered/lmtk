FROM python:3.10-slim

ENV FLIT_ROOT_INSTALL=1
ENV EDITOR=nano

COPY pyproject.toml /root/lmtk/pyproject.toml
COPY README.md /root/lmtk/README.md
COPY lmtk/ /root/lmtk/lmtk

WORKDIR /root/lmtk

RUN apt update
RUN apt install nano

RUN python3 -m pip install flit
RUN python3 -m flit install

ENTRYPOINT [ "/usr/local/bin/lmtk" ]