#!/bin/env python
import time
import qbittorrent

print("Starting grafana-qbittorrent")

while True:
    qbittorrent.qbittorrentPeers()
    time.sleep(60)    
