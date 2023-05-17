from urllib.parse import urlparse

a = 'http://www.cwi.nl:80/%7Eguido/Python.html'
b = '/data/Python.html'
c = 532
d = u'dkakasdkjdjakdjadjfalskdjfalk'
e = 'http://stackoverflow.xy'

def uri_validator(x):
    try:
        result = urlparse(x)
        return all([result.scheme and result.netloc])
    except:
        return False

print(uri_validator(a))
print(uri_validator(b))
print(uri_validator(c))
print(uri_validator(d))
print(uri_validator(e))