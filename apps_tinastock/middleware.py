from django.shortcuts import render
import requests
import logging

logger = logging.getLogger(__name__)

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
                "nombre_ventes": 0,
                "variants": []
            }
        }
    """
    try:
        url = f"https://api.tina-stock.com/v1/products/{productId}/detail/"
        logger.info(f"Récupération du produit avec l'ID: {productId}")
        logger.debug(f"URL de l'API: {url}")
        response = requests.get(url)
        logger.debug(f"Statut de la réponse API: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Produit récupéré avec succès: {productId}")
            return data
        else:
            logger.warning(f"Échec de la récupération du produit {productId}. Statut: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du produit {productId}: {str(e)}", exc_info=True)
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
            logger.info(f"Erreur {response.status_code} interceptée pour: {request.path}")
            # recuperer le param de la requete productId
            productId = request.GET.get('productId')
            logger.debug(f"Paramètre productId reçu: {productId}")
            product = None
            if productId:
                logger.info(f"Tentative de récupération du produit avec productId: {productId}")
                api_response = get_product_by_product_id(productId)
                if api_response and api_response.get("success"):
                    data = api_response.get("data")
                    logger.info(f"Produit récupéré avec succès depuis l'API: {productId}")

                    product = {
                        "id": data.get("id"),
                        "name": data.get("name"),
                        "description": data.get("description"),
                        "image": data.get("images")[0] if data.get("images") else None,
                        "price": data.get("price"),
                    }
                    logger.debug(f"Produit formaté: {product.get('name')}")
                else:
                    logger.warning(f"Impossible de récupérer le produit {productId} depuis l'API")
            else:
                logger.debug("Aucun productId fourni dans la requête")
            context = {
                "product": product,
                "request": request,
            }
            logger.debug(f"Rendu de la page 404.html avec produit: {'présent' if product else 'absent'}")
            return render(request, "404.html", context, status=200)
        
        return response

