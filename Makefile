mig:
	python3 manage.py makemigrations
	python3 manage.py migrate

super:
	python3 manage.py createsuperuser
stub:
	pip3 install django-stubs

lang:
	python manage.py makemessages -l uz
	python manage.py makemessages -l ru
	python manage.py makemessages -l en
	python manage.py makemessages -l ar
	python manage.py makemessages -l ko

compile:
	python manage.py compilemessages
