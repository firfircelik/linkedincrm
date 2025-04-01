from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseBadRequest
import json
from .models import Campaign, Profile, Account, Excel_file, PromptManagement, Linkedin_user,ScrapperProxy, UserMetricsDistribution, SavedSearch, LeadsList, Experience
import pandas as pd
import numpy as np
from django.contrib.auth.views import LoginView
from django.utils import timezone
from .forms import LoginForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, get_user_model
from django.contrib import messages
from django.utils.datastructures import MultiValueDictKeyError
from urllib import parse as urlparse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
import plotly.graph_objects as go
from plotly.offline import plot
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.db.models import Count, Prefetch
from django.core.paginator import Paginator
from .forms import AccountProxyForm
import csv
from django.http import HttpResponse
from django.db.models import Sum
from django.db import transaction
from django.db.models import Q
from django.db.models import F
from simple_search import search_filter
from datetime import datetime, timedelta
import io
from .serializers import CampaignSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from utils.download_statistics import calculate_account_data
from django.contrib.auth import authenticate, login
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from django.db.models import OuterRef, Subquery
from django.middleware.csrf import get_token
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from simple_search import search_filter

def transform_json(input_json):
            first_names = input_json.get('FirstName', [])
            last_names = input_json.get('LastName', [])
            urls = input_json.get('ProfileLink', [])
            locations = input_json.get('Location', [''])[0]  # Assuming we take the first location
            job_titles = input_json.get('TagLineTitle', [''])[0]  # Assuming we take the first job title
            company = []

            # Concatenating names if they are in lists
            names = [' '.join(pair) for pair in zip(first_names, last_names)]

            # Creating the new JSON structure
            output_json = {
                'urls': urls,
                'names': names,
                'company': company,
                'profile_location': locations,
                'jobtitle': job_titles
            }

            return output_json

def is_superuser(user):
    return user.is_superuser


class UserLoginView(LoginView):
    template_name = 'login.html'
    form_class = LoginForm
    success_url = 'Home'  
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('Home')
        return super().get(request, *args, **kwargs) 
    
# REST API FOR LOGIN
class UserLoginAPIView(APIView):
    authentication_classes = []  # Exempt from CSRF token validation

    def post(self, request, format=None):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({
                'status': 400,
                'message': 'Both username and password are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)

        if user is not None:
            return Response({
                'status': 200,
                'message': 'Successfully logged in.',
                'user_id': user.id,
                'is_superuser': user.is_superuser
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 403,
                'message': 'Email or Password is Incorrect.'
            }, status=status.HTTP_403_FORBIDDEN)
   
@login_required    
def logout_view(request):
    logout(request)
    return redirect('login')


def convert(data):
    # Check for NaN values for various types (e.g., float, np.float64)
    if (isinstance(data, (float, np.float64)) and np.isnan(data)):
        return None

    # Recursive conversion for dictionaries
    elif isinstance(data, dict):
        return {convert(key): convert(value) for key, value in data.items()}

    # Recursive conversion for lists
    elif isinstance(data, list):
        return [convert(element) for element in data]

    # Return the data as-is for other types
    else:
        return data
    

# Create your views here.
@login_required 
def index(request):

    return render(
        request,
        "base.html"
    )

@login_required 
@user_passes_test(is_superuser, login_url='/')
def pipeline(request):
    # Get query parameters for filtering
    selected_campaign = request.GET.get('campaign')
    selected_status = request.GET.get('status')
    number_retrieved = request.GET.get('number_retrieved', '') == 'on'
    selected_name_link = request.GET.get('name_link', '')

    # Fetch profiles with optional filtering
    profiles = Profile.objects.all()
    if selected_campaign:
        profiles = profiles.filter(campaign__id=selected_campaign)
    if selected_status:
        profiles = profiles.filter(status=selected_status)
    if number_retrieved:
        profiles = profiles.exclude(contact_number='').exclude(contact_number=None)
    if selected_name_link is not None and selected_name_link != "":
    # if selected_name_link:
        profiles = profiles.filter(
            Q(name__icontains=selected_name_link) |
            Q(link__icontains=selected_name_link))


    profiles = profiles.order_by('-id')
    # Get all campaigns and statuses for the dropdown
    campaigns = Campaign.objects.all()
    statuses = Profile.objects.values_list('status', flat=True).distinct()
    # pagination
    profiles_per_page = 10 
    paginator = Paginator(profiles, profiles_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "pipeline.html", {
        'campaigns': campaigns,
        'statuses': statuses,
        'selected_campaign': selected_campaign,
        'selected_status': selected_status,
        'page_obj': page_obj,
        'number_retrieved': number_retrieved,

    })

@login_required 
@user_passes_test(is_superuser, login_url='/')
def pending_campaigns(request):
    data = Excel_file.objects.filter(created_at__isnull=True).order_by('-id')

    return render(
        request,
        "pending_campaigns.html", {'json_files': data}
    )

@login_required 
@user_passes_test(is_superuser, login_url='/')
def campaign(request):
    status_filter = request.GET.get('status', '')

    # Start with all campaigns and apply status filter if present
    if status_filter:
        if status_filter == 'completed':
            campaigns_query = Campaign.objects.filter(status='finished')  # Adjust 'finished' to your completed status
        elif status_filter == 'pending':
            campaigns_query = Campaign.objects.exclude(status='finished')
    else:
        campaigns_query = Campaign.objects.all()
    campaigns_query = campaigns_query.exclude(boolean_search__isnull=False)
    #campaigns_query = campaigns_query.exclude(name='Marisol S NB LION')
    campaigns_query = campaigns_query.order_by('-id')

    # campaigns = Campaign.objects.all().order_by('-id')
    paginator = Paginator(campaigns_query, 10)  # Show 10 campaigns per page
    page_number = request.GET.get('page')
    campaigns = paginator.get_page(page_number)

    # Looping through each campaign
    campaigns = Campaign.objects.all().exclude(boolean_search__isnull=False).order_by('-id').prefetch_related(
    Prefetch('profile_set'), 
    Prefetch('excel_file_set')
)

    for campaign in campaigns:
        # Use prefetched data instead of querying each time
        profiles = list(campaign.profile_set.all())
        total_profiles = len(profiles)
        approached_profiles = sum(1 for p in profiles if p.status != 'Excluded')
        accepted_profiles = sum(1 for p in profiles if p.status == 'Accepted')
        excluded_profiles = sum(1 for p in profiles if p.status == 'Excluded')

        if not campaign.total_profile_count:
            total_urls = 0
            # Using prefetched excel_files
            for excel_file in campaign.excel_file_set.all():
                try:
                    json_data = json.loads(excel_file.json_data)
                    if 'urls' in json_data and isinstance(json_data['urls'], list):
                        total_urls += len(json_data['urls'])
                except json.JSONDecodeError:
                    continue
            campaign.total_profile_count = total_urls

        campaign.connects_sent = approached_profiles
        campaign.connect_accepted = accepted_profiles
        campaign.excluded_profiles = excluded_profiles

        # Only calculate percentage if there's a change to avoid unnecessary calculations
        if total_profiles and campaign.total_profile_count:
            if total_profiles > 0 and campaign.total_profile_count > 0:
                campaign.campaign_completion_percentage = round((total_profiles / campaign.total_profile_count) * 100, 2)
            if campaign.total_profile_count == total_profiles:
                campaign.status = "finished"

        # Save changes if there are any
        campaign.save()


    # page_obj = paginator.get_page(page_number)

    return render(
        request,
        "campaign.html", {'page_obj': campaigns}
    )

# Analysis page
@login_required 
@user_passes_test(is_superuser, login_url='/')
def analysis(request):
    names = []
    total_requests = []
    accepted_requests = []
    excluded_requests = []
    phone_number_count = []
    campaigns = Campaign.objects.exclude(category = "lion").order_by('-id')
    # Looping through each campaign
    for campaign in campaigns:
        names.append(campaign.name)
        # Counting total profiles associated with the current campaign
        total_profiles = Profile.objects.filter(campaign=campaign).exclude(status='Excluded').count()

        # Counting profiles where status is Accepted for the current campaign
        accepted_profiles = Profile.objects.filter(campaign=campaign, status='Accepted').count()
        # Counting profiles where status is Accepted for the current campaign
        excluded_profiles = Profile.objects.filter(campaign=campaign, status='Excluded').count()

        # Assigning the counts to the fields
        campaign.connects_sent = total_profiles
        campaign.connect_accepted = accepted_profiles
        campaign.excluded_profiles = excluded_profiles

        total_requests.append(total_profiles)
        accepted_requests.append(accepted_profiles)
        excluded_requests.append(excluded_profiles)

        # For Analysis 
        if total_profiles == 0 and excluded_profiles== 0 :
            accepted_percentage = excluded_profiles_percentage = None
            campaign.accepted_percentage = accepted_percentage
            campaign.excluded_profiles_percentage = excluded_profiles_percentage
        elif total_profiles== 0:
            excluded_profiles_percentage = excluded_profiles/(total_profiles+ excluded_profiles)
            accepted_percentage = None
            campaign.excluded_profiles_percentage = round(excluded_profiles_percentage*100, 2)
            campaign.accepted_percentage = accepted_percentage

        else:
            accepted_percentage = accepted_profiles / total_profiles
            excluded_profiles_percentage = excluded_profiles/(total_profiles+ excluded_profiles)
            campaign.accepted_percentage = round(accepted_percentage*100, 2)
            campaign.excluded_profiles_percentage = round(excluded_profiles_percentage*100, 2)

        total_contacts = total_profiles
        phone_numbers = Profile.objects.filter(campaign=campaign).exclude(contact_number__isnull=True).count()
        phone_number_count.append(phone_numbers)
        if total_contacts!=0:
            phone_number_percentage = phone_numbers/total_contacts
            campaign.phone_number_percentage = round(phone_number_percentage * 100, 2)
        else: 
            phone_number_percentage = None
            campaign.phone_number_percentage = phone_number_percentage


        # Saving the campaign object
        campaign.save()

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=names,
        y=total_requests,
        name='Sent Requests',
        text=total_requests,
        textposition='outside',
        marker_color='rgb(55, 83, 109)',
        hovertemplate='<i>Campaign</i>: %{x}<br>' +
                    '<b>Sent Requests</b>: %{y}<br>'
    ))

    fig.add_trace(go.Bar(
        x=names,
        y=accepted_requests,
        name='Accepted Requests',
        text=accepted_requests,
        textposition='outside',
        marker_color='rgb(39, 116, 174)',
        hovertemplate='<i>Campaign</i>: %{x}<br>' +
                    '<b>Accepted Requests</b>: %{y}<br>'
    ))

    fig.add_trace(go.Bar(
    x=names,
    y=excluded_requests,
    name='Excluded Requests',
    text=excluded_requests,
    textposition='outside',
    marker_color='rgb(102, 178, 255)',
    hovertemplate='<i>Campaign</i>: %{x}<br>' +
                '<b>Excluded Requests</b>: %{y}<br>'
    ))
    fig.add_trace(go.Bar(
    x=names,
    y=phone_number_count,
    name='Phone Numbers',
    text=phone_number_count,
    textposition='outside',
    marker_color='rgb(115, 216, 230)',
    hovertemplate='<i>Campaign</i>: %{x}<br>' +
                '<b>Contact Extracted Requests</b>: %{y}<br>'
    ))

    
    fig.update_layout(
        title_text='Campaign Analysis Overview',
        title_x=0.5,
        xaxis_title="Campaigns",
        yaxis_title="Counts",
        autosize=True,
        margin=dict(l=50, r=50, b=100, t=100, pad=4),
        plot_bgcolor='white',
        showlegend=True,
        barmode='group',
        yaxis=dict(
            showgrid=True,
            gridcolor='LightGray',
        ),
    )
    plot_div = plot(fig, output_type='div')

    return render(
        request,
        "analysis.html", {'campaign': campaigns, 'plot_div': plot_div}, 
    )


@login_required
def new_campaign(request):
    accounts = Account.objects.all().distinct()
    saved_searches = None
    linkedin_user = Linkedin_user.objects.filter(user_id=request.user)
    if linkedin_user:
        linkedin_user = linkedin_user.first()
        saved_searches = SavedSearch.objects.filter(linkedinuser=linkedin_user)
        lead_lists = LeadsList.objects.filter(linkedinuser=linkedin_user)
    leads = Excel_file.objects.filter(campaign__isnull=True, created_at__isnull = False).order_by('-id')
    leads_formatted = []

    for excel_file in leads:
        if excel_file.json_data is None:
            continue
        try:
            json_data =  json.loads(excel_file.json_data)

        except json.JSONDecodeError:
            continue
        except AttributeError:
            continue
        except ObjectDoesNotExist:
            continue
        if json_data.get('urls'):
            profile_link_count = len(json_data.get('urls', []))
        else:
            profile_link_count = len(json_data.get('ProfileLink', []))

        leads_formatted.append({
            "id": excel_file.id,
            "profile_link_count": profile_link_count,
            "created_at": excel_file.created_at.strftime('%b %d, %Y %H:%M:%S'),
            "name": excel_file.name
        })
    


    if request.method == 'POST':
        # Extract form data from the request
        default_value = None
        category_type = request.POST.get('category_type', default_value)
        campaign_name = request.POST.get('campaign_name', default_value)
        start_date = request.POST.get('startDateTime', default_value)
        end_date = request.POST.get('endDateTime', default_value)
        daily_count = request.POST.get('daily_count', default_value)
        job_title = request.POST.get('jobtitle', default_value)
        category = request.POST.get('category', default_value)
        search_value = request.POST.get('searchValue', default_value)

        location = request.POST.get('location', default_value)
        account_id = request.POST.get('account_id', default_value)

        lead_id = request.POST.get('lead_id', default_value)
        selected_account = None
        if account_id:
            selected_account = Account.objects.get(pk=account_id)
        excel_file = None
        

        try:
            excel_file = request.FILES['listFile']
        except MultiValueDictKeyError:
            pass



        
        if excel_file:
            try:
                data_xls = pd.read_csv(excel_file)
                urls_list = data_xls['ProfileLink'].tolist()
                profile_location = data_xls['Location'].tolist()
                jobtitle = data_xls['TagLineTitle'].tolist()
                first_name_list = data_xls['FirstName'].tolist()
                second_name_list = data_xls['LastName'].tolist()
                names = [f"{first} {second}" for first, second in zip(first_name_list, second_name_list)]

                # Validation Logic
                if all(pd.isna(urls_list)) or all(pd.isna(first_name_list)) or all(pd.isna(second_name_list)):
                    messages.error(request, "Error: URLs list, first name list, and second name list cannot be empty.")
                    return render(request, 'new_campaign.html', {'accounts': accounts})
                
                elif not urls_list or not first_name_list or not second_name_list:
                    messages.error(request, "Error: URLs list, first name list, and second name list cannot be empty.")
                    return render(request, 'new_campaign.html', {'accounts': accounts})
                
                elif not any(profile_location) and not any(jobtitle):
                    messages.error(request, "Error: At least one of company profile location or job title must not be empty.")
                    return render(request, 'new_campaign.html', {'accounts': accounts})
                elif all(pd.isna(profile_location)) and all(pd.isna(jobtitle)):
                    messages.error(request, "Error: At least one of company profile location or job title must not be empty.")
                    return render(request, 'new_campaign.html', {'accounts': accounts})

                data_dict = json.dumps({'urls': urls_list, 'names': names, 'profile_location': profile_location, 'jobtitle': jobtitle})
            except Exception as e:
                print(f"Error reading the Excel file: {e}")
                messages.error(request, f"Error reading the Excel file: {e}")
                return render(request, 'new_campaign.html', {'accounts': accounts, 'leads':leads_formatted })

    


        # Create a new Campaign object and save it to the database
        if category_type == 'New':
           
            campaign = Campaign.objects.create(
                name=campaign_name,
                location=location,
                start_date=start_date,
                end_date=end_date,
                daily_count=daily_count,
                job_title=job_title,
                account = selected_account,
                category=category,
                search_value=search_value
            )
            if excel_file:
                
                excel = Excel_file(campaign=campaign, json_data=data_dict)
                excel.save()
        elif lead_id and category_type=='Existing':
         
            campaign = Campaign.objects.create(
            name=campaign_name,
            location=location,
            start_date=start_date,
            end_date=end_date,
            daily_count=daily_count,
            job_title=job_title,
            account = selected_account,
            category=category,
            search_value=search_value
        )
            
            excel_file = Excel_file.objects.get(id=lead_id)
            if not excel_file.duplicate:
                data_to_transform = excel_file.json_data
                transformed_data = transform_json(data_to_transform)
                excel_file.json_data = json.dumps(transformed_data, indent=4)
                excel_file.campaign = campaign
                excel_file.save()
            else:
                existing_dict = excel_file.json_data
                Excel_file.objects.create(json_data=existing_dict, campaign=campaign)



        if category_type=='AutoScrapper':
            # category_type = request.POST.get('category_type')
            campaign_name = request.POST.get('campaign_name', '')
            boolean_search = ''
            leads_list_obj = None
            saved_search_obj = None

            acategory = request.POST.get('acategory')
            if acategory == "leads_list":
                lead_list = request.POST.get('lead_list', '')
                if lead_lists and lead_list:
                    leads_list_obj = LeadsList.objects.get(id=lead_list)
            else:
                boolean_search = request.POST.get('booleanSearch', '')
                saved_search = request.POST.get('saved_search', '')
                if saved_searches and saved_search:
                    saved_search_obj = SavedSearch.objects.get(id=saved_search)


            start_date = request.POST.get('startDateTime', '')
            end_date = request.POST.get('endDateTime', '')
            minpage = int(request.POST.get('minpage', '1'))
            maxpage = int(request.POST.get('maxpage', '100'))
            minExperience = request.POST.get('minExperience', '')
            maxExperience = request.POST.get('maxExperience', '')
            min_age = request.POST.get('minAge', '')
            max_age = request.POST.get('maxAge', '')
            min_salary = request.POST.get('minSalary', '')
            max_salary = request.POST.get('maxSalary', '')
            batch_size = request.POST.get('batchSize', '')
            gender = request.POST.get('gender', '')
            gpt_prompt = request.POST.get('gpt_prompt', '')

            # Extracting the 'currentCompany' field from the POST data and converting it into a list
            includeNationality_list = request.POST.get('includeNationality', '').split(',')
            
            # Remove any empty strings in case the input was not filled
            includeNationality_list = [includeNationality.strip() for includeNationality in includeNationality_list if includeNationality.strip()]

            # Extracting the 'currentCompany' field from the POST data and converting it into a list
            excludeNationality_list = request.POST.get('excludeNationality', '').split(',')
            
            # Remove any empty strings in case the input was not filled
            excludeNationality_list = [excludeNationality.strip() for excludeNationality in excludeNationality_list if excludeNationality.strip()]

            local = request.POST.get('local', False)  
            expat = request.POST.get('expat', False)  
            if local:
                local = True
            if expat:
                expat = True

            
            

            campaign = Campaign.objects.create(
                name=campaign_name,
                boolean_search=boolean_search,
                start_date=start_date,
                end_date=end_date,
                min_age=min_age,
                max_age=max_age,
                min_experience=minExperience,
                max_experience=maxExperience,
                min_salary=min_salary,
                max_salary=max_salary,
                batch_size=batch_size,
                include_nationality_list=includeNationality_list,
                exclude_nationality_list=excludeNationality_list,
                local=local,
                expat=expat,
                autoscrapper=True,
                saved_search=saved_search_obj,
                lead_list=leads_list_obj,
                minpage=minpage,
                maxpage=maxpage,
                gender=gender,
                gpt_prompt=gpt_prompt
            )
                            
        return redirect('new_campaign')
    return render(request, 'new_campaign.html', {'accounts': accounts,  'leads':leads_formatted, "saved_searches": saved_searches, "lead_lists": lead_lists})


def map_excel_to_template(excel_df):
   
    names_split = excel_df['names'].str.split(' ', n=1, expand=True)
    excel_df['First Name'] = names_split[0]
    excel_df['Second Name'] = names_split[1].fillna('')  # Fill NaN with empty strings
    
    # Map columns from excel_df to the template format
    mapped_df = pd.DataFrame({
        'ProfileLink': excel_df['urls'],
        'FirstName': excel_df['First Name'],
        'LastName': excel_df['Second Name'],
        'Email' : '',
        'Phone' : '',
        'Twitter' : '',
        'Messenger' : '',
        'TagLineTitle': excel_df['jobtitle'],
        'Location': excel_df['profile_location'],
    })
    
    return mapped_df



@login_required 
def setting(request):
    linkedin_user = Linkedin_user.objects.filter(user_id=request.user).first()
    scrapper_proxy = ScrapperProxy.objects.filter(user_id=request.user).first()
    leads = Excel_file.objects.filter(campaign__isnull=True, created_at__isnull = False).order_by('-id')
    leads_formatted = []

    for excel_file in leads:
        if excel_file.json_data is None:
            continue
        try:
            json_data =  json.loads(excel_file.json_data)

        except json.JSONDecodeError:
            continue
        except AttributeError:
            continue
        except ObjectDoesNotExist:
            continue
        if json_data.get('urls'):
            profile_link_count = len(json_data.get('urls', []))
        else:
            profile_link_count = len(json_data.get('ProfileLink', []))

        leads_formatted.append({
            "id": excel_file.id,
            "profile_link_count": profile_link_count,
            "created_at": excel_file.created_at.strftime('%b %d, %Y %H:%M:%S'),
            "name": excel_file.name
        })

    if request.method == "POST":
        excel_file = None
        lead_id = request.POST.get('lead_id', None)
        if lead_id:
            excel_file_instance = Excel_file.objects.get(id=lead_id)
            json_data = excel_file_instance.json_data

            # Ensure json_data is in a correct format
            if isinstance(json_data, str):
                # If json_data is a string, parse it to a Python object
                json_data = json.loads(json_data)
            filename = excel_file_instance.name
             
            # Convert the JSON data to a pandas DataFrame
            df = pd.DataFrame(json_data)
            
            # Here, we assume you adjust df to match the campaign template format
            # For this example, let's just pass df directly assuming it represents the Excel file's content
            # In real usage, you'd call map_excel_to_template here
            mapped_df = map_excel_to_template(df)  # Adjust the function call as necessary
            
            # Create a BytesIO buffer to save the Excel file in memory
            buffer = io.BytesIO()
            
            # Use the Excel writer and save the file to the buffer
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                mapped_df.to_excel(writer, index=False)
            
            # Go to the beginning of the stream
            buffer.seek(0)
            
            # Create a response, setting the content type to 'application/vnd.ms-excel'
            # This will prompt the browser to download the file
            response = HttpResponse(buffer.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            
            # Set the content disposition to 'attachment' with a filename
            response['Content-Disposition'] = f'attachment; filename="{filename}.xlsx"'
            
            return response

        try:
            excel_file = request.FILES['listFile']
        except MultiValueDictKeyError:
            pass
        # if 'data-linkedin-id' in request.POST:
        if request.POST.get('linkedin-id'):
            linkedin_id = int(request.POST.get('linkedin-id'))
            Linkedin_user.objects.filter(id=linkedin_id).delete()
            scrapper_id = int(request.POST.get('scrapper-id'))
            ScrapperProxy.objects.filter(id=scrapper_id).delete()
            return redirect('Setting')
        if request.POST.get('cookies'):
        # Extract data from the POST request
            name = request.POST.get('name')
            cookies = request.POST.get('cookies')
            proxyip = request.POST.get('proxyip')
            proxyport = request.POST.get('proxyport')
            proxyuser = request.POST.get('proxyuser')
            proxypass = request.POST.get('proxypass')

            # Data validation (just a basic example, consider using Django Forms for more comprehensive validation)
            if not all([name, cookies, proxyip, proxyport, proxyuser, proxypass]):
                return HttpResponseBadRequest("All fields are required")

            # Create the Account object
            account = Account(
                name=name,
                cookies=cookies,
                proxyip=proxyip,
                proxyport=proxyport,
                proxyuser=proxyuser,
                proxypass=proxypass
            )

            # Save the object to the database
            account.save()
        elif request.POST.get("file_name") and excel_file:
            file_name = request.POST.get("file_name")
            try:
                data_xls = pd.read_csv(excel_file)
                urls_list = data_xls['ProfileLink'].tolist()
                profile_location = data_xls['Location'].tolist()
                jobtitle = data_xls['TagLineTitle'].tolist()
                first_name_list = data_xls['FirstName'].tolist()
                second_name_list = data_xls['LastName'].tolist()
                names = [f"{first} {second}" for first, second in zip(first_name_list, second_name_list)]

                # Validation Logic
                if all(pd.isna(urls_list)) or all(pd.isna(first_name_list)) or all(pd.isna(second_name_list)):
                    messages.error(request, "Error: URLs list, first name list, and second name list cannot be empty.")
                    return render(request, 'new_campaign.html', {'accounts': accounts})
                
                elif not urls_list or not first_name_list or not second_name_list:
                    messages.error(request, "Error: URLs list, first name list, and second name list cannot be empty.")
                    return render(request, 'new_campaign.html', {'accounts': accounts})
                
                elif not any(profile_location) and not any(jobtitle):
                    messages.error(request, "Error: At least one of company profile location or job title must not be empty.")
                    return render(request, 'new_campaign.html', {'accounts': accounts})
                elif all(pd.isna(profile_location)) and all(pd.isna(jobtitle)):
                    messages.error(request, "Error: At least one of company profile location or job title must not be empty.")
                    return render(request, 'new_campaign.html', {'accounts': accounts})

                data_dict = json.dumps({'urls': urls_list, 'names': names, 'profile_location': profile_location, 'jobtitle': jobtitle})
                Excel_file.objects.create(json_data = data_dict, name=file_name, duplicate=True)
            except Exception as e:
                print(f"Error reading the Excel file: {e}")
                messages.error(request, f"Error reading the Excel file: {e}")
                return render(request, 'setting.html', {'linkedin_user':linkedin_user })



        else:
            email = request.POST.get('email')
            password = request.POST.get('password')
            cookies = request.POST.get('linkedin_cookies')
            scrapper_ip = request.POST.get('scrapper_ip')
            scrapper_port = request.POST.get('scrapper_port')
            scrapper_user = request.POST.get('scrapper_user')
            scrapper_pass = request.POST.get('scrapper_pass')

            if not all([email, cookies, scrapper_ip, scrapper_pass, scrapper_port, scrapper_user]):
                return HttpResponseBadRequest("All Details are required")
            if Linkedin_user.objects.filter(user_id=request.user):
                return HttpResponseBadRequest("Linkedin account already exist")
            linkedin_user = Linkedin_user(
                email = email,
                password = password,
                cookies = cookies,
                user_id = request.user
            )
            scrapper_proxy = ScrapperProxy(
                proxyip= scrapper_ip,
                proxyport= scrapper_port,
                proxyuser = scrapper_user,
                proxypass= scrapper_pass,
                user_id = request.user
            )
            # Save the objects to the database
            linkedin_user.save()
            scrapper_proxy.save()
        
       # Return a success response
        return redirect('Setting')
    return render(request, 'setting.html', {'linkedin_user':linkedin_user ,'scrapper_details': scrapper_proxy,  'leads':leads_formatted},)



@login_required 
@user_passes_test(is_superuser, login_url='/')
def accounts(request):
    if request.method == "POST":
        restrict_view = request.POST.get("restrict_view")
        account_id = request.POST.get("account_id")
        if restrict_view and account_id: 
            account = Account.objects.get(id=account_id)
            account.restrict_view = restrict_view
            account.save()
            current_url = request.get_full_path()
            url_params = urlparse.urlparse(current_url).query
            return redirect(f'/accounts/?{url_params}')
        data = json.loads(request.body)
        action = data.get('action')
        if action == 'delete':
            account_id = data.get('account_id')
            if account_id:
                try:
                    # Begin a transaction
                    with transaction.atomic():
                        # Delete associated campaigns and user metrics distributions
                        Campaign.objects.filter(account_id=account_id).delete()
                        UserMetricsDistribution.objects.filter(account_id=account_id).delete()
                        
                        # Now, delete the account
                        account = Account.objects.get(id=account_id)
                        account.delete()
                        return JsonResponse({'success': True, 'message': 'Account and related data deleted successfully'})
                except Account.DoesNotExist:
                    return JsonResponse({'success': False, 'message': 'Account does not exist'})
                except Exception as e:
                    # Handle unexpected errors
                    return JsonResponse({'success': False, 'message': f'An error occurred: {str(e)}'})

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            data = json.loads(request.body)
            call_id = data.get('id')
            row_data = data.get('rowData')
            
            field = data.get('field')
            value = data.get('value').strip()
            
            call = Account.objects.get(id=call_id)

            for field, value in row_data.items():
                value = value.strip()
                setattr(call, field, value)

            call.save()
            return JsonResponse({"success": True})  # Consider returning JSON response for AJAX
     
    accounts = Account.objects.all().order_by("-id") 

    return render(request, 'accounts.html', {'accounts': accounts})

@login_required 
@user_passes_test(is_superuser, login_url='/')
def prompt_management(request):
    if request.method == "POST":
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            data = json.loads(request.body)
            call_id = data.get('id')
            row_data = data.get('rowData')
            
            field = data.get('field')
            value = data.get('value').strip()
            


            call = PromptManagement.objects.get(id=call_id)

            for field, value in row_data.items():
                value = value.strip()
                setattr(call, field, value)

            call.save()
            return JsonResponse({"success": True})  # Consider returning JSON response for AJAX
        else:
            value = request.POST['value']
            prompt = request.POST['prompt']
           
            PromptManagement.objects.create(
                value = value.strip(),
                prompt=prompt.strip() )
            current_url = request.get_full_path()
            url_params = urlparse.urlparse(current_url).query
            return redirect(f'/prompt_management/?{url_params}')
        
       
        
    prompts_data = PromptManagement.objects.all().order_by("-id") 

   
    return render(request, 'prompt_management.html', {"prompts_data": prompts_data})

# Account Details
@login_required 
@user_passes_test(is_superuser, login_url='/')
def account_details(request, account_id):
    stats_data = {}
    account_name = Account.objects.filter(id=account_id).values_list('name', flat=True)
    campaigns_with_profile_count = Campaign.objects.filter(
    account_id=account_id
    ).annotate(
        profile_count=Count('profile')
    ).values(
        'id', 'name', 'profile_count', 'start_date', 'end_date', 'status',
    )

    # Extract the campaign IDs from the QuerySet
    campaign_ids = [campaign['id'] for campaign in campaigns_with_profile_count]
    # Use the campaign IDs to filter profiles
    all_profiles = Profile.objects.filter(campaign_id__in=campaign_ids)
    total_profiles_count=len(all_profiles)
    # Data For Modal
    new_profile_data = all_profiles
    number_retrieved = request.GET.get('numberRetrieved', None)
    status_sent = request.GET.get('statusSent', None)
    intro_message_success=request.GET.get('introMessageSuccess', None)
    if number_retrieved:
        new_profile_data = all_profiles.exclude(contact_number__isnull=True).exclude(contact_number='').exclude(contact_number = 'Video Call Excluded')
    elif status_sent:
        new_profile_data = all_profiles.filter(status='Sent').exclude(contact_number__isnull=False)
    elif intro_message_success:
        new_profile_data = all_profiles.filter(intro_message='Success').exclude(contact_number__isnull=False)

    if number_retrieved:
        # Create the HttpResponse object with the appropriate CSV header.
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="filtered_profiles.csv"'

        writer = csv.writer(response)
        writer.writerow(['Name', 'Link', 'Contact Number', 'Last Communication', 'Campaign'])

        for profile in new_profile_data:
            # Convert contact_number to string and prepend with a tab
            contact_number_str = f"\'{profile.contact_number}"
            writer.writerow([
                profile.name,
                profile.link,
                contact_number_str,  # This will force Excel to treat it as text
                profile.last_communication,
                profile.campaign.name
            ])

        return response
    
    elif status_sent or intro_message_success:
        # Create the HttpResponse object with the appropriate CSV header.
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="filtered_profiles.csv"'

        writer = csv.writer(response)
        writer.writerow(['Name', 'Link', 'Campaign'])

        for profile in new_profile_data:
            # Convert contact_number to string and prepend with a tab
            contact_number_str = f"\'{profile.contact_number}"
            writer.writerow([
                profile.name,
                profile.link,
                profile.campaign.name
            ])

        return response

    # Code For Rest of the page
    if total_profiles_count > 0:
        success_profiles_count = all_profiles.filter(intro_message="Success").count()
        reply_rate = round((success_profiles_count / total_profiles_count),2) 
        reply_ratio = round((success_profiles_count / total_profiles_count * 100),2)
        stats_data ["reply_rate"] = reply_rate
        stats_data["reply_ratio"] = reply_ratio

        accepted_status_count = all_profiles.filter(status="Accepted").count()
        acceptance_rate = round((accepted_status_count / total_profiles_count),2)
        acceptance_ratio = round((success_profiles_count / total_profiles_count *100),2)
        stats_data["acceptance_rate"] = acceptance_rate
        stats_data["acceptance_ratio"] = acceptance_ratio
    else:
        stats_data ["reply_rate"] = 0
        stats_data["reply_ratio"] = 0
        stats_data["acceptance_rate"] = 0
        stats_data["acceptance_ratio"] = 0

    account = Account.objects.get(id=account_id)  # Get the specific account
    if request.method == 'POST':
        form = AccountProxyForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            # Redirect to prevent resubmission
            return redirect('account_details', account_id=account.id)
    else:
        form = AccountProxyForm(instance=account)

    return render(
        request,
        "account_details.html", {'stats': stats_data, 'campaigns':campaigns_with_profile_count, 'account_name': account_name.first(), 'form': form, 'account_id': account_id }, 
    )
@login_required 
@user_passes_test(is_superuser, login_url='/')
def user_metrics_distribution(request):
    # users= Linkedin_user.objects.all().order_by('-id')
    if request.method == 'POST':
        # Handle AJAX request
        data = json.loads(request.body.decode('utf-8'))
        action = data.get('action')
        
        if action == 'assign':
            user_id = data.get('user_id')
            account_ids = data.get('account_ids')
            for account_id in account_ids:
                account = Account.objects.get(id=account_id)
                UserMetricsDistribution.objects.create(user_id=user_id, account=account)
            return JsonResponse({"success": True, "message": "Accounts assigned successfully."})

        elif action == 'delete':
            user_id = data.get('user_id')
            account_id = data.get('account_id')
            # Your logic to delete the assigned account from the user
            UserMetricsDistribution.objects.filter(user_id=user_id, account_id=account_id).delete()
            return JsonResponse({"success": True, "message": "Account unlinked successfully."})
    User = get_user_model()
    #users = User.objects.all().distinct()
    users = User.objects.filter(username__icontains='capital3pm').distinct()

    # accounts = Account.objects.all().order_by('-id')
    assigned_account_ids = UserMetricsDistribution.objects.values_list('account', flat=True)

    # Exclude these accounts when fetching the list of accounts to assign
    available_accounts = Account.objects.exclude(id__in=assigned_account_ids).order_by('-id').distinct()
    for user in users:
        assigned_account_ids = UserMetricsDistribution.objects.filter(user=user).values_list('account', flat=True)
        user.assigned_accounts = Account.objects.filter(id__in=assigned_account_ids)

    return render(
        request,
        "user_metrics_distribution.html", {'users': users, 'accounts': available_accounts}
    )

@login_required 
@user_passes_test(is_superuser, login_url='/')
def cold_leads(request,  user_id=None):
    if user_id:
        current_user = get_object_or_404(User, id=user_id)
    else:
        current_user = request.user
    user_metrics = UserMetricsDistribution.objects.filter(user=current_user)
    # Extract all unique Account objects associated with these UserMetricsDistribution objects
    connected_accounts = Account.objects.filter(usermetricsdistribution__in=user_metrics).distinct()
    connected_campaigns = Campaign.objects.filter(account__in=connected_accounts).order_by('-start_date').distinct()
    profiles_query = Profile.objects.filter(
        campaign__in=connected_campaigns).exclude(
        contact_number__isnull=True  # Excludes profiles with null contact numbers
    ).exclude(
        contact_number=''  # Excludes profiles with empty string as contact number
    ).exclude(
        contact_number='Video Call Excluded'  # Excludes profiles with 'Video Call Excluded'
    ).select_related('campaign__account').annotate(
        account_name=F('campaign__account__name'),  
        campaign_name=F('campaign__name'),  # Annotates with the name of the campaign
        campaign_start_date=F('campaign__start_date'),  # Annotates with the start date of the campaign
        campaign_end_date=F('campaign__end_date')  # Annotates with the end date of the campaign
    ).order_by('-last_communication').values(
        'name', 'contact_number', 'last_communication', 'account_name',
        'campaign_name', 'campaign_start_date', 'campaign_end_date', 'status', 'intro_message'  # Include these in the values() call
    )
    new_profile_data= profiles_query
    number_retrieved = request.GET.get('numberRetrieved', None)
    status_sent = request.GET.get('statusSent', None)
    intro_message_success=request.GET.get('introMessageSuccess', None)
    if number_retrieved:
        new_profile_data = new_profile_data.exclude(contact_number__isnull=True).exclude(contact_number='').exclude(contact_number = 'Video Call Excluded')
    if status_sent:
        new_profile_data = new_profile_data.filter(status='Sent')
    if intro_message_success:
        new_profile_data = new_profile_data.filter(intro_message='Success')
    if number_retrieved or status_sent or intro_message_success:
        # Setup the response for a CSV download
        response = HttpResponse(content_type='text/csv')
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        response['Content-Disposition'] = f'attachment; filename="filtered_profiles_{current_time}.csv"'

        # Create a CSV writer
        writer = csv.writer(response)
        # Write the header row
        writer.writerow(['Name', 'Link', 'Contact Number', 'Last Communication', 'Campaign'])
        for profile in new_profile_data:
            # Handle both dictionary and object-type profiles
            contact_number_str = f"\'{profile.get('contact_number', '') if isinstance(profile, dict) else profile.contact_number}"
            writer.writerow([
                profile.get('name', '') if isinstance(profile, dict) else profile.name,
                profile.get('link', '') if isinstance(profile, dict) else profile.link,
                contact_number_str,
                profile.get('last_communication', '') if isinstance(profile, dict) else profile.last_communication,
                profile.get('campaign', {}).get('name', '') if isinstance(profile, dict) else profile.campaign.name
            ])

        # Return the response for downloading
        return response
    # Apply pagination to profiles
    profiles_per_page = 10  # Adjust the number of items per page as needed
    paginator = Paginator(profiles_query, profiles_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'cold_leads.html', {'page_obj': page_obj})

class CampaignListAPIView(APIView):
    #permission_classes = [IsAuthenticated, IsAdminUser]
 
    def get(self, request):
        query = request.query_params.get('query')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        status = request.query_params.get('status')
        user = request.query_params.get('user')
        if user:
            queryset = Campaign.objects.filter(
                Q(saved_search__linkedinuser__user_id=user) | Q(lead_list__linkedinuser__user_id=user)
            ).order_by('-id')
        else:
            queryset = Campaign.objects.order_by('-id')


        if query:
            search_fields = ["name", "account__name"]
            f = search_filter(search_fields, query)
            queryset = queryset.filter(f)
        if start_date:
            queryset = queryset.filter(start_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(end_date__lte=end_date)
        if status:
            queryset = queryset.filter(status__icontains=status)
        # Paginate the Campaign queryset directly
        page_size = 10  # Number of campaigns per page
        paginator = Paginator(queryset , page_size)
        page_number = request.query_params.get('page', 1)
        page_obj = paginator.get_page(page_number)

        # Now process each campaign in the paginated page
        campaigns_data = []
        for campaign in page_obj:
            campaign_data = CampaignSerializer(campaign).data
            profiles = list(campaign.profile_set.all())
            total_profiles = len(profiles)
            approached_profiles = sum(1 for p in profiles if p.status != 'Excluded' and p.status != 'Scrapped')
            accepted_profiles = sum(1 for p in profiles if p.status != 'Excluded' and p.status != 'Scrapped' and p.status != 'Sent' and p.status)
            excluded_profiles = sum(1 for p in profiles if p.status == 'Excluded')
            scrapped_profiles = sum(1 for p in profiles if p.status == 'Scrapped')

            # Update the campaign data dictionary
            campaign_data['total_profiles'] = total_profiles
            campaign_data['connects_sent'] = approached_profiles
            campaign_data['connect_accepted'] = accepted_profiles
            campaign_data['excluded_profiles'] = excluded_profiles
            campaign_data['scrapped_profiles'] = scrapped_profiles

            if total_profiles:
                campaign_data['connects_sent_percentage'] = int((approached_profiles/total_profiles)*100)
                campaign_data['connect_accepted_percentage'] = int((accepted_profiles/total_profiles)*100)
                campaign_data['excluded_profiles_percentage'] = int((excluded_profiles/total_profiles)*100)
                if campaign.autoscrapper:
                    campaign_data['scrapped_profiles_percentage'] = int((scrapped_profiles/campaign.batch_size)*100)
                else:
                    campaign_data['scrapped_profiles_percentage'] = 0


            else:
                campaign_data['connects_sent_percentage'] = 0
                campaign_data['connect_accepted_percentage'] = 0
                campaign_data['excluded_profiles_percentage'] = 0
                campaign_data['scrapped_profiles_percentage'] = 0
            if not campaign.total_profile_count:
                total_urls = 0
                # Using prefetched excel_files
                for excel_file in campaign.excel_file_set.all():
                    try:
                        json_data = json.loads(excel_file.json_data)
                        if 'urls' in json_data and isinstance(json_data['urls'], list):
                            total_urls += len(json_data['urls'])
                    except json.JSONDecodeError:
                        pass 
                campaign.total_profile_count = total_urls


            # Only calculate percentage if there's a change to avoid unnecessary calculations
            if campaign.autoscrapper:
                if campaign.batch_size:
                    campaign_data['campaign_completion_percentage'] = round((total_profiles / campaign.batch_size) * 100, 2)
                else:
                    campaign_data['campaign_completion_percentage'] = 0

            elif total_profiles and campaign.total_profile_count:
                if total_profiles > 0 and campaign.total_profile_count > 0:
                    campaign.campaign_completion_percentage = round((total_profiles / campaign.total_profile_count) * 100, 2)
                    campaign_data['campaign_completion_percentage'] = round((total_profiles / campaign.total_profile_count) * 100, 2)
                    
                if campaign.total_profile_count == total_profiles:
                    campaign.status = "finished"

            campaigns_data.append(campaign_data)

        # Return only the current page's data
        return Response({
            'total_pages': paginator.num_pages,
            'current_page': int(page_number),
            'campaigns': campaigns_data
        })
    
@login_required 
def account_reporting(request):

    if request.GET.get('end_date'):
        selected_date_str = timezone.make_aware(datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d'))
        selected_date_str = selected_date_str + timedelta(days=1)
    else:
        selected_date_str = timezone.now()
        selected_date_str = selected_date_str + timedelta(days=1)

    if request.GET.get('start_date'):
        start_date_str = timezone.make_aware(datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d'))
    else:
        start_date_str = selected_date_str - timedelta(days=7)
    print(start_date_str)
    print(selected_date_str)
    
    accounts = calculate_account_data(start_date_str, selected_date_str)

    return render(request, "account_reporting.html", {
        "accounts": accounts, 
        'end_date': selected_date_str.strftime('%Y-%m-%d'), 'start_date': start_date_str.strftime('%Y-%m-%d')
    })

class ColdLeadsAPIView(APIView):
    #permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id', None)
        query = request.query_params.get('query')
        lead_status = request.query_params.get('lead_status')
        
        if user_id:
            current_user = get_object_or_404(User, id=user_id)
        else:
            print("IN ELSE")
            current_user = request.user
        
        user_metrics = UserMetricsDistribution.objects.filter(user=current_user)
        connected_accounts = Account.objects.filter(usermetricsdistribution__in=user_metrics).distinct()
        connected_campaigns = Campaign.objects.filter(account__in=connected_accounts).order_by('-start_date').distinct()
        
        latest_experience = Experience.objects.filter(
            profile=OuterRef('pk')
        ).order_by('id')  # Order by id ascending to get the oldest id as the latest experience

        # Base profiles query
        profiles_query = Profile.objects.exclude(
            contact_number__isnull=True
        ).exclude(
            contact_number=''
        ).exclude(
            contact_number='Video Call Excluded'
        ).exclude(contact_number='Video Call').exclude(contact_number="'Video Call").select_related('campaign__account').annotate(
            account_name=F('campaign__account__name'),
            campaign_name=F('campaign__name'),
            campaign_start_date=F('campaign__start_date'),
            campaign_end_date=F('campaign__end_date'),
            latest_experience_company=Subquery(latest_experience.values('company_name')[:1]),
        ).order_by('-id').values(
            'id','name', 'contact_number', 'last_communication', 'account_name',
            'campaign_name', 'campaign_start_date', 'campaign_end_date', 'status', 'intro_message','headline','location',
            'latest_experience_company', 'lead_status', 'link'
        )

        # Apply campaign filter only if the user is not a superuser
        if not current_user.is_superuser:
            profiles_query = profiles_query.filter(
                campaign__in=connected_campaigns
            )

        if lead_status:
            if lead_status.lower() == "new":
                profiles_query = profiles_query.filter(
                    Q(lead_status__iexact="new") | Q(lead_status__isnull=True)
                )
            else:
                profiles_query = profiles_query.filter(lead_status=lead_status)

        if query:
            search_fields = ["contact_number", "name", "campaign__account__name"]
            f = search_filter(search_fields, query)
            profiles_query = profiles_query.filter(f)

        profiles_per_page = 10
        paginator = Paginator(profiles_query, profiles_per_page)
        page_number = request.query_params.get('page')
        if not page_number:
            page_number = 1
        
        page_obj = paginator.get_page(page_number)
        return Response({'total_pages': paginator.num_pages,
                         'current_page': int(page_number),
                         "leads": page_obj.object_list})


class UpdateLeadStatusAPIView(APIView):
    #permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, *args, **kwargs):
        profile_id = kwargs.get('profile_id')
        if not profile_id:
            return Response({"error": "Profile ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        new_lead_status = request.query_params.get('lead_status')
        if not new_lead_status:
            return Response({"error": "Lead status is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        profile = get_object_or_404(Profile, pk=profile_id)
        
        profile.lead_status = new_lead_status
        profile.lead_last_contact = timezone.now()
        profile.save()
        return Response({"status": 200,"message": "Lead status updated successfully."}, status=status.HTTP_200_OK)
    

class AccountsPerformanceAPIView(APIView):
    #permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request,  *args, **kwargs):
        start_date = request.GET.get('start_date', None)
        end_date = request.GET.get('end_date', None)
        if start_date:
            selected_date_str = timezone.make_aware(datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d'))
            selected_date_str = selected_date_str + timedelta(days=1)
        else:
            selected_date_str = timezone.now()
            selected_date_str = selected_date_str + timedelta(days=1)

        if end_date:
            start_date_str = timezone.make_aware(datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d'))
        else:
            start_date_str = selected_date_str - timedelta(days=7)
        print(start_date_str)
        print(selected_date_str)
        
        accounts = calculate_account_data(start_date_str, selected_date_str)
        return Response({"accounts":accounts})