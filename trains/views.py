from django.shortcuts import render
from .forms import TrainsInfo
from .forms import TrainRoute
from .forms import LiveTrain
from .forms import PnrStatus
from .forms import FareEnquiry
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
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import SignupForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from dal import autocomplete
from .models import Station, Train, Route

import requests
# Create your views here.

def signup(request):
    if request.user.is_authenticated():
        return redirect('trains:index')
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            message = render_to_string('acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            mail_subject = 'Activate your blog account.'
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            #return HttpResponse('Please confirm your email address to complete the registration')
            context = {}
            return render(request, "trains/confirm.html", context)
    else:
        form = SignupForm()

    return render(request, 'signup.html', {'form': form})

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        # return redirect('home')
        context = {'msg':"Thank you for varification."}
        return render(request, "trains/valid.html", context)
    else:
        context = {'msg':"Activation link is invalid."}
        return render(request, "trains/valid.html", context)

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
    if not request.user.is_authenticated():
        return redirect('trains:user-login')
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
                #return render(request, "trains/index.html")
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


#   For autocomplete features
class StationAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):

        qs = Station.objects.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs

# Fuction for search train
def search_sd(request):
    if not request.user.is_authenticated():
        return redirect('trains:user-login')

    if request.method == "POST":
        form = TrainsInfo(request.POST)
        if form.is_valid():
            apikey = 'ie9dbl6e4e'
            source_name = request.POST.get('source')
            source = Station.objects.filter(pk=source_name).values('code').first()['code']
            dest_name = request.POST.get('destination')
            dest = Station.objects.filter(pk=dest_name).values('code').first()['code']
            date = request.POST.get('date_day')+'-'+request.POST.get('date_month')+'-'+request.POST.get('date_year')
            cl = request.POST.get('cl')
            quota  = request.POST.get('quota')

            url = 'http://api.railwayapi.com/v2/between/source/'
            url = url + source + '/dest/' + dest + '/date/' + date + '/apikey/' + apikey + '/'
            print (url);


            # Requesting API for trains between stations
            r = requests.get(url)

            print(r)
            if r.status_code != 200:
                return "There was a problem: {} !".format(r.text)
            else :
                trains_found = r.json()
                print(trains_found)

            #seat_availability = {};
            a = []
            num_trains = 0
            for t in trains_found['trains']:
                if Train.objects.filter(number = t['number']).count() == 0:
                    obj = Train(name = t['name'], number = t['number'])
                    obj.save()
                    url2 = 'http://api.railwayapi.com/v2/route/train/' + t['number'] + '/apikey/' + apikey + '/'
                    r2 = requests.get(url2)

                    temp2 = r2.json()
                    print (temp2)

                    tid = Train.objects.filter(number=t['number'])[0].id
                    tid = get_object_or_404(Train, pk=tid)
                    sn = 1;
                    for i in temp2['route']:
                        sid = Station.objects.filter(code=i['station']['code'])
                        if sid.count() == 0:
                            continue
                        sid = Station.objects.filter(code=i['station']['code'])[0].id
                        sid = get_object_or_404(Station, pk=sid)
                        #sno = i['no']
                        sno = sn;
                        obj = Route(tid = tid, sid = sid, serial_no = sno)
                        obj.save()
                        sn = sn + 1;

                url = 'http://api.railwayapi.com/v2/check-seat/train/'
                url = url + t['number'] + '/source/' + source + '/dest/' + dest + '/date/' + date + '/class/' + cl + '/quota/' + quota + '/apikey/' + apikey + '/'
                r = requests.get(url)
                #print(r + 'error line no 196')

                temp = r.json()
                print(url)

                te = []
                te.append(t['name'])
                te.append(t['number'])
                #print(temp)
                for i in temp['availability']:
                    te.append(i['status'])
                    break
                if len(te) == 2:
                    te.append("NA")

                tid_this = Train.objects.filter(number = t['number'])[0].id
                sid_this = Station.objects.filter(code = source)[0].id
                src = Route.objects.filter(tid=tid_this, sid=sid_this)
                if len(src) == 0:
                    continue
                source_sn_no = src[0].serial_no;
                start = max(1, source_sn_no - 5)

                sn_code_5 = []
                sn_name_5 = []
                sn_code_string = ""
                sn_name_string = ""
                for x in range (start, source_sn_no):
                    sn_code_5.append((Route.objects.filter(tid = tid_this, serial_no = x)[0].sid).code)
                    sn_name_5.append((Route.objects.filter(tid = tid_this, serial_no = x)[0].sid).name)
                te.append(len(sn_code_5))

                for x in sn_code_5:
                    sn_code_string = sn_code_string + x + ','
                for x in sn_name_5:
                    sn_name_string = sn_name_string + x + ','

                te.append(sn_code_5)
                te.append(sn_code_string)
                te.append(sn_name_string)

                a.append(te)
                num_trains = num_trains + 1

            source_name = Station.objects.filter(code=source)[0].name
            #availability = {'trains':trainsName, 'number':trainsNumber, 'available':trainSeat, 'quota':quota, 'cl':cl, 'date':date}
            #trains_available = {'trains_found': trains_found['trains'], 'trains_total' : trains_found['total'], 'cl':cl, 'quota':quota }
            #a = [[0,1,2], [5,6,7]]
            availability = {'trains': a, 'cl':cl, 'quota':quota, 'date':date, 'dest' :dest ,'src':source, 'src_name':source_name, 'num_trains':num_trains, 'api':apikey}

            return render(request, 'trains/display.html', availability)
    else:
        form = TrainsInfo()
    return render(request, 'trains/search_sd.html', {'form': form})


# For train route search
def search_train(request):
    if not request.user.is_authenticated():
        return redirect('trains:user-login')
    if request.method == "POST":
        form = TrainRoute(request.POST)
        if form.is_valid():
            apikey = 'ie9dbl6e4e'
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

#   For live train search feature
def live_train(request):
    if not request.user.is_authenticated():
        return redirect('trains:user-login')
    if request.method == "POST":
        form = LiveTrain(request.POST)
        if form.is_valid():
            apikey = 'ie9dbl6e4e'
            train_no = request.POST.get('train_number')
            date = request.POST.get('date_day') + '-' + request.POST.get('date_month') + '-' + request.POST.get(
                'date_year')
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

def fareEnquiry(request):
    if not request.user.is_authenticated():
        return redirect('trains:user-login')
    if request.method == "POST":
        form = FareEnquiry(request.POST)
        if form.is_valid():
            apikey = 'ie9dbl6e4e'

            train_number = request.POST.get('train_number')
            source = request.POST.get('source')
            dest = request.POST.get('destination')
            date = request.POST.get('date_day') + '-' + request.POST.get('date_month') + '-' + request.POST.get(
                'date_year')
            cl = request.POST.get('cl')
            quota  = request.POST.get('quota')
            age = 18

            url = 'http://api.railwayapi.com/v2/fare/tarin/'
            url = url + train_number+'/source/'+ source + '/dest/' + dest +'/age/'+age+'/quota/'+quota+ '/date/' + date + '/apikey/' + apikey + '/'
            r = requests.get(url)
            fare_search = r.json()

            trDetail = fare_search['train']
            frm = fare_search['from_station']
            to  = fare_search['to_station']
            quota  = fare_search['quota']
            te = []
            for i in fare_search['fare']:
                te.append(i['code'])
                te.append(i['name'])
                te.append(i['fare'])

            enquiry = {'from':frm,'to':to,'train_detail':trDetail,'fare': te, 'cl':cl, 'quota':quota, 'date':date}

            return render(request, 'trains/display_fareEnquiry.html', enquiry)
    else:
        form = FareEnquiry()
    return render(request, 'trains/search_sd.html', {'form': form})


def pnrStatus(request):
    if not request.user.is_authenticated():
        return redirect('trains:user-login')
    if request.method == "POST":
        form = PnrStatus(request.POST)
        if form.is_valid():
            apikey = 'ie9dbl6e4e'
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
