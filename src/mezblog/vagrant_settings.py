DEBUG = True

SECRET_KEY = "1aa1bb74-e7uu-4a86-921e-1b888fffffffffffffff-ffff-1111-2222-bbbbbbbbbbbbbbbbbbbb-1111-1111-1111-111111111111"
NEVERCACHE_KEY = "22222222-2222-2222-2222-22222222222222222222-2222-2222-2222-22222222222222222222-2222-2222-2222-222222222222"
ALLOWED_HOSTS = ['*']
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "mezblog",
        "USER": "mezblog",
        "PASSWORD": "password",
        "HOST": "",
        "PORT": "",
    }
}
