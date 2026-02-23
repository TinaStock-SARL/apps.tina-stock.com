from django.conf import settings
from django.http import JsonResponse
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

def format_amount_with_spaces(amount):
    """
    Formate un montant avec des espaces comme séparateurs de milliers
    Exemple: 192000 -> "192 000"
    """
    try:
        amount_int = int(float(amount))
        amount_str = str(amount_int)
        # Ajouter des espaces tous les 3 chiffres en partant de la fin
        formatted = ''
        for i, digit in enumerate(reversed(amount_str)):
            if i > 0 and i % 3 == 0:
                formatted = ' ' + formatted
            formatted = digit + formatted
        return formatted
    except (ValueError, TypeError):
        return str(amount)

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
    View pour afficher la page de paiement avec les informations de commande et les produits.
    Affiche les produits groupés par lieu, puis un bouton "Payer pour [Nom]" qui redirige vers payment_url.
    """
    order_id = request.GET.get('orderId')
    
    if not order_id:
        context = {
            'order': None,
            'error': 'Aucun identifiant de commande fourni',
            'image_url': request.build_absolute_uri(settings.MEDIA_URL + 'pay-for-me.png'),
            'page_url': request.build_absolute_uri(request.get_full_path()),
        }
        return render(request, 'payment.html', context)
    
    try:
        url = f"https://api.tina-stock.com/v1/orders/minimal-info/{order_id}/"
        response = requests.get(url)
        
        if response.status_code == 200:
            api_data = response.json()
            
            if api_data.get("success") and api_data.get("data"):
                order_data = api_data.get("data")
                
                image_url = request.build_absolute_uri(settings.MEDIA_URL + 'pay-for-me.png')
                page_url = request.build_absolute_uri(request.get_full_path())
                delivery_amount = order_data.get('delivery_amount') or order_data.get('delivery_fee') or 0
                total_amount = order_data.get('total_amount', 0)
                subtotal_amount = order_data.get('subtotal_amount') or order_data.get('items_total') or (total_amount - delivery_amount)
                full_name = f"{order_data.get('first_name', '')} {order_data.get('last_name', '')}".strip()
                
                # Formater les montants dans orders_by_location
                orders_by_location = order_data.get('orders_by_location', [])
                for loc in orders_by_location:
                    for order in loc.get('orders', []):
                        for item in order.get('items', []):
                            item['formatted_unit_price'] = format_amount_with_spaces(item.get('unit_price', 0))
                            item['formatted_total_price'] = format_amount_with_spaces(item.get('total_price', 0))
                
                context = {
                    'order': {
                        'order_number': order_data.get('order_number', ''),
                        'first_name': order_data.get('first_name', ''),
                        'last_name': order_data.get('last_name', ''),
                        'full_name': full_name or 'Client',
                        'subtotal_amount': subtotal_amount,
                        'formatted_subtotal': format_amount_with_spaces(subtotal_amount),
                        'delivery_amount': delivery_amount,
                        'formatted_delivery': format_amount_with_spaces(delivery_amount),
                        'total_amount': total_amount,
                        'formatted_amount': format_amount_with_spaces(total_amount),
                        'currency': order_data.get('currency', 'GNF'),
                        'payment_url': order_data.get('payment_url'),
                        'reference': order_data.get('reference', ''),
                        'orders_by_location': orders_by_location,
                    },
                    'image_url': image_url,
                    'page_url': page_url,
                    'error': None
                }
                return render(request, 'payment.html', context)
            else:
                context = {
                    'order': None,
                    'error': 'Données de commande invalides',
                    'image_url': request.build_absolute_uri(settings.MEDIA_URL + 'pay-for-me.png'),
                    'page_url': request.build_absolute_uri(request.get_full_path()),
                }
                return render(request, 'payment.html', context)
        else:
            context = {
                'order': None,
                'error': f'Erreur lors de la récupération des informations (Code: {response.status_code})',
                'image_url': request.build_absolute_uri(settings.MEDIA_URL + 'pay-for-me.png'),
                'page_url': request.build_absolute_uri(request.get_full_path()),
            }
            return render(request, 'payment.html', context)
            
    except Exception as e:
        context = {
            'order': None,
            'error': 'Une erreur est survenue lors de la récupération des informations',
            'image_url': request.build_absolute_uri(settings.MEDIA_URL + 'pay-for-me.png'),
            'page_url': request.build_absolute_uri(request.get_full_path()),
        }
        return render(request, 'payment.html', context)


def cart_shared_result(request):
    """
    View pour afficher la page du panier partagé avec les meta tags Open Graph
    Récupère le code partagé depuis request.GET (param: code)
    """
    shared_code = request.GET.get('code')
    
    if not shared_code:
        logger.warning("Aucun code partagé fourni dans la requête")
        context = {
            'cart': None,
            'error': 'Aucun code de panier partagé fourni',
            'image_url': request.build_absolute_uri(settings.MEDIA_URL + 'pay-for-me.png'),
            'page_url': request.build_absolute_uri(request.get_full_path()),
        }
        return render(request, 'cart_shared_result.html', context)
    
    try:
        url = f"https://api.tina-stock.com/v1/shared-cart/{shared_code}/"
        logger.info(f"Récupération du panier partagé pour code: {shared_code}")
        response = requests.get(url)
        logger.debug(f"Statut de la réponse API: {response.status_code}")
        
        if response.status_code == 200:
            api_data = response.json()
            
            if api_data.get("success") and api_data.get("data"):
                cart_data = api_data.get("data")
                
                # URLs pour OG
                page_url = request.build_absolute_uri(request.get_full_path())
                image_url = request.build_absolute_uri(settings.MEDIA_URL + 'pay-shared-cart.png')
                
                # Formater les montants
                total_amount = cart_data.get('total_amount', 0)
                delivery = cart_data.get('delivery') or {}
                total_delivery_fee = delivery.get('total_delivery_fee', 0) if isinstance(delivery, dict) else 0
                grand_total = total_amount + total_delivery_fee
                
                # Préparer les items avec montants formatés
                items = cart_data.get('items', [])
                for item in items:
                    item['formatted_price'] = format_amount_with_spaces(item.get('price', 0))
                    item['formatted_total_price'] = format_amount_with_spaces(item.get('total_price', 0))
                
                context = {
                    'cart': {
                        'share_code': cart_data.get('share_code', ''),
                        'shared_cart_id': cart_data.get('shared_cart_id', ''),
                        'items': items,
                        'total_amount': total_amount,
                        'formatted_total_amount': format_amount_with_spaces(total_amount),
                        'total_delivery_fee': total_delivery_fee,
                        'formatted_total_delivery_fee': format_amount_with_spaces(total_delivery_fee),
                        'grand_total': grand_total,
                        'formatted_grand_total': format_amount_with_spaces(grand_total),
                        'delivery': delivery,
                        'expires_at': cart_data.get('expires_at'),
                        'is_active': cart_data.get('is_active', False),
                        'is_paid': cart_data.get('is_paid', False),
                        'qr_code_url': cart_data.get('qr_code_url'),
                        'currency': 'GNF',
                    },
                    'image_url': image_url,
                    'page_url': page_url,
                    'error': None,
                }
                logger.info(f"Panier partagé récupéré avec succès: {shared_code}")
                return render(request, 'cart_shared_result.html', context)
            else:
                logger.warning(f"Réponse API invalide pour code: {shared_code}")
                context = {
                    'cart': None,
                    'error': 'Panier partagé introuvable ou invalide',
                    'image_url': request.build_absolute_uri(settings.MEDIA_URL + 'pay-for-me.png'),
                    'page_url': request.build_absolute_uri(request.get_full_path()),
                }
                return render(request, 'cart_shared_result.html', context)
        else:
            logger.warning(f"Échec récupération panier partagé. Statut: {response.status_code}")
            context = {
                'cart': None,
                'error': f'Impossible de charger le panier (Code: {response.status_code})',
                'image_url': request.build_absolute_uri(settings.MEDIA_URL + 'pay-for-me.png'),
                'page_url': request.build_absolute_uri(request.get_full_path()),
            }
            return render(request, 'cart_shared_result.html', context)
            
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du panier partagé {shared_code}: {str(e)}", exc_info=True)
        context = {
            'cart': None,
            'error': 'Une erreur est survenue lors du chargement du panier',
            'image_url': request.build_absolute_uri(settings.MEDIA_URL + 'pay-for-me.png'),
            'page_url': request.build_absolute_uri(request.get_full_path()),
        }
        return render(request, 'cart_shared_result.html', context)
