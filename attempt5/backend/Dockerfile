FROM python:3.10

RUN apt update && apt install -y ffmpeg curl

WORKDIR /app

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "fetch_and_store.py"]
