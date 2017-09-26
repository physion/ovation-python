# Starting from Python 3 base image
FROM python:3

# Set the WORKDIR to /app so all following commands run in /app
WORKDIR /app

# Adding requirements files before installing requirements
COPY requirements.txt dev-requirements.txt ./

# Install requirements and dev requirements through pip. Those should include
# nostest, pytest or any other test framework you use
RUN pip install -r requirements.txt -r dev-requirements.txt

# Adding the whole repository to the image
COPY . ./
