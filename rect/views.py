# Create your views here.
from django.http import HttpResponse
from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets, views

from rect.serializers import *
from rect.forms import ScheduleForm
from utils.mixin_utils import LoginRequiredMixin





