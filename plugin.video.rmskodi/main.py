import sys
import json
import urllib.request
import urllib.parse
import urllib.error
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

ADDON = xbmcaddon.Addon()
HANDLE = int(sys.argv[1])
BASE_URL = ADDON.getSetting('base_url') or 'https://cloud.strea.ru'
API_BASE = BASE_URL.rstrip('/') + '/api/v1'
USER_AGENT = 'Kodi/plugin.video.rmskodi/1.0'


def log(msg, level=xbmc.LOGDEBUG):
    xbmc.log(f'[rmskodi] {msg}', level)


# ---------------------------------------------------------------------------
# API client
# ---------------------------------------------------------------------------

def api_get(path):
    url = API_BASE + path
    log(f'GET {url}')
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        log(f'HTTP {e.code} for {url}', xbmc.LOGERROR)
    except Exception as e:
        log(f'Request failed: {e}', xbmc.LOGERROR)
    return {'data': []}


# ---------------------------------------------------------------------------
# URL builder
# ---------------------------------------------------------------------------

def _url(action, **params):
    params['action'] = action
    return sys.argv[0] + '?' + urllib.parse.urlencode(params)


# ---------------------------------------------------------------------------
# Navigation helpers
# ---------------------------------------------------------------------------

def _add_dir(label, url, is_folder=True, is_playable=False):
    li = xbmcgui.ListItem(label)
    if is_playable:
        li.setProperty('IsPlayable', 'true')
    xbmcplugin.addDirectoryItem(HANDLE, url, li, is_folder)
    return li


# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------

def list_years():
    """Top level – show available seasons."""
    xbmcplugin.setContent(HANDLE, 'files')
    data = api_get('/events/years')
    years = data.get('data', [2026])
    for year in sorted(years, reverse=True):
        _add_dir(str(year), _url('championships', year=str(year)))
    xbmcplugin.endOfDirectory(HANDLE)


def list_championships(year):
    """Second level – show championships (MotoGP, Moto2, Moto3, …)."""
    xbmcplugin.setContent(HANDLE, 'files')
    data = api_get('/events/championships')
    champs = data.get('data', [])
    for champ in champs:
        if isinstance(champ, dict):
            name = champ.get('name', champ.get('code', str(champ)))
        else:
            name = str(champ)
        _add_dir(name, _url('events', year=year, championship=name))
    xbmcplugin.endOfDirectory(HANDLE)


def list_events(year, championship):
    """Third level – show race weekends for a given year + championship."""
    xbmcplugin.setContent(HANDLE, 'videos')
    path = f'/events?year={year}&championship={urllib.parse.quote(championship)}&archive=1'
    data = api_get(path)
    events = data.get('data', [])
    for ev in events:
        label = (ev.get('title') or ev.get('shortTitle') or
                 ev.get('slug', '').replace('-', ' ').title())
        rn = ev.get('roundNumber')
        if rn:
            label = f"R{rn:02d}  {label}"
        _add_dir(label, _url('sessions', slug=ev['slug']))
    xbmcplugin.endOfDirectory(HANDLE)


def list_sessions(slug):
    """Fourth level – show available session recordings for one event."""
    xbmcplugin.setContent(HANDLE, 'videos')
    data = api_get(f'/events/{slug}/videos')
    groups = data.get('data', [])
    for group in groups:
        class_name = group.get('className', '')
        for file_info in group.get('files', []):
            prefix = file_info.get('prefix', '')
            if not prefix:
                continue
            label = file_info.get('label', prefix)
            if class_name:
                label = f'[{class_name}] {label}'
            _add_dir(
                label,
                _url('play', slug=slug, prefix=prefix),
                is_folder=False,
                is_playable=True,
            )
    xbmcplugin.endOfDirectory(HANDLE)


def play_video(slug, prefix):
    """Resolve the HLS URL for the given event + session prefix and play it."""
    data = api_get(f'/events/{slug}/videos')
    groups = data.get('data', [])
    hls_url = None

    for group in groups:
        for file_info in group.get('files', []):
            if file_info.get('prefix') == prefix:
                if file_info.get('hasHls') and file_info.get('hlsUrl'):
                    hls_url = file_info['hlsUrl']
                break
        if hls_url:
            break

    if hls_url:
        log(f'Playing HLS: {hls_url}')
        li = xbmcgui.ListItem(path=hls_url)
        li.setMimeType('application/x-mpegURL')
        li.setContentLookup(False)
        xbmcplugin.setResolvedUrl(HANDLE, True, li)
    else:
        log(f'No playable URL for slug={slug} prefix={prefix}', xbmc.LOGERROR)
        xbmcplugin.setResolvedUrl(HANDLE, False, xbmcgui.ListItem())


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

def router(paramstring):
    params = dict(urllib.parse.parse_qsl(paramstring))
    action = params.get('action', 'years')

    if action == 'years':
        list_years()
    elif action == 'championships':
        list_championships(params.get('year', '2026'))
    elif action == 'events':
        list_events(params.get('year', '2026'),
                    params.get('championship', 'MotoGP'))
    elif action == 'sessions':
        list_sessions(params.get('slug', ''))
    elif action == 'play':
        play_video(params.get('slug', ''), params.get('prefix', ''))
    else:
        log(f'Unknown action: {action}', xbmc.LOGERROR)
        xbmcplugin.endOfDirectory(HANDLE)


if __name__ == '__main__':
    raw = sys.argv[2] if len(sys.argv) > 2 else ''
    if raw.startswith('?'):
        raw = raw[1:]
    try:
        router(raw)
    except Exception as e:
        log(f'Unhandled error: {e}', xbmc.LOGERROR)
        import traceback
        log(traceback.format_exc(), xbmc.LOGERROR)
        xbmcgui.Dialog().notification(
            'RuMotoSport',
            f'Error: {e}',
            xbmcgui.NOTIFICATION_ERROR,
            5000,
        )
        xbmcplugin.endOfDirectory(HANDLE)
