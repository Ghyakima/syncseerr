import os, sys
from requests import get, post, delete
from json import loads

EVENT_TYPES = ['SeriesDelete', 'MovieDelete']

def main():
    event_type = os.environ.get('sonarr_eventtype') or os.environ.get('radarr_eventtype')

    if event_type not in EVENT_TYPES:
        return print(f"Unsupported event type ({event_type})", file=sys.stderr)

    sync_url = os.environ.get('SYNC_URL') or "http://jellyseerr:5055/api/v1"
    sync_key = os.environ.get('SYNC_KEY') or None
    sync_safe = os.environ.get('SYNC_SAFE') or "True"

    if (sync_url or sync_key) is None:
        return print("Syncseerr can't continue with URL/KEY to *seerr", file=sys.stderr)

    title = os.environ.get('sonarr_series_title') or os.environ.get('radarr_movie_title')
    iddb = os.environ.get('sonarr_series_tvdbid') or os.environ.get('radarr_movie_tmdbid')
    imdbid = os.environ.get('sonarr_series_imdbid') or os.environ.get('radarr_movie_imdbid')
    deletedfiles = os.environ.get('sonarr_series_deletedfiles') or os.environ.get('radarr_movie_deletedfiles')

    if deletedfiles == "False":
        return print('Files not deleted. Skipping...', file=sys.stderr)

    # Get available media from *seerr
    media = get(f"{sync_url}/media?filter=allavailable&take=-1", headers={'x-api-key': sync_key})

    if media.status_code != 200:
        return print('Something went wrong. Invalid URL/KEY?', file=sys.stderr)

    # Try to match id's
    for item in loads(media.content)['results']:
        if (item['tvdbId'] or item['tmdbId']) == int(iddb) or item['imdbId'] == imdbid:
            if sync_safe == "True":
                issue = { 'issueType': 0, 'message': "Syncseerr - Delete request", 'mediaId': item['id'] }
                result = post(f"{sync_url}/issue", json=issue, headers={'x-api-key': sync_key})
                if result.status_code == 200:
                  return print(f"Sucessfuly created issue for '{title}' ({item['id']})")

            elif sync_safe == "False":
                result = delete(f"{sync_url}/media/{item['id']}", headers={'x-api-key': sync_key})
                if result.status_code == 204:
                    return print(f"Sucessfully deleted '{title}' data from *seerr")

    return print(f"Syncseerr couldn't find '{title}'", file=sys.stderr)

if __name__ == '__main__':
    main()