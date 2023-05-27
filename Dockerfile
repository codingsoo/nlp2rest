FROM python:3.9

COPY requirements.txt /temp/requirements.txt
RUN pip3 install --no-cache-dir -r /temp/requirements.txt

COPY . .

RUN python3 download_nltk_resources.py

EXPOSE 4000

# Define the command to run the application
CMD ["python3", "app.py"]