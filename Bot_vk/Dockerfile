FROM python:3.8

RUN mkdir -p /usr/src/Bot_vk/
WORKDIR /usr/src/Bot_vk/


COPY . /usr/src/Bot_vk/
RUN pip install --no-cache-dir -r requirements.txt




EXPOSE 8082

CMD ["python3", "test_callback.py"]