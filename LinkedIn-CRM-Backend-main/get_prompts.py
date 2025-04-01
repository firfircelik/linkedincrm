import psycopg2
import time

def get_db():
    DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'yes54321',
        'HOST': 'linkedin-crm.cjqbwdujjpbk.eu-west-2.rds.amazonaws.com',
        'PORT': '5432',
    }
}

    db_settings = DATABASES['default']

    connected = False
    while not connected:
        try:
            conn = psycopg2.connect(
                dbname=db_settings['NAME'],
                user=db_settings['USER'],
                password=db_settings['PASSWORD'],
                host=db_settings['HOST'],
                port=db_settings['PORT']
            )
            connected = True
            # If the connection was successful, you can proceed with your operations
            # ...
        except psycopg2.OperationalError as e:
            print(f"Error connecting to the database: {e}")
            print("Attempting to reconnect in 5 seconds...")
            time.sleep(5)
    # Get a cursor
    cursor = conn.cursor()
    return cursor, conn

def prompts():
    cursor, conn = get_db()
   
    cursor.execute("""SELECT * FROM "CRM_promptmanagement" WHERE id = 9;""")
    cell1 = cursor.fetchone()[2]
    intro_prompt = cell1
    cursor.execute("""SELECT * FROM "CRM_promptmanagement" WHERE id = 6;""")
    cell2 = cursor.fetchone()[2]
    follow_up = cell2
    #print(intro_prompt)
    #print(follow_up)
    conn.close()
    return intro_prompt, follow_up

