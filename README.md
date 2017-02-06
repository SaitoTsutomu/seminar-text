Make Semiar Text.
========

1) Prepare PDF.
2) docker run -it --rm tsutomu7/seminar-text cat /config.yml.sample > config.yml
3) Edit config.yml
4) docker run -it --rm -v $PWD:/tmp tsutomu7/seminar-text
5) Use out.pdf

## config.yml

Item|Description
:--|:--
file|Input file name
range|List of target page number(0-)
numup|Input pages per an output page
hasTitle|Contents has a title page
titles|List of string in a title page
toEven|Make to even
flowToDown|Page flow direction when 4 up