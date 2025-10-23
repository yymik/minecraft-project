from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    """
    Allows to get a value from a dictionary using a variable key in Django templates.
    Usage: {{ mydict|get_item:mykey }}
    """
    if hasattr(dictionary, 'get'): # dictionary가 get 메소드를 가지고 있는지 확인 (더 안전)
        return dictionary.get(key)
    return None # get 메소드가 없거나 키가 없으면 None 반환