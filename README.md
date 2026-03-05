# Streaming Crypto Pipeline

Soy Gian Cruz.

Pipeline de datos en tiempo real para el mercado de criptomonedas. Consume la API publica de CoinGecko para capturar snapshots de mercado, historial de precios y metricas de volatilidad de las 10 principales criptos por capitalizacion.

El mercado crypto opera 24/7 sin cierres de sesion, lo que genera un volumen de datos continuo ideal para practicar patrones de ingestion en streaming y near-real-time.

## Que hace

- Captura snapshots de mercado (precio, cap, volumen, variacion 24h/7d/30d)
- Descarga historial de precios diarios (90 dias por defecto)
- Calcula retornos diarios y volatilidad rolling
- Detecta pumps y dumps por umbral de retorno
- Calcula dominancia de mercado y correlacion entre pares
- Calcula distancia al ATH (all-time high)
- Valida calidad de datos (completitud, precios negativos, cobertura temporal)
- Carga a SQLite con esquema dimensional (dim_coin, market_snapshot, price_history)
- Modo loop para polling continuo con intervalo configurable
- Docker para despliegue como servicio

## Instalacion

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Uso

```bash
# Snapshot unico del mercado
python -m src.pipeline --mode snapshot

# Historial de 90 dias
python -m src.pipeline --mode history --days 90

# Snapshot + historial
python -m src.pipeline --mode full

# Polling continuo cada 60 segundos
python -m src.pipeline --mode snapshot --loop --interval 60
```

### Docker

```bash
docker-compose up -d
```

## Tests

```bash
pytest tests/ -v
```

## Stack

- Python 3.10+
- requests + pandas + numpy
- SQLite
- Docker
- pytest

## Estructura

```
streaming-crypto-pipeline/
├── src/
│   ├── config/settings.py
│   ├── extract/coingecko_client.py
│   ├── transform/
│   │   ├── cleaner.py
│   │   └── enricher.py
│   ├── quality/validators.py
│   ├── load/warehouse.py
│   ├── utils/logger.py
│   └── pipeline.py
├── tests/
│   ├── fixtures/market_sample.json
│   └── ...
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## What it does

Real-time data pipeline for the cryptocurrency market. Consumes CoinGecko public API to capture market snapshots, price history, and volatility metrics for the top 10 cryptos by market cap.

Supports continuous polling mode for near-real-time ingestion, with Docker deployment for running as a background service.

---

## Fuentes de datos

| Fuente | Descripcion | Enlace |
|--------|-------------|--------|
| CoinGecko API | API publica de datos de criptomonedas en tiempo real | [https://www.coingecko.com/en/api](https://www.coingecko.com/en/api) |
| CoinGecko - Documentacion API v3 | Referencia completa de endpoints | [https://docs.coingecko.com/reference/introduction](https://docs.coingecko.com/reference/introduction) |
| CoinMarketCap | Referencia cruzada de capitalizacion y volumen | [https://coinmarketcap.com/](https://coinmarketcap.com/) |
