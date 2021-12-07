import os
from django.http.response import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from carhub.models import UserProxy, Car


@csrf_exempt
def protected_media(request, folder, file):
    document=None
    if folder == 'rc':
        document = get_object_or_404(Car, rc=os.path.join(folder, file).replace("\\","/"))
        document.dl = None
    elif folder == 'dl':
        document = get_object_or_404(UserProxy, dl=os.path.join(folder, file).replace("\\","/"))
        document.rc = None
    else:
        return JsonResponse({'message': "Not Found."}, status = 404)
    if request.user == document.user or request.user.is_superuser :
        response = FileResponse(document.dl or document.rc)
        return response
    else:
        return JsonResponse({'message': "Not authorized to access this media."}, status = 401)