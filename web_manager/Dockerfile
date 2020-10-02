FROM python:3.8

RUN mkdir -p /usr/src/web_manager/
WORKDIR /usr/src/web_manager/


COPY . /usr/src/web_manager/
RUN pip install --no-cache-dir -r requirements.txt


EXPOSE 8081

RUN chmod a+x ./run.sh

CMD ["./run.sh"]