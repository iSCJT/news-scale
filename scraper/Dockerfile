FROM python:3.10

WORKDIR /scraper

COPY ./scraper/requirements.txt ./scraper/requirements.txt

RUN pip3 install --no-cache-dir --upgrade -r /scraper/requirements.txt
# ADD main.py .

# RUN pip3 install requests beautifulsoup4 transformers[torch]

COPY ./scraper/src /scraper/src

CMD ["python", "./scraper/src/main.py"]