import json,re,sys,urllib.request,html,concurrent.futures as cf
import os; os.chdir(os.path.dirname(os.path.abspath(__file__)))
jobs=json.load(open("jobs.json",encoding="utf-8"))
pat=re.compile(r'self\.__next_f\.push\(\[1,("(?:[^"\\]|\\.)*")\]\)')
def get(j):
    err=""
    for _ in range(3):
        try:
            h=urllib.request.urlopen(urllib.request.Request("https://jobs.micro1.ai/post/"+j["job_id"],headers={"User-Agent":"Mozilla/5.0"}),timeout=40).read().decode("utf-8")
            out={}
            m=re.search(r'referral_enabled\W*(\d)',h); out["ref_on"]=int(m.group(1)) if m else None
            m=re.search(r'referral_reward_amount\W*(\d+)',h); out["ref_amt"]=int(m.group(1)) if m else None
            for m in pat.finditer(h):
                if "JobPosting" in m.group(1) and "@context" in m.group(1):
                    s=json.loads(m.group(1)); o=json.loads(s[s.index("{"):])
                    d=html.unescape(re.sub(r'<[^>]+>','\n',o["description"])); d=re.sub(r'\n\s*\n+','\n',d).strip()
                    out.update(desc=d,countries=[x.get("name") for x in o.get("applicantLocationRequirements",[]) or []],valid=o.get("validThrough"))
                    break
            return j["job_id"],out
        except Exception as e: err=str(e)
    return j["job_id"],{"error":err}
with cf.ThreadPoolExecutor(8) as ex: res=dict(ex.map(get,jobs))
json.dump(res,open("details.json","w",encoding="utf-8"),ensure_ascii=False)
print(len(res),"err",sum(1 for v in res.values() if "error" in v),"ref_on",sum(1 for v in res.values() if v.get("ref_on")==1),"desc",sum(1 for v in res.values() if v.get("desc")))
