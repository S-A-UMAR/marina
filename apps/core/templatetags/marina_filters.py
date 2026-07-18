from django import template
from decimal import Decimal

register = template.Library()


@register.filter
def naira(value):
    """
    Format a number as Nigerian Naira.
    Usage: {{ product.selling_price|naira }}
    Output: ₦75,000 or ₦1,250,000
    """
    try:
        value = Decimal(str(value))
        # Format with commas, no decimal places for whole naira
        if value == value.to_integral_value():
            formatted = f'{int(value):,}'
        else:
            formatted = f'{value:,.2f}'
        return f'₦{formatted}'
    except (ValueError, TypeError, Exception):
        return f'₦{value}'


@register.filter
def naira_plain(value):
    """Like naira but without the ₦ symbol (for input placeholders etc.)"""
    try:
        value = Decimal(str(value))
        if value == value.to_integral_value():
            return f'{int(value):,}'
        return f'{value:,.2f}'
    except Exception:
        return str(value)


@register.filter
def multiply(value, arg):
    """Multiply value by arg — useful for item subtotals in templates."""
    try:
        return Decimal(str(value)) * Decimal(str(arg))
    except Exception:
        return 0


@register.filter
def get_item(dictionary, key):
    """Retrieve value from dictionary by key."""
    if not dictionary:
        return None
    try:
        return dictionary.get(key)
    except AttributeError:
        return None

