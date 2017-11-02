FROM python:alpine
RUN mkdir /app
WORKDIR /app
ADD ./requirements /app
RUN  pip install gunicorn \
  && pip install -r requirements
ADD . /app/
ENV PORT=80
ENV IP_ADRESSS=0.0.0.0
ENV WORKERS=1
CMD gunicorn -b ${IP_ADDRESS}:${PORT} -w ${WORKERS} app:app
