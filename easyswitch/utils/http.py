"""
EasySwitch - HTTP Wrapper for API requests
"""
import json
import logging
from typing import Dict, Optional, Any, Union, List

import aiohttp
from aiohttp import ClientTimeout

from easyswitch.exceptions import (
    NetworkError, APIError, RateLimitError
)


logger = logging.getLogger("easyswitch.http")


class HTTPClient:
    """Asyncronous Client for APIs requests."""
    
    def __init__(
        self,
        base_url: str,
        default_headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        debug: bool = False,
        proxy: Optional[str] = None
    ):
        """
        Initialise le client HTTP.
        
        Args:
            base_url: URL de base pour toutes les requêtes
            default_headers: En-têtes par défaut à inclure dans toutes les requêtes
            timeout: Délai d'attente en secondes
            debug: Mode debug pour afficher plus d'informations
            proxy: URL du proxy à utiliser
        """
        self.base_url = base_url.rstrip('/')
        self.default_headers = default_headers or {}
        self.timeout = ClientTimeout(total=timeout)
        self.debug = debug
        self.proxy = proxy
        
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], List[Any], str]] = None,
        json_data: Optional[Union[Dict[str, Any], List[Any]]] = None
    ) -> Dict[str, Any]:
        """
        Effectue une requête HTTP.
        
        Args:
            method: Méthode HTTP (GET, POST, PUT, DELETE, etc.)
            endpoint: Point de terminaison (sera ajouté à l'URL de base)
            headers: En-têtes HTTP supplémentaires
            params: Paramètres de requête
            data: Données de formulaire ou corps brut
            json_data: Données JSON à envoyer dans le corps
            
        Returns:
            Dict[str, Any]: Réponse JSON
            
        Raises:
            NetworkError: En cas d'erreur réseau
            APIError: En cas d'erreur renvoyée par l'API
            RateLimitError: En cas de limitation de débit
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        # Fusionner les en-têtes
        merged_headers = {**self.default_headers}
        if headers:
            merged_headers.update(headers)
        
        if self.debug:
            logger.debug(f"Requête {method} vers {url}")
            logger.debug(f"En-têtes: {merged_headers}")
            logger.debug(f"Paramètres: {params}")
            if data:
                logger.debug(f"Données: {data}")
            if json_data:
                logger.debug(f"JSON: {json_data}")
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.request(
                    method=method,
                    url=url,
                    headers=merged_headers,
                    params=params,
                    data=data,
                    json=json_data,
                    proxy=self.proxy
                ) as response:
                    content_type = response.headers.get('Content-Type', '')
                    
                    if 'application/json' in content_type:
                        response_data = await response.json()
                    else:
                        text_response = await response.text()
                        try:
                            response_data = json.loads(text_response)
                        except json.JSONDecodeError:
                            response_data = {"raw_response": text_response}
                    
                    if self.debug:
                        logger.debug(f"Statut: {response.status}")
                        logger.debug(f"Réponse: {response_data}")
                    
                    if response.status == 429:
                        raise RateLimitError(
                            message="Limite de débit atteinte",
                            status_code=response.status,
                            raw_response=response_data
                        )
                    
                    if not 200 <= response.status < 300:
                        raise APIError(
                            message=f"Erreur API: {response.status}",
                            status_code=response.status,
                            raw_response=response_data
                        )
                    
                    return response_data
                    
        except aiohttp.ClientError as e:
            logger.error(f"Erreur réseau: {str(e)}")
            raise NetworkError(f"Erreur de communication réseau: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"Erreur de décodage JSON: {str(e)}")
            raise APIError(message=f"Réponse JSON invalide: {str(e)}")
    
    async def get(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Effectue une requête GET.
        
        Args:
            endpoint: Point de terminaison
            headers: En-têtes HTTP supplémentaires
            params: Paramètres de requête
            
        Returns:
            Dict[str, Any]: Réponse JSON
        """
        return await self._make_request("GET", endpoint, headers, params)
    
    async def post(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], str]] = None,
        json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Effectue une requête POST.
        
        Args:
            endpoint: Point de terminaison
            headers: En-têtes HTTP supplémentaires
            params: Paramètres de requête
            data: Données de formulaire ou corps brut
            json_data: Données JSON à envoyer dans le corps
            
        Returns:
            Dict[str, Any]: Réponse JSON
        """
        return await self._make_request("POST", endpoint, headers, params, data, json_data)
    
    async def put(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], str]] = None,
        json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Effectue une requête PUT.
        
        Args:
            endpoint: Point de terminaison
            headers: En-têtes HTTP supplémentaires
            params: Paramètres de requête
            data: Données de formulaire ou corps brut
            json_data: Données JSON à envoyer dans le corps
            
        Returns:
            Dict[str, Any]: Réponse JSON
        """
        return await self._make_request("PUT", endpoint, headers, params, data, json_data)
    
    async def delete(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], str]] = None,
        json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Effectue une requête DELETE.
        
        Args:
            endpoint: Point de terminaison
            headers: En-têtes HTTP supplémentaires
            params: Paramètres de requête
            data: Données de formulaire ou corps brut
            json_data: Données JSON à envoyer dans le corps
            
        Returns:
            Dict[str, Any]: Réponse JSON
        """
        return await self._make_request("DELETE", endpoint, headers, params, data, json_data)
    
    async def patch(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], str]] = None,
        json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Effectue une requête PATCH.
        
        Args:
            endpoint: Point de terminaison
            headers: En-têtes HTTP supplémentaires
            params: Paramètres de requête
            data: Données de formulaire ou corps brut
            json_data: Données JSON à envoyer dans le corps
            
        Returns:
            Dict[str, Any]: Réponse JSON
        """
        return await self._make_request("PATCH", endpoint, headers, params, data, json_data)