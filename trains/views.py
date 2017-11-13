from django.shortcuts import render
from .forms import TrainsInfo
from .forms import TrainRoute
from .forms import LiveTrain
from .forms import PnrStatus
from django.http import  HttpResponse
from django.contrib.auth.mixins import PermissionRequiredMixin

from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.views.generic import View
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404

from .forms import UserForm

import requests
# Create your views here.
def search_sd(request):
    if request.method == "POST":
        form = TrainsInfo(request.POST)
        if form.is_valid():
            apikey = 'bahh2im9g9'

            source = request.POST.get('source')
            dest = request.POST.get('destination')
            date = request.POST.get('date')
            cl = request.POST.get('cl')
            quota  = request.POST.get('quota')

            url = 'http://api.railwayapi.com/v2/between/source/'
            url = url + source + '/dest/' + dest + '/date/' + date + '/apikey/' + apikey + '/'
            r = requests.get(url)
            trains_found = r.json()

            #seat_availability = {};
            a = []

            for t in trains_found['trains']:
                te = []
                url = 'http://api.railwayapi.com/v2/check-seat/train/'
                url = url + t['number'] + '/source/' + source + '/dest/' + dest + '/date/' + date + '/class/' + cl + '/quota/' + quota + '/apikey/' + apikey + '/'
                r = requests.get(url)
                temp = r.json()

                for i in temp['availability']:
                    te.append(i['status'])
                    te.append(t['name'])
                    te.append(t['number'])
                    a.append(te)
                    break

            #availability = {'trains':trainsName, 'number':trainsNumber, 'available':trainSeat, 'quota':quota, 'cl':cl, 'date':date}
            #trains_available = {'trains_found': trains_found['trains'], 'trains_total' : trains_found['total'], 'cl':cl, 'quota':quota }
            #a = [[0,1,2], [5,6,7]]
            availability = {'trains': a, 'cl':cl, 'quota':quota, 'date':date}

            return render(request, 'trains/display.html', availability)
    else:
        form = TrainsInfo()
    return render(request, 'trains/search_sd.html', {'form': form})


def search_train(request):
    if request.method == "POST":
        form = TrainRoute(request.POST)
        if form.is_valid():
            apikey = 'bahh2im9g9'
            train_no = request.POST.get('train_number')
            url = 'http://api.railwayapi.com/v2/route/train/'
            url = url + train_no + '/apikey/' + apikey + '/'
            r = requests.get(url)
            route_found = r.json()
            route_available = {'train_name': route_found['train'], 'train_route' : route_found['route']}
            return render(request, 'trains/display_route.html', route_available)
    else:
        form = TrainRoute()
    return render(request, 'trains/search_train.html', {'form': form})

def live_train(request):
    if request.method == "POST":
        form = LiveTrain(request.POST)
        if form.is_valid():
            apikey = 'bahh2im9g9'
            train_no = request.POST.get('train_number')
            date = request.POST.get('date')
            url = 'http://api.railwayapi.com/v2/live/train/'
            url = url + train_no + '/date/' + date + '/apikey/' + apikey + '/'
            r = requests.get(url)
            live_status = r.json()
            live_available = {'train_name': live_status['train'], 'train_route': live_status['route'],
                              'train_position': live_status['position']}
            return render(request, 'trains/display_status.html', live_available)
    else:
        form = LiveTrain()
    return render(request, 'trains/search_train.html', {'form': form})

def pnrStatus(request):
    if request.method == "POST":
        form = PnrStatus(request.POST)
        if form.is_valid():
            apikey = 'bahh2im9g9'
            pnr = request.POST.get('pnr_number')
            url = 'http://api.railwayapi.com/v2/pnr-status/pnr/'
            url = url + pnr+ '/apikey/' + apikey + '/'
            r = requests.get(url)
            pnr_status = r.json()
            live_available = {'pnr': pnr_status['pnr'], 'charting_status': pnr_status['chart_prepared'],
                              'passenger_list': pnr_status['passengers'],'doj': pnr_status['doj'],'train': pnr_status['train'],
                              'quota':pnr_status['journey_class'],'bpt' :pnr_status['boarding_point'],
                              'to':pnr_status['reservation_upto']}
            return render(request, 'trains/display_pnrStatus.html', live_available)
    else:
        form = PnrStatus()
    return render(request, 'trains/pnrStatus.html', {'form': form})

class UserFormView(View):
    form_class = UserForm
    template_name = 'trains/registration_form.html'

    #display blank form
    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form':form})

    # after submit
    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            user = form.save(commit=False)

            # clean data
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user.set_password(password)
            user.save()

            #return user objects if credentials are correct

            user = authenticate(username = username, password = password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('trains:index')
        return render(request, self.template_name, {'form':form})


def index(request):
    context = {}
    return render(request, "trains/index.html", context)

def login_view(request):
    if request.user.is_authenticated():
        return redirect('trains:index')
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('trains:index')
            else:
                 return render(request, 'trains/login.html', {'error_message': 'Your account has been disabled'})
        else:
             return render(request, 'trains/login.html', {'error_message': 'Invalid login'})
    return render(request, 'trains/login.html')


def logout_view(request):
    logout(request)
    # Redirect to a success page.
    return redirect('trains:user-login')