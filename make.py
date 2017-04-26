"""Make OR Seminar text"""
import sys, yaml
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pdfrw import PdfReader
from pdfrw.buildxobj import pagexobj
from pdfrw.toreportlab import makerl
from more_itertools import chunked
def addHeaderFooter(option, numcnts, np=[0]):
    if (option&O_NOPAGEFEED)==0:
        np[0] += 1
    if header and (option&O_NOHEADER)==0:
        c.setFillColor('gray')
        c.drawRightString(w_-8, h_-16, header)
    if footer and (option&O_NOFOOTER)==0:
        c.setFillColor('black')
        c.drawCentredString(w_/2, mgn/2+2, footer%(np[0],numcnts))
def addPage(c, w, h, numup, i, pg, trsc):
    pgw, pgh = pg.w, pg.h
    islandscape = pgw >= pgh
    if not islandscape:
        pgw, pgh = pgh, pgw
    r = trsc[2] if trsc else [min(w/pgh,h/pgw), min(w/pgw,h/2/pgh), min(w/pgh,h/pgw)/2][abs(numup)//2]
    c.saveState()
    if trsc:
        c.translate(trsc[0], trsc[1])
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
    elif numup == -2:
        if islandscape:
            c.translate((w-pgw*r)/2, (i%2)*pgh*r+(h-pgh*r*2)/2)
        else:
            c.translate((w*3-pgw*r)/2, (i%2)*pgh*r+(h-pgh*r*2)/2)
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

O_NOHEADER = 1
O_NOFOOTER = 2
O_NOPAGEFEED = 4
O_ISRAW = 8
with open(sys.argv[1] if len(sys.argv) > 1 else 'config.yml', encoding='utf8') as fp:
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
    option = ((O_NOHEADER if cnt.get('noHeader', False) else 0)
             |(O_NOFOOTER if cnt.get('noFooter', False) else 0)
             |(O_NOPAGEFEED if cnt.get('noPageFeed', False) else 0)
             |(O_ISRAW if cnt.get('isRaw', False) else 0))
    trsc = cnt.get('transScale', None)
    numup = cnt.get('numup', 1)
    assert numup in [1,2,4]
    toEven = cnt.get('toEven', False)
    if cnt.get('hasTitle', False):
        cnts.append((-1, option, trsc, cnt['titles'])) # header
        if toEven:
            cnts.append((0, option, trsc, None)) # blank
    pr = PdfReader(cnt['file'])
    rng = cnt.get('range', 'range(pr.numPages)')
    if isinstance(rng, str):
        rng = eval(rng)
    nm = numup if numup == 1 or not cnt.get('flowToDown', False) else -numup
    pages = [pagexobj(pr.pages[i]) for i in rng]
    for pgs in chunked(pages, numup):
        cnts.append((nm, option, trsc, pgs))
    if toEven and (len(pages)+numup-1)//numup % 2:
        cnts.append((0, option, trsc, None)) # blank
numcnts = 0
for _, option, _, _ in cnts:
    if (option&O_NOPAGEFEED) == 0:
        numcnts += 1
for numup, option, trsc, pgs in cnts:
    addHeaderFooter(option, numcnts)
    if option&O_ISRAW:
        c.saveState()
        if trsc:
            c.translate(trsc[0], trsc[1])
            c.scale(trsc[2], trsc[2])
        if pgs:
            for pg in pgs:
                c.doForm(makerl(c, pg))
        c.restoreState()
    elif numup == -1: # header
        c.translate(80, h/2-80)
        for p,s in zip(ttfntpos, pgs):
            c.setFontSize(p[0])
            c.drawString(*p[1:], s)
    elif numup != 0:
        c.translate(w_/2-w/2, h_/2-h/2)
        for i, pg in enumerate(pgs):
            addPage(c, w, h, numup, i, pg, trsc)
    c.showPage()
c.save()
