import xlsxwriter
from CRM.models import Account, Profile
from django.utils import timezone
from django.db.models import Q

from io import BytesIO
from datetime import date
from django.db.models import Q
from datetime import datetime, timedelta
from django.utils import timezone
# Create a date object for March 26, 2024
# Function to calculate the data

def count_contact_numbers(contact_str):
    # Remove any unexpected whitespace and split by comma
    numbers = contact_str.replace(" ", "").split(',')
    # Return the count of non-empty entries
    return len([num for num in numbers if num])

def calculate_account_data(campaign_start_date, campaign_end_date):
    today_date = timezone.now()
    difference = abs(today_date - campaign_start_date).days
    if difference > 5:
        mid_date = campaign_start_date + timedelta(days=5)
    else:
        mid_date = campaign_end_date
    print(campaign_start_date)
    print(campaign_end_date)
    print(mid_date)

    accounts_data = []
    for account in Account.objects.all():
        profiles = Profile.objects.filter(
            campaign__account=account,
            campaign__name__iregex=r'^(?!.*lion).*$'
        ).exclude(campaign__category='lion')
        if not profiles:
            continue

        total_profiles = profiles.filter(
            campaign__account=account,
            campaign__start_date__range=[campaign_start_date, campaign_end_date]
        ).distinct('link').count()
        sent_profiles = profiles.filter(
            campaign__account=account,
            campaign__start_date__range=[campaign_start_date, campaign_end_date]
        ).exclude(status="Excluded").distinct('link').count()
        excluded_profiles = profiles.filter(
            campaign__account=account,
            status="Excluded",
            campaign__start_date__range=[campaign_start_date, campaign_end_date]
        ).distinct('link').count()

        accepted_profiles = profiles.filter(
            campaign__account=account,
            campaign__start_date__range=[campaign_start_date, campaign_end_date],
            last_communication__isnull=False
        ).exclude(status="Sent").exclude(status="Excluded").exclude(status="Scrapped").distinct('link').count()

        replied_profiles = profiles.filter(
            campaign__account=account,
            campaign__start_date__range=[campaign_start_date, campaign_end_date],
            last_communication__isnull=False
        ).filter(Q(intro_message="Success") | Q(status="Replied") | Q(contact_number__isnull=False)).distinct('link').count()

        contact_shared_profiles_start_to_mid = profiles.filter(
            campaign__account=account,
            contact_number__isnull=False,
            last_communication__range=[campaign_start_date, mid_date],
            last_communication__isnull=False
        ).exclude(contact_number__in=["Video Call Excluded", "Video Call"]).exclude(status__in=["Closed", "closed"]).distinct('link')

        contact_shared_profiles_mid_to_end = profiles.filter(
            campaign__account=account,
            contact_number__isnull=False,
            last_communication__range=[mid_date+ timedelta(days=1), campaign_end_date],
            last_communication__isnull=False
        ).exclude(contact_number__in=["Video Call Excluded", "Video Call"]).distinct('link')

        # Example usage in your code
        total_count_start_to_mid = sum(count_contact_numbers(profile.contact_number) for profile in contact_shared_profiles_start_to_mid)
        total_count_mid_to_end = sum(count_contact_numbers(profile.contact_number) for profile in contact_shared_profiles_mid_to_end)

        total_count = total_count_start_to_mid + total_count_mid_to_end

        accepted_rate = int((accepted_profiles / sent_profiles * 100) if sent_profiles else 0)
        replied_rate = int((replied_profiles / sent_profiles * 100) if sent_profiles else 0)
        contact_shared_rate = int((total_count / sent_profiles * 100) if sent_profiles else 0)
        if contact_shared_rate > 100:
            contact_shared_rate = 100

        accounts_data.append({
            'name': account.name,
            'total_profiles': total_profiles,
            'sent_profiles': sent_profiles,
            'excluded_profiles': excluded_profiles,
            'accepted_profiles': accepted_profiles,
            'replied_profiles': replied_profiles,
            'contact_shared_profiles': total_count,
            'accepted_rate': accepted_rate,
            'replied_rate': replied_rate,
            'contact_shared_rate': contact_shared_rate,
        })
    return accounts_data

# Function to create Excel file
def create_excel_file():
    data = calculate_account_data()
    # Specify the path where you want to save your Excel file
    file_path = 'accounts_statistics.xlsx'

    workbook = xlsxwriter.Workbook(file_path)
    worksheet = workbook.add_worksheet()

    # Set up the headers
    headers = [
        'Account Name', 'Total Profiles','Sent Profiles', 'Excluded Profiles', 'Accepted Profiles', 'Replied Profiles',
        'Contact Number Shared Profiles', 'Accepted Rate', 'Replied Rate',
        'Contact Shared Rate'
    ]
    for col_num, header in enumerate(headers):
        worksheet.write(0, col_num, header)

    # Write the data
    for row_num, account_data in enumerate(data, start=1):
        for col_num, (key, value) in enumerate(account_data.items()):
            worksheet.write(row_num, col_num, value)

    # Close the workbook to save it
    workbook.close()
