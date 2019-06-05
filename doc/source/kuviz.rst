Custom visualizations (aka Kuviz)
=================================

Create
^^^^^^
::

  from carto.kuvizs import KuvizManager

  km = KuvizManager(auth_client)
  html = "<html><body><h1>Hi Kuviz</h1></body></html>"
  kuviz = km.create(html=html, name="public-kuviz")

  print(kuviz.id)
  print(kuviz.url)


Create with password
^^^^^^^^^^^^^^^^^^^^
::

  from carto.kuvizs import KuvizManager

  km = KuvizManager(auth_client)
  html = "<html><body><h1>Hi Kuviz</h1></body></html>"
  kuviz = km.create(html=html, name="password-protected-kuviz", password="your-password")

  print(kuviz.id)
  print(kuviz.url)


List all Kuviz
^^^^^^^^^^^^^^

WIP


Update
^^^^^^

WIP


Delete
^^^^^^

WIP
