import yfinance as yf
import plotly.graph_objects as go


class CompanyNotFoundError(Exception):
    pass


PRICE_PERIODS = {
    "1mo": "1 miesiąc",
    "3mo": "3 miesiące",
    "6mo": "6 miesięcy",
    "1y": "1 rok",
    "2y": "2 lata",
    "5y": "5 lat",
}

DEFAULT_PRICE_PERIOD = "6mo"


def normalize_price_period(period: str | None) -> str:
    if period in PRICE_PERIODS:
        return period
    return DEFAULT_PRICE_PERIOD


def search_companies(query: str, max_results: int = 10) -> list[dict]:
    query = query.strip()
    if not query:
        return []

    search = yf.Search(query, max_results=max_results)
    results = []

    for quote in search.quotes:
        if quote.get("quoteType") != "EQUITY":
            continue
        results.append({
            "ticker": quote.get("symbol", ""),
            "name": quote.get("longname") or quote.get("shortname", ""),
            "exchange": quote.get("exchDisp") or quote.get("exchange", ""),
            "sector": quote.get("sector", ""),
        })

    if not results and len(query) <= 10:
        info = get_company_info(query.upper())
        if info:
            results.append({
                "ticker": info["ticker"],
                "name": info["name"],
                "exchange": info.get("exchange", ""),
                "sector": info.get("sector", ""),
            })

    return results


def get_company_info(ticker: str) -> dict | None:
    ticker = ticker.strip().upper()
    if not ticker:
        return None

    company = yf.Ticker(ticker)
    info = company.info or {}

    if not info.get("longName") and not info.get("shortName"):
        history = company.history(period="5d")
        if history.empty:
            return None

    return {
        "ticker": ticker,
        "name": info.get("longName") or info.get("shortName") or ticker,
        "country": info.get("country", "Brak danych"),
        "sector": info.get("sector", "Brak danych"),
        "exchange": info.get("exchange", "Brak danych"),
        "description": info.get("longBusinessSummary", "Brak opisu."),
    }


def get_price_history(ticker: str, period: str = DEFAULT_PRICE_PERIOD):
    data = yf.download(
        tickers=ticker,
        period=period,
        interval="1d",
        rounding=True,
        multi_level_index=False,
        progress=False,
    )
    return data


def get_price_table_rows(ticker: str, period: str = DEFAULT_PRICE_PERIOD) -> list[dict]:
    data = get_price_history(ticker, period=period)
    if data.empty:
        return []

    rows = []
    for date, row in data.iloc[::-1].iterrows():
        rows.append({
            "date": date.strftime("%d.%m.%Y"),
            "open": row["Open"],
            "high": row["High"],
            "low": row["Low"],
            "close": row["Close"],
            "volume": f"{int(row['Volume']):,}".replace(",", " "),
        })
    return rows


def build_candlestick_chart(ticker: str, period: str = DEFAULT_PRICE_PERIOD) -> go.Figure | None:
    data = get_price_history(ticker, period=period)
    if data.empty:
        return None

    chart = go.Figure()
    chart.add_trace(go.Candlestick(
        x=data.index,
        open=data["Open"],
        high=data["High"],
        low=data["Low"],
        close=data["Close"],
        name="Cena",
    ))
    chart.update_layout(
        title=f"{ticker} — wykres cen ({PRICE_PERIODS.get(period, period)})",
        yaxis_title="Cena akcji (USD)",
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return chart
