
build:
	./debBuild.sh

clean:
	rm tmp -r 
	rm /usr/local/bin/mypl
	rm /usr/local/mypl -r

lint:
	./lint.sh

test:
	pytest src/bin/hw6_tests.py
