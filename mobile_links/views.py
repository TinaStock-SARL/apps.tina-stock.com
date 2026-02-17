from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
import requests
import logging

logger = logging.getLogger(__name__)

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

def payment_page(request):
    """
    View pour afficher une page de paiement avec les meta tags Open Graph
    Récupère l'order_id depuis request.GET et fait un appel API pour récupérer les infos
    """
    order_id = request.GET.get('order_id')
    
    if not order_id:
        logger.warning("Aucun order_id fourni dans la requête")
        context = {
            'order': None,
            'error': 'Aucun identifiant de commande fourni'
        }
        return render(request, 'payment.html', context)
    
    try:
        url = f"https://api.tina-stock.com/orders/minimal-info/{order_id}/"
        response = requests.get(url)
        
        if response.status_code == 200:
            api_data = response.json()
            
            if api_data.get("success") and api_data.get("data"):
                order_data = api_data.get("data")
                
                # Construire l'URL complète de l'image
                image_url = request.build_absolute_uri(settings.MEDIA_URL + 'pay-for-me.png')
                
                # Construire l'URL complète de la page
                page_url = request.build_absolute_uri(request.get_full_path())
                
                context = {
                    'order': {
                        'order_number': order_data.get('order_number', ''),
                        'first_name': order_data.get('first_name', ''),
                        'last_name': order_data.get('last_name', ''),
                        'full_name': f"{order_data.get('first_name', '')} {order_data.get('last_name', '')}".strip(),
                        'total_amount': order_data.get('total_amount', 0),
                        'currency': order_data.get('currency', 'GNF'),
                        'order_id': order_id,
                    },
                    'image_url': image_url,
                    'page_url': page_url,
                    'error': None
                }
                return render(request, 'payment.html', context)
            else:
                context = {
                    'order': None,
                    'error': 'Données de commande invalides'
                }
                return render(request, 'payment.html', context)
        else:
            context = {
                'order': None,
                'error': f'Erreur lors de la récupération des informations (Code: {response.status_code})'
            }
            return render(request, 'payment.html', context)
            
    except Exception as e:
        context = {
            'order': None,
            'error': 'Une erreur est survenue lors de la récupération des informations'
        }
        return render(request, 'payment.html', context)
