from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseBadRequest
import json
from .models import Campaign, Profile, Account, Excel_file, PromptManagement, Linkedin_user,ScrapperProxy, UserMetricsDistribution, SavedSearch, LeadsList, Experience
import pandas as pd
import numpy as np

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
from rest_framework.permissions import IsAuthenticated  #, IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from utils.download_statistics import calculate_account_data
from django.contrib.auth import authenticate, login
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from django.db.models import OuterRef, Subquery
from django.middleware.csrf import get_token
from rest_framework import generics
from .utils import map_excel_to_template, transform_json
from rest_framework.generics import ListCreateAPIView, ListAPIView
from .models import Note
from .serializers import NoteSerializer, AccountSerializer,  SavedSearchSerializer, LeadsListSerializer

class NewCampaignAPIView(APIView):

    def post(self, request, *args, **kwargs):
        accounts = Account.objects.all().distinct()
        saved_searches = None
        lead_lists = None    
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
        

        # if request.method == 'POST':
        # Extract form data from the request
        default_value = None
        category_type = request.data.get('category_type', default_value)
        campaign_name = request.data.get('campaign_name', default_value)
        start_date = request.data.get('startDateTime', default_value)
        end_date = request.data.get('endDateTime', default_value)
        daily_count = request.data.get('daily_count', 0)
        if daily_count == '':
            daily_count =0

        job_title = request.data.get('jobtitle', default_value)
        category = request.data.get('category', default_value)
        search_value = request.data.get('searchValue', default_value)

        location = request.data.get('location', default_value)
        account_id = request.data.get('account_id', default_value)

        lead_id = request.data.get('lead_id', default_value)
        selected_account = None
        if account_id:
            selected_account = Account.objects.get(pk=account_id)
        excel_file = None
        

        try:
            # excel_file = request.FILES['listFile']
            excel_file = request.FILES.get('listfile', None)

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
                    return Response({"status":409, "message": "URLs list, first name list, and second name list cannot be empty."}, status=status.HTTP_200_OK)

                
                elif not urls_list or not first_name_list or not second_name_list:
                    return Response({"status":409, "message": "URLs list, first name list, and second name list cannot be empty."}, status=status.HTTP_200_OK)

                
                elif not any(profile_location) and not any(jobtitle):
                    # messages.error(request, "Error: At least one of company profile location or job title must not be empty.")
                    return Response({"status":409, "message": "At least one of company profile location or job title must not be empty."}, status=status.HTTP_200_OK)

                elif all(pd.isna(profile_location)) and all(pd.isna(jobtitle)):
                    return Response({"status":409, "message": "At least one of company profile location or job title must not be empty."}, status=status.HTTP_200_OK)
                data_dict = json.dumps({'urls': urls_list, 'names': names, 'profile_location': profile_location, 'jobtitle': jobtitle})
            except Exception as e:
                print(f"Error reading the Excel file: {e}")
                return Response({"status":500, "message": "Something Went Wrong"}, status=status.HTTP_200_OK)
            

    


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
            campaign_name = request.data.get('campaign_name', '')
            boolean_search = ''
            leads_list_obj = None
            saved_search_obj = None

            acategory = request.data.get('acategory')
            if acategory == "leads_list":
                lead_list = request.data.get('lead_list', '')
                if lead_list:
                    leads_list_obj = LeadsList.objects.get(id=int(lead_list))
            else:
                boolean_search = request.data.get('booleanSearch', '')
                saved_search = request.data.get('saved_search', '')
                if saved_search:
                    saved_search_obj = SavedSearch.objects.get(id=int(saved_search))


            start_date = request.data.get('startDateTime', '')
            end_date = request.data.get('endDateTime', '')
            minpage = int(request.data.get('minpage', '1'))
            maxpage = int(request.data.get('maxpage', '100'))
            minExperience = request.data.get('minExperience', 0)
            maxExperience = request.data.get('maxExperience', 0)
            min_age = request.data.get('minAge', 0)
            max_age = request.data.get('maxAge', 0)
            min_salary = request.data.get('minSalary', 0)
            max_salary = request.data.get('maxSalary', 0)
            batch_size = request.data.get('batch_size', 0)
            if batch_size == '':
                batch_size = 0
            elif batch_size:
                batch_size = int(batch_size)
            gender = request.data.get('gender', '')

            # Extracting the 'currentCompany' field from the POST data and converting it into a list
            includeNationality_list = request.data.get('includeNationality', '').split(',')
            
            # Remove any empty strings in case the input was not filled
            includeNationality_list = [includeNationality.strip() for includeNationality in includeNationality_list if includeNationality.strip()]
            nationalityBatch = int(request.data.get('nationalityBatch', 1))

            # Extracting the 'currentCompany' field from the POST data and converting it into a list
            excludeNationality_list = request.data.get('excludeNationality', '').split(',')
            
            # Remove any empty strings in case the input was not filled
            excludeNationality_list = [excludeNationality.strip() for excludeNationality in excludeNationality_list if excludeNationality.strip()]

            # Extracting the 'currentCompany' field from the POST data and converting it into a list
            includeFirstNames_list = request.data.get('firstNames', '').split(',')
            
            # Remove any empty strings in case the input was not filled
            includeFirstNames_list = [includeFirstName.strip() for includeFirstName in includeFirstNames_list if includeFirstName.strip()]

             # Extracting the 'currentCompany' field from the POST data and converting it into a list
            excludeFirstNames_list = request.data.get('firstNamesExclude', '').split(',')
            
            # Remove any empty strings in case the input was not filled
            excludeFirstNames_list = [excludeFirstName.strip() for excludeFirstName in excludeFirstNames_list if excludeFirstName.strip()]

            local = request.data.get('local', False)  
            expat = request.data.get('expat', False)  
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
                include_first_names_list = includeFirstNames_list,
                exclude_first_names_list = excludeFirstNames_list,
                nationality_batch = nationalityBatch,
                local=local,
                expat=expat,
                autoscrapper=True,
                saved_search=saved_search_obj,
                lead_list=leads_list_obj,
                minpage=minpage,
                maxpage=maxpage,
                gender=gender,
            )
                            
        # return redirect('new_campaign')
        return Response({"status":200, "message": "Campaign Added Successfully"}, status=status.HTTP_200_OK)    
class ProfileUpdateAPIView(APIView):
    def patch(self, request, pk, *args, **kwargs):
        print("PK", pk)
        # Fetch the profile based on the primary key provided in the URL
        profile = get_object_or_404(Profile, pk=pk)
        # Update fields if they are included in the request body
        for field, value in request.data.items():
            # Check if the field is actually a valid model field
            if hasattr(profile, field):
                setattr(profile, field, value)
        
        # Save the updated profile
        profile.save()
        # You might want to serialize the profile data here to return it
        return Response({"status":200, "message": "Profile updated successfully"}, status=status.HTTP_200_OK)

class ConnectLinkedinAccountAPIView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        cookies = request.data.get('linkedin_cookies')
        scrapper_ip = request.data.get('scrapper_ip')
        scrapper_port = request.data.get('scrapper_port')
        scrapper_user = request.data.get('scrapper_user')
        scrapper_pass = request.data.get('scrapper_pass')
        user_id = int(request.data.get('user_id'))
        user = User.objects.get(id=user_id)


        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return HttpResponseBadRequest("Invalid user ID")

        if not all([email, cookies, scrapper_ip, scrapper_pass, scrapper_port, scrapper_user]):
            return HttpResponseBadRequest("All Details are required")

        # Delete existing Linkedin_user and ScrapperProxy objects if they exist
        Linkedin_user.objects.filter(user_id=user).delete()
        ScrapperProxy.objects.filter(user_id=user).delete()

        linkedin_user = Linkedin_user(
            email=email,
            password=password,
            cookies=cookies,
            user_id=user
        )
        scrapper_proxy = ScrapperProxy(
            proxyip=scrapper_ip,
            proxyport=scrapper_port,
            proxyuser=scrapper_user,
            proxypass=scrapper_pass,
            user_id=user
        )
        # Save the objects to the database
        linkedin_user.save()
        scrapper_proxy.save()
        return Response({"status": 200, "message": "Linkedin Account Added with Proxy"}, status=status.HTTP_200_OK)
    
class ConnectLinkedinAccountAPIViewV1(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        cookies = request.data.get('linkedin_cookies')
        scrapper_ip = request.data.get('scrapper_ip')
        scrapper_port = request.data.get('scrapper_port')
        scrapper_user = request.data.get('scrapper_user')
        scrapper_pass = request.data.get('scrapper_pass')
        user_id = int(request.data.get('user_id'))

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return HttpResponseBadRequest("Invalid user ID")

        if not all([email, cookies]):
            return HttpResponseBadRequest("Email and LinkedIn cookies are required")

        # Update or create Linkedin_user object
        linkedin_user, created = Linkedin_user.objects.get_or_create(user_id=user)
        linkedin_user.email = email
        linkedin_user.password = password
        linkedin_user.cookies = cookies
        linkedin_user.save()

        # Only create or update ScrapperProxy if all required details are provided
        if all([scrapper_ip, scrapper_port, scrapper_user, scrapper_pass]):
            scrapper_proxy, created = ScrapperProxy.objects.get_or_create(user_id=user)
            scrapper_proxy.proxyip = scrapper_ip
            scrapper_proxy.proxyport = scrapper_port
            scrapper_proxy.proxyuser = scrapper_user
            scrapper_proxy.proxypass = scrapper_pass
            scrapper_proxy.save()

            return Response({"status": 200, "message": "LinkedIn Account and Scrapper Proxy Updated"}, status=status.HTTP_200_OK)
        else:
            return Response({"status": 200, "message": "LinkedIn Account Updated. Scrapper Proxy details were not provided, so it was not created/updated."}, status=status.HTTP_200_OK)

class LeadsFileListAPIView(APIView):
    def get(self, request, *args, **kwargs):
        user_id = request.query_params.get('user')
        #print(user_id)
        # linkedin_user = Linkedin_user.objects.filter(user_id=request.user).first()
        # scrapper_proxy = ScrapperProxy.objects.filter(user_id=request.user).first()
        if user_id:
            leads = Excel_file.objects.filter(campaign__isnull=True, created_at__isnull = False, json_data__isnull=False, user = user_id).order_by('-id')
        else:
            leads = Excel_file.objects.filter(campaign__isnull=True, created_at__isnull = False, json_data__isnull=False).order_by('-id')

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
        return Response({"status":200, "message": "Leads Found successfully", "leads": leads_formatted}, status=status.HTTP_200_OK)


class LeadsFileListAPIViewV1(APIView):
    def get(self, request, *args, **kwargs):
        user_id = request.query_params.get('user')
        #print(user_id)
        # linkedin_user = Linkedin_user.objects.filter(user_id=request.user).first()
        # scrapper_proxy = ScrapperProxy.objects.filter(user_id=request.user).first()
        if user_id:
            leads = Campaign.objects.filter(
                        Q(saved_search__isnull=False) | Q(lead_list__isnull=False),
                        Q(saved_search__linkedinuser__user_id=user_id) | Q(lead_list__linkedinuser__user_id=user_id),
                        autoscrapper=True
                    ).order_by('-id')
        else:
            leads = Campaign.objects.filter(
                        autoscrapper=True
                    ).order_by('-id')

        leads_formatted = []

        for excel_file in leads:

            leads_formatted.append({
                "id": excel_file.id,
                "name": excel_file.name
            })
        return Response({"status":200, "message": "Leads Found successfully", "leads": leads_formatted}, status=status.HTTP_200_OK)

class LeadsListDownloadAPIView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            lead_id = kwargs.get('lead_id')
            if not lead_id:
                return Response({"error": "lead_id is required"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                excel_file_instance = Excel_file.objects.get(id=lead_id)
            except Excel_file.DoesNotExist:
                return Response({"error": "Excel file not found"}, status=status.HTTP_404_NOT_FOUND)

            json_data = excel_file_instance.json_data

            # Ensure json_data is in a correct format
            if isinstance(json_data, str):
                json_data = json.loads(json_data)

            filename = excel_file_instance.name

            # Convert the JSON data to a pandas DataFrame
            df = pd.DataFrame(json_data)

            # Log the DataFrame to inspect its content
            print("DataFrame content:\n", df)

            # Assuming map_excel_to_template is causing the issue
            # mapped_df = map_excel_to_template(df)  # Ensure this function works correctly

            # For debugging, use the DataFrame directly
            mapped_df = df

            # Create a BytesIO buffer to save the Excel file in memory
            buffer = io.BytesIO()

            # Use the Excel writer and save the file to the buffer
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                mapped_df.to_excel(writer, index=False)

            # Go to the beginning of the stream
            buffer.seek(0)

            # Create a response, setting the content type to 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            response = HttpResponse(buffer.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

            # Set the content disposition to 'attachment' with a filename
            response['Content-Disposition'] = f'attachment; filename="{filename}.xlsx"'

            return response
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CampaignProfilesDownloadAPIView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            campaign_id = kwargs.get('campaign_id')
            if not campaign_id:
                return Response({"error": "campaign_id is required"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                profiles = Profile.objects.filter(campaign_id=campaign_id)
            except Profile.DoesNotExist:
                return Response({"error": "No profiles found for this campaign"}, status=status.HTTP_404_NOT_FOUND)

            # Prepare the data for the Excel file
            data = []
            for profile in profiles:
                # Split name into first and last names
                name_parts = profile.name.split() if profile.name else ["", ""]
                first_name = name_parts[0] if len(name_parts) > 0 else ""
                last_name = name_parts[1] if len(name_parts) > 1 else ""

                # Create the row data
                row = {
                    "ProfileLink": profile.link or "",
                    "FirstName": first_name,
                    "LastName": last_name,
                    "Email": "",  # Empty as specified
                    "Phone": "",  # Empty as specified
                    "Twitter": "",  # Empty as specified
                    "Messenger": "",  # Empty as specified
                    "TagLineTitle": profile.headline or "",
                    "Location": profile.location or "",
                }
                data.append(row)

            # Convert the list of dictionaries to a DataFrame
            df = pd.DataFrame(data)

            # Create a BytesIO buffer to save the Excel file in memory
            buffer = io.BytesIO()

            # Use the Excel writer and save the file to the buffer
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)

            # Go to the beginning of the stream
            buffer.seek(0)

            # Create a response, setting the content type to 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            response = HttpResponse(buffer.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

            # Set the content disposition to 'attachment' with a filename
            response['Content-Disposition'] = f'attachment; filename="campaign_{campaign_id}_profiles.xlsx"'

            return response
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
          
class UploadLeadsFileAPIView(APIView):
    def post(self, request, pk, *args, **kwargs):
        excel_file = request.FILES['listFile']
        if request.data.get("file_name") and excel_file:
            file_name = request.data.get("file_name")
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
                    return Response({"status":409, "message": "URLs list, first name list, and second name list cannot be empty."}, status=status.HTTP_200_OK)
      
                elif not urls_list or not first_name_list or not second_name_list:
                    return Response({"status":409, "message": "Error: URLs list, first name list, and second name list cannot be empty."}, status=status.HTTP_200_OK)
                
                elif not any(profile_location) and not any(jobtitle):
                    return Response({"status":409, "message": "Error: At least one of company profile location or job title must not be empty."}, status=status.HTTP_200_OK)
                    
                elif all(pd.isna(profile_location)) and all(pd.isna(jobtitle)):
                    return Response({"status":409, "message": "Error: At least one of company profile location or job title must not be empty."}, status=status.HTTP_200_OK)
                data_dict = json.dumps({'urls': urls_list, 'names': names, 'profile_location': profile_location, 'jobtitle': jobtitle})
                Excel_file.objects.create(json_data = data_dict, name=file_name, duplicate=True)
                return Response({"status":200, "message": "Leads File Uploaded Successfully"}, status=status.HTTP_200_OK)
                
            except Exception as e:
                print(f"Error reading the Excel file: {e}")
                return Response({"status":500, "message": "Something Went Wrong"}, status=status.HTTP_200_OK)
            
class AddAccountAPIView(APIView):
    def post(self, request, pk, *args, **kwargs):
            name = request.data.get('name')
            cookies = request.data.get('cookies')
            proxyip = request.data.get('proxyip')
            proxyport = request.data.get('proxyport')
            proxyuser = request.data.get('proxyuser')
            proxypass = request.data.get('proxypass')

            # Data validation (just a basic example, consider using Django Forms for more comprehensive validation)
            if not all([name, cookies, proxyip, proxyport, proxyuser, proxypass]):
                # return HttpResponseBadRequest("All fields are required")
                return Response({"status":409, "message": "All fields are required"}, status=status.HTTP_200_OK)
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
            return Response({"status":200, "message": "Account Created Successfully"}, status=status.HTTP_200_OK)
    
class NoteListCreateAPIView(ListCreateAPIView):
    serializer_class = NoteSerializer

    def get_queryset(self):
        # Retrieve the profile ID from the URL.
        profile_id = self.kwargs['profile_id']
        return Note.objects.filter(profile_id=profile_id)

    def perform_create(self, serializer):
        # Assuming 'profile_id' is passed as a URL parameter to the POST request
        profile_id = self.kwargs['profile_id']
        serializer.save(profile_id=profile_id)

class AccountListView(ListAPIView):
    queryset = Account.objects.all()  # Get all accounts
    serializer_class = AccountSerializer

class SavedSearchListView(ListAPIView):
    serializer_class = SavedSearchSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return SavedSearch.objects.filter(linkedinuser__user_id=user_id)

class LeadsListView(ListAPIView):
    serializer_class = LeadsListSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return LeadsList.objects.filter(linkedinuser__user_id=user_id)