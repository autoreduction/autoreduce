from django.shortcuts import render
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.contrib.auth import logout as django_logout
from autoreduce_webapp.uows_client import UOWSClient
from autoreduce_webapp.icat_communication import ICATCommunication
from autoreduce_webapp.settings import UOWS_LOGIN_URL
from reduction_viewer.models import Experiment

def index(request):
    if request.user.is_authenticated() and request.session['sessionid'] and UOWSClient().check_session(request.session['sessionid']):
        return redirect('run_list')
    elif request.GET.get('sessionid'):
        # TODO: login user using session ID
        request.session['sessionid'] = request.GET.get('sessionid')
        if UOWSClient().check_session(request.session['sessionid']):
            return redirect('run_list')

    return redirect(UOWS_LOGIN_URL + request.build_absolute_uri('index'))

def logout(request):
    django_logout(request)
    session_id = request.session.get('session_id')
    if session_id:
        UOWSClient().logout(session_id)
    return redirect('index')

def run_queue(request):
    context_dictionary = {}
    return render_to_response('base.html', context_dictionary, RequestContext(request))

def run_list(request):
    context_dictionary = {}
    instruments = {}
    instrument_names = ICATCommunication().get_valid_instruments(requst.user.username)
    experiments = ICATCommunication().get_valid_experiments_for_instruments(requst.user.username, instrument_names)
    for instrument in instrument_names:
        instruments[instrument_name] = []
        instrument_experiments = experiments[instrument]
        for experiment in instrument_experiments:
            if Experiment.objects.filter(reference_number=experiment.name):
                instruments[instrument_name].append(experiment.name)
    
    context_dictionary['instrument_list'] = instruments

    return render_to_response('run_list.html', context_dictionary, RequestContext(request))

def run_summary(request, run_number, run_version=0):
    context_dictionary = {}
    return render_to_response('base.html', context_dictionary, RequestContext(request))

def instrument_summary(request, instrument):
    context_dictionary = {}
    return render_to_response('base.html', context_dictionary, RequestContext(request))

def experiment_summary(request, reference_number):
    context_dictionary = {}
    return render_to_response('base.html', context_dictionary, RequestContext(request))
