import gettext
import os

import ajenti


language = ajenti.config.tree.language
localedir = os.path.abspath(os.path.join(os.path.split(ajenti.__file__)[0], 'locales'))
try:
    translation = gettext.translation(
        'ajenti', 
        localedir=localedir, 
        languages=([language] if language else None),
    )
except IOError:  # not such translation
    translation = gettext.NullTranslations()
translation.install(unicode=True)  


def list_locales():
    return [_ for _ in os.listdir(localedir) if len(_) == 5]
