## Maps API

The `Maps API`_ allows to create and instantiate named and anonymous maps:

```python

  from carto.maps import NamedMapManager, NamedMap
  import json

  # write the path to a local file with a JSON named map template
  JSON_TEMPLATE = ""

  named_map_manager = NamedMapManager(auth_client)
  named_map = NamedMap(named_map_manager.client)

  with open(JSON_TEMPLATE) as named_map_json:
      template = json.load(named_map_json)

  # Create named map
  named = named_map_manager.create(template=template)
```

```python

  from carto.maps import AnonymousMap
  import json

  # write the path to a local file with a JSON named map template
  JSON_TEMPLATE = ""

  anonymous = AnonymousMap(auth_client)
  with open(JSON_TEMPLATE) as anonymous_map_json:
      template = json.load(anonymous_map_json)

  # Create anonymous map
  anonymous.instantiate(template)
```

**Tip:** If you want to learn more about Maps API, browse its [guides]({{site.mapsapi_docs}}/guides/) and [reference]({{site.mapsapi_docs}}/reference/).

### Instantiate a named map

```python

  from carto.maps import NamedMapManager, NamedMap
  import json

  # write the path to a local file with a JSON named map template
  JSON_TEMPLATE = ""

  # write here the ID of the named map
  NAMED_MAP_ID = ""

  # write here the token you set to the named map when created
  NAMED_MAP_TOKEN = ""

  named_map_manager = NamedMapManager(auth_client)
  named_map = named_map_manager.get(NAMED_MAP_ID)

  with open(JSON_TEMPLATE) as template_json:
      template = json.load(template_json)

  named_map.instantiate(template, NAMED_MAP_TOKEN)
```

### Work with named maps

```python

  from carto.maps import NamedMapManager, NamedMap

  # write here the ID of the named map
  NAMED_MAP_ID = ""

  # get the named map created
  named_map = named_map_manager.get(NAMED_MAP_ID)

  # update named map
  named_map.view = None
  named_map.save()

  # delete named map
  named_map.delete()

  # list all named maps
  named_maps = named_map_manager.all()
```

For more examples on how to use the Maps API, please refer to the [examples]({{site.pythonsdk_docs}}/examples/) section.
