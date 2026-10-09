import json, re, html, sys, os, unicodedata
SRC = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1]
DATE_PT, DATE_EN, DATE_ISO = sys.argv[2], sys.argv[3], sys.argv[4]
BASE = "https://marcocotas.github.io/trabalho-treino-ia/"
CODE = "fe7c988b-82fb-4680-9275-f5844b11d8c0"
Q = f"?referralCode={CODE}&utm_source=referral&utm_medium=share&utm_campaign=job_referral"
GERAL = "https://refer.micro1.ai/referral/jobs" + Q
E = html.escape

J = {j['job_id']: j for j in json.load(open(f'{SRC}/jobs.json', encoding='utf-8'))}
D = json.load(open(f'{SRC}/details.json', encoding='utf-8'))

AREA = {  # slug: (pt, en)
 'law': ('Direito', 'Law'), 'software-engineering': ('Programação', 'Software engineering'),
 'language-audio': ('Línguas e áudio', 'Languages & audio'), 'robotics': ('Robótica', 'Robotics'),
 'sciences-research': ('Ciência e investigação', 'Science & research'), 'finance': ('Finanças', 'Finance'),
 'medicine': ('Saúde e medicina', 'Health & medicine'), 'generalist': ('Generalistas', 'Generalist'),
 'business-operations': ('Gestão e operações', 'Business & operations'), 'ai-machine-learning': ('IA e machine learning', 'AI & machine learning'),
 'applied-engineering': ('Engenharia', 'Engineering'), 'arts-design': ('Arte e design', 'Arts & design'),
 'sales-marketing': ('Vendas e marketing', 'Sales & marketing'), 'data-analysis': ('Análise de dados', 'Data analysis'),
 'humanities': ('Humanidades', 'Humanities'), 'cybersecurity': ('Cibersegurança', 'Cybersecurity'),
 'education': ('Educação', 'Education'), 'retail-hospitality': ('Comércio e hotelaria', 'Retail & hospitality'),
}
def area(j): return AREA.get(j.get('domain_slug'), ('Outras áreas', 'Other'))

def slugify(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')[:70]

def location(desc):
    m = re.search(r'(?im)^\s*Location\s*:?\s*\n?\s*(.+)$', desc)
    if not m: return ''
    v = m.group(1).strip()
    if v.lower().startswith('location'): v = v.split(':', 1)[-1].strip()
    return v[:120]

US = re.compile(r'\b(US|U\.S\.|USA|United States|UK|United Kingdom|Canada|India|Australia|Brazil|Japan|Germany|France|Spain|Italy|Mexico|Philippines|Nigeria|Kenya|LATAM|Latin America|Korea|China)\b', re.I)
OPEN = re.compile(r'(global|worldwide|anywhere|any country|europe|\bEU\b|EMEA|portugal|international|all countries)', re.I)
EXPL = re.compile(r'(global|worldwide|worlwide|anywhere|europe|\bEU\b|EMEA|portugal)', re.I)
USHINT = re.compile(r'(U\.?S\.?[- ]based|US only|U\.S\. only|United States only|based in the (US|U\.S\.|United States)|US residents|U\.S\. residents|must reside in the (US|U\.S\.|United States)|US citizens|U\.S\. citizens)', re.I)
def open_pt(loc, desc=''):
    """2 = explicitly open to Europe/worldwide, 1 = generic remote with no country limit found, 0 = restricted"""
    if not loc: return 0
    if EXPL.search(loc) and not re.search(r'\bonly\b', loc, re.I): return 2
    if re.fullmatch(r'\s*(fully\s+)?remote\s*\.?\s*', loc, re.I): return 0 if USHINT.search(desc) else 1
    return 0

def rate(j):
    r = j.get('ideal_hourly_rate') or {}
    if r.get('min') and r.get('max'): return f"{r['min']}–{r['max']} USD/h" if r['min'] != r['max'] else f"{r['min']} USD/h"
    if r.get('max'): return f"{r['max']} USD/h"
    if j.get('ideal_monthly_salary_max'): return f"{j.get('ideal_monthly_salary_min') or ''}–{j['ideal_monthly_salary_max']} USD/mês".lstrip('–')
    return ''

jobs = []
seen = set()
for jid, d in D.items():
    if d.get('ref_on') != 1 or not d.get('ref_amt') or jid not in J: continue
    j = J[jid]; name = re.sub(r'\s+', ' ', j['job_name']).strip()
    s = slugify(name) + '-' + jid[:6]
    loc = location(d.get('desc', ''))
    jobs.append(dict(id=jid, name=name, slug=s, area=area(j), loc=loc, pt=open_pt(loc, d.get('desc', '')), rate=rate(j),
                     desc=d.get('desc', ''), url=f"https://jobs.micro1.ai/post/{jid}" + Q, posted=(j.get('date_posted') or '')[:10]))
jobs.sort(key=lambda x: (-x['pt'], x['area'][1], x['name']))

CSS = open(f'{SRC}/style.css', encoding='utf-8').read()

def page(lang, title, desc, body, path, alt=None, script=''):
    canon = BASE + path
    alts = ''
    if alt:
        for hl, p in alt: alts += f'<link rel="alternate" hreflang="{hl}" href="{BASE + p}">'
    return f'''<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(desc)}"><link rel="canonical" href="{canon}">{alts}
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:url" content="{canon}">
<style>{CSS}</style></head><body><main>
{body}
</main>{script}</body></html>'''

T = {
 'pt': dict(
   nav='<nav><a href="{r}index.html">Vagas</a> · <a href="{r}guia-entrevista-micro1.html">Guia da entrevista</a> · <a href="{r}en/index.html">English</a></nav>',
   disc='<div class="box"><b>Divulgação:</b> os botões "Candidatar" são links de referral meus. Se te candidatares por eles, fores selecionado e trabalhares 10 horas, a micro1 paga-me um prémio. A ti não custa nada. <b>Não trabalho para a micro1 nem sou recrutador</b>: a seleção, os valores e as horas dependem só deles, e não há garantias. Se preferires, candidata-te directamente em micro1.ai.</div>',
   foot=f'<footer>Página pessoal e independente de Marco Cotas (Coimbra). Não é um site da micro1. Sem formulários nem cookies. Vagas e valores copiados das páginas oficiais a {DATE_PT} e podem ter mudado: confirma sempre na página da micro1.</footer>',
   apply='Candidatar em micro1.ai', more='Ver detalhes', loc='Local', pay='Pagamento anunciado pela micro1', open='Aceita Europa', all='Todas', only='Esconder vagas só para os EUA ou outro país', search='Procurar vaga (ex.: lawyer, python, portuguese)',
 ),
 'en': dict(
   nav='<nav><a href="{r}en/index.html">Jobs</a> · <a href="{r}en/micro1-interview-guide.html">Interview guide</a> · <a href="{r}index.html">Português</a></nav>',
   disc='<div class="box"><b>Disclosure:</b> the "Apply" buttons are my referral links. If you apply through them, get selected and work 10 hours, micro1 pays me a bonus. It costs you nothing. <b>I don\'t work for micro1 and I\'m not a recruiter</b>: selection, pay and hours are up to them, and nothing is guaranteed. You can also apply directly on micro1.ai.</div>',
   foot=f'<footer>Independent personal page by Marco Cotas (Portugal). Not a micro1 website. No forms, no cookies. Jobs and pay copied from micro1\'s official pages on {DATE_EN} and may have changed: always check the micro1 page.</footer>',
   apply='Apply on micro1.ai', more='Details', loc='Location', pay='Pay listed by micro1', open='Europe OK', all='All', only='Hide roles limited to the US or another country', search='Search jobs (e.g. lawyer, python, portuguese)',
 ),
}

def card(x, lang, r):
    t = T[lang]; a = x['area'][0 if lang == 'pt' else 1]
    badge = f'<span class="ok">{t["open"]}</span>' if x['pt'] == 2 else ''
    return f'''<article class="job" data-d="{E(a)}" data-pt="{1 if x['pt'] else 0}" data-s="{E((x['name'] + ' ' + a + ' ' + x['loc']).lower())}"><span class="tag">{E(a)}</span>{badge}<h3><a href="{r}vagas/{x['slug']}.html">{E(x['name'])}</a></h3>
<p><b>{t['loc']}:</b> {E(x['loc'] or '—')}{'<br><b>' + t['pay'] + ':</b> ' + E(x['rate']) if x['rate'] else ''}</p>
<a class="btn" href="{x['url']}" target="_blank" rel="noopener sponsored">{t['apply']}</a><a class="sub" href="{r}vagas/{x['slug']}.html">{t['more']}</a></article>'''

FILTER_JS = '''<script>
const g=document.getElementById('g'),q=document.getElementById('q'),o=document.getElementById('o');let f='*';
function run(){const s=q.value.toLowerCase().trim();let n=0;g.querySelectorAll('.job').forEach(j=>{const v=(f=='*'||j.dataset.d==f)&&(!o.checked||j.dataset.pt=='1')&&(!s||j.dataset.s.includes(s));j.style.display=v?'':'none';if(v)n++});document.getElementById('n').textContent=n}
document.querySelectorAll('.f').forEach(b=>b.onclick=()=>{document.querySelectorAll('.f').forEach(x=>x.classList.remove('on'));b.classList.add('on');f=b.dataset.f;run()});q.oninput=run;o.onchange=run;run();
</script>'''

def listing(lang):
    t = T[lang]; r = '' if lang == 'pt' else '../'
    areas = sorted({x['area'][0 if lang == 'pt' else 1] for x in jobs})
    filt = f'<button class="f on" data-f="*">{t["all"]}</button>' + ''.join(f'<button class="f" data-f="{E(a)}">{E(a)}</button>' for a in areas)
    cards = '\n'.join(card(x, lang, r) for x in jobs)
    npt = sum(1 for x in jobs if x['pt'] == 2); nrem = sum(1 for x in jobs if x['pt'] == 1)
    if lang == 'pt':
        head = f'''<p class="tag">Página pessoal de Marco Cotas, Coimbra</p>
<h1>Trabalho freelance remoto a treinar inteligência artificial</h1>
<p class="lead">Todas as vagas abertas da micro1 (empresa dos EUA que contrata especialistas para treinar e avaliar modelos de IA): {len(jobs)} vagas, {npt} dizem explicitamente aceitar a Europa ou qualquer país e {nrem} dizem só "Remote" (confirma o país na vaga). Actualizado a {DATE_PT}.</p>
{t['disc']}
<h2>Como funciona</h2>
<ol><li>Escolhes uma vaga que encaixe na tua formação. Confirma o campo "Local".</li>
<li>Candidatas-te no site da micro1 e fazes uma entrevista por IA, em inglês (cerca de 20 a 40 minutos). <a href="guia-entrevista-micro1.html">Lê o guia da entrevista antes</a>.</li>
<li>A micro1 decide quem entra. Quem entra trabalha como independente, remoto, com horário flexível.</li></ol>
<p>É gratuito. Nunca te devem pedir dinheiro, MB WAY ou dados bancários para começar. Se alguém pedir, é burla.</p>'''
        title = 'Vagas de treino de IA na micro1: trabalho remoto (lista actualizada)'
        mdesc = f'{len(jobs)} vagas freelance remotas de treino de inteligência artificial na micro1, com filtro por área e por país. Página independente, links de referral divulgados.'
        faq = '''<h2>Perguntas</h2>
<details><summary>Isto é burla?</summary><p>A micro1 é uma empresa real (micro1.ai). A candidatura é feita no site deles e é gratuita. Esta página é minha, não deles: só junto as vagas e partilho o meu link.</p></details>
<details><summary>Quanto se ganha?</summary><p>Não prometo valores. Cada vaga mostra o valor que a micro1 anuncia, e depende de seres selecionado e de haver tarefas.</p></details>
<details><summary>Preciso de inglês?</summary><p>Sim. As vagas e a entrevista são em inglês (há vagas para falantes de português, mas a entrevista continua a ser em inglês).</p></details>
<details><summary>Como se recebe e que impostos?</summary><p>A micro1 explica as condições a quem é selecionado. Trabalhas como independente; em Portugal isso normalmente quer dizer recibos verdes. Confirma com um contabilista.</p></details>
<details><summary>Tu ganhas alguma coisa?</summary><p>Sim, um prémio pago pela micro1 se fores selecionado e trabalhares 10 horas. Não tenho qualquer influência na seleção e não partilho o prémio.</p></details>'''
    else:
        head = f'''<p class="tag">Personal page by Marco Cotas, Portugal</p>
<h1>Remote AI training jobs at micro1</h1>
<p class="lead">Every open micro1 role (US company hiring experts to train and evaluate AI models): {len(jobs)} roles, {npt} explicitly open to Europe or worldwide and {nrem} listed just as "Remote" (check the country on the role). Updated {DATE_EN}.</p>
{t['disc']}
<h2>How it works</h2>
<ol><li>Pick a role that fits your background. Check the "Location" field.</li>
<li>Apply on micro1's site and take an AI interview in English (about 20 to 40 minutes). <a href="micro1-interview-guide.html">Read the interview guide first</a>.</li>
<li>micro1 decides who gets in. Accepted experts work as independent contractors, remote, flexible hours.</li></ol>
<p>Applying is free. Nobody should ever ask you for money or bank details to start. If they do, it's a scam.</p>'''
        title = 'micro1 jobs: remote AI training roles (updated list)'
        mdesc = f'{len(jobs)} remote freelance AI training roles at micro1, filterable by field and location. Independent page, referral links disclosed.'
        faq = '''<h2>FAQ</h2>
<details><summary>Is micro1 legit?</summary><p>micro1 is a real company (micro1.ai). You apply on their site for free. This page is mine, not theirs: I list the roles and share my link.</p></details>
<details><summary>How much does it pay?</summary><p>I don't promise anything. Each role shows the rate micro1 lists; actual work depends on being selected and on available tasks.</p></details>
<details><summary>Do I get paid as an employee?</summary><p>No, roles are freelance/contractor. micro1 explains payment terms to selected experts.</p></details>
<details><summary>Do you earn anything?</summary><p>Yes, a bonus paid by micro1 if you're selected and work 10 hours. I have no influence on selection and I don't share the bonus.</p></details>'''
    body = (t['nav'].format(r=r) + head +
            f'<h2>{"Vagas abertas" if lang=="pt" else "Open roles"} (<span id="n">{len(jobs)}</span>)</h2>'
            f'<input id="q" class="q" type="search" placeholder="{t["search"]}"><label class="chk"><input id="o" type="checkbox"> {t["only"]}</label>'
            f'<div>{filt}</div><div class="grid" id="g">\n{cards}\n</div>'
            f'<p style="margin-top:18px">{"Não encontras a tua área?" if lang=="pt" else "Not your field?"} <a href="{GERAL}" target="_blank" rel="noopener sponsored">{"Ver todas as vagas no site da micro1" if lang=="pt" else "See all roles on micro1"}</a> ({"link de referral" if lang=="pt" else "referral link"}).</p>'
            + faq + t['foot'])
    path = 'index.html' if lang == 'pt' else 'en/index.html'
    return path, page('pt-PT' if lang == 'pt' else 'en', title, mdesc, body, path, alt=[('pt', 'index.html'), ('en', 'en/index.html'), ('x-default', 'en/index.html')], script=FILTER_JS)

def render_desc(d):
    out = []
    for line in d.split('\n'):
        l = line.strip()
        if not l: continue
        if l.endswith(':') and len(l) < 60: out.append(f'<h3>{E(l[:-1])}</h3>')
        else: out.append(f'<p>{E(l)}</p>')
    return '\n'.join(out)

def job_page(x):
    r = '../'
    a_pt, a_en = x['area']
    title = f"{x['name']} (remote, micro1) | AI training job"
    mdesc = f"{x['name']}: remote freelance AI training role at micro1. {('Location: ' + x['loc'] + '. ') if x['loc'] else ''}{('Pay listed: ' + x['rate'] + '. ') if x['rate'] else ''}How to apply and prepare for the AI interview."
    body = f'''{T['en']['nav'].format(r=r)}
<p class="tag">{E(a_en)} · {E(a_pt)}</p>
<h1>{E(x['name'])}</h1>
<p class="lead"><b>Location:</b> {E(x['loc'] or 'see role')}{'<br><b>Pay listed by micro1:</b> ' + E(x['rate']) if x['rate'] else ''}<br><b>Type:</b> remote, freelance (micro1)</p>
<a class="btn big" href="{x['url']}" target="_blank" rel="noopener sponsored">Apply on micro1.ai</a>
<p class="small">Before applying: <a href="{r}en/micro1-interview-guide.html">how the micro1 AI interview works</a> · <a href="{r}guia-entrevista-micro1.html">guia em português</a></p>
{T['en']['disc']}
<h2>Role description (from micro1)</h2>
<div class="desc">{render_desc(x['desc'])}</div>
<a class="btn big" href="{x['url']}" target="_blank" rel="noopener sponsored">Apply on micro1.ai</a>
<p class="small"><a href="{r}en/index.html">← All {len(jobs)} micro1 roles</a> · <a href="{r}index.html">Todas as vagas (PT)</a></p>
{T['en']['foot']}'''
    path = f"vagas/{x['slug']}.html"
    return path, page('en', title, mdesc, body, path)

def guide(lang):
    src = open(f'{SRC}/guide_{lang}.html', encoding='utf-8').read()
    r = '' if lang == 'pt' else '../'
    meta = re.search(r'<!--title:(.*?)-->\s*<!--desc:(.*?)-->', src)
    body = T[lang]['nav'].format(r=r) + src.replace('{{GERAL}}', GERAL).replace('{{R}}', r).replace('{{N}}', str(len(jobs))) + T[lang]['disc'] + T[lang]['foot']
    path = 'guia-entrevista-micro1.html' if lang == 'pt' else 'en/micro1-interview-guide.html'
    return path, page('pt-PT' if lang == 'pt' else 'en', meta.group(1).strip(), meta.group(2).strip(), body, path,
                      alt=[('pt', 'guia-entrevista-micro1.html'), ('en', 'en/micro1-interview-guide.html')])

files = [listing('pt'), listing('en'), guide('pt'), guide('en')] + [job_page(x) for x in jobs]
os.makedirs(f'{OUT}/vagas', exist_ok=True); os.makedirs(f'{OUT}/en', exist_ok=True)
for f in os.listdir(f'{OUT}/vagas'): os.remove(f'{OUT}/vagas/{f}')
for p, h in files:
    open(f'{OUT}/{p}', 'w', encoding='utf-8').write(h)
sm = ''.join(f'<url><loc>{BASE}{p}</loc><lastmod>{DATE_ISO}</lastmod></url>' for p, _ in files)
open(f'{OUT}/sitemap.xml', 'w', encoding='utf-8').write(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>')
open(f'{OUT}/robots.txt', 'w', encoding='utf-8').write(f'User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n')
print('pages', len(files), 'jobs', len(jobs), 'explicit', sum(1 for x in jobs if x['pt']==2), 'remote', sum(1 for x in jobs if x['pt']==1), 'noloc', sum(1 for x in jobs if not x['loc']))
