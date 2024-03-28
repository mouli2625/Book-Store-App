import pytest
import responses

@pytest.fixture

def mock_authentication():
    with responses.RequestsMock(assert_all_requests_are_fired=False):
        res=responses.add(
            method=responses.GET
            url='http://127.0.0.1:5000/getUser?user_id=1'
            json={
                'user_id':1,
                'username':'Mouli',
                'password':'Mouli^123',
                'email':'chandramouli3939@gmail.com'
                'is_superkey':'True',
                'is_verified':'True'
            }
        )