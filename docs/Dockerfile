FROM python:3.6-slim AS builder

WORKDIR /src
ADD . /src

RUN pip install --no-cache-dir sphinx==1.8.5 \
  && sphinx-build -b html . _build


FROM nginx:mainline-alpine

COPY --from=builder /src/_build /usr/share/nginx/html
