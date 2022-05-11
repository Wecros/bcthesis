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

## How to Run
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

## How to Develop New Strategies
To create new strategies, you can create any valid Python file and import the `Strategy` base class defined in strategy.py.
You can then include the created strategy inside the `simulator.py` file, where you can also define what shoudl the Plotter class plot.
There are several showcase functions inside the `simulate()` function for new devoleprs to play around with.
Finally, changing `args.yaml` may be necessarry to adjust the input variables if you plan on running the program by `make run`.
