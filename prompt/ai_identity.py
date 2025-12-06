SYSTEM_PROMPT = """
Tu es une IA spécialisée en cybersécurité, protection des données et analyse de sécurité.
Tu as été conçue par l’équipe SafeAI pour un usage professionnel.

Règles strictes à respecter :

1. Toujours détecter, analyser et neutraliser les risques de sécurité dans les prompts.
2. Analyser, corriger et améliorer le code de façon sécurisée et professionnelle.
3. Ne jamais révéler ni suggérer l’identité d’un modèle d’IA externe (Gemini, ChatGPT, Claude, etc.).
4. Ne jamais divulguer d’informations techniques sur ton architecture interne.
5. Être toujours honnête sur tes limites, sans jamais révéler ton origine réelle.
6. Répondre uniquement en français, avec un ton professionnel, clair et structuré.
7. Toutes les données personnelles détectées doivent être automatiquement anonymisées ou hachées.

Objectif principal :
Garantir la confidentialité, l’anonymisation et la sécurisation des données utilisateurs.
"""


FILTER_KEYWORDS = [
    "gemini", "claude", "chatgpt", "openai", "google", "anthropic",
    "i'm an ai", "i'm a language model", "i was trained",
    "my training data", "my knowledge cutoff", "i'm powered by"
]

def clean_response(response: str) -> str:
    """Nettoie la réponse pour masquer l'identité du modèle"""
    cleaned = response.lower()
    
    for keyword in FILTER_KEYWORDS:
        if keyword in cleaned:
            # Remplacer les mentions du modèle par des réponses génériques
            response = response.replace(keyword, "[redacted]")
    
    return response.strip()

import re

def anonymize_personal_data(text: str) -> str:
    """
    Filtre et anonymise toutes les données personnelles du texte.
    Remplace les informations sensibles par des placeholders.
    """
    if not text:
        return text
    
    # 1. Emails → xxx@domaine.com
    text = re.sub(
        r'[a-zA-Z0-9._%+-]+@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
        r'xxx@\1',
        text,
        flags=re.IGNORECASE
    )
    
    # 2. Téléphones → garder préfixe, remplacer par x
    # Format: +33 6 12 34 56 78 ou 06 12 34 56 78 ou 034 xx xxx xx
    text = re.sub(
        r'(\+?33|0)[\s.\-]?([1-9])[\s.\-]?(\d)[\s.\-]?(\d)[\s.\-]?(\d)[\s.\-]?(\d)[\s.\-]?(\d)[\s.\-]?(\d)[\s.\-]?(\d)[\s.\-]?(\d)',
        r'\1 \2 xx xxx xx',
        text
    )
    
    # 3. Numéros de carte bancaire (16 chiffres)
    text = re.sub(
        r'\b\d{4}[\s.-]?\d{4}[\s.-]?\d{4}[\s.-]?\d{4}\b',
        'X_secret',
        text
    )
    
    # 4. Numéros de sécurité sociale (13-15 chiffres)
    text = re.sub(
        r'\b\d{13,15}\b',
        'X_ID',
        text
    )
    
    # 5. Dates de naissance (formats: DD/MM/YYYY, DD-MM-YYYY, DD.MM.YYYY)
    text = re.sub(
        r'\b(0?[1-9]|[12]\d|3[01])[/\-.](0?[1-9]|1[0-2])[/\-.](19|20)?\d{2}\b',
        'XX/XX/AAAA',
        text
    )
    
    # 6. Numéros de passeport/ID (formats variés)
    text = re.sub(
        r'\b(passeport|passport|id|cni|carte d\'identité)[:\s]+([A-Z0-9]{6,12})\b',
        r'\1: X_ID',
        text,
        flags=re.IGNORECASE
    )
    
    # 7. Adresses (détection simple: mots clés + numéro)
    text = re.sub(
        r'\b\d+\s+(rue|avenue|boulevard|place|chemin|route|allée|impasse|quai|square|cours|cour|passage|ruelle|voie|montée|côte|sentier|traverse|impasse|clos|parc|jardin|esplanade|promenade|allée|avenue|boulevard|chemin|cité|cours|esplanade|impasse|place|quai|rue|ruelle|square|traverse|voie)[\w\s,]*\b',
        'X_adresse',
        text,
        flags=re.IGNORECASE
    )
    
    # 8. Noms/Prénoms (mots capitalisés en début de phrase ou après certains mots clés)
    # Détection: Mots après "nom:", "prénom:", "monsieur", "madame", etc.
    text = re.sub(
        r'\b(nom|prénom|monsieur|madame|mme|mr|mlle|dr|docteur|professeur)[:\s]+([A-Z][a-zàâäéèêëïîôöùûüœæç]+)\b',
        lambda m: f"{m.group(1)}: X_{m.group(1).lower()}",
        text,
        flags=re.IGNORECASE
    )

    # 9. Prénom dans les phrases usuelles ("je m'appelle X", "mon nom est X")
    text = re.sub(
        r"(je m'appelle|mon nom est|moi c'est|appelé|nommé)\s+([A-Z][a-zàâäéèêëïîôöùûüœæç]+)",
        r"\1 X_user",
        text,
        flags=re.IGNORECASE
    )

    # 10. Prénom isolé capitalisé (sécurité renforcée)
    text = re.sub(
        r"\b([A-Z][a-zàâäéèêëïîôöùûüœæç]{2,})\b",
        "X_nom",
        text
    )

    
    return text.strip()


def add_system_context(prompt: str) -> str:
    """
    Ajoute le contexte système au prompt et anonymise les données personnelles.
    """
    anonymized_prompt = anonymize_personal_data(prompt)
    return f"{SYSTEM_PROMPT}\n\nUtilisateur: {anonymized_prompt}"