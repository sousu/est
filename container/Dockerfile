FROM alpine:latest

ENV QDBM_VERSION=qdbm-1.8.78
ENV QDBM_URL=https://dbmx.net/qdbm/qdbm-1.8.78.tar.gz
ENV HE_VERSION=hyperestraier-1.4.13
ENV HE_URL=https://dbmx.net/hyperestraier/hyperestraier-1.4.13.tar.gz

RUN apk update && \
    apk --no-cache add curl gcc make libc-dev zlib-dev lighttpd poppler-utils \
        python3 py3-pip py3-lxml py3-pillow antiword && \
    pip install --break-system-packages --no-cache-dir python-docx openpyxl python-pptx striprtf && \
    curl -o /tmp/qdbm.tar.gz ${QDBM_URL} && \
    curl -o /tmp/hyperestraier.tar.gz ${HE_URL} && \
    tar xzf /tmp/qdbm.tar.gz -C /tmp && \
    tar xzf /tmp/hyperestraier.tar.gz -C /tmp && \
    cd /tmp/${QDBM_VERSION} && ./configure && make && make install && \
    cd /tmp/${HE_VERSION} && ./configure && make && make install && \
    rm -rf /tmp && \
    apk del curl gcc make libc-dev zlib-dev && \
    mkdir -p /htdocs /casket /target

COPY entrypoint /entrypoint
COPY estfx /usr/local/bin/estfx
RUN chmod +x /entrypoint /usr/local/bin/estfx

EXPOSE 80
ENTRYPOINT ["/entrypoint"]
