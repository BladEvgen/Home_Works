from django import template
from django.utils.translation import get_language
from django.contrib.auth.models import User
from django.utils.timesince import timesince
from django.utils import timezone
from olx_copy import models

register = template.Library()


@register.filter(name="custom_cut")
def cutstom_cut(text: any, length: int) -> str:
    if len(str(text)) > length:
        return str(text)[:length] + "..."
    return str(text)


@register.filter(name="digit_beautify")
def digit_beautify(value):
    lang = get_language()

    separator = "," if lang == "ru" else "."

    if isinstance(value, int):
        formatted_value = f"{value:,d}"
    elif isinstance(value, str) and value.isdigit():
        formatted_value = f"{float(value):,d}"
    else:
        formatted_value = str(value)

    return formatted_value


@register.filter(name="relative_time")
def relative_time(datetime_value):
    delta = timezone.now() - datetime_value

    if delta.days == 0 and delta.seconds < 86400:
        return timesince(datetime_value, timezone.now())
    else:
        return datetime_value.strftime("%H:%M %d.%m.%Y")


@register.filter(name="discount_percentage")
def discount_percentage(original_price, discounted_price):
    if original_price and discounted_price:
        original_price = (
            int(original_price)
            if isinstance(original_price, str) and original_price.isdigit()
            else original_price
        )
        discounted_price = (
            int(discounted_price)
            if isinstance(discounted_price, str) and discounted_price.isdigit()
            else discounted_price
        )

        if original_price > discounted_price:
            discount = ((original_price - discounted_price) / original_price) * 100
            return f"{discount:.2f}%"

    return "0%"
