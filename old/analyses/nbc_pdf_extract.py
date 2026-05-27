from pypdf import PdfReader
p = r'C:\Users\jayzh\.claude\projects\C--Users-jayzh-projects-macro-research-department\63e74897-7417-49f5-8f39-1031f5e21841\tool-results\webfetch-1778474355849-j3l93v.pdf'
r = PdfReader(p)
print('pages:', len(r.pages))
for i, page in enumerate(r.pages[:6]):
    print(f'--- page {i+1} ---')
    txt = page.extract_text() or ''
    print(txt[:3000])
    print()
