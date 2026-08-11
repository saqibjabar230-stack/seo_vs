import random
from typing import Dict, Any, Tuple
from core.universal_model import ContentDocument
from utils.logger import get_logger
from utils.http import request_with_retry

logger = get_logger("theme_appyn")

class AppynAdapter:
    @staticmethod
    def apply_custom_fields(doc: ContentDocument, post_id: str, site_url: str, auth: Tuple[str, str], headers: Dict[str, str]) -> bool:
        """
        Pushes custom fields required by the Appyn Theme using the seo-automation endpoint.
        """
        # Determine Appyn description (fallback to excerpt or first paragraph logic)
        appyn_desc = doc.seo_metadata.meta_description
        if not appyn_desc and doc.introduction:
            appyn_desc = doc.introduction[:300] + ('...' if len(doc.introduction) > 300 else '')
            
        payload = {
            "post_id": int(post_id),
            "datos_informacion": {
                "app_status": "new",
                "descripcion": appyn_desc,
                "version": doc.custom_fields.get("version") or "1.0.0",
                "tamano": doc.custom_fields.get("size") or "50MB",
                "fecha_actualizacion": doc.custom_fields.get("updated_at") or "Just now",
                "requerimientos": doc.custom_fields.get("requirements") or "Android",
                "descargas": doc.custom_fields.get("downloads") or "10k+",
                "categoria_app": doc.custom_fields.get("category") or "GAMES",
                "os": doc.custom_fields.get("os") or "ANDROID",
                "offer": {"amount": "", "currency": "USD"},
                "rating": doc.custom_fields.get("rating") or doc.custom_fields.get("stars") or "5.0"
            },
            "datos_download": {
                "option": "links",
                "type": "apk",
                "0": {
                    "link": "#",
                    "texto": "DOWNLOAD APK"
                }
            }
        }
        
        url = f"{site_url.rstrip('/')}/wp-json/seo-automation/v1/update-meta"
        try:
            resp = request_with_retry('POST', url, json=payload, headers=headers, auth=auth, timeout=15)
            if resp.status_code in [200, 201]:
                logger.info(f"Appyn custom fields successfully applied for Post {post_id}.")
                return True
            else:
                logger.warning(f"Appyn update failed with status {resp.status_code}")
        except Exception as e:
            logger.error(f"Failed to update Appyn custom fields: {e}")
            
        return False
