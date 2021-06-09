import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from unittest.mock import patch
from uuid import UUID

from users.masking import mask_string, mask_uuid, unmask_string, unmask_uuid
from users.models import Profile
from users.tests.conftest import PROFILE_TEST_DATA, TEST_USER_PASSWORD
from users.tests.utils import _create_token

User = get_user_model()


@pytest.mark.django_db
def test_profile_get_list(profile, api_client):
    # Listing profiles should not be not allowed, since a user should
    # not be able to view anybody else's profiles.
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {_create_token(profile)}")
    response = api_client.get(reverse("users:profile-list"))
    assert response.status_code == 405


@pytest.mark.django_db
def test_profile_get_detail(profile, api_client):
    # The user should be able to retrieve their own profile
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {_create_token(profile)}")
    response = api_client.get(
        reverse("users:profile-detail", args=(mask_uuid(profile.pk),))
    )
    assert response.status_code == 200
    assert response.data == PROFILE_TEST_DATA


@pytest.mark.django_db
def test_profile_get_detail_fails_if_not_own_profile(
    profile, other_profile, api_client
):
    # The user should not be able to view other users' profiles
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {_create_token(profile)}")
    response = api_client.get(
        reverse("users:profile-detail", args=(mask_uuid(other_profile.pk),))
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_profile_get_detail_fails_if_not_authenticated(profile, api_client):
    # An unauthenticated user should not be able to view any profiles
    response = api_client.get(
        reverse("users:profile-detail", args=(mask_uuid(profile.pk),))
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_profile_post(api_client):
    # Creating new profile should be allowed as an unauthenticated user
    response = api_client.post(reverse("users:profile-list"), PROFILE_TEST_DATA)
    assert response.status_code == 201
    user = User.objects.get()
    # Response should contain masked profile ID and password
    assert user.profile.pk == unmask_uuid(response.data["profile_id"])
    assert user.profile.pk == UUID(PROFILE_TEST_DATA["id"])
    assert user.check_password(unmask_string(response.data["password"]))
    # We should be able to look up a profile based on the unmasked username
    profile = Profile.objects.get(pk=unmask_uuid(response.data["profile_id"]))
    profile_data = PROFILE_TEST_DATA.copy()
    # The created profile should contain all the data from the request
    for attr in ["first_name", "last_name", "email"]:
        assert str(getattr(profile.user, attr)) == str(profile_data.pop(attr))
    for attr, value in profile_data.items():
        assert str(getattr(profile, attr)) == str(value)


@pytest.mark.django_db
def test_profile_put(profile, api_client):
    # A user should be able to update their own profile
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {_create_token(profile)}")
    url = reverse("users:profile-detail", args=(mask_uuid(profile.pk),))
    put_data = {
        **PROFILE_TEST_DATA,
        "first_name": "Maija",
        "street_address": "Kauppakatu 23",
    }
    response = api_client.put(url, put_data)
    assert response.status_code == 200
    assert response.data == put_data
    profile.refresh_from_db()
    for attr in ["first_name", "last_name", "email"]:
        assert str(getattr(profile.user, attr)) == str(put_data.pop(attr))
    for attr, value in put_data.items():
        assert str(getattr(profile, attr)) == str(value)


@pytest.mark.django_db
def test_profile_put_fails_if_not_own_profile(profile, other_profile, api_client):
    # A user should not be able to update other users' profiles
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {_create_token(profile)}")
    url = reverse("users:profile-detail", args=(mask_uuid(other_profile.pk),))
    put_data = {
        **PROFILE_TEST_DATA,
        "first_name": "Maija",
        "street_address": "Kauppakatu 23",
    }
    response = api_client.put(url, put_data)
    assert response.status_code == 403


@pytest.mark.django_db
def test_profile_put_fails_if_not_authenticated(profile, api_client):
    # An unauthenticated user should not be able to update any profiles
    response = api_client.put(
        reverse("users:profile-detail", args=(mask_uuid(profile.pk),)),
        PROFILE_TEST_DATA,
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_profile_patch(profile, api_client):
    # Partial updates should not be allowed
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {_create_token(profile)}")
    url = reverse("users:profile-detail", args=(mask_uuid(profile.pk),))
    response = api_client.patch(
        url, {"first_name": "Maija", "street_address": "Kauppakatu 23"}
    )
    assert response.status_code == 405


@pytest.mark.django_db
def test_profile_patch_fails_if_not_authenticated(profile, api_client):
    # An unauthenticated user should not be able to partially update any profiles
    response = api_client.patch(
        reverse("users:profile-detail", args=(mask_uuid(profile.pk),)),
        PROFILE_TEST_DATA,
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_profile_delete(profile, api_client):
    # A user should be able to delete their own profile
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {_create_token(profile)}")
    url = reverse("users:profile-detail", args=(mask_uuid(profile.pk),))
    response = api_client.delete(url)
    assert response.status_code == 204
    assert not User.objects.filter(pk=profile.user.pk).exists()
    assert not Profile.objects.filter(pk=profile.pk).exists()


@pytest.mark.django_db
def test_profile_delete_fails_if_not_own_profile(profile, other_profile, api_client):
    # A user should not be able to delete other users' profiles
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {_create_token(profile)}")
    url = reverse("users:profile-detail", args=(mask_uuid(other_profile.pk),))
    response = api_client.delete(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_profile_delete_fails_if_not_authenticated(profile, api_client):
    # An unauthenticated user should not be able to delete any profiles
    response = api_client.delete(
        reverse("users:profile-detail", args=(mask_uuid(profile.pk),)),
        PROFILE_TEST_DATA,
    )
    assert response.status_code == 401


@pytest.mark.django_db
@patch.object(Profile.objects, "create")
def test_profile_creation_is_rolled_back_on_profile_create_error(
    patched_profile_objects_create, api_client
):
    patched_profile_objects_create.side_effect = Exception
    with pytest.raises(Exception):
        api_client.post(reverse("users:profile-list"), PROFILE_TEST_DATA)
    assert not User.objects.filter(
        first_name=PROFILE_TEST_DATA["first_name"],
        last_name=PROFILE_TEST_DATA["last_name"],
        email=PROFILE_TEST_DATA["email"],
    ).exists()
    assert not Profile.objects.exists()


@pytest.mark.django_db
def test_profile_update_is_rolled_back_on_profile_save_error(profile, api_client):
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {_create_token(profile)}")
    with patch.object(Profile, "save") as patched_profile_save:
        patched_profile_save.side_effect = Exception
        with pytest.raises(Exception):
            url = reverse("users:profile-detail", args=(mask_uuid(profile.pk),))
            put_data = {
                **PROFILE_TEST_DATA,
                "first_name": "Maija",
                "street_address": "Kauppakatu 23",
            }
            api_client.put(url, put_data)
    profile.refresh_from_db()
    assert profile.user.first_name == PROFILE_TEST_DATA["first_name"]
    assert profile.street_address == PROFILE_TEST_DATA["street_address"]


@pytest.mark.django_db
def test_token(profile, api_client):
    # The user should receive refresh and access tokens
    # when logging in with valid credentials.
    credentials = {
        "profile_id": mask_uuid(profile.pk),
        "password": mask_string(TEST_USER_PASSWORD),
    }
    response = api_client.post(reverse("token_obtain_pair"), credentials)
    assert response.status_code == 200
    assert "refresh" in response.data
    assert "access" in response.data


@pytest.mark.django_db
def test_token_fails_if_credentials_are_invalid(profile, api_client):
    # The user should not receive any tokens if the credentials are invalid
    credentials = {
        "profile_id": mask_uuid(profile.pk),
        "password": mask_string("wrong password"),
    }
    response = api_client.post(reverse("token_obtain_pair"), credentials)
    assert response.status_code == 401


@pytest.mark.django_db
def test_token_refresh(profile, api_client):
    # The user should receive an access token, given a valid refresh token
    refresh_token = RefreshToken.for_user(profile.user)
    post_data = {"refresh": str(refresh_token)}
    response = api_client.post(reverse("token_refresh"), post_data)
    assert response.status_code == 200
    assert "access" in response.data
