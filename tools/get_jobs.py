"""Step 1 of the refresh: download all open micro1 jobs to jobs.json (public portal API)."""
import json, os, urllib.request
os.chdir(os.path.dirname(os.path.abspath(__file__)))
jobs, page = [], 1
while True:
    req = urllib.request.Request(f"https://prod-api.micro1.ai/api/v1/job/portal?page={page}&limit=100",
        data=json.dumps({"action": "get_all_jobs"}).encode(), headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"})
    r = json.load(urllib.request.urlopen(req, timeout=60))
    batch = r.get("data") or r.get("jobs") or []
    if isinstance(batch, dict): batch = batch.get("jobs") or batch.get("data") or []
    if not batch: break
    jobs += batch; page += 1
json.dump(jobs, open("jobs.json", "w", encoding="utf-8"), ensure_ascii=False)
print(len(jobs), "jobs")
