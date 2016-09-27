name=python-dynpart-partition-director
version=0.08
tag=master
git=https://github.com/indigo-dc/dynpart.git
source_dir=sources
rpmbuild_dir=$(shell pwd)/rpmbuild
spec=dynpart-pd.spec
dist=$(shell rpm --eval '%dist' | sed 's/%dist/.el5/')

.PHONY: clean rpm

all: rpm

print-info:
	@echo
	@echo
	@echo "Packaging $(name) fetched from $(git) for tag $(tag)."
	@echo

prepare-sources: sanity-checks clean
	mkdir -p $(source_dir)/$(name)
	git clone $(git) $(source_dir)/$(name)
	cd $(source_dir)/$(name) && git checkout $(tag) && git archive --format=tar --prefix=$(name)-$(version)/ $(tag) > $(name)-$(version).tar
	cd $(source_dir) && gzip $(name)/$(name)-$(version).tar
	cp $(source_dir)/$(name)/$(name)-$(version).tar.gz $(source_dir)/$(name)-$(version).tar.gz

rpm: prepare-sources
	mkdir -p $(rpmbuild_dir)/BUILD \
	$(rpmbuild_dir)/RPMS \
	$(rpmbuild_dir)/SOURCES \
	$(rpmbuild_dir)/SPECS \
	$(rpmbuild_dir)/SRPMS
	cp $(source_dir)/$(name)-$(version).tar.gz $(rpmbuild_dir)/SOURCES
	rpmbuild --nodeps -v -ba $(source_dir)/$(name)/packaging/rpm/$(spec) --define "_topdir $(rpmbuild_dir)" --define "dist $(dist)" --define "version $(version)"

clean:
	rm -rf $(source_dir) $(rpmbuild_dir)

sanity-checks:
ifndef version
	$(error version is undefined)
endif
