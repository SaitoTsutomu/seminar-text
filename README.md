Make Semiar Text.
========

1) Prepare PDF.
2) docker run -it --rm tsutomu7/seminar-text cat /config.yml.sample > config.yml
3) Edit config.yml
4) docker run -it --rm -v $PWD:/tmp tsutomu7/seminar-text
5) Use out.pdf