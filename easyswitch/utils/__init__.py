import platform
from importlib import metadata

try:
    __version__ = metadata.version('easyswitch')
except metadata.PackageNotFoundError:
    __version__ = '0.0.0'
    


USER_AGENT = (
    f'EasySwitch-python/{__version__} ({platform.machine()}'
    f'{platform.system().lower()}) Python/{platform.python_version()}'
    )


####    PARSE PHONE NUMBER
def parse_phone(number:str, raise_exception = False):
    ''' Return A dict of countrycode and national number '''
    
    import phonenumbers

    try:
        parsed_number = phonenumbers.parse(number,None)
        return {
            'country_code': parsed_number.country_code,
            'national_number': parsed_number.national_number
        }
    except phonenumbers.NumberParseException:
        # Raise an exception if needed
        if raise_exception:
            raise phonenumbers.NumberParseException(
                'Invalid phone number'
            )
        return {
            'country_code': None,
            'national_number': None
        }