FROM tsutomu7/scientific-python

COPY make.py config.yml.sample /tmp/
WORKDIR /tmp
CMD ["python", "make.py"]
