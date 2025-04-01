import pandas as pd

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