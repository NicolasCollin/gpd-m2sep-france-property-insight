from fpi.map_config.geocoding import geocode_address


class TestGeocodeAddressLive:
    """
    Tests for geocode_address using live requests.
    Note : These tests depend on network access and the Nominatim service.

    """

    def test_valid_address(self):
        """
        A real address should return valid coordinates.

        """
        lat, lng = geocode_address("10 rue de la Paix, 75002 Paris, FRANCE")

        assert isinstance(lat, float)
        assert isinstance(lng, float)
        assert 48 <= lat <= 49
        assert 2 <= lng <= 3

    def test_partial_address(self):
        """
        Partial address should fallback to simple geocode.

        """
        lat, lng = geocode_address("rue de la Paix, Paris")

        assert isinstance(lat, float)
        assert isinstance(lng, float)
        assert 48 <= lat <= 49
        assert 2 <= lng <= 3

    def test_invalid_address(self):
        """
        Nonexistent or empty addresses should return (None, None).

        """
        for address in ["", "   ", None, "Address no exist"]:
            lat, lng = geocode_address(address)
            assert lat is None
            assert lng is None

    def test_strip_whitespace(self):
        """
        Leading/trailing spaces should not affect geocoding.

        """
        lat1, lng1 = geocode_address("10 RUE DE LA PAIX, 75002 PARIS 02, FRANCE")
        lat2, lng2 = geocode_address("   10 RUE DE LA PAIX, 75002 PARIS 02, FRANCE   ")
        assert lat1 == lat2
        assert lng1 == lng2
