Custom visualizations (aka Kuviz)
=================================

Create a Kuviz Manager
^^^^^^^^^^^^^^^^^^^^^^
::

  from carto.auth import APIKeyAuthClient
  from carto.kuvizs import KuvizManager

  auth_client = APIKeyAuthClient(api_key=API_KEY, base_url=BASE_URL)
  km = KuvizManager(auth_client)


Create a Kuviz
^^^^^^^^^^^^^^
::

  html = "<html><body><h1>Working with CARTO Kuviz</h1></body></html>"
  public_kuviz = km.create(html=html, name="kuviz-public-test")


Create a Kuviz with password
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
::

  html = "<html><body><h1>Working with CARTO Kuviz</h1></body></html>"
  password_kuviz = km.create(html=html, name="kuviz-password-test", password="1234")


List all Kuviz
^^^^^^^^^^^^^^
::

  kuvizs = km.all()


Update a kuviz
^^^^^^^^^^^^^^
::

  new_html = "<html><body><h1>Another HTML</h1></body></html>"
  public_kuviz.data = new_html
  public_kuviz.save()


Adding a password
^^^^^^^^^^^^^^^^^^
::

  public_kuviz.password = "1234"
  public_kuviz.save()


Removing a password
^^^^^^^^^^^^^^^^^^^
::

  public_kuviz.password = None
  public_kuviz.save()


Delete
^^^^^^
::

  public_kuviz.delete()

