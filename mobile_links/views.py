from django.conf import settings
from django.http import JsonResponse

def assetlinks(request):
    return JsonResponse(
        [
            {
                "relation": ["delegate_permission/common.handle_all_urls"],
                "target": {
                    "namespace": "android_app",
                    "package_name": "com.tinastock.tinastock",
                    "sha256_cert_fingerprints": [
                        settings.SHA_256  # À remplacer
                    ]
                }
            }
        ],
        safe=False
    )


def apple_app_site_association(request):
    return JsonResponse({
        "applinks": {
            "apps": [],
            "details": [
                {
                    "appID": "SSX32PJDA3.com.tinastock.tinastock",
                    "paths": ["*"]
                }
            ]
        }
    })
