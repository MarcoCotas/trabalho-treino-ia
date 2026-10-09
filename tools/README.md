# Refresh the job board

Run from this folder, then commit and push the repo root:

    python get_jobs.py      # all open jobs from the micro1 portal API -> jobs.json
    python fetch.py         # each job page (referral flag, description) -> details.json
    python build_site.py .. "9 de outubro de 2026" "9 October 2026" 2026-10-09

`build_site.py` rewrites index.html, en/, vagas/, the guides, sitemap.xml and robots.txt in the repo root.
Guide text lives in guide_pt.html / guide_en.html; styles in style.css.
