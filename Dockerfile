FROM python:3.10
LABEL maintainer="Debabrata Bhattacharya"

COPY /techtrends /app
WORKDIR /app
RUN python -m pip install -r requirements.txt
RUN python init_db.py
EXPOSE 3111

# command to run on container start
CMD ["python", "app.py"]
