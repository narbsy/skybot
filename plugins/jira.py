import locale
import re
import time

from util import hook, http

locale.setlocale(locale.LC_ALL, '')

jira_re = r'(?:.*[^A-Z]+)?([A-Z]{2,}-[0-9]+).*'

jira_default = "http://jira"

def jiralink(jiraid, bot):
  return bot.config.get('urls', {}).get('jira', jira_default) + "/browse/" + jiraid

@hook.regex(jira_re)
def jira_url(match, bot=None):
    jiraid = match.group(1)
    if re.search(r'http://[^ ]*' + jiraid, match.group(0)) != None:
      return None
    return jiralink(jiraid, bot)

