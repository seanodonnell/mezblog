DEBUG = True

SECRET_KEY = "1aa1bb74-e7uu-4a86-921e-1b888fffffffffffffff-ffff-1111-2222-bbbbbbbbbbbbbbbbbbbb-1111-1111-1111-111111111111"
NEVERCACHE_KEY = "22222222-2222-2222-2222-22222222222222222222-2222-2222-2222-22222222222222222222-2222-2222-2222-222222222222"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "mezblog",
        "USER": "mezblog",
        "PASSWORD": "password",
        # Set to empty string for localhost. Not used with sqlite3.
        "HOST": "",
        # Set to empty string for default. Not used with sqlite3.
        "PORT": "",
    }
}
