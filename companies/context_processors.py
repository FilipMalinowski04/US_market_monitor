from .models import WatchedCompany


def watchlist_count(request):
    return {"watchlist_count": WatchedCompany.objects.count()}
