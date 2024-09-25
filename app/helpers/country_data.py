from app.schema.object_models.v0.country_model import FullCountryModel
_country_objects = {
    'ZA': {
        'name': 'South Africa',
        'code': 'ZA',
        'dialing_code': '+27',
                'currency': {
                    'code': 'ZAR',
                        'symbol': 'R',
                        'name': 'South African Rand',
                },
    },
    'CA': {
        'name': 'Canada',
        'code': 'CA',
        'dialing_code': '+1',
                'currency': {
                    'code': 'CAD',
                        'symbol': 'CA$',
                        'name': 'Canadian Dollar',
                },
    },
    'MZ': {
        'name': 'Mozambique',
        'code': 'MZ',
        'dialing_code': '+258',
                'currency': {
                    'code': 'MZN',
                        'symbol': 'MTn',
                        'name': 'Mozambican Metical',
                },
    },
    'IN': {
        'name': 'India',
        'code': 'IN',
        'dialing_code': '+91',
                'currency': {
                    'code': 'INR',
                        'symbol': '₹',
                        'name': 'Indian Rupee',
                },
    },
    'UA': {
        'name': 'Ukraine',
        'code': 'UA',
        'dialing_code': '+380',
        'currency': {
            'code': 'UAH',
            'symbol': '₴',
            'name': 'Ukranian hryvnia'
        }
    }
}


def get_country(country_code: str):
    country = _country_objects.get(country_code)
    return country


def list_available_countries():
    countries = []
    for key, value in _country_objects.items():
        value = FullCountryModel.model_validate(value)
        data_format = {
            'value': value.name,
            'code': key,
            'label': f"{value.dialing_code} ({key})"
        }
        countries.append(data_format)

    return countries
