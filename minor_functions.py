import re
from aiogram import types


def del_span(message):
    '''First at all deal with common cases using re.sub'''

    new_message = re.sub('''<span>|</span>''', '', message)

    '''Now we delete all other possible cases with 'span' in it'''

    def recursion(new_message):
        if new_message.find('<span') == -1:
            return new_message
        index_op_tag = new_message.find('<span')
        index_cls_tag = new_message.find('>', index_op_tag) + 1
        new_message_without_span = new_message[:index_op_tag:] + new_message[index_cls_tag::]
        return recursion(new_message_without_span)

    return recursion(new_message)


# --------------------------------------------------------------------------------------------------------
def media_preparation(media, caption):
    if media.endswith("jpg") or media.endswith("png"):
        return types.InputMediaPhoto(media=media,
                                     caption=caption,
                                     parse_mode="HTML")
    elif media.endswith("mp4") or media.endswith('gif'):
        return types.InputMediaVideo(media=media,
                                     caption=caption,
                                     parse_mode="HTML")


# --------------------------------------------------------------------------------------------------------
def add_tegs(message):
    index = message.rfind
    if index("<strong>") > index("</strong>"):
        message = message + "</strong>"
    if index("<em>") > index("</em>"):
        message = message + "</em>"
    if index("<") > index(">"):
        message = message[:index("<")]
    return message


def caption_preparation(message):
    """A caption cannot contain more than 1024 characters, so we're gonna check it."""

    message = del_span(message)
    if len(message) > 1024:
        message = message[:1000] + "..."
    message = re.sub('''&gt;|<sup>|</sup>|<sub>|</sub>''', "", message)
    message = re.sub('''<br>''', "\n", message)
    return add_tegs(message)
# --------------------------------------------------------------------------------------------------------
