import sys
import os
import urllib2
import base64
import difflib

USERNAME = Prefs['username']
PASSWORD = Prefs['password']
BASE_URL = "http://myanimelist.net/api/anime/search.xml?q="

def Start():
  Log("[MyAnimeList Agent]: Starting MyAnimeList.net Agent")
  
def doSearch(results, media, lang):
  Log("[MyAnimeList Agent]: Search for Anime: " + media.show)
  
  #create url with name of anime 
  mal_url = BASE_URL + String.Quote(media.show, usePlus=True)
  
  #encode with the username and password
  auth = String.Base64Encode('%s:%s' % (USERNAME, PASSWORD))
  headers = {'Authorization': 'Basic %s' % auth}
  
  #get the xml dom from adress with authorization
  xml = XML.ElementFromURL(mal_url, headers=headers)
  
  Log("[MyAnimeList Agent]: Animes found for: " + media.show)
  #add data to results
  for item in list(xml):
    Log(str(item[0].text) + ": " + str(item[1].text))
    anime_id = str(item[0].text) + ":" + str(item[1].text)
    anime_name = str(item[1].text)
    anime_score = int((difflib.SequenceMatcher(None, str(item[1].text), media.show).ratio())*100)

    results.Append(MetadataSearchResult(id=anime_id, name=anime_name, year=None, score=anime_score, lang=Locale.Language.English))
    
  return
  
def doUpdate(metadata, media, lang):

  Log("[MyAnimeList Agent]: Update Anime-data:")
  
  #a little bit of hacking here to get the anime name through the anime id
  #because myanimelist doesnt support searching for a id (yet)
  id_name = metadata.id.split(':')

  anime_id = id_name[0]
  anime_name = id_name[1]
  
  #create the url with the name
  mal_url = BASE_URL + String.Quote(id_name[1], usePlus=True)
  
  #encode
  auth = String.Base64Encode('%s:%s' % (USERNAME, PASSWORD))
  headers = {'Authorization': 'Basic %s' % auth}
  
  #get xml dom
  xml = XML.ElementFromURL(mal_url, headers=headers)
  
  #add information to the metadata
  Log("[MyAnimeList Agent]: Adding Anime-data to show ")
  for entry in xml:
    #Log("Anime id: " + entry[0].text)
    if int(entry[0].text) == int(anime_id):
      Log("[MyAnimeList Agent]: Anime found! Adding to metadata")
      for item in entry:
        if item.tag == 'id':
          Log("id: " + item.text)
        if item.tag == 'title':
          Log("title: " + item.text)
          metadata.title = item.text
        if item.tag == 'synopsis':
          Log("synopsis: " + item.text)
          metadata.summary = item.text
        if item.tag == 'start_date':
          Log("start_date: " + item.text)
          metadata.originally_available_at = Datetime.ParseDate(item.text)
        if item.tag == 'image':
          Log("image: " + item.text)
          metadata.posters[item.text] = Proxy.Media(HTTP.Request(item.text).content)
  return      

class MALAgentTV(Agent.TV_Shows):
  name = "MyAnimeList.net"
  languages = [ Locale.Language.English ]
  primary_provider = True
  
  def search(self, results, media, lang):
    #try:
    doSearch(results, media, lang)
      #break
    #except (urllib2.HTTPError) as e:
      #if e.code == 401:
        #Log("[MyAnimeList Agent]: EXCEPTION - Unauthorized to access MyAnimeList.net! Enter your Account in agent settings")
        #Log(e)
      #if e.code == 404:
        #Log("[MyAnimeList Agent]: EXCEPTION - MyAnimeList.net not accessable")
        #Log(e)
    #except:
      #pass
    return
  
  def update(self, metadata, media, lang):
    doUpdate(metadata, media, lang)
    return
