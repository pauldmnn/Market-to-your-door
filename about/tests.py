import pytest
from about.models import AboutUs


@pytest.mark.django_db
class TestAboutUsModelAndView:

    def test_about_us_model_str(self):
        about = AboutUs.objects.create(title="Our Story", content="We deliver fresh produce.")
        assert str(about) == "About Page Content"


