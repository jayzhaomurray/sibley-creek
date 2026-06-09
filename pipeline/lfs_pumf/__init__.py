"""LFS PUMF acquisition and harmonization package.

Fetches Statistics Canada Labour Force Survey Public Use Microdata Files,
trims to the employee regression sample, and writes canonical parquet files
to data/raw/lfs_pumf/{YYYY-MM}.parquet with sidecar .meta.json files.

Two URL patterns are used (per spike findings 2026-06-05):
  Recent months  : https://www150.statcan.gc.ca/n1/pub/71m0001x/2021001/{YYYY-MM}-CSV.zip
  Historical     : https://www150.statcan.gc.ca/n1/pub/71m0001x/2021001/hist/{YYYY}-CSV.zip
                   (annual bundle, 12 monthly CSVs inside)

StatCan performs TLS fingerprinting — only requests with a Chrome User-Agent
passes. httpx and urllib both fail at the TLS handshake layer. The downloader
is isolated here; the rest of the pipeline uses httpx as normal.
"""
