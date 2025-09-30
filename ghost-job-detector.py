import requests
from bs4 import BeautifulSoup
import re
import time

# scrapers

def scrape_weworkremotely(limit_pages=1):
    base = "https://weworkremotely.com/categories/remote-programming-jobs"
    jobs = []
    for page in range(1, limit_pages + 1):
        url = f"{base}?&page={page}"
        html = requests.get(url, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")
        for post in soup.select("li.feature"):
            try:
                title = post.find("span", class_="title").get_text(strip=True)
                company = post.find("span", class_="company").get_text(strip=True)
                link = "https://weworkremotely.com" + post.find("a")["href"]
                jobs.append({"title": title, "company": company, "link": link, "source": "WeWorkRemotely"})
            except Exception:
                continue
        time.sleep(1)
    return jobs

def scrape_remoteok(limit_pages=1):
    url = "https://remoteok.com/remote-dev-jobs"
    html = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10).text
    soup = BeautifulSoup(html, "html.parser")
    jobs = []
    for row in soup.select("tr.job")[:limit_pages * 20]:
        try:
            title = row.find("td", {"class": "company_and_position"}).find("h2").get_text(strip=True)
            company = row.find("td", {"class": "company_and_position"}).find("h3").get_text(strip=True)
            link = "https://remoteok.com" + row.find("a", class_="preventLink")["href"]
            jobs.append({"title": title, "company": company, "link": link, "source": "RemoteOK"})
        except Exception:
            continue
    time.sleep(1)
    return jobs

def scrape_indeed(query="software engineer", location="remote", limit_pages=5):
    jobs = []
    for page in range(0, limit_pages * 10, 10):  # 10 results per page
        url = f"https://www.indeed.com/jobs?q={query}&l={location}&start={page}"
        html = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")
        for div in soup.select("td.resultContent"):
            try:
                title = div.find("h2", class_="jobTitle").get_text(strip=True)
                company = div.find("span", class_="companyName").get_text(strip=True)
                link = "https://www.indeed.com" + div.find("a")["href"]
                jobs.append({"title": title, "company": company, "link": link, "source": "Indeed"})
            except Exception:
                continue
        time.sleep(2)
    return jobs

# heuristics 

def score_job(job):
    score = 100
    reasons = []
    title, company = job["title"], job["company"]
    text = (title + " " + company).lower()

    # Strong red flags
    if re.search(r'no experience|required fee|quick money|crypto|wire transfer', text):
        score -= 40
        reasons.append("Suspicious keywords (scam-like terms)")
    if len(company.split()) == 1 and len(company) < 4:
        score -= 20
        reasons.append("Very short or vague company name")
    if "remote" in title.lower() and "usa" in title.lower() and "india" in text:
        score -= 15
        reasons.append("Geography mismatch (USA vs India)")

    # Softer warnings
    if len(title.split()) <= 2:
        score -= 10
        reasons.append("Vague job title")
    if "intern" in title.lower() and "unpaid" in text:
        score -= 20
        reasons.append("Unpaid internship mention")

    return max(0, score), reasons

# company check

def check_company_online(company):
    """Search DuckDuckGo for company LinkedIn or Indeed presence."""
    try:
        q = f"{company} site:linkedin.com OR site:indeed.com"
        url = "https://duckduckgo.com/html/"
        resp = requests.get(url, params={"q": q}, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        results = soup.select("a.result__a")
        return len(results) > 0
    except Exception:
        return False

# job scraping flow

def main():
    print("Scraping jobs...")

    jobs = []
    jobs.extend(scrape_weworkremotely(limit_pages=1))
    jobs.extend(scrape_remoteok(limit_pages=1))
    jobs.extend(scrape_indeed(query="software engineer", location="remote", limit_pages=5))

    print(f"Collected {len(jobs)} jobs. Scoring...\n")

    for job in jobs:
        trust, reasons = score_job(job)
        company_found = check_company_online(job["company"])
        if not company_found:
            trust -= 20
            reasons.append("No LinkedIn/Indeed footprint found")

        flag = "OK"
        if trust < 40:
            flag = "SUSPICIOUS"
        elif trust < 70:
            flag = "CHECK"

        print("-------------------------------------------------")
        print(f"Source:  {job['source']}")
        print(f"Title:   {job['title']}")
        print(f"Company: {job['company']}")
        print(f"Link:    {job['link']}")
        print(f"Score:   {trust} [{flag}]")
        if reasons:
            print("Reasons:")
            for r in reasons:
                print(f"  - {r}")
        else:
            print("Reasons: None (looks fine)")
        time.sleep(2)

if __name__ == "__main__":
    main()
