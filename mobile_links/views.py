from django.conf import settings
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
import requests
import logging

logger = logging.getLogger(__name__)

def is_bot_or_crawler(user_agent):
    """
    Vérifie si le User-Agent est un bot/crawler (WhatsApp, Facebook, Twitter, etc.)
    """
    if not user_agent:
        return False
    
    user_agent_lower = user_agent.lower()
    bot_keywords = [
        'whatsapp',
        'facebookexternalhit',
        'facebot',
        'twitterbot',
        'linkedinbot',
        'telegrambot',
        'slackbot',
        'skypeuripreview',
        'discordbot',
        'googlebot',
        'bingbot',
        'yandexbot',
        'baiduspider',
        'crawler',
        'spider',
        'bot'
    ]
    
    return any(keyword in user_agent_lower for keyword in bot_keywords)

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
    - Si c'est un bot/crawler (WhatsApp, Facebook, etc.) : affiche la page HTML avec meta tags
    - Si c'est un navigateur normal : redirige vers payment_url si disponible
    """
    order_id = request.GET.get('order_id')
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    is_bot = is_bot_or_crawler(user_agent)
    
    logger.info(f"Requête payment_page - order_id: {order_id}, is_bot: {is_bot}, user_agent: {user_agent[:100]}")
    
    if not order_id:
        logger.warning("Aucun order_id fourni dans la requête")
        context = {
            'order': None,
            'error': 'Aucun identifiant de commande fourni',
            'image_url': request.build_absolute_uri(settings.MEDIA_URL + 'pay-for-me.png'),
            'page_url': request.build_absolute_uri(request.get_full_path()),
        }
        return render(request, 'payment.html', context)
    
    try:
        url = f"https://dev.tina-stock.com/orders/minimal-info/{order_id}/"
        logger.debug(f"URL de l'API: {url}")
        response = requests.get(url)
        logger.debug(f"Statut de la réponse API: {response.status_code}")
        
        if response.status_code == 200:
            api_data = response.json()
            logger.info(f"Informations de commande récupérées avec succès pour order_id: {order_id}")
            
            if api_data.get("success") and api_data.get("data"):
                order_data = api_data.get("data")
                payment_url = order_data.get('payment_url')
                
                # Si c'est un navigateur normal (pas un bot) ET qu'on a un payment_url, rediriger
                if not is_bot and payment_url:
                    logger.info(f"Redirection vers payment_url pour order_id: {order_id} (navigateur normal)")
                    return HttpResponseRedirect(payment_url)
                
                # Sinon, afficher la page HTML (pour les bots ou si pas de payment_url)
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
                logger.debug(f"Affichage de la page HTML pour order_id: {order_id} (is_bot: {is_bot}, payment_url: {payment_url})")
                return render(request, 'payment.html', context)
            else:
                logger.warning(f"La réponse API ne contient pas de données valides pour order_id: {order_id}")
                context = {
                    'order': None,
                    'error': 'Données de commande invalides',
                    'image_url': request.build_absolute_uri(settings.MEDIA_URL + 'pay-for-me.png'),
                    'page_url': request.build_absolute_uri(request.get_full_path()),
                }
                return render(request, 'payment.html', context)
        else:
            logger.warning(f"Échec de la récupération des informations. Statut: {response.status_code}")
            context = {
                'order': None,
                'error': f'Erreur lors de la récupération des informations (Code: {response.status_code})',
                'image_url': request.build_absolute_uri(settings.MEDIA_URL + 'pay-for-me.png'),
                'page_url': request.build_absolute_uri(request.get_full_path()),
            }
            return render(request, 'payment.html', context)
            
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des informations de commande {order_id}: {str(e)}", exc_info=True)
        context = {
            'order': None,
            'error': 'Une erreur est survenue lors de la récupération des informations',
            'image_url': request.build_absolute_uri(settings.MEDIA_URL + 'pay-for-me.png'),
            'page_url': request.build_absolute_uri(request.get_full_path()),
        }
        return render(request, 'payment.html', context)
