from django.shortcuts import render
import requests
import logging

logger = logging.getLogger(__name__)

def format_amount_with_spaces(amount):
    """Formate un montant avec des espaces comme séparateurs de milliers"""
    try:
        amount_int = int(float(amount))
        amount_str = str(amount_int)
        formatted = ''
        for i, digit in enumerate(reversed(amount_str)):
            if i > 0 and i % 3 == 0:
                formatted = ' ' + formatted
            formatted = digit + formatted
        return formatted
    except (ValueError, TypeError):
        return str(amount)

def get_product_by_product_id(productId):
    """
    Récupère les détails d'un produit par son ID
    Args:
        productId: ID du produit
    Returns:
        {
            "success": true,
            "detail": "Détails du produit récupérés avec succès",
            "data": {
                "id": "e3859f64-9219-4dd5-8ec9-905dc0cc0b2c",
                "name": "Clé USB SanDisk 32gb",
                "description": "Clé USB SanDisk 32 GB – Rapide & Fiable\n\nLa clé USB 32 GB est idéale pour stocker et transporter facilement vos fichiers essentiels : documents, photos, vidéos et musiques. Grâce à sa vitesse de transfert élevée, vous gagnez du temps lors des copies. Son design compact et robuste permet de l’emporter partout sans risque.\n\nCapacité : 32 Go\nTransfert rapide (USB 3.1)\nCompatible Windows, macOS, Android (OTG)\nPlug & Play – aucune installation requise\nDesign métallique élégant et résistant\n\nParfaite pour les étudiants, professionnels et usage quotidien.",
                "category": "Électronique",
                "type": "simple",
                "price": 58850.0,
                "promo_price": null,
                "images": [
                    "https://media.tina-stock.com/tinastock_media_access/products-files/4.png"
                ],
                "og_image_url": "https://media.tina-stock.com/tinastock_media_access/products-files/4.png",
                "nombre_ventes": 0,
                "variants": []
            }
        }
    """
    try:
        url = f"https://api.tina-stock.com/v2/products/{productId}/detail/"
        response = requests.get(url)
        logger.debug(f"Statut de la réponse API: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return None
    except Exception as e:
        return None

class Custom404Middleware:
    """
    Middleware pour intercepter les erreurs 404 et 400 et afficher une page personnalisée
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Si la réponse est une erreur 404 ou 400, on affiche notre page personnalisée
        if response.status_code in (400, 404):
            # recuperer le param de la requete productId
            productId = request.GET.get('productId')
            product = None
            if productId:
                api_response = get_product_by_product_id(productId)
                if api_response and api_response.get("success"):
                    data = api_response.get("data")
                    price_val = data.get("price") or 0
                    promo_val = data.get("promo_price")
                    images = data.get("images") or []
                    variants = data.get("variants") or []
                    for v in variants:
                        v["formatted_price"] = format_amount_with_spaces(v.get("price", 0))
                        v["formatted_promo_price"] = format_amount_with_spaces(v.get("promo_price")) if v.get("promo_price") else None
                    product = {
                        "id": data.get("id"),
                        "name": data.get("name"),
                        "description": data.get("description"),
                        "category": data.get("category"),
                        "type": data.get("type", "simple"),
                        "image": images[0] if images else None,
                        "images": images,
                        "price": price_val,
                        "formatted_price": format_amount_with_spaces(price_val),
                        "promo_price": promo_val,
                        "formatted_promo_price": format_amount_with_spaces(promo_val) if promo_val else None,
                        "og_url": f"https://apps.tina-stock.com/product_detail?productId={productId}",
                        "og_image_url": data.get("og_image_url") or (images[0] if images else None),
                        "nombre_ventes": data.get("nombre_ventes", 0),
                        "variants": variants,
                    }
                
            context = {
                "product": product,
                "request": request,
            }
            return render(request, "404.html", context, status=200)
        
        return response

