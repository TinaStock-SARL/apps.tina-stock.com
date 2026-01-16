from django.shortcuts import render


class Custom404Middleware:
    """
    Middleware pour intercepter les erreurs 404 et 400 et afficher une page personnalisée
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Si la réponse est une erreur 404 ou 400, on affiche notre page personnalisée
        if response.status_code == 404:
            return render(request, '404.html', status=404)
        elif response.status_code == 400:
            return render(request, '404.html', status=400)
        
        return response

