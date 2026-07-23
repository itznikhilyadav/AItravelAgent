import logging
import os
import re
import markdown as md_lib
from bs4 import BeautifulSoup
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.conf import settings
from .models import ChatHistory

logger = logging.getLogger(__name__)

# ── API Key ───────────────────────────────────────────────────────────────────
# Set GROQ_API_KEY in your .env or environment — never hard-code it in source.
GROQ_API_KEY = getattr(
    settings, 'GROQ_API_KEY',
    os.environ.get('GROQ_API_KEY', '')
)

# ── System prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are TravelAI, an expert AI travel assistant.

CRITICAL: Format EVERY response in Markdown using the rules below.
Never write plain paragraphs — always use bullets and section headings.

FORMATTING RULES:
1. Start with ONE short summary sentence (no heading).
2. Use ## with an emoji for every section heading.
3. Use * for ALL bullet points.
4. Use **bold** for place names, prices, and important terms.
5. Use numbered lists (1. 2. 3.) only for ranked or ordered items.
6. Keep each bullet to one line.
7. End every response with a practical tip or suggested next question.
8. Never write more than 2 sentences in a row without a bullet.

SECTION TEMPLATES (copy these patterns exactly):

Hotels:
## 🏨 Recommended Hotels
* **Hotel Name** — Rs X,XXX/night
  Area, City | WiFi · Pool · Breakfast

Itinerary:
## 🗓️ Day-by-Day Plan
**Day 1 — Title**
* 09:00 — Activity
* 12:00 — Lunch at **Restaurant Name**
* 15:00 — Visit **Place Name**

Flights:
## ✈️ Flight Options
* **Airline** — Rs X,XXX return | City → City | HH:MM–HH:MM

Restaurants:
## 🍽️ Top Restaurants
* **Name** — Rs XXX/person | Area · Cuisine
  Must try: **Dish**

Budget:
## 💰 Budget Breakdown
* **Flights** — Rs X,XXX
* **Hotels** — Rs X,XXX/night
* **Food** — Rs XXX/day
* **Total (7 days)** — **Rs XX,XXX**

Weather:
## 🌤️ Weather
* **Temperature**: XX°C
* **Condition**: Description
* **Pack**: Item, Item, Item

Places:
## 📍 Top Places to Visit
1. **Place Name** — short description
   * Timings: 9 AM–6 PM · Entry: Rs XX

Use Rs for rupees, $ for dollars. Always use real place names.
Return ONLY valid Markdown — no HTML, no code fences."""


# ── Helpers ───────────────────────────────────────────────────────────────────

def build_conversation_history(chats, max_turns: int = 6) -> list:
    """
    Return the last `max_turns` exchanges as a list of role/content dicts,
    oldest first, so the model has multi-turn context.
    """
    recent = list(chats.order_by('-created_at')[:max_turns])
    recent.reverse()
    history = []
    for chat in recent:
        history.append({"role": "user",      "content": chat.message})
        history.append({"role": "assistant", "content": chat.response})
    return history


def convert_markdown_to_html(text: str) -> str:
    """
    Convert the AI's Markdown reply into safe, guaranteed-balanced HTML.

    Uses the `markdown` library for parsing and BeautifulSoup for DOM
    manipulation, so a malformed or unexpected response can NEVER produce
    unclosed tags that corrupt the surrounding page layout.
    """
    if not text or not text.strip():
        return '<div class="resp-section"><p class="resp-text">No response received.</p></div>'

    # ── Step 1: promote standalone bold lines to ## headings ──────────────
    lines = text.split('\n')
    promoted = []
    for line in lines:
        s = line.strip()
        if (s.startswith('**') and s.endswith('**')
                and len(s.replace('*', '').strip()) > 3):
            promoted.append('## ' + s)
        else:
            promoted.append(line)
    text = '\n'.join(promoted)

    # ── Step 2: Markdown → raw HTML ───────────────────────────────────────
    raw_html = md_lib.markdown(
        text,
        extensions=[
            'markdown.extensions.fenced_code',
            'markdown.extensions.tables',
            'markdown.extensions.nl2br',
        ]
    )

    # ── Step 3: parse with BeautifulSoup & add CSS classes ────────────────
    soup = BeautifulSoup(raw_html, 'html.parser')

    for tag in soup.find_all('ul'):
        tag['class'] = tag.get('class', []) + ['resp-list']
    for tag in soup.find_all('ol'):
        tag['class'] = tag.get('class', []) + ['resp-list', 'resp-ol']
    for tag in soup.find_all('li'):
        tag['class'] = tag.get('class', []) + ['resp-item']
    for tag in soup.find_all('strong'):
        tag['class'] = tag.get('class', []) + ['resp-bold']
    for tag in soup.find_all('p'):
        tag['class'] = tag.get('class', []) + ['resp-text']
    for tag in soup.find_all('a', href=True):
        tag['target'] = '_blank'
        tag['rel']    = 'noopener noreferrer'
        tag['class']  = tag.get('class', []) + ['resp-link']
        if tag.string:
            tag.string = tag.string + ' ↗'

    # ── Step 4: regroup nodes into <div class="resp-section"> blocks ──────
    # A new section starts at every <h2>. We build the DOM tree with
    # BeautifulSoup objects — never string concatenation — so it's
    # impossible to emit an unbalanced or stray tag.
    wrapper = soup.new_tag('div')
    section = None

    for node in list(soup.contents):
        if getattr(node, 'name', None) == 'h2':
            node['class'] = node.get('class', []) + ['resp-heading']
            section = soup.new_tag('div', **{'class': 'resp-section'})
            wrapper.append(section)
            section.append(node)
        else:
            if section is None:
                section = soup.new_tag('div', **{'class': 'resp-section'})
                wrapper.append(section)
            section.append(node)

    return str(wrapper)


# ── Groq call ─────────────────────────────────────────────────────────────────

def get_ai_response(message: str, history_messages: list = None) -> str:
    """
    Send `message` (with optional prior-turn history) to Groq's
    Llama 3.3 70B model and return the formatted HTML response.
    Falls back to a friendly error bubble on any exception.
    """
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if history_messages:
            messages.extend(history_messages)
        messages.append({"role": "user", "content": message})

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=1500,
            temperature=0.7,
        )
        raw = completion.choices[0].message.content.strip()
        return convert_markdown_to_html(raw)

    except Exception:
        logger.exception("Groq API request failed")
        return (
            '<div class="resp-section">'
            '<p class="resp-text">'
            '⚠️ Sorry, I couldn\'t reach the AI right now. '
            'Please try again in a moment.'
            '</p></div>'
        )


# ── View ──────────────────────────────────────────────────────────────────────

@login_required(login_url='/users/login/')
def chat_page(request):
    """
    GET  → render the chat page with full history + sidebar recent chats.
    POST → save user message, get AI response, redirect (PRG pattern).
    """
    user_chats = ChatHistory.objects.filter(user=request.user)

    # Full history for display — oldest first
    chats = user_chats.order_by('created_at')

    # Sidebar — newest 6, for quick navigation
    recent_chats = user_chats.order_by('-created_at')[:6]

    if request.method == 'POST':
        message = request.POST.get('message', '').strip()

        if message:
            # Build multi-turn context (last 6 exchanges)
            history = build_conversation_history(user_chats, max_turns=6)
            response = get_ai_response(message, history_messages=history)

            ChatHistory.objects.create(
                user=request.user,
                message=message,
                response=response,
            )

        # PRG: always redirect after POST to prevent double-submit on refresh
        return redirect('chatbot:chat')

    return render(request, 'chatbot/chat.html', {
        'chats':        chats,
        'recent_chats': recent_chats,
    })