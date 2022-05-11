FROM python:3.9

WORKDIR /backtester

COPY args.yaml .
COPY backtester backtester
COPY data data
COPY output output
COPY requirements*.txt .
COPY Makefile .

RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /backtester

CMD ["bash"]
