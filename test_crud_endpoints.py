"""
Test script to verify the manual CRUD endpoints work correctly
Run this after starting the Django server
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

# First, let's get a token (you'll need to update these credentials)
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

def test_list_equipements(token):
    """Test GET /api/equipements/"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/equipements/", headers=headers)
    print(f"\n1. List Equipements (GET /api/equipements/)")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Found {len(data)} equipements")
        return data
    else:
        print(f"   Error: {response.text}")
    return []

def test_create_equipement(token):
    """Test POST /api/equipements/"""
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "nom": "Test Equipment",
        "statut": "AUTORISE",
        "description": "Test equipment created via manual CRUD API"
    }
    response = requests.post(f"{BASE_URL}/equipements/", json=data, headers=headers)
    print(f"\n2. Create Equipement (POST /api/equipements/)")
    print(f"   Status: {response.status_code}")
    if response.status_code == 201:
        created = response.json()
        print(f"   Created equipement with ID: {created['id_equipement']}")
        return created
    else:
        print(f"   Error: {response.text}")
    return None

def test_get_equipement(token, pk):
    """Test GET /api/equipements/{id}/"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/equipements/{pk}/", headers=headers)
    print(f"\n3. Get Single Equipement (GET /api/equipements/{pk}/)")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Name: {data['nom']}, Status: {data['statut']}")
        return data
    else:
        print(f"   Error: {response.text}")
    return None

def test_update_equipement(token, pk):
    """Test PUT /api/equipements/{id}/"""
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "nom": "Updated Test Equipment",
        "statut": "INTERDIT",
        "description": "Updated via PUT request"
    }
    response = requests.put(f"{BASE_URL}/equipements/{pk}/", json=data, headers=headers)
    print(f"\n4. Update Equipement (PUT /api/equipements/{pk}/)")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        updated = response.json()
        print(f"   Updated: {updated['nom']}, {updated['statut']}")
        return updated
    else:
        print(f"   Error: {response.text}")
    return None

def test_partial_update_equipement(token, pk):
    """Test PATCH /api/equipements/{id}/"""
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "statut": "SOUMIS"
    }
    response = requests.patch(f"{BASE_URL}/equipements/{pk}/", json=data, headers=headers)
    print(f"\n5. Partial Update (PATCH /api/equipements/{pk}/)")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        updated = response.json()
        print(f"   Updated status to: {updated['statut']}")
        return updated
    else:
        print(f"   Error: {response.text}")
    return None

def test_delete_equipement(token, pk):
    """Test DELETE /api/equipements/{id}/"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(f"{BASE_URL}/equipements/{pk}/", headers=headers)
    print(f"\n6. Delete Equipement (DELETE /api/equipements/{pk}/)")
    print(f"   Status: {response.status_code}")
    if response.status_code == 204:
        print(f"   Successfully deleted equipement {pk}")
        return True
    else:
        print(f"   Error: {response.text}")
    return False

def main():
    print("=" * 60)
    print("Testing Manual CRUD API Endpoints")
    print("=" * 60)
    
    # Get authentication token
    print("\n0. Authenticating...")
    token = get_token()
    if not token:
        print("❌ Authentication failed. Please update credentials in the script.")
        return
    print("   ✓ Authentication successful")
    
    # Test all CRUD operations
    test_list_equipements(token)
    
    created = test_create_equipement(token)
    if created:
        pk = created['id_equipement']
        test_get_equipement(token, pk)
        test_update_equipement(token, pk)
        test_partial_update_equipement(token, pk)
        test_delete_equipement(token, pk)
    
    print("\n" + "=" * 60)
    print("Testing Complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
