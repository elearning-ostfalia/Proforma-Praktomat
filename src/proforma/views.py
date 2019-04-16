# -*- coding: utf-8 -*-
from django.views.decorators.csrf import csrf_exempt

import api_v2
import api_non_proforma



import logging


logger = logging.getLogger(__name__)


# external proforma entry point
@csrf_exempt  # disable csrf-cookie
def grade_api_v2(request):
    return api_v2.grade_api_v2(request)


@csrf_exempt  # disable csrf-cookie
def grade_api_non_proforma(request):
    return api_non_proforma.grade_api_lon_capa(request)


