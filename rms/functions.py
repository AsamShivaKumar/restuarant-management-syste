from rms.models import Report
from rms.report_generation import generate_report_async
from django.http import HttpResponse
import json

def genReport(request):
    report_id = len(Report.objects.all()) + 1
    new_report = Report(url = 'report' + str(report_id) + '.csv', status = 'pending')
    new_report.save()
    generate_report_async(new_report.url,new_report.id)

    return HttpResponse(json.dumps({'report_id': report_id}),content_type='application/json')

def getReport(request):
    report_id = request.GET.get('report_id')
    if(report_id == None): return HttpResponse("Provide report id!")
    report = Report.objects.get(id=report_id)

    if(report.status == 'pending'): return HttpResponse("Running!")
    else: 
        res = HttpResponse(content_type='text/csv')
        res['Content-Disposition'] = 'attachment; filename="' + report.url + '"'
        return res