from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render

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
            },
            {
                "relation": [
                "delegate_permission/common.handle_all_urls",
                "delegate_permission/common.get_login_creds"
                ],
                "target": {
                    "namespace": "android_app",
                    "package_name": "gn.kinnovate.tinastock_client",
                    "sha256_cert_fingerprints": [
                        "04:F8:AB:BE:DD:60:49:4F:60:CE:C6:20:7D:3D:83:FE:FD:F8:89:49:CE:87:AA:54:7F:39:90:FC:C2:3C:BB:1F"
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
