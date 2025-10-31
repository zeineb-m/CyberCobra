
import os
import json
import requests
import re
from django.conf import settings


def get_security_recommendations(address, zone_type=None, nearby_places=None):
    """
    Get AI security recommendations from Gemini API
    
    Args:
        address (str): The location address
        zone_type (str): Type of zone (school, hospital, general, etc.)
        nearby_places (list): List of nearby places with name, type, distance
        
    Returns:
        list: List of security recommendation strings
    """
    
    # Get API key from settings or environment
    api_key = getattr(settings, 'GEMINI_API_KEY', os.getenv('GEMINI_API_KEY', 'AIzaSyCLSb6C9qx62C-K32X22Q1EWFqFBoHPCDM'))
    
    if not api_key:
        print("Warning: GEMINI_API_KEY not configured")
        return get_fallback_recommendations(zone_type)
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={api_key}"
    
    # Build context with nearby places if available
    places_context = ""
    if nearby_places and len(nearby_places) > 0:
        places_list = [
            f"{p.get('name', 'Unknown')} ({p.get('type', 'place')}, {p.get('distance', 0)}m away)" 
            for p in nearby_places[:10]
        ]
        places_context = f"\nNearby places include: {', '.join(places_list)}."
    
    zone_context = f"\nZone Type: {zone_type}" if zone_type else ""
    
    prompt = f"""As a security expert, analyze this location and provide specific security recommendations:

Location: {address}{zone_context}{places_context}

IMPORTANT INSTRUCTIONS:
1. First, assess the security risk level of this location based on:
   - Type of facility (government buildings, banks, schools = higher risk)
   - Sensitivity of operations
   - Public accessibility
   - Nearby sensitive facilities
   - Potential threats

2. Based on your risk assessment, provide recommendations:
   - HIGH RISK facilities (courthouse, bank, government, military): Provide 6-8 recommendations
   - MEDIUM RISK facilities (school, hospital, commercial): Provide 4-5 recommendations  
   - LOW RISK facilities (residential, general area): Provide 2-3 recommendations

3. Each recommendation must be:
   - A single, clear, actionable statement
   - Specific to the facility type
   - Formatted as a plain text string

Focus areas to consider:
- Physical security measures
- Surveillance and monitoring
- Access control
- Perimeter security
- Emergency response
- Risk mitigation specific to nearby facilities

Return ONLY a JSON array of recommendation strings, nothing else. Format: ["recommendation 1", "recommendation 2", ...]"""
    
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 1024,
            "responseMimeType": "application/json",
            "responseSchema": {
                "type": "array",
                "items": {
                    "type": "string"
                }
            }
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('candidates') and data['candidates'][0].get('content', {}).get('parts'):
            content = data['candidates'][0]['content']['parts'][0]['text'].strip()
            
            # Try to parse as JSON array
            try:
                recommendations = json.loads(content)
                if isinstance(recommendations, list) and len(recommendations) > 0:
                    cleaned_recs = []
                    for rec in recommendations:
                        if isinstance(rec, str) and len(rec.strip()) > 10:
                            cleaned_recs.append(rec.strip())
                    
                    if cleaned_recs:
                        return cleaned_recs
            except json.JSONDecodeError:
                pass
            
            # Fallback: Extract recommendations from text
            json_match = re.search(r'\[[\s\S]*\]', content)
            if json_match:
                try:
                    recommendations = json.loads(json_match[0])
                    return [r.strip() for r in recommendations if isinstance(r, str) and len(r.strip()) > 10]
                except:
                    pass
            
            # Last resort: split by newlines
            lines = content.split('\n')
            cleaned_lines = []
            for line in lines:
                line = line.strip()
                if not line or line.startswith('[') or line.startswith(']'):
                    continue
                line = re.sub(r'^[-*•]\s*', '', line)
                line = re.sub(r'^\d+\.\s*', '', line)
                line = re.sub(r'^[""]|[""]$', '', line)
                line = line.strip().rstrip(',')
                if len(line) > 10:
                    cleaned_lines.append(line)
            
            if cleaned_lines:
                return cleaned_lines
        
        return get_fallback_recommendations(zone_type)
        
    except requests.exceptions.Timeout:
        print("AI API request timed out")
        return get_fallback_recommendations(zone_type)
    except requests.exceptions.RequestException as e:
        print(f"Error getting AI recommendations: {e}")
        return get_fallback_recommendations(zone_type)
    except Exception as e:
        print(f"Unexpected error in AI service: {e}")
        return get_fallback_recommendations(zone_type)


def get_fallback_recommendations(zone_type=None):
    """Provide fallback recommendations when AI service is unavailable"""
    
    general_recommendations = [
        "Install CCTV cameras at all entry and exit points",
        "Implement access control system with ID verification",
        "Ensure adequate perimeter lighting for night security",
        "Conduct regular security patrols of the premises",
        "Establish emergency evacuation procedures and conduct drills",
    ]
    
    high_risk_recommendations = {
        'bank': [
            "Install bullet-resistant glass at teller stations",
            "Implement dual authentication for vault access",
            "Install panic buttons at all service counters",
            "Deploy armed security personnel during business hours",
            "Install time-delay safes for cash handling",
            "Implement advanced surveillance with facial recognition",
        ],
        'government': [
            "Install vehicle barriers and checkpoints at entrance",
            "Implement metal detectors and bag screening",
            "Deploy K-9 units for regular sweeps",
            "Establish secure communication systems",
            "Create designated secure zones with restricted access",
            "Implement visitor management system with background checks",
        ],
        'school': [
            "Install lockdown systems in all classrooms",
            "Implement single point of entry with security desk",
            "Install panic buttons in administrative areas",
            "Conduct regular emergency drills with students and staff",
            "Implement visitor sign-in and ID verification system",
        ],
        'hospital': [
            "Secure pharmaceutical storage areas with controlled access",
            "Install panic buttons in emergency and psychiatric areas",
            "Implement infant security tracking system",
            "Control access to sensitive medical areas",
            "Deploy security personnel in emergency department",
        ],
    }
    
    if zone_type:
        zone_type_lower = zone_type.lower()
        for key, recs in high_risk_recommendations.items():
            if key in zone_type_lower:
                return recs
    
    return general_recommendations

