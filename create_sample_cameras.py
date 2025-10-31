"""
Quick script to add sample cameras to the database
Run this to populate the database with example data matching the screenshot
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CyberCobra.settings')
django.setup()

from gestion_camera.models import Camera

def create_sample_cameras():
    """Create sample cameras matching the screenshot design"""
    
    # Clear existing cameras (optional)
    # Camera.objects.all().delete()
    
    sample_cameras = [
        {
            'name': 'Front Gate',
            'zone': 'Zone A',
            'ip_address': '192.168.1.10',
            'resolution': '4K',
            'status': Camera.Status.RECORDING
        },
        {
            'name': 'Parking Lot',
            'zone': 'Zone B',
            'ip_address': '192.168.1.11',
            'resolution': '1080p',
            'status': Camera.Status.RECORDING
        },
        {
            'name': 'Main Entrance',
            'zone': 'Zone A',
            'ip_address': '192.168.1.12',
            'resolution': '2K',
            'status': Camera.Status.RECORDING
        },
        {
            'name': 'Rear Exit',
            'zone': 'Zone C',
            'ip_address': '192.168.1.13',
            'resolution': '1080p',
            'status': Camera.Status.OFFLINE
        },
        {
            'name': 'Server Room',
            'zone': 'Zone D',
            'ip_address': '192.168.1.14',
            'resolution': '4K',
            'status': Camera.Status.MAINTENANCE
        },
    ]
    
    created_count = 0
    for camera_data in sample_cameras:
        camera, created = Camera.objects.get_or_create(
            name=camera_data['name'],
            defaults=camera_data
        )
        if created:
            created_count += 1
            print(f"✓ Created: {camera.name} - {camera.zone} ({camera.ip_address})")
        else:
            print(f"• Already exists: {camera.name}")
    
    print(f"\n{created_count} new cameras added to database")
    print(f"Total cameras in database: {Camera.objects.count()}")

if __name__ == "__main__":
    print("=" * 60)
    print("Creating Sample Cameras")
    print("=" * 60)
    create_sample_cameras()
    print("\nYou can now access the cameras in:")
    print("  - Django Admin: http://localhost:8000/admin/")
    print("  - Frontend: http://localhost:3000/cameras")
    print("  - API: http://localhost:8000/api/cameras/")
