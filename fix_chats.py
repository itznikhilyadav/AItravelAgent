import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from chatbot.models import ChatHistory
from chatbot.views import convert_markdown_to_html
from bs4 import BeautifulSoup

count = 0
for chat in ChatHistory.objects.all():
    plain = BeautifulSoup(chat.response, 'html.parser').get_text('\n')
    chat.response = convert_markdown_to_html(plain)
    chat.save()
    count += 1

print(f"Fixed {count} chat records.")