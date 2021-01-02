from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from crawler.models import Site, Crawl


@csrf_exempt
def site(request, site_id):
    site_obj = Site.objects.get(id=site_id)
    return JsonResponse(data={
        'content': site_obj.content.content,
        'url': site_obj.url,
    }, status=200)


def crawl(request, crawl_id):
    data = []
    for parent in Crawl.objects.get(id=crawl_id).site_set.filter(parent=None):
        data.append({
            'link': parent.url,
            'id': parent.id,
            'data': get_data(parent)
        })

    return JsonResponse(data={
        'data': data
    }, status=200)


def get_data(site_obj):
    data = []

    for site_ in site_obj.site_set.all():
        data.append({
            'link': site_.url,
            'id': site_.id,
            'data': get_data(site_)
        })

    return data
