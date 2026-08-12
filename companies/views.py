from collections import defaultdict

from django.contrib import messages
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .data import get_companies_alphabetically
from .models import WatchedCompany
from .services.report_service import CompanyReportGenerator
from .services.yfinance_service import (
    PRICE_PERIODS,
    build_candlestick_chart,
    get_company_info,
    get_price_table_rows,
    normalize_price_period,
    search_companies,
)


def _group_companies_by_letter(companies: list[dict]) -> list[tuple[str, list[dict]]]:
    groups = defaultdict(list)
    for company in companies:
        letter = company["name"][0].upper()
        groups[letter].append(company)
    return sorted(groups.items())


def search_view(request):
    query = request.GET.get("q", "").strip()
    results = search_companies(query) if query else []
    watched_tickers = set(WatchedCompany.objects.values_list("ticker", flat=True))
    catalog = get_companies_alphabetically()
    catalog_groups = _group_companies_by_letter(catalog)

    return render(request, "companies/search.html", {
        "query": query,
        "results": results,
        "watched_tickers": watched_tickers,
        "catalog_groups": catalog_groups,
        "catalog_count": len(catalog),
    })


def company_detail(request, ticker):
    ticker = ticker.upper()
    info = get_company_info(ticker)
    if not info:
        raise Http404("Nie znaleziono spółki.")

    period = normalize_price_period(request.GET.get("period"))
    chart = build_candlestick_chart(ticker, period=period)
    chart_html = chart.to_html(full_html=False, include_plotlyjs="cdn") if chart else None
    price_rows = get_price_table_rows(ticker, period=period)
    is_watched = WatchedCompany.objects.filter(ticker=ticker).exists()

    return render(request, "companies/company_detail.html", {
        "info": info,
        "chart_html": chart_html,
        "price_rows": price_rows,
        "period": period,
        "period_label": PRICE_PERIODS[period],
        "periods": PRICE_PERIODS,
        "is_watched": is_watched,
    })


def watchlist_view(request):
    companies = WatchedCompany.objects.order_by("name")
    return render(request, "companies/watchlist.html", {
        "companies": companies,
    })


@require_POST
def add_to_watchlist(request, ticker):
    ticker = ticker.upper()
    info = get_company_info(ticker)
    if not info:
        messages.error(request, f"Nie znaleziono spółki: {ticker}")
        return redirect("search")

    WatchedCompany.objects.update_or_create(
        ticker=ticker,
        defaults={
            "name": info["name"],
            "country": info["country"],
            "sector": info["sector"],
        },
    )
    messages.success(request, f"Dodano {info['name']} ({ticker}) do obserwowanych.")
    next_url = request.POST.get("next", "")
    if next_url:
        return redirect(next_url)
    return redirect("company_detail", ticker=ticker)


@require_POST
def remove_from_watchlist(request, ticker):
    ticker = ticker.upper()
    company = get_object_or_404(WatchedCompany, ticker=ticker)
    company.delete()
    messages.success(request, f"Usunięto {ticker} z obserwowanych.")

    next_url = request.POST.get("next", "")
    if next_url:
        return redirect(next_url)
    return redirect("watchlist")


def download_report(request, ticker):
    ticker = ticker.upper()
    period = normalize_price_period(request.GET.get("period"))
    generator = CompanyReportGenerator(ticker, period=period)

    try:
        doc_path, filename = generator.generate()
        with open(doc_path, "rb") as doc_file:
            content = doc_file.read()
        generator.cleanup()

        response = HttpResponse(
            content,
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response
    except ValueError as exc:
        messages.error(request, str(exc))
        return redirect(f"{reverse('company_detail', kwargs={'ticker': ticker})}?period={period}")
