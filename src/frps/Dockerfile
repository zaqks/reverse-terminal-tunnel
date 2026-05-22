FROM alpine:3.20

ARG FRP_VERSION=0.68.1

RUN apk add --no-cache wget tar

WORKDIR /app

RUN wget https://github.com/fatedier/frp/releases/download/v${FRP_VERSION}/frp_${FRP_VERSION}_linux_amd64.tar.gz \
    && tar -xzf frp_${FRP_VERSION}_linux_amd64.tar.gz \
    && mv frp_${FRP_VERSION}_linux_amd64/* . \
    && rm -rf frp_${FRP_VERSION}_linux_amd64*

EXPOSE 7860 7860

CMD ["./frps", "-c", "./frps.ini"]