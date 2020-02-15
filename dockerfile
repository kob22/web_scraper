FROM python:3
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENV FLASK_APP=web_scraper.py
ENV FLASK_DEBUG=True
EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0"]
