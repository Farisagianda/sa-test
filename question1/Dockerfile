FROM continuumio/miniconda3:25.3.1-1 AS base

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
       tini ca-certificates curl build-essential git pkg-config \
  && rm -rf /var/lib/apt/lists/*

ARG USER=app
ARG UID=10001
RUN useradd -m -u ${UID} -s /bin/bash ${USER}
WORKDIR /workspace

COPY requirements-py2.txt requirements-py3.txt packages-r.txt /tmp/deps/

RUN conda config --system --add channels conda-forge && \
    conda config --system --set channel_priority strict && \
    conda install -y mamba && conda clean -afy

RUN mamba create -y -n py2 python=2.7 pip && \
    mamba create -y -n py3 python=3.13 pip && \
    mamba create -y -n r-env r-base=4.4 r-essentials && \
    conda clean -afy

RUN conda run -n py2 pip install --no-cache-dir -r /tmp/deps/requirements-py2.txt && \
    conda run -n py3 pip install --no-cache-dir -r /tmp/deps/requirements-py3.txt

COPY packages-r.txt /tmp/deps/packages-r.txt
RUN set -eux; \
    CONDA_PKGS="$(awk 'NF && $1 !~ /^#/' /tmp/deps/packages-r.txt \
                  | tr '[:upper:]' '[:lower:]' \
                  | sed 's/^/r-/' \
                  | xargs)"; \
    mamba install -y -n r-env -c conda-forge ${CONDA_PKGS} && \
    conda clean -afy

RUN printf '%s\n' \
  '#!/bin/sh' \
  'exec conda run -n py2 python "$@"' > /usr/local/bin/python2 && chmod +x /usr/local/bin/python2 && \
    printf '%s\n' \
  '#!/bin/sh' \
  'exec conda run -n py3 python "$@"' > /usr/local/bin/python3 && chmod +x /usr/local/bin/python3 && \
    printf '%s\n' \
  '#!/bin/sh' \
  'exec conda run -n r-env R "$@"' > /usr/local/bin/R && chmod +x /usr/local/bin/R && \
    printf '%s\n' \
  '#!/bin/sh' \
  'exec conda run -n r-env Rscript "$@"' > /usr/local/bin/Rscript && chmod +x /usr/local/bin/Rscript

HEALTHCHECK --interval=60s --timeout=5s --start-period=30s --retries=3 \
  CMD /bin/sh -lc 'python3 -c "import sys; print(sys.version)"; Rscript -e "cat(R.version.string, \"\\n\")" >/dev/null 2>&1 || exit 1'

USER ${USER}

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["bash"]