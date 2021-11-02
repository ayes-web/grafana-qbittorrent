def qbittorrentPeers():
    import requests
    import json
    import socket, struct
    import psycopg2 
    import pygeohash
    import time
    import os

    #qbittorrent credentials
    qb_server_ip = os.environ['QB_SERVER_IP']
    qbport = os.environ['QB_PORT']
    qbusername = os.environ['QB_USERNAME']
    qbpassword = os.environ['QB_PASSWORD']

    server_address = "http://" + qb_server_ip + ":" + qbport

    s = requests.Session()
    s.get(server_address + "/api/v2/auth/login?username=" + qbusername + "&password=" + qbpassword)
    torrents = json.loads(s.get(server_address + "/api/v2/torrents/info").text)

    conn = psycopg2.connect(database=os.environ['POSTGRES_DB'], user=os.environ['POSTGRES_USER'], password=os.environ['POSTGRES_PASSWORD'], host=os.environ['POSTGRES_SERVER_IP'], port=os.environ['POSTGRES_PORT'])
    conn.autocommit = True

    for torrent in torrents:
        torrent_peers = json.loads(s.get(server_address + "/api/v2/sync/torrentPeers?hash=" + torrent["hash"]).text)
        current_time  = str(int(time.time()))
    
        for peer in torrent_peers["peers"]:
            ip = peer.split(":")[0]
        
            request_url = 'https://geolocation-db.com/jsonp/' + ip
            response = requests.get(request_url)
            result = response.content.decode()

            result = result.split("(")[1].strip(")")
            result  = json.loads(result)
        
            latitude = result['latitude']
            longitude = result['longitude']

            if (latitude == 0 and longitude == 0) or (latitude == "Not found" and longitude == "Not found"):
                continue #Sometimes (especially in public trackers) some IP's in the private IP space show up as peers. This should filter those.

            try:
                geohash = pygeohash.encode(float(latitude), float(longitude))
            except:
                continue

            cur = conn.cursor()

            cur.execute("SELECT ip FROM public.peers WHERE ip='" + str(ip) + "';")
            data = cur.fetchall()

            if (len(data) == 0):
                cur.execute("INSERT INTO public.peers (ip, geohash, last_saw, first_saw) VALUES ('" + str(ip) + "', '" + geohash + "', '" + current_time + "', '" + current_time + "');")
            else:     
                cur.execute("UPDATE public.peers SET last_saw='" + current_time + "' WHERE ip='" + str(ip) + "';")

    conn.close()

    s.get(server_address + "/api/v2/auth/logout")
