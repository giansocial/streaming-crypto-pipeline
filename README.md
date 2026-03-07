# Streaming Crypto Pipeline

¿Sabías que el mercado de criptomonedas opera 24/7 sin cierres de sesión y genera más de USD 80 billones en volumen anual? Un pump de 20% en Bitcoin puede ocurrir en horas, y la correlación entre activos cambia semana a semana. La mayoría de dashboards crypto muestran precios en tiempo real, pero ninguno te deja cruzar volatilidad, dominancia y detección de anomalías en un solo modelo.

Soy Gian Cruz. Construí este pipeline para consumir la API pública de CoinGecko en modo near-real-time, capturar snapshots de mercado de las 10 principales criptos, calcular retornos diarios, volatilidad rolling, dominancia de mercado, correlación entre pares y detección de pumps/dumps. Todo containerizado con Docker para correr como servicio.

## Qué hace

- Captura snapshots de mercado (precio, cap, volumen, variación 24h/7d/30d)
- Descarga historial de precios diarios (90 días por defecto)
- Calcula retornos diarios y volatilidad rolling
- Detecta pumps y dumps por umbral de retorno
- Calcula dominancia de mercado y correlación entre pares
- Calcula distancia al ATH (all-time high)
- Valida calidad de datos (completitud, precios negativos, cobertura temporal)
- Carga a SQLite con esquema dimensional (dim_coin, market_snapshot, price_history)
- Modo loop para polling continuo con intervalo configurable
- Docker para despliegue como servicio

## Instalación

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

| Fuente | Descripción | Enlace |
|--------|-------------|--------|
| CoinGecko API | API pública de datos de criptomonedas en tiempo real | [https://www.coingecko.com/en/api](https://www.coingecko.com/en/api) |
| CoinGecko - Documentación API v3 | Referencia completa de endpoints | [https://docs.coingecko.com/reference/introduction](https://docs.coingecko.com/reference/introduction) |
| CoinMarketCap | Referencia cruzada de capitalización y volumen | [https://coinmarketcap.com/](https://coinmarketcap.com/) |
