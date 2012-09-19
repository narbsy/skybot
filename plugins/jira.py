import locale
import re
import httplib
import base64
import json

from util import hook, http

locale.setlocale(locale.LC_ALL, '')

jira_re = r'([A-Z]{2,}-[0-9]+)'

# Initialize on first call
jira_projects = None

def jira_link(domain, jiraid):
  return "http://" + domain + "/browse/" + jiraid

@hook.regex(jira_re)
def jira_url(match, bot=None):
    settings = bot.config.get('jira_settings', {})
    if jira_projects == None:
      jiraprojects = set(map(lambda p: p['key'], jira_api(settings, '/rest/api/2.0.alpha1/project')));

    jiraid = match.group(0)
    if not jiraid.split("-")[0] in jiraprojects:
      return None
    if re.search(r'http://[^ ]*' + jiraid, match.group(0)) != None:
      return None

    url = jira_link(settings["domain"], jiraid)
    issue = jira_issue(settings, jiraid)

    if "errorMessages" in issue:
      return ", ".join(issue["errorMessages"])

    return "<a href='%s'> %s </a>" % (url, issue["fields"]["summary"]["value"])

def jira_issue(settings, issue):
  return jira_api(settings, "/rest/api/2.0.alpha1/issue/" + issue)

def jira_api(settings, path):
  return json.loads(https_get(settings["domain"], path, settings["username"], settings["password"]))

def https_get(domain, path, username, password):
  conn = httplib.HTTPConnection(domain)
  auth = base64.b64encode(username+":"+password).decode("ascii")
  headers = { 'Authorization' : 'Basic %s' %  auth }
  conn.request('GET', path, headers=headers)
  return conn.getresponse().read()
