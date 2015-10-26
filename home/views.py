import json
import requests
from django.shortcuts import render, redirect

from tot import settings


def index(request):
    user = request.user
    return render(
        request,
        'home/index.html',
        {'user': user}
    )


def about(request):
    return render(request, 'home/about.html')


def find_legislator(request):
    senator = request.session.get('sen_from_address')
    representative = request.session.get('rep_from_address')

    if senator and representative:
        senator = json.loads(senator)
        representative = json.loads(representative)

    return render(
        request,
        'home/find_legislator.html',
        {'address_senator': senator, 'address_representative': representative}
    )


def get_latlon(request):
    apikey = 'placeholder'
    if request.is_ajax():
        lat = request.GET.get('lat', '')
        lon = request.GET.get('lon', '')

        api_resp = requests.get(
            settings.DOMAIN + '/api/people/?latitude={}&longitude={}&apikey={}'.format(
                lat, lon, apikey
            )
        ).json()

        if api_resp['meta']['pagination']['count'] == 2:
            for person in api_resp['data']:
                person_dict = {
                    'name': person['attributes']['name'],
                    'url': person['links']['self'],
                    'id': person['id'],
                    'image': person['attributes']['image']
                }
                if 'Senators' in person['attributes']['image']:
                    request.session['sen_from_address'] = json.dumps(person_dict)
                else:
                    request.session['rep_from_address'] = json.dumps(person_dict)
        else:
            request.session['sen_from_address'] = request.session['rep_from_address'] = json.dumps({'name': 'none found'})

    request.session.modified = True
    return redirect(find_legislator)
