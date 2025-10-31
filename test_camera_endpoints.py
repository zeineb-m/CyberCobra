"""
Test script to verify the Camera CRUD endpoints work correctly
Run this after starting the Django server
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def get_token():
    """Get JWT token for authentication"""
    response = requests.post(f"{BASE_URL}/auth/login/", json={
        "username": "admin",  # Update with your credentials
        "password": "admin"   # Update with your credentials
    })
    if response.status_code == 200:
        return response.json()["access"]
    else:
        print(f"Login failed: {response.status_code}")
        print(response.text)
        return None

def test_list_cameras(token):
    """Test GET /api/cameras/"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/cameras/", headers=headers)
    print(f"\n1. List Cameras (GET /api/cameras/)")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Found {len(data)} cameras")
        return data
    else:
        print(f"   Error: {response.text}")
    return []

def test_create_camera(token):
    """Test POST /api/cameras/"""
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "name": "Test Camera",
        "zone": "Test Zone",
        "ip_address": "192.168.1.100",
        "resolution": "1080p",
        "status": "RECORDING"
    }
    response = requests.post(f"{BASE_URL}/cameras/", json=data, headers=headers)
    print(f"\n2. Create Camera (POST /api/cameras/)")
    print(f"   Status: {response.status_code}")
    if response.status_code == 201:
        created = response.json()
        print(f"   Created camera with ID: {created['id_camera']}")
        print(f"   Name: {created['name']}, Zone: {created['zone']}")
        return created
    else:
        print(f"   Error: {response.text}")
    return None

def test_get_camera(token, pk):
    """Test GET /api/cameras/{id}/"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/cameras/{pk}/", headers=headers)
    print(f"\n3. Get Single Camera (GET /api/cameras/{pk}/)")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Name: {data['name']}, IP: {data['ip_address']}, Status: {data['status']}")
        return data
    else:
        print(f"   Error: {response.text}")
    return None

def test_update_camera(token, pk):
    """Test PUT /api/cameras/{id}/"""
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "name": "Updated Test Camera",
        "zone": "Updated Zone",
        "ip_address": "192.168.1.101",
        "resolution": "4K",
        "status": "MAINTENANCE"
    }
    response = requests.put(f"{BASE_URL}/cameras/{pk}/", json=data, headers=headers)
    print(f"\n4. Update Camera (PUT /api/cameras/{pk}/)")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        updated = response.json()
        print(f"   Updated: {updated['name']}, {updated['resolution']}, {updated['status']}")
        return updated
    else:
        print(f"   Error: {response.text}")
    return None

def test_partial_update_camera(token, pk):
    """Test PATCH /api/cameras/{id}/"""
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "status": "OFFLINE"
    }
    response = requests.patch(f"{BASE_URL}/cameras/{pk}/", json=data, headers=headers)
    print(f"\n5. Partial Update (PATCH /api/cameras/{pk}/)")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        updated = response.json()
        print(f"   Updated status to: {updated['status']}")
        return updated
    else:
        print(f"   Error: {response.text}")
    return None

def test_delete_camera(token, pk):
    """Test DELETE /api/cameras/{id}/"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(f"{BASE_URL}/cameras/{pk}/", headers=headers)
    print(f"\n6. Delete Camera (DELETE /api/cameras/{pk}/)")
    print(f"   Status: {response.status_code}")
    if response.status_code == 204:
        print(f"   Successfully deleted camera {pk}")
        return True
    else:
        print(f"   Error: {response.text}")
    return False

def main():
    print("=" * 60)
    print("Testing Camera CRUD API Endpoints")
    print("=" * 60)
    
    # Get authentication token
    print("\n0. Authenticating...")
    token = get_token()
    if not token:
        print("❌ Authentication failed. Please update credentials in the script.")
        return
    print("   ✓ Authentication successful")
    
    # Test all CRUD operations
    test_list_cameras(token)
    
    created = test_create_camera(token)
    if created:
        pk = created['id_camera']
        test_get_camera(token, pk)
        test_update_camera(token, pk)
        test_partial_update_camera(token, pk)
        test_delete_camera(token, pk)
    
    print("\n" + "=" * 60)
    print("Testing Complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
