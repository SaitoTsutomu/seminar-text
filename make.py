"""Make OR Seminar text"""
import yaml
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pdfrw import PdfReader
from pdfrw.buildxobj import pagexobj
from pdfrw.toreportlab import makerl
from more_itertools import chunked
pdfmetrics.registerFont(TTFont('IPAexGothic', '/usr/share/fonts/ipaexg.ttf'))

def addpage(np=[0]):
    np[0] += 1
    c.setFillColor('gray')
    c.drawRightString(w_-8, h_-16, header)
    c.setFillColor('black')
    c.drawCentredString(w_/2, mgn/2+2, '%d/%d'%(np[0],nn))

with open('config.yml', encoding='utf8') as fp:
    config = yaml.load(fp)
header = config['param']['header']
mgn = config['param']['margin']
titpar = config['param']['titlepar']
contents = config['contents']
keys = ['title1','title2','title3','name','depart']
c = Canvas(config['param']['outfile'], initialFontName='IPAexGothic', initialFontSize=12)
w_, h_ = c._pagesize
r_ = min(1 - 2*mgn/w_, 1 - 2*mgn/h_)
w, h, nn = r_*w_, r_*h_, 0
for cnt in contents:
    tw = 2 if cnt['twoup'] else 4
    if cnt['hasTitle']:
        nn += 2
    pr = PdfReader(cnt['file'])
    if isinstance(cnt['range'], str):
        cnt['range'] = eval(cnt['range'])
    nn += (len(cnt['range'])+tw*2-1)//(tw*2)*2
for cnt in contents:
    tw = 2 if cnt['twoup'] else 4
    if cnt['hasTitle']:
        addpage()
        c.translate(80, h/2-80)
        for p,s in zip(titpar, [cnt[k] for k in keys]):
            c.setFontSize(p[0])
            c.drawString(*p[1:], s)
        c.showPage()
        addpage()
        c.showPage()
    pr = PdfReader(cnt['file'])
    pages = [pagexobj(pr.pages[i]) for i in cnt['range']]
    for pgs in chunked(pages, tw):
        addpage()
        c.translate(w_/2-w/2, h_/2-h/2)
        for i, pg in enumerate(pgs):
            r = min(w/pg.h, h/pg.w)/2 if tw == 4 else min(w/pg.w, h/pg.h/2)
            c.saveState()
            if tw == 4:
                c.translate((1+i//2)*w/2+(w/2-pg.h*r)/2, (i%2)*h/2+(h/2-pg.w*r)/2)
            else:
                c.translate((w-pg.w*r)/2, (1-i%2)*pg.h*r+(h-pg.h*r*2)/2)
            if tw == 4:
                c.rotate(90)
            c.scale(r, r)
            c.doForm(makerl(c, pg))
            c.setStrokeColor('gray')
            c.rect(0,0,pg.w,pg.h)
            c.restoreState()
        c.showPage()
    if (len(pages)+tw-1)//tw%2:
        addpage()
        c.showPage()
c.save()
