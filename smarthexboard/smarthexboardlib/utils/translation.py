import gettext
from pathlib import Path


# set current language
BASE_DIR = Path(__file__).resolve().parent.parent
lang_translations = gettext.translation('base', localedir=BASE_DIR / 'locales', languages=['en'])
lang_translations.install()


def gettext_lazy(key: str) -> str:
	# from utils.translation import gettext_lazy as _
	# print(f'gettext_lazy("{key}") has no translation')
	return lang_translations.gettext(key)

