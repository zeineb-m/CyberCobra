import json
from django.shortcuts import render
from django.http import HttpResponse
from .models import Report
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializer import ReportSerializer
import google.generativeai as genai


# Create your views here.
# request -> response
# request handler

@api_view(['GET'])
def get_reports(request):
    return Response(ReportSerializer(Report.objects.all(), many=True).data)

@api_view(['POST'])
def create_report(request):
    serializer = ReportSerializer(data = request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(status= status.HTTP_201_CREATED )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(["PUT", "GET", "DELETE"])
def specific_report(request, pk):
    try:
        report = Report.objects.get(pk=pk)
    except Report.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == "GET" :
        serializer = ReportSerializer(report)
        return Response(serializer.data)
    
    elif request.method == "PUT":
        serializer = ReportSerializer(report, data= request.data)
        if serializer.is_valid() :
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == "DELETE":
        report.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


from rest_framework import status

@api_view(["POST"])
def summarize_report(request):      
    # With DRF, use request.data (already parsed JSON)
    subject = request.data.get('subject', '')
    body = request.data.get('body', '')
    model_name = "gemini-2.5-flash"
    context = f"""
           Summarize this report: subject: "{subject}. Body: {body}"
        """
    try:
        # New way:
        genai.configure(api_key="AIzaSyBuzdqLkRf0ZRjJWE5G9590eDzrSttM5co")
        model = genai.GenerativeModel(model_name)
        # Step 1: Generate SPARQL query from AI
        response = model.generate_content(context)

        response_text = response.text if hasattr(response, "text") else str(response)

              # Fix: Use correct Response parameters (data and status)
        return Response(
            data={"message": response_text},
            status=status.HTTP_200_OK
        )   
    
    except Exception as e:
        # Fix: Use correct Response parameters
        return Response(
            data={"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )