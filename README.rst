
hxarc
===============================

web version of https://github.com/Colin-Fredericks/hx_util


quickstart
==========

Make sure you have docker_ installed to try this quickstart.

::

    # clone this repo
    $> git clone https://github.com/nmaekawa/hxarc
    
    # start docker services
    $> docker-compose up
    $> docker-compose exec web python manage.py migrate
    $> docker-compese exec web python manage.py createsupersuser
    $> open http://localhost:8000/admin

To login into the django admin UI, use the user:password created above in
`createsuperuser`; in the table `Consumers` create a new record with a consumer
and secret key of your choice.

To configure hxarc in an lti consumer, the launch parameters below are
required:

    - consumer-key: "consumer-just-created"
    - consumer-secret: "secret-just-created"
    - lis_person_sourcedid: "some-string"

---eop

.. _docker: https://www.docker.com



