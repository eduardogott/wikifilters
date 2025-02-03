import pywikibot
from collections import deque
from log import Log
from time import sleep
from pywikibot.data.api import Request
import json
import re
import difflib
from language import language

logger = Log('main')

site = pywikibot.Site('pt', 'wikipedia', user="Gottert")
site.login()

queue = deque()
already_processed = deque(maxlen=1000) 

with open('filters.json', 'r') as f:
    regexes = json.load(f)

def get_recent_changes(site, limit=30):
    logger.info("Monitoring recent changes...")

    req = Request(site=site, parameters={
        'action': 'query',
        'list': 'recentchanges',
        'rcprop': 'title|ids',
        'rcnamespace': '0|1|2|3|4|5',
        'rclimit': limit,
    })
    data = req.submit()
    changes = data.get('query', {}).get('recentchanges', [])

    for change in changes:
        title = change.get('title')
        revid = change.get('revid')

        if revid in already_processed:
            continue

        if title == "Usuário:Eduardo Gottert/Testes/Bot":
            page = pywikibot.Page(site, title)
            if page.latest_revision.user != "Gottert":
                queue.append(page)

        already_processed.append(revid)
        

def perform_actions(page: pywikibot.Page):
    global text
    if page.revision_count() == 1:
        text = page.text
        
    else:
        revs = list(page.revisions())
        old_id = revs[1]['revid']
        
        old_rev = page.getOldVersion(old_id)
        new_rev = page.text
        
        diff = difflib.ndiff(old_rev.splitlines(), new_rev.splitlines())

        text = " ".join([line[2:] for line in diff if line.startswith('+')])

        logger.debug("Added text:" + text)
        
    for regex in regexes:
        patterns = regexes.get(regex)['patterns']
        match_all = regexes.get(regex)['match_all']
        flags = regexes.get(regex)['flags']
        
        _flags = 0
        for flag in flags:
            if flag == 'i':
                _flags |= re.IGNORECASE  # Use bitwise OR to set re.IGNORECASE for 'i'
        
        matches = []
        for pattern in patterns:
            if re.search(pattern, text, _flags): 
                matches.append(1)
            else:
                matches.append(0)  # Ensure we track non-matches as well
                
        if match_all:
            # All patterns must match
            if sum(matches) == len(matches):
                print(f'Match in filter {regex} ({page.title(with_ns=True)}, {page.latest_revision_id}) (match_all)')
                logger.debug(f'Match in filter {regex} ({page.title(with_ns=True)}, {page.latest_revision_id}) (one match)')
        else:
            # Only one pattern needs to match
            if sum(matches) > 0:
                print(f'Match in filter {regex} ({page.title(with_ns=True)}, {page.latest_revision_id}) (one match)')
                logger.debug(f'Match in filter {regex} ({page.title(with_ns=True)}, {page.latest_revision_id}) (one match)')

    lang = language(text)
    if lang != 'pt':
        print(f'Possible text in other language: {lang} ({page.title(with_ns=True)}, {page.latest_revision_id})')
        logger.debug(f'Possible text in other language: {lang} ({page.title(with_ns=True)}, {page.latest_revision_id})')

while True:
    get_recent_changes(site)

    while queue:
        page = queue.popleft() 
        perform_actions(page)

    sleep(5)