from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response
from rest_framework import status as http_status

def base_response_exception_handler(exc, context):
    """
    Tüm hataları şu formda döndür:
    {
      "status": false,
      "message": <dict>,   # her zaman dict
      "data": null
    }
    """
    resp = drf_exception_handler(exc, context)

    if resp is None:
        # DRF handle etmediyse (beklenmeyen hata)
        return Response(
            {"status": False, "message": {"detail": "Internal server error"}, "data": None},
            status=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    data = resp.data

    # message'ı her zaman dict'e normalize et
    if isinstance(data, dict):
        if "detail" in data and len(data) == 1:
            # tek bir genel mesaj
            message = {"detail": str(data["detail"])}
        else:
            # field/non_field hataları -> tüm değerleri string listesine çevir
            message = {}
            for k, v in data.items():
                if isinstance(v, (list, tuple)):
                    message[k] = [str(x) for x in v]
                else:
                    message[k] = [str(v)]
    else:
        # dict değilse genel "detail" alanına koy
        message = {"detail": str(data)}

    return Response(
        {"status": False, "message": message, "data": None},
        status=resp.status_code,
        headers=resp.headers,
    )