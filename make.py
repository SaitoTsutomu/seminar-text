"""Make OR Seminar text"""
import yaml
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pdfrw import PdfReader
from pdfrw.buildxobj import pagexobj
from pdfrw.toreportlab import makerl
from more_itertools import chunked
def addHeaderFooter(np=[0]):
    np[0] += 1
    if header:
        c.setFillColor('gray')
        c.drawRightString(w_-8, h_-16, header)
    if footer:
        c.setFillColor('black')
        c.drawCentredString(w_/2, mgn/2+2, footer%(np[0],len(cnts)))
def addPage(c, w, h, numup, pg):
    pgw, pgh = pg.w, pg.h
    islandscape = pgw >= pgh
    if not islandscape:
        pgw, pgh = pgh, pgw
    r = [min(w/pgh,h/pgw), min(w/pgw,h/2/pgh), min(w/pgh,h/pgw)/2][abs(numup)//2]
    c.saveState()
    if numup == 1:
        if islandscape:
            c.translate(pgh*r+(w-pgh*r)/2, (h-pgw*r)/2)
            c.rotate(90)
    elif numup == 2:
        if islandscape:
            c.translate((w-pgw*r)/2, (1-i%2)*pgh*r+(h-pgh*r*2)/2)
        else:
            c.translate((w*3-pgw*r)/2, (1-i%2)*pgh*r+(h-pgh*r*2)/2)
            c.rotate(90)
    elif numup == 4:
        if islandscape:
            c.translate((1+i//2)*w/2+(w/2-pgh*r)/2, (i%2)*h/2+(h/2-pgw*r)/2)
            c.rotate(90)
        else:
            c.translate((i%2)*w/2+(w/2-pgh*r)/2, (1-i//2)*h/2+(h/2-pgw*r)/2)
    elif numup == -4:
        if islandscape:
            c.translate((1+i%2)*w/2+(w/2-pgh*r)/2, (i//2)*h/2+(h/2-pgw*r)/2)
            c.rotate(90)
        else:
            c.translate((i//2)*w/2+(w/2-pgh*r)/2, (1-i%2)*h/2+(h/2-pgw*r)/2)
    c.scale(r, r)
    c.doForm(makerl(c, pg))
    c.setStrokeColor('gray')
    c.rect(0,0,pg.w,pg.h)
    c.restoreState()

with open('config.yml', encoding='utf8') as fp:
    config = yaml.load(fp)
contents = config['contents']
param = config['param']
mgn = param.get('margin', 10)
fontFile = param.get('fontFile', '/usr/share/fonts/ipaexg.ttf')
pdfmetrics.registerFont(TTFont('IPAexGothic', fontFile))
fntsz = param.get('fontSize', 12)
header = param.get('header')
footer = param.get('footer')
ttfntpos = param.get('titleFontPos', [])
c = Canvas(param.get('outFile', 'out.pdf'),
    initialFontName='IPAexGothic', initialFontSize=fntsz)
w_, h_ = c._pagesize
r_ = min(1 - 2*mgn/w_, 1 - 2*mgn/h_)
w, h = r_*w_, r_*h_
cnts = []
for cnt in contents:
    numup = cnt.get('numup', 4)
    assert numup in [1,2,4]
    toEven = cnt.get('toEven', False)
    if cnt.get('hasTitle', False):
        cnts.append((-1, cnt['titles'])) # header
        if toEven:
            cnts.append((0, None)) # blank
    pr = PdfReader(cnt['file'])
    rng = cnt.get('range', 'range(pr.numPages)')
    if isinstance(rng, str):
        rng = eval(rng)
    nm = numup if numup != 4 or not cnt.get('flowToDown', False) else -4
    pages = [pagexobj(pr.pages[i]) for i in rng]
    for pgs in chunked(pages, numup):
        cnts.append((nm, pgs))
    if toEven and (len(pages)+numup-1)//numup % 2:
        cnts.append((0, None)) # blank
for numup, pgs in cnts:
    addHeaderFooter()
    if numup == -1: # header
        c.translate(80, h/2-80)
        for p,s in zip(ttfntpos, pgs):
            c.setFontSize(p[0])
            c.drawString(*p[1:], s)
    elif numup != 0:
        c.translate(w_/2-w/2, h_/2-h/2)
        for i, pg in enumerate(pgs):
            addPage(c, w, h, numup, pg)
    c.showPage()
c.save()
