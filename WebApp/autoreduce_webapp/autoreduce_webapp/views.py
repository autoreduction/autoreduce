# ############################################################################### #
# Autoreduction Repository : https://github.com/ISISScientificComputing/autoreduce
#
# Copyright &copy; 2019 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""
Handle page responses for WebApp
"""
import os
import sys
from django.shortcuts import render_to_response
from django.template import RequestContext
# pylint: disable=no-member

from utils.project.structure import get_project_root
sys.path.append(os.path.join(get_project_root(), 'WebApp', 'autoreduce_webapp'))

from reduction_viewer.models import Setting


def get_admin_email():
    """Check the settings for a valid admin email"""
    try:
        admin_email = Setting.objects.get(name='admin_email')
        return admin_email.value
    # pylint: disable=bare-except
    except:
        return ''


def handler400(request, exception):
    """Error 400 handler"""
    response = render_to_response('400.html',
                                  {'admin_email': get_admin_email()},
                                  RequestContext(request))
    response.status_code = 400
    return response


def handler404(request, exception):
    """Error 404 handler"""
    response = render_to_response('404.html',
                                  {'admin_email': get_admin_email()},
                                  RequestContext(request))
    response.status_code = 404
    return response


def handler403(request, exception):
    """Error 403 handler"""
    response = render_to_response('403.html',
                                  {'admin_email': get_admin_email()},
                                  RequestContext(request))
    response.status_code = 403
    return response


def handler500(request):
    """Error 500 handler"""
    response = render_to_response('500.html',
                                  {'admin_email': get_admin_email()},
                                  RequestContext(request))
    response.status_code = 500
    return response
