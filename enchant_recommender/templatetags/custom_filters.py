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

# 💡 좋아요 기능 구현을 위해 새로 추가하는 필터
@register.filter(name='in_list')
def in_list(value, list_):
    """
    Checks if a value is present in a list of primary keys.
    Usage: {% if post.pk|in_list:liked_post_pks %}...
    """
    # post.pk는 보통 정수형이고 liked_post_pks는 values_list로 가져온 정수형 리스트일 수 있습니다.
    # 안전하게 비교하기 위해 str() 변환 대신 정수형으로 변환하여 비교합니다.
    try:
        # 템플릿의 post.pk를 리스트의 요소 타입에 맞춥니다.
        value_int = int(value)
        return value_int in list_
    except (ValueError, TypeError):
        # 변환이 불가능하면, 문자열로도 시도해봅니다. (가장 안전한 방법)
        return str(value) in list_