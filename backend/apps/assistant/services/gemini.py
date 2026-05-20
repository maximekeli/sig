"""Client Google Gemini — assistant conversationnel SIG Sols Togo."""
import json
import logging

from django.conf import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Tu es l'assistant IA de SIG Sols Togo (DISIA / DUSOL), plateforme de cartographie \
des sols de la région Maritime au Togo.

Tu aides les utilisateurs sur :
- la cartographie et l'interprétation des sols (pH, types, fertilité) ;
- les parcelles agricoles et l'analyse spatiale ;
- les données NASA (NDVI, humidité SMAP) ;
- le quiz pédagogique et les fiches éducatives ;
- la navigation et les fonctionnalités de la plateforme.

Réponds en français, de façon claire et pédagogique. Si le contexte JSON fourni \
contient des données précises (parcelle, point de sol, quiz), appuie-toi dessus. \
Sinon, donne des conseils généraux sans inventer de valeurs chiffrées locales. \
Reste concis (3–8 phrases sauf demande de détail)."""


def is_available():
    return bool(getattr(settings, 'GEMINI_API_KEY', ''))


def chat_with_gemini(message, history=None, context=None):
    """
    Envoie un message à Gemini avec historique et contexte applicatif.
    Retourne (reply_text, error_message).
    """
    api_key = getattr(settings, 'GEMINI_API_KEY', '')
    if not api_key:
        return None, 'Assistant IA non configuré (GEMINI_API_KEY manquante).'

    try:
        import google.generativeai as genai
    except ImportError:
        return None, 'Bibliothèque google-generativeai non installée sur le serveur.'

    model_name = getattr(settings, 'GEMINI_MODEL', 'gemini-2.0-flash')
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name, system_instruction=SYSTEM_PROMPT)

    gemini_history = []
    for item in (history or [])[-12:]:
        role = item.get('role', 'user')
        content = str(item.get('content', '')).strip()
        if not content:
            continue
        gemini_history.append({
            'role': 'user' if role == 'user' else 'model',
            'parts': [content],
        })

    user_text = str(message).strip()
    if context:
        try:
            ctx_str = json.dumps(context, ensure_ascii=False, default=str)
        except (TypeError, ValueError):
            ctx_str = str(context)
        if len(ctx_str) > 6000:
            ctx_str = ctx_str[:6000] + '…'
        user_text = f'{user_text}\n\n[Contexte SIG Sols JSON]\n{ctx_str}'

    try:
        chat = model.start_chat(history=gemini_history)
        response = chat.send_message(user_text)
        reply = (response.text or '').strip()
        if not reply:
            return None, 'Réponse vide du modèle Gemini.'
        return reply, None
    except Exception as exc:
        logger.warning('Gemini chat error: %s', exc)
        return None, f'Erreur Gemini : {exc}'
