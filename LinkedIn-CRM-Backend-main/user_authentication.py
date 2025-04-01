import django
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
import psycopg2
import time


# Configure Django settings
settings.configure(
    SECRET_KEY='django-insecure-fov*(a0ppyvn9b03xfot_r=nj*rukvyhoj%n(q+!2!u(qv7@=q',
    INSTALLED_APPS=[
        'django.contrib.auth',
        'django.contrib.contenttypes',
    ],
    PASSWORD_HASHERS=[
        'django.contrib.auth.hashers.PBKDF2PasswordHasher',
        'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
        'django.contrib.auth.hashers.Argon2PasswordHasher',
        'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    ],
)

# Initialize Django
django.setup()


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




def get_stored_hash(username):
    cursor, conn = get_db()  # Assuming get_db() properly sets up your database connection
    cursor.execute("""SELECT password FROM auth_user WHERE username = %s;""", (username,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def get_users(user, password):
    

    cursor, conn = get_db()
    cursor.execute("""SELECT * FROM auth_user WHERE username = %s AND password = %s;""", (user, password))
    rows = cursor.fetchone()
    conn.close()
    return rows[0]


def authenticate_user(username, password):

    stored_hash = get_stored_hash(username)
    if stored_hash:
        if check_password(password, stored_hash):
            return get_users(username, stored_hash)

    return None

print(authenticate_user("haris1", "Seecs@444"))