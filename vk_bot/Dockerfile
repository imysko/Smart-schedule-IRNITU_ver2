FROM python:3.8

RUN mkdir -p /usr/src/vk_bot/
WORKDIR /usr/src/vk_bot/

COPY . /usr/src/vk_bot/
RUN pip install --no-cache-dir -r requirements.txt


CMD ["python3", "vk_bot.py"]