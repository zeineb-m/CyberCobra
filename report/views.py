from django.shortcuts import render
from django.http import HttpResponse
from .models import Report
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializer import ReportSerializer


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
