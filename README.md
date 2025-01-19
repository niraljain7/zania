Steps to run Docker -

  - docker build -t zania .
  - docker run -d -p 8000:8000 zania


Steps to run test - 

  - cd app
  - python3 -m venv venv
  - source venv/bin/activate
  - pip install -r requirements.txt
  - python manage.py test orders
