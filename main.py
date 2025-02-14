import pywikibot
from collections import deque
from log import Log
from time import sleep
from pywikibot.data.api import Request
import json
import re
import difflib
from language import language
from datetime import datetime

self_username = "Gottert"
logger = Log('main')

site = pywikibot.Site('pt', 'wikipedia', user=self_username)
site.login()

queue = deque()
already_processed = deque(maxlen=1000) 

groups = ['*', 'autopatrolled', 'ipblock-exempt', 'user', 'confirmed', 'autoconfirmed', 'extendedconfirmed', 'autoextendedconfirmed', 'autoreviewer', 'rollbacker', 'eliminator', 'bot', 'sysop', 'bureaucrat']

with open('filters.json', 'r') as f:
    regexes = json.load(f)

with open('others.json', 'r') as f:
    others = json.load(f)

def add_result(dif, filter, user, summary, title):
    logger.trace(f"Adding {dif} to results.json")
    timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    
    result_dict =  {"dif": dif,
                    "filter": filter,
                    "timestamp": timestamp,
                    "user": user,
                    "edit_summary": summary,
                    "page_title": title}
    
    logger.trace(f"Dict {result_dict} for {dif}")
    
    try:
        with open('results.json', 'r') as f:
            result_json = json.load(f)
            logger.trace(f"Loaded results.json")
            
    except (FileNotFoundError, json.JSONDecodeError):  # Handle missing/corrupted file
        result_json = {"already_listed": {}, "last_update": "never", "results": [], "stats": {"filter_activations": {}, "activations_by_user": {}}, "update_interval": 120}
    
    result_json['results'].append(result_dict)
    logger.trace(f"Appendend the the dict to the json")
    
    with open('results.json', 'w') as f:
        json.dump(result_json, f, indent=4)
        logger.trace(f"Dumped results.json")

def add_filter_actiovation(filter):
    ...
    
def add_user_activation(user):
    ...
        
def get_recent_changes(site, limit=30):
    logger.info("Monitoring recent changes...")
    try:
        req = Request(site=site, parameters={
            'action': 'query',
            'list': 'recentchanges',
            'rcprop': 'title|ids',
            'rclimit': limit,
        })
        logger.trace("Submitting request")
        
        data = req.submit()
        logger.trace("Request returned")
        
        changes = data.get('query', {}).get('recentchanges', [])
    
    except Exception as e:
        logger.warn("Error at recent changes request!", e.args)

    for change in changes:
        title = change.get('title')
        revid = change.get('revid')
        logger.trace(f"Processing {revid}")

        if revid in already_processed:
            logger.trace(f"Rev {revid} already processed")
            continue

        page = pywikibot.Page(site, title)
        if page.exists():
            logger.trace(f"Page {page.title(with_ns=True)} exists")
            if page.latest_revision.user != self_username:
                logger.trace(f"Last rev for {page.title(with_ns=True)} wasn't self, queued")
                queue.append(page)

        already_processed.append(revid)
        
def perform_actions(page: pywikibot.Page):
    try:
        global text
        if page.revision_count() == 1:
            logger.trace(f"Page {page.title(with_ns=True)} is new")
            text = page.text
            
        else:
            revs = list(page.revisions())
            old_id = revs[1]['revid']
            
            old_rev = page.getOldVersion(old_id)
            new_rev = page.text
            
            diff = difflib.ndiff(old_rev.splitlines(), new_rev.splitlines())
            
            text = " ".join([line[2:] for line in diff if line.startswith('+')])

            logger.debug(f"(User:{page.latest_revision.user}, {page.title(with_ns=True)}), added text: " + text)
            
        for regex in regexes:
            patterns = regexes.get(regex)['patterns']
            match_all = regexes.get(regex)['match_all']
            flags = regexes.get(regex)['flags']
            exempt = regexes.get(regex)['exempt_group']
            namespace = regexes.get(regex).get('namespace')
            negative = regexes.get(regex).get('negative')
            
            if negative:
                continue
            
            if namespace and page.namespace() not in namespace:
                logger.trace(f"Page {page.title(with_ns=True)} not in {regex} namespaces")
                continue
            
            user = pywikibot.User(site, page.latest_revision.user)
            _groups = user.groups()
            
            highest = '*'
            for group in _groups:
                if group in groups:
                    if groups.index(highest) < groups.index(group):
                        highest = group
                    
            if groups.index(highest) >= groups.index(exempt):
                logger.trace(f"User {user.username} exempt from filter {regex}")
                continue
            
            _flags = 0
            for flag in flags:
                if flag == 'i':
                    _flags |= re.IGNORECASE
            
            matches = []
            for pattern in patterns:
                """if negative:
                    if re.search(pattern, neg_text, _flags): 
                        matches.append(1)
                    else:
                        matches.append(0)
                else:"""
                if re.search(pattern, text, _flags): 
                    matches.append(1)
                else:
                    matches.append(0)
                    
            if match_all:
                if sum(matches) == len(matches):
                    print(f'Match in filter {regex} ({page.title(with_ns=True)}, {page.latest_revision_id}, {page.latest_revision.user}) (match_all)')
                    logger.debug(f'Match in filter {regex} ({page.title(with_ns=True)}, {page.latest_revision_id}, {page.latest_revision.user}) (one match)')
                    add_result(page.latest_revision_id, regex, page.latest_revision.user, page.latest_revision.comment, page.title(with_ns=True))
            else:
                if sum(matches) > 0:
                    print(f'Match in filter {regex} ({page.title(with_ns=True)}, {page.latest_revision_id}, {page.latest_revision.user}) (one match)')
                    logger.debug(f'Match in filter {regex} ({page.title(with_ns=True)}, {page.latest_revision_id}, {page.latest_revision.user}) (one match)')
                    add_result(page.latest_revision_id, regex, page.latest_revision.user, page.latest_revision.comment, page.title(with_ns=True))
            
        if others.get('language').get('use') == True:
            if groups.index(highest) < groups.index(others.get('language').get('exempt')):
                if others.get('language').get('min_bytes') <= len(text):
                    lang = language(text)
                    if lang != 'pt':
                        print(f'Possible text in other language: {lang} (User:{page.latest_revision.user}, {page.title(with_ns=True)} {page.latest_revision_id})')
    
    except pywikibot.exceptions.NoPageError:
        logger.trace("Page deleted in the meantime")
        return
    
    except Exception:
        logger.trace("Undisclosed exception while analysing page")
        return


logger.info("Starting...")
while True:
    get_recent_changes(site)

    logger.trace("Queue is: " + ", ".join(page.title(with_ns=True) for page in queue))
    
    while queue:
        page = queue.popleft() 
        perform_actions(page)

    sleep(5)