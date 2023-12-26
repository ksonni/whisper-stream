install:
	cd api && make install
	cd ui && npm install 
	cd protobuf && make install

type_check:
	cd api && make type_check
	cd ui && npm run type-check

test:
	cd api && make test
	cd ui && npm run build-only
