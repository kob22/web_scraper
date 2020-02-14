FROM python:3
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENV FLASK_APP web_scrapper.py
CMD flask run
