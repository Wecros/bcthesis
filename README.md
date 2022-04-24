# Adaptive Trading Strategies for Cryptocurrencies (Adaptivní obchodní strategie pro kryptoměny)

The main text of the thesis can be found in xfilip46-thesis.pdf of the root folder.

## Installation
Multiple options are available.

Local install:
```
make installdeps
```

Virtual environment installation:
```
make create-venv
. venv/bin/activate
make installdeps
```

Containerized development:
```
make docker-build  # docker-compose build
```

## How to run
There are a few ways to run the project.

Via Makefile:
```
make run
```

With arguments:
```
python -m backtester <your_arguments>
```

Via Docker:
```
make docker-up  # docker-compose up
```
