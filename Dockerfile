FROM python:3.10-slim

ENV FLIT_ROOT_INSTALL=1
ENV EDITOR=nano

COPY pyproject.toml /root/gpt-repl/pyproject.toml
COPY README.md /root/gpt-repl/README.md
COPY gpt_repl/ /root/gpt-repl/gpt_repl

WORKDIR /root/gpt-repl

RUN apt update
RUN apt install nano

RUN python3 -m pip install flit
RUN python3 -m flit install

ENTRYPOINT [ "/usr/local/bin/gpt-repl" ]