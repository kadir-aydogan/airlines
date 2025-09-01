from rest_framework.renderers import JSONRenderer

class BaseResponseJSONRenderer(JSONRenderer):
    """
    Tüm JSON responseları şu forma sarar:
    {
      "status": true,
      "message": null,
      "data": <orijinal data>
    }

    İstisnalar:
    - Zaten {status, message, data} şeklindeyse dokunma.
    - bytes/str gibi ham tipleri sarmamaya çalış (file, csv vb. için).
    """
    def render(self, data, accepted_media_type=None, renderer_context=None):
        # Exception durumlarında bizim exception handler zaten saracak.
        resp = renderer_context.get("response") if renderer_context else None
        request = renderer_context.get("request") if renderer_context else None

        # bypass header (isteğe bağlı)
        # if request and request.headers.get("X-Bypass-Base-Response") == "1":
        #     return super().render(data, accepted_media_type, renderer_context)

        # None → 204 No Content gibi durumlar
        if resp is not None:
            resp["X-Base-Response"] = "1"

        if data is None:
            wrapped = {"status": True, "message": None, "data": None}
            return super().render(wrapped, accepted_media_type, renderer_context)

        # halihazırda sarılıysa dokunma
        if isinstance(data, dict) and {"status", "message", "data"}.issubset(set(data.keys())):
            return super().render(data, accepted_media_type, renderer_context)

        # bytes/str gibi tipler: dokunma
        if isinstance(data, (bytes, str)):
            return super().render(data, accepted_media_type, renderer_context)

        wrapped = {
            "status": True,
            "message": None,
            "data": data,
        }
        return super().render(wrapped, accepted_media_type, renderer_context)