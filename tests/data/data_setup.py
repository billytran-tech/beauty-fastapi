from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClient
from pydantic_settings import BaseSettings, SettingsConfigDict
# from pymongo.server_api import ServerApi
from pymongo.server_api import ServerApi
from tests.setup.config_tests import env
import asyncio
import certifi
ca = certifi.where()

user_ids = [
    'auth0|65159b2f50dd72103eb7d497',
    'auth0|6515871250dd72103eb7be01',
    'auth0|651599fa9745d9c63c264402',
]

default_schedule = {
    "preffered_timezone": "",
    "daily_schedule": {
        "monday": {
            "is_available": False,
            "operating_hours": {
                "start_time": None,
                "end_time": None
            },
            "blocked_hours": []
        },
        "tuesday": {
            "is_available": False,
            "operating_hours": {
                "start_time": None,
                "end_time": None
            },
            "blocked_hours": []
        },
        "wednesday": {
            "is_available": False,
            "operating_hours": {
                "start_time": None,
                "end_time": None
            },
            "blocked_hours": []
        },
        "thursday": {
            "is_available": False,
            "operating_hours": {
                "start_time": None,
                "end_time": None
            },
            "blocked_hours": []
        },
        "friday": {
            "is_available": False,
            "operating_hours": {
                "start_time": None,
                "end_time": None
            },
            "blocked_hours": []
        },
        "saturday": {
            "is_available": False,
            "operating_hours": {
                "start_time": None,
                "end_time": None
            },
            "blocked_hours": []
        },
        "sunday": {
            "is_available": False,
            "operating_hours": {
                "start_time": None,
                "end_time": None
            },
            "blocked_hours": []
        }
    },
    "blocked_dates": []
}

default_settings = {
    "settings": {
        "notification_preferences": {
            "BookingChanges": {
                "sms": True,
                "email": True,
                "whatsapp": False
            },
            "BookingReminders": {
                "sms": True,
                "email": True,
                "whatsapp": False
            },
            "SuavUpdates": {
                "sms": False,
                "email": True,
                "whatsapp": False
            },
            "SecuritySettings": {
                "sms": True,
                "email": True,
                "whatsapp": False
            }
        }
    }
}
usernames = [
    {
        '_id': '6515991b5bf739e936cf0a3d',
        'username': 'suavbarber',
        'user_id': 'auth0|6515871250dd72103eb7be01'
    },
    {
        '_id': '65159a4916d0abba9ff9ff93',
        'username': 'suavhairstudio',
        'user_id': 'auth0|651599fa9745d9c63c264402'
    },
    {
        '_id': '65159b7516d0abba9ff9ff95',
        'username': 'suavnails',
        'user_id': 'auth0|65159b2f50dd72103eb7d497'
    },
]

merchants = [
    {
        '_id': '66b7bef302bbd03990e3d72d',
        'username_id': '65159a4916d0abba9ff9ff93',
        'name': 'Maria',
        'profession': 'Hair Stylist',
        'profile_image_url': 'https://suavmedia.blob.core.windows.net/suav-media-uploads/650455dfa16c0afdb169db00/profile/SB202309151306153ca4e156SuavBraidsProfile.jpeg',
        'bio': 'Discover the perfect blend of style and comfort at Chic & Cozy Hair Studio. Our salon specializes in creating stunning looks while providing a welcoming and relaxed atmosphere. From trendy cuts to intricate braids, our talented stylists are dedicated to enhancing your natural beauty. Book your appointment today and experience the elegance of Chic & Cozy Hair Studio. Your hair, your style, your sanctuary.',
        'location': {
            'cordinates': {
                'longitude': -75.67536679999999,
                'latitude': 45.3803878,
            },
            'country': {
                'name': 'Canada',
                'code': 'CA',
                'currency': {
                    'code': 'CAD',
                    'symbol': 'CA$',
                    'name': 'Canadian Dollar'
                }
            },
            'city': 'Ottawa',
            'street_address': '1059, Aldea Ave, Ottawa, ON K1H 8B8, Canada'
        },
        'user_id': 'auth0|651599fa9745d9c63c264402',
        'schedule': default_schedule,
        'settings': default_settings,
    },
    {
        '_id': '66b7bef502bbd03990e3d72e',
        'username_id': '65159b7516d0abba9ff9ff95',
        'name': "Emilia's Nails",
        'profession': 'Nail Artist',
        'profile_image_url': 'https://suavmedia.blob.core.windows.net/suav-media-uploads/65045b8c6d77d3cdca6bc787/profile/SB20230915145441a99d703fNailArtProfile.jpeg',
        'bio': "Indulge in the art of self-care at Nail Bliss Haven. Step into a world of impeccable nail craftsmanship and relaxation. Our talented nail technicians are dedicated to transforming your hands and feet into stunning works of art. From luxurious manicures and pedicures to creative nail designs, we're here to enhance your natural beauty and leave you feeling pampered and polished. Visit Nail Bliss Haven today and treat yourself to a moment of bliss and beauty. Your nails, your sanctuary.",
        'location': {
            'cordinates': {
                'longitude': -79.3853742,
                'latitude': 43.6496228,
            },
            'country': {
                'name': 'Canada',
                'code': 'CA',
                'currency': {
                    'code': 'CAD',
                    'symbol': 'CA$',
                    'name': 'Canadian Dollar'
                }
            },
            'city': 'Toronto',
            'street_address': '145 Richmond St W, Toronto, ON M5H2L2, Canada'
        },
        'user_id': 'auth0|65159b2f50dd72103eb7d497',
        'schedule': default_schedule,
        'settings': default_settings,
    },
    {
        '_id': '66b7bef502bbd03990e3d72f',
        'username_id': '6515991b5bf739e936cf0a3d',
        'name': "Emanual's Barbershop",
        'profession': 'Barber',
        'profile_image_url': 'https://suavmedia.blob.core.windows.net/suav-media-uploads/650440dda16c0afdb169daff/profile/SB20230915113906fdebdef3SuavBarberMedia.jpg',
        'bio': 'Discover the art of grooming at BarberShop XYZ in Toronto, Canada. Our skilled barbers deliver precision haircuts, expert shaves, and a relaxing experience. Book today and elevate your style.',
        'location': {
            'cordinates': {
                'longitude': -79.88573989999999,
                'latitude': 43.5111844,
            },
            'country': {
                'name': 'Canada',
                'code': 'CA',
                'currency': {
                    'code': 'CAD',
                    'symbol': 'CA$',
                    'name': 'Canadian Dollar'
                }
            },
            'city': 'Milton',
            'street_address': '123 Main St E, Milton, ON L9T 1N4, Canada'
        },
        'user_id': 'auth0|6515871250dd72103eb7be01',
        'schedule': default_schedule,
        'settings': default_settings,
    },
]


services = [
    {
        '_id': '65159fe54d02150c08adc9e6',
        'service_name': 'Nail Art and Design',
        'duration_minutes': 120,
        'out_call': True,
        'description': '',
        'price': {
            'currency': {
                'code': 'CAD',
                'symbol': 'CA$',
                'name': 'Canadian Dollar'
            },
            'amount': '35.00'
        },
        'images': ['https://suavmedia.blob.core.windows.net/suav-media-uploads/650440dda16c0afdb169daff/services/SB202309151458535140ee1dNails3.jpeg', 'https://suavmedia.blob.core.windows.net/suav-media-uploads/650440dda16c0afdb169daff/services/SB20230915145853aba88d54NailArt1.jpeg', 'https://suavmedia.blob.core.windows.net/suav-media-uploads/650440dda16c0afdb169daff/services/SB20230915145853c8c693f1GelNails1.jpeg'],
        'owner_id': 'auth0|65159b2f50dd72103eb7d497'
    },
    {
        '_id': '651bf79d9e553ef557a7e444',
        'service_name': 'Out-call Wedding Package',
        'duration_minutes': '180',
        'out_call': '',
        'descritpion': "Let us bring our professional barber services to your wedding venue. We'll ensure the groom and groomsmen look their best.",
        'price': {
            'currency': {
                'code': 'CAD',
                'symbol': 'CA$',
                'name': 'Canadian Dollar'
            },
            'amount': '300.00'
        },
        'images': ['https://suavmedia.blob.core.windows.net/suav-media-uploads/6515991b5bf739e936cf0a3c/services/SB202310031114352d0b84dfBeardTrim1.jpg', 'https://suavmedia.blob.core.windows.net/suav-media-uploads/6515991b5bf739e936cf0a3c/services/SB20231003111435a980d11dBeardTrim3.jpg', 'https://suavmedia.blob.core.windows.net/suav-media-uploads/6515991b5bf739e936cf0a3c/services/SB202310031114367a2bd8a8Haircut1.jpg', 'https://suavmedia.blob.core.windows.net/suav-media-uploads/6515991b5bf739e936cf0a3c/services/SB20231003111436831e335cHaircut2.jpg', 'https://suavmedia.blob.core.windows.net/suav-media-uploads/6515991b5bf739e936cf0a3c/services/SB202310031114365fe021b4Haircut3.jpg'],
        'owner_id': 'auth0|6515871250dd72103eb7be01'
    },
    {
        '_id': '65159f6716d0abba9ff9ff96',
        'service_name': 'Classic Haircut',
        'duration_minutes': '',
        'out_call': '',
        'descritpion': 'A timeless haircut that suits your style and preferences. Our experienced barbers will give you a fresh look.',
        'price': {
            'currency': {
                'code': 'CAD',
                'symbol': 'CA$',
                'name': 'Canadian Dollar'
            },
            'amount': '25.00'
        },
        'images': ['https://suavmedia.blob.core.windows.net/suav-media-uploads/650440dda16c0afdb169daff/services/SB2023091512380020aab913Haircut1.jpg', 'https://suavmedia.blob.core.windows.net/suav-media-uploads/650440dda16c0afdb169daff/services/SB202309151238000a552a5eHaircut2.jpg', 'https://suavmedia.blob.core.windows.net/suav-media-uploads/650440dda16c0afdb169daff/services/SB20230915123801dcba1e80Haircut3.jpg', 'https://suavmedia.blob.core.windows.net/suav-media-uploads/650440dda16c0afdb169daff/services/SB2023091512380163c292ceHaircut4.jpg'],
        'owner_id': 'auth0|6515871250dd72103eb7be01'
    },
    {
        '_id': '6515a3d533e5f40fe30f814c',
        'service_name': 'Box Braids Installation',
        'duration_minutes': 300,
        'out_call': False,
        'descritpion': 'Elevate your style with our Box Braids Installation service. Our skilled braiders are experts in creating stunning box braids that not only look fantastic but also promote hair health. We use top-quality extensions and products to ensure durability and a long-lasting, beautiful finish. Whether you prefer long, short, thin, or thick braids, our stylists will work with you to achieve the look you desire',
        'price': {
            'currency': {
                'code': 'CAD',
                'symbol': 'CA$',
                'name': 'Canadian Dollar'
            },
            'amount': '160.00'
        },
        'images': ['https://suavmedia.blob.core.windows.net/suav-media-uploads/650455dfa16c0afdb169db00/services/SB20230915151008cfd28c02BoxBraids1.jpeg', 'https://suavmedia.blob.core.windows.net/suav-media-uploads/650455dfa16c0afdb169db00/services/SB202309151510128072cd30BoxBraids2.jpeg', 'https://suavmedia.blob.core.windows.net/suav-media-uploads/650455dfa16c0afdb169db00/services/SB20230915151019d208f4f3BoxBraids3.jpeg', 'https://suavmedia.blob.core.windows.net/suav-media-uploads/650455dfa16c0afdb169db00/services/SB20230915151021b292c793BoxBraids4.jpeg'],
        'owner_id': 'auth0|651599fa9745d9c63c264402'
    },
    {
        '_id': '6515a4004d02150c08adc9e7',
        'service_name': 'Loc Maintenance and Styling',
        'duration_minutes': '150',
        'out_call': '',
        'descritpion': 'Keep your locs looking their best with our Loc Maintenance and Styling service. Our experts will provide a thorough cleansing, retwisting, and styling to ensure your locs are well-maintained and showcase your unique personality. Choose from a variety of loc styles, from classic to intricate designs.',
        'price': {
            'currency': {
                'code': 'CAD',
                'symbol': 'CA$',
                'name': 'Canadian Dollar'
            },
            'amount': '95.00'
        },
        'images': ['https://suavmedia.blob.core.windows.net/suav-media-uploads/650455dfa16c0afdb169db00/services/SB20230915152156e998f7bdLocs1.jpeg', 'https://suavmedia.blob.core.windows.net/suav-media-uploads/650455dfa16c0afdb169db00/services/SB20230915152211d0513484Locs2.jpeg', 'https://suavmedia.blob.core.windows.net/suav-media-uploads/650455dfa16c0afdb169db00/services/SB202309151522122289c1d0Locs3.jpeg', 'https://suavmedia.blob.core.windows.net/suav-media-uploads/650455dfa16c0afdb169db00/services/SB202309151522170cac6411Locs5.jpeg', 'https://suavmedia.blob.core.windows.net/suav-media-uploads/650455dfa16c0afdb169db00/services/SB20230915152219e624c5faLocs6.jpeg'],
        'owner_id': 'auth0|651599fa9745d9c63c264402'
    }
]

merchant_card_response = [
    {
        'name': "Emanual's Barbershop",
        'profession': 'Barber',
        'profile_image_url': 'https://suavmedia.blob.core.windows.net/suav-media-uploads/650440dda16c0afdb169daff/profile/SB20230915113906fdebdef3SuavBarberMedia.jpg',

        'location': {
            'cordinates': {
                'longitude': -79.3853742,
                'latitude': 43.6496228,
            },
            'country': {
                'name': 'Canada',
                'code': 'CA',
                'currency': {
                    'code': 'CAD',
                    'symbol': 'CA$',
                    'name': 'Canadian Dollar'
                }
            },
            'city': 'Toronto',
            'street_address': '145 Richmond St W, Toronto, ON M5H2L2, Canada'
        },
        'username': 'suavbarber',
    },
    {
        'name': 'Maria',
        'profession': 'Hair Stylist',
        'profile_image_url': 'https://suavmedia.blob.core.windows.net/suav-media-uploads/650455dfa16c0afdb169db00/profile/SB202309151306153ca4e156SuavBraidsProfile.jpeg',
        'location': {
            'cordinates': {
                'longitude': -75.67536679999999,
                'latitude': 45.3803878,
            },
            'country': {
                'name': 'Canada',
                'code': 'CA',
                'currency': {
                    'code': 'CAD',
                    'symbol': 'CA$',
                    'name': 'Canadian Dollar'
                }
            },
            'city': 'Ottawa',
            'street_address': '1059, Aldea Ave, Ottawa, ON K1H 8B8, Canada'
        },
        'location': {

        },
        'username': 'suavhairstudio',
    },
    {
        'name': "Emilia's Nails",
        'profession': 'Nail Artist',
        'profile_image_url': 'https://suavmedia.blob.core.windows.net/suav-media-uploads/65045b8c6d77d3cdca6bc787/profile/SB20230915145441a99d703fNailArtProfile.jpeg',
        'location': {
            'cordinates': {
                'longitude': -79.3853742,
                'latitude': 43.6496228,
            },
            'country': {
                'name': 'Canada',
                'code': 'CA',
                'currency': {
                    'code': 'CAD',
                    'symbol': 'CA$',
                    'name': 'Canadian Dollar'
                }
            },
            'city': 'Toronto',
            'street_address': '145 Richmond St W, Toronto, ON M5H2L2, Canada'
        },
        'username': 'suavnails'
    }
]


async def populate_db() -> None:
    client = AsyncIOMotorClient(
        env.test_db_url, tlsCAFile=ca, server_api=ServerApi('1'))
    db = client[env.test_db_name]

    for merchant in merchants:
        await db['merchants'].insert_one(merchant)

    for username in usernames:
        await db['usernames'].insert_one(username)

    for service in services:
        await db['services'].insert_one(service)

    return
    # populate merchants
    # populate usernames
    # populate services
    pass
# asyncio.run(populate_db())
