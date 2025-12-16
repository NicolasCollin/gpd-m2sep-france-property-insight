from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim

geolocator: Nominatim = Nominatim(user_agent="fpi_geocoder_v1")
geocode: RateLimiter = RateLimiter(geolocator.geocode, min_delay_seconds=1.0, max_retries=2, swallow_exceptions=True)


def geocode_address(address: str) -> tuple:
    """
    Geocode a single address using Nominatim.

    Args:
        address: The address string to geocode.

    Returns:
        A tuple of (latitude, longitude) or (None, None) if not found.
    """
    if not address or not isinstance(address, str) or address.strip() == "":
        return None, None

    address_clean: str = address.strip()

    try:
        location = geocode(address_clean, timeout=10)
        if location:
            return location.latitude, location.longitude

        simple_address: str = address_clean.split(",")[0] + ", FRANCE"
        location = geocode(simple_address, timeout=5)
        if location:
            return location.latitude, location.longitude

    except Exception:
        pass

    return None, None
