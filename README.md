
# syncseerr


Sync Sonarr/Radarr media removal with overseerr/jellyseerr

## LSIO docker installation
* nano /config/custom-cont-init.d/install_syncseerr.sh
```
#!/bin/bash

VERSION=1.0.0

echo  '---- Installing Python3 & requests module ----'

if command -v apt-get > /dev/null; then
  apt-get update -qq -y > /dev/null
  apt-get install python3-pip -qq -y > /dev/null
elif command -v apk > /dev/null; then
  apk add -q --no-cache python3 py3-pip
else
  exit 1
fi

pip install -q requests

echo  '---- Downloading syncseerr ----'
cd /
curl --no-progress-meter https://github.com/Ghyakima/syncseerr/archive/refs/tags/v${VERSION}.tar.gz -O -J -L

tar xzf syncseerr-${VERSION}.tar.gz
rm -rf syncseerr-${VERSION}.tar.gz

if [ -d  "/syncseerr" ];  then
	rm -rf syncseerr
fi

mv syncseerr-${VERSION} syncseerr

echo -e '#!/bin/bash\npython3 /syncseerr/syncseerr.py'  > /syncseerr/syncseerr

chown -R ${PUID}:${PGID} /syncseerr
chmod +x /syncseerr/syncseerr
```
* Add environmental variables to Sonarr/Radarr

| Variable | Description |
|--|--|
| SYNC_URL | *seerr URL (default: http://jellyseerr:5055/api/v1) |
| SYNC_KEY | *seerr API_KEY (default: None) |
| SYNC_SAFE | If True, syncseerr will add issue to matched media (default: True)

* Restart container
* In Sonarr/Radarr add new custom script connection
```
Name: syncseerr
Trigger: On Series Delete/On Movie Delete
Path: /syncseerr/syncseerr
```

