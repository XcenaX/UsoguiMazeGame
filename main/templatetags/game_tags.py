from django import template

register = template.Library()

@register.filter
def get_win_gain(user, opponent_rating):
    return user.get_win_gain(opponent_rating)

@register.filter
def get_lose_gain(user, opponent_rating):
    return user.get_lose_gain(opponent_rating)

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, {'right': False, 'bottom': False, 'left': False, 'top': False})

@register.filter
def times(number):
    return range(number)

@register.filter(name='subtract')
def subtract(value, arg):
    return value - arg

@register.filter(name='contains')
def contains(value, arg):
    return arg in value

@register.filter(name='strip')
def strip(value):
    return value.strip()