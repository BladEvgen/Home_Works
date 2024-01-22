from django import template
from django.utils.timesince import timesince
from django.utils import timezone
from django.utils.translation import get_language
from django.utils import formats
from olx_copy import models

register = template.Library()


@register.simple_tag
def item_image_url(item):
    return item.get_image_url() if item else None


@register.simple_tag
def digit_beautify(value):
    src = str(value)
    if "." in src:
        out, rnd = src.split(".")
    else:
        out, rnd = src, "0"
    chunks = [out[max(i - 3, 0) : i] for i in range(len(out), 0, -3)][::-1]
    formatted_out = " ".join(chunks)

    return f"{formatted_out}.{rnd}"


@register.simple_tag
def relative_time(datetime_value):
    delta = timezone.now() - datetime_value

    if delta.days == 0 and delta.seconds < 86400:
        return timesince(datetime_value, timezone.now())
    else:
        return datetime_value.strftime("%H:%M %d.%m.%Y")


@register.filter(name="custom_cut")
def cutstom_cut(text: any, length: int) -> str:
    if len(str(text)) > length:
        return str(text)[:length] + "..."
    return str(text)


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


@register.simple_tag
def formatted_date(date):
    language = get_language()
    if language == "en":
        return date.strftime("%b. %d, %Y")
    elif language == "ru":
        return date.strftime("%d.%m.%Y")
    else:
        # ENG AS DEFAULT
        return date.strftime("%b. %d, %Y")


@register.simple_tag
def formatted_time(time):
    language = get_language()
    if language == "en":
        return formats.date_format(time, "M d Y g:i A")
    elif language == "ru":
        return time.strftime("%H:%M %d.%m.%Y ")
    else:
        # ENG AS DEFAULT
        return formats.date_format(time, "M d Y g:i A")


@register.simple_tag(takes_context=True)
def check_access(context: dict, action_slug: str = "") -> bool:
    user: models.User = context["request"].user
    if not user.is_authenticated:
        return False
    profile: models.UserProfile = user.profile
    is_access: bool = profile.check_access(action_slug)
    return is_access
