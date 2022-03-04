FROM python:3.6
RUN pip install flask
RUN pip install pymongo
RUN pip install datetime
COPY main.py /app/main.py
WORKDIR /app
ENV FLASK_HOST=0.0.0.0
ENV FLASK_PORT=6000
EXPOSE 6000
CMD ["python", "main.py"]