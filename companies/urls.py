from django.urls import path

from . import views

urlpatterns = [
    path("", views.search_view, name="search"),
    path("watchlist/", views.watchlist_view, name="watchlist"),
    path("company/<str:ticker>/", views.company_detail, name="company_detail"),
    path("company/<str:ticker>/watch/", views.add_to_watchlist, name="add_to_watchlist"),
    path("company/<str:ticker>/unwatch/", views.remove_from_watchlist, name="remove_from_watchlist"),
    path("company/<str:ticker>/report/", views.download_report, name="download_report"),
]
