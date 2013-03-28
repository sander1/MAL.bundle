SEARCH_URL = "http://myanimelist.net/api/anime/search.xml?q=%s"

def Start():
	Log("[MyAnimeList Agent]: Starting MyAnimeList.net Agent")
	HTTP.CacheTime = CACHE_1MONTH

def createAuthorizationHeader():
	auth = String.Base64Encode('%s:%s' % (Prefs['username'], Prefs['password']))
	return {'Authorization': 'Basic %s' % auth}

class MALAgentTV(Agent.TV_Shows):
	name = "MyAnimeList.net"
	languages = [ Locale.Language.English ]
	primary_provider = True

	def search(self, results, media, lang):

		if Prefs['username'] and Prefs['password']:

			if media.show.endswith(' Ova'):
				media.show = '%s (OVA)' % media.show.rsplit(' ', 1)[0]
			elif media.show.endswith(' Tv'):
				media.show = '%s (TV)' % media.show.rsplit(' ', 1)[0]

			Log("[MyAnimeList Agent]: Search for Anime: %s" % media.show)

			#create url with name of anime
			mal_url = SEARCH_URL % media.show.replace(' ', '+')

			try:
				#get the xml dom from adress with authorization
				xml = XML.ElementFromURL(mal_url, headers=createAuthorizationHeader())

				#add data to results
				for entry in xml.xpath('//entry'):
					id = entry.xpath('./id/text()')[0]
					name = entry.xpath('./title/text()')[0]

					try:
						year = entry.xpath('./start_date/text()')[0].split('-')[0]
					except:
						year = None

					score = 100 - abs(String.LevenshteinDistance(name, media.show))

					results.Append(MetadataSearchResult(
						id = id,
						name = name,
						year = year,
						score = score,
						lang = Locale.Language.English
					))
			except:
				Log("[MyAnimeList Agent]: Error in retrieving xml data, or 0 results for search query for: %s" % media.show)
		else:
			Log("[MyAnimeList Agent]: Username/password not set")

	def update(self, metadata, media, lang):

		Log("[MyAnimeList Agent]: Update Anime-data: %s" % media.title)

		#create the url with the name
		mal_url = SEARCH_URL % media.title.replace(' ', '+')

		#get xml dom
		xml = XML.ElementFromURL(mal_url, headers=createAuthorizationHeader())
		entry = xml.xpath('//entry/id[text()="%s"]/parent::entry' % metadata.id)[0]

		#add information to the metadata
		Log("[MyAnimeList Agent]: Adding Anime-data to show")

		for item in entry:
			if item.tag == 'title':
				metadata.title = item.text
			if item.tag == 'synopsis':
				metadata.summary = String.StripTags(item.text)
			if item.tag == 'start_date':
				metadata.originally_available_at = Datetime.ParseDate(item.text)
			if item.tag == 'image':
				if item.text not in metadata.posters:
					metadata.posters[item.text] = Proxy.Media(HTTP.Request(item.text).content)
