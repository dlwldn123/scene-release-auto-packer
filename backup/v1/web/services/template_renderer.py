"""
Service de rendu des templates NFO avec placeholders.
"""

import logging
import re
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def render_nfo_template(template_content: str, variables: Dict[str, Any]) -> str:
    """
    Rend un template NFO en remplaçant les placeholders.

    Supporte les formats :
    - {{variable}} : Remplacement simple
    - {variable} : Remplacement simple (alternative)
    - {{#if variable}}...{{/if}} : Conditionnelle (si variable existe et non vide)
    - {{#ifnot variable}}...{{/ifnot}} : Conditionnelle inverse

    Args:
        template_content: Contenu du template avec placeholders
        variables: Dictionnaire de variables pour remplissage

    Returns:
        Template rendu avec variables remplacées
    """
    rendered = template_content

    # Traiter les conditionnelles {{#if variable}}...{{/if}}
    rendered = _process_conditionals(rendered, variables, "if")

    # Traiter les conditionnelles inverses {{#ifnot variable}}...{{/ifnot}}
    rendered = _process_conditionals(rendered, variables, "ifnot", inverse=True)

    # Remplacer les variables simples {{variable}} ou {variable}
    # Format {{variable}} en priorité
    pattern = r"\{\{([^}]+)\}\}"
    for match in re.finditer(pattern, rendered):
        var_name = match.group(1).strip()
        if var_name not in [
            "#if",
            "#ifnot",
            "/if",
            "/ifnot",
        ]:  # Ignorer les commandes conditionnelles
            value = variables.get(var_name, "")
            rendered = rendered.replace(match.group(0), str(value) if value else "")

    # Format {variable} (sans doubles accolades)
    pattern = r"\{([^}]+)\}"
    for match in re.finditer(pattern, rendered):
        var_name = match.group(1).strip()
        if not var_name.startswith("#") and not var_name.startswith("/"):
            value = variables.get(var_name, "")
            rendered = rendered.replace(match.group(0), str(value) if value else "")

    return rendered


def _process_conditionals(
    content: str,
    variables: Dict[str, Any],
    conditional_type: str,
    inverse: bool = False,
) -> str:
    """
    Traite les conditionnelles dans le template.

    Args:
        content: Contenu template
        variables: Variables disponibles
        conditional_type: Type conditionnelle ('if' ou 'ifnot')
        inverse: Si True, inverse la logique

    Returns:
        Contenu avec conditionnelles traitées
    """
    pattern = r"\{\{#%s\s+([^}]+)\}\}(.*?)\{\{/%s\}\}" % (
        conditional_type,
        conditional_type,
    )

    def replace_conditional(match):
        var_name = match.group(1).strip()
        inner_content = match.group(2)

        var_value = variables.get(var_name)
        condition_met = bool(var_value) if not inverse else not bool(var_value)

        if condition_met:
            return inner_content
        else:
            return ""

    return re.sub(pattern, replace_conditional, content, flags=re.DOTALL)


def get_template_variables(template_content: str) -> Dict[str, str]:
    """
    Extrait la liste des variables utilisées dans un template.

    Args:
        template_content: Contenu du template

    Returns:
        Dictionnaire {variable: description} des variables trouvées
    """
    variables = {}

    # Chercher {{variable}} ou {variable}
    pattern = r"\{\{?([^}]+)\}\}?"
    matches = re.findall(pattern, template_content)

    for match in matches:
        var_name = match.strip()
        # Ignorer les commandes conditionnelles
        if not var_name.startswith("#") and not var_name.startswith("/"):
            if var_name not in variables:
                variables[var_name] = f"Variable {var_name}"

    return variables


def load_template_from_db(template_id: int) -> Optional[str]:
    """
    Charge un template depuis la base de données.

    Args:
        template_id: ID du template dans la DB

    Returns:
        Contenu du template ou None si introuvable
    """
    try:
        from web.database import db
        from web.models.template import NfoTemplate

        template = NfoTemplate.query.get(template_id)
        if template:
            return template.content
    except Exception as e:
        logger.warning(f"Erreur chargement template DB: {e}")

    return None


def get_default_template_from_db() -> Optional[str]:
    """
    Récupère le template par défaut depuis la base de données.

    Returns:
        Contenu du template par défaut ou None
    """
    try:
        from web.database import db
        from web.models.template import NfoTemplate

        template = NfoTemplate.query.filter_by(is_default=True).first()
        if template:
            return template.content
    except Exception as e:
        logger.warning(f"Erreur récupération template par défaut: {e}")

    return None
