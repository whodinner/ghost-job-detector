## ghost job detector

A Python tool that scrapes jobs from Indeed, RemoteOK, and WeWorkRemotely, scores them using heuristics, and cross-checks company footprints on LinkedIn/Indeed via DuckDuckGo. The goal: detect ghost jobs and scam postings before wasting time.

# Features

- Scrapes 5 pages from Indeed, 1 page each from RemoteOK and WeWorkRemotely

- Flags suspicious listings with:

- scammy keywords (quick money, no experience, wire transfer, etc.)

- Vague job titles or company names

- Unpaid internships

- Geographic mismatches

- Missing LinkedIn/Indeed presence

- Prints results to -terminal- with score, flag, and reasons

## how to install
- install the latest version of python
- pip install requests beautifulsoup4

# Disclaimer: Scraping is sometimes frowned upon and you may get throttled. Feel free to not use this and use common sense. You can also use the above as general guidelines for searching. 
