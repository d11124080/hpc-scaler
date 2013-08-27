TAR=tar
GZIP_ENV=--best

PREFIX=/home/ronan/project/hpc-scaler/ClusterInterface/Drivers/Torque/pbs_python/fourthreefive
exec_prefix=$(PREFIX)
BINDIR=$(PREFIX)/bin

DOCDIR=/home/ronan/project/hpc-scaler/ClusterInterface/Drivers/Torque/pbs_python/fourthreefive
EXAMPLES=$(DOCDIR)/examples

.PHONY: install pythonlib
pythonlib:
	#(cd src; make)
	python setup.py build

#install: pythonlib sara_install
install: pythonlib
	python ./setup.py install --prefix $(DESTDIR)/$(exec_prefix) ;

sara_install:
	install -D examples/new_rack_pbsmon.py $(DESTDIR)/$(BINDIR)/pbsmon

clean:
	rm -rf config.log config.cache config.status build

distclean: clean
	rm Makefile setup.py
