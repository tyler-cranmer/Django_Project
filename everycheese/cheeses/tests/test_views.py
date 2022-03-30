import pytest
from pytest_django.asserts import assertContains
from django.urls import reverse
from .factories import CheeseFactory, cheese
from ..models import Cheese
from ..views import (
    CheeseCreateView,
    CheeseListView,
    CheeseDetailView,
    CheeseUpdateView) 

from .factories import UserFactory

@pytest.fixture
def user():
    return UserFactory()

pytestmark = pytest.mark.django_db  

def test_good_cheese_update_view(client, user, cheese):
    # Authenticate the user
    client.force_login(user)
    # Get the URL
    url = reverse("cheeses:update",
        kwargs={"slug": cheese.slug})
    # Fetch the GET request for our new cheese
    response = client.get(url)
    # Test that the response is valid
    assertContains(response, "Update Cheese")


def test_good_cheese_list_view_expanded(rf):
    url = reverse("cheeses:list")
    request = rf.get(url)
    callable_obj = CheeseListView.as_view()
    response = callable_obj(request)
    assertContains(response, 'Cheese List')

def test_good_cheese_list_view(rf):
    request = rf.get(reverse("cheese:list"))
    response = CheeseListView.as_view()(request)
    assertContains(response, 'Cheese List')

def test_good_cheese_detail_view(rf, cheese):
    url = reverse("cheese:detail", kwargs={'slug':cheese.slug})
    request = rf.get(url)

    callable_obj = CheeseDetailView.as_view()
    response = callable_obj(request, slug=cheese.slug)
    assertContains(response, cheese.name)


def test_good_cheese_create_view(client,user):
    client.force_login(user)
    url = reverse("cheeses:add")
    response = client.get(url)
    assert response.status_code == 200

def test_detail_contains_cheese_data(rf):
    cheese = CheeseFactory()
    url = reverse("cheese:detail", kwargs={'slug': cheese.slug})
    request = rf.get(url)
    callable_obj = CheeseDetailView.as_view()
    response = callable_obj(request, slug=cheese.slug)
    assertContains(response, cheese.name)
    assertContains(response, cheese.get_firmness_display())
    assertContains(response, cheese.country_of_origin.name)

def test_cheese_create_form_valid(client, user):
    client.force_login(user)
    form_data={
        "name": "Paski Sir",
        "description" : "A salty son of a bitch",
        "firmness" : Cheese.Firmness.HARD,
    }

    url = reverse("cheese:add")
    response = client.post(url, form_data)

    assert response.status_code == 302

    cheese =  Cheese.objects.get(name="Paski Sir")
    assert cheese.description == "A salty son of a bitch"
    assert cheese.creator == user

def test_cheese_create_correct_title(client, user):
    """Page title for CheeseCreateView should be Add Cheese."""
    # Authenticate the user
    client.force_login(user)
    # Call the cheese add view
    response = client.get(reverse("cheeses:add"))
    # Confirm that 'Add Cheese' is in the rendered HTML
    assertContains(response, "Add Cheese")

def test_cheese_update(client, user, cheese):
    """POST request to CheeseUpdateView updates a cheese
        and redirects.
    """
    # Authenticate the user
    client.force_login(user)
    # Make a request for our new cheese
    form_data = {
        "name": cheese.name,
        "description": "Something new",
        "firmness": cheese.firmness,
    }
    url = reverse("cheeses:update", 
        kwargs={"slug": cheese.slug})
    response = client.post(url, form_data)

    # Check that the cheese has been changed
    cheese.refresh_from_db()
    assert cheese.description == "Something new"
