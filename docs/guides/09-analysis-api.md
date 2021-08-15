## Analysis API

This allows managing the definition, execution and monitoring of analyses in a simple way, with some basic command line output.

There's an option to use short identifiers, valid during the session, instead of the actual (long) identifiers.

The output of commands that follow the execution of an analysis will be updated periodically with the configured frequency.

Example of use, list jobs:

```python
from carto.analysis import AnalysisContext

analysis = AnalysisContext(
    auth_client,
    minimum_update_time=4, # Update frequency: 4 seconds
    autosleep=True         # Updates will wait minimum_update_time and then be performed
)

# List analysis jobs
for job in analysis.jobs():
    print(job.info())
```

Output:

```
bigquery-example 1.0.0 (rtorre-analysis)
kmeans 1.0.0 (jgoizueta-analysis)
kmeans-r 1.0.0 (rtorre-analysis)
```

Create a new analysis job:

```python
job = analysis.create_job(
    {
        "name": "kmeans-test",
        "image": "rafatower/kmeans:v1.0.0",
        "version": "1.0.0",
        "description": "KMeans clusters",
        "parameters": ["n_clusters", "dataset", "columns"]
    }
)
print(job.info())
```

Output:

```
kmeans 1.0.0 (YOUR-USER-NAME)
```

Example 2: execute the job and show it's execution progress

```python
params = {
    "n_clusters": 3,
    "dataset": "brooklyn_poverty",
    "columns": ["poverty_per_pop"]
}
schedule = job.execute_and_follow(params)
```

Output (final state):
```
kmeans/1 2019-01-30 10:25:32 : dead : C:1 S:0 F:0 L:0 Q:0 R:0
kmeans/1/1 2019-01-30 10:25:32 : success (ran from 2019-01-30 10:25:33+00:00 to 2019-01-30 10:25:41+00:00)
EVENTS
Task received by client Time:1548843932611818957
Building Task Directory Time:1548843932612050357
Task started by client Time:1548843933127955118
Exit Code: 0 Time:1548843941822685581

STDOUT
Config: {u'conn': u'postgresql://development_cartodb_user_21247c38-f9b5-4cdb-9f11-f21e8edca58e:6ea8860cdae0549b96c88bd00a02bee21c557a88development_cartodb_user_21247c38-f9b5-4cdb-9f11-f21e8edca58e@10.0.32.28:9432/cartodb_dev_user_21247c38-f9b5-4cdb-9f11-f21e8edca58e_db', u'n_clusters': 3, u'columns': [u'poverty_per_pop'], u'dataset': u'brooklyn_poverty'}
Output written to table brooklyn_poverty_kmeans_out
```

Note that short identifiers are used for schedules (`kmeans/1`) and executions (`kmeans/1/1`). These are valid tokens for the session.

Example 3: show a schedule's info, and list its executioins

```python
schedule.show()
for execution in schedule.executions():
    print(execution.info())
```

Output:

```
kmeans/3 2019-01-30 10:25:32 : dead : C:1 S:0 F:0 L:0 Q:0 R:0
kmeans/3/1 2019-01-30 10:25:32 : success (ran from 2019-01-30 10:25:33+00:00 to 2019-01-30 10:25:41+00:00)
```

The first line shows the (short) id of the schedule we created, the state and a summary of:
* `C` number of complete executions
* `S` number of starting executions
* `F` number of failed executions
* `L` number of lost executions
* `Q` number of queued executions
* `R` number of running executions

The second line shows information about then only (complete) execution.

Example 4: show the last execution of an schedule

```python
exec = schedule.executions()[-1]
exec.show()
```

Output:

```
kmeans/3/1 2019-01-30 10:25:32 : success (ran from 2019-01-30 10:25:33+00:00 to 2019-01-30 10:25:41+00:00)
EVENTS
Task received by client Time:1548843932611818957
Building Task Directory Time:1548843932612050357
Task started by client Time:1548843933127955118
Exit Code: 0 Time:1548843941822685581

STDOUT
Config: {u'conn': u'postgresql://development_cartodb_user_21247c38-f9b5-4cdb-9f11-f21e8edca58e:6ea8860cdae0549b96c88bd00a02bee21c557a88development_cartodb_user_21247c38-f9b5-4cdb-9f11-f21e8edca58e@10.0.32.28:9432/cartodb_dev_user_21247c38-f9b5-4cdb-9f11-f21e8edca58e_db', u'n_clusters': 3, u'columns': [u'poverty_per_pop'], u'dataset': u'brooklyn_poverty'}
Output written to table brooklyn_poverty_kmeans_out
```

Example 5: Select job by name and list it's schedules

```python
job = analysis.job_by_name('kmeans')
for schedule in job.schedules():
    schedule.show()
```

Output:

```
kmeans/1 2019-01-25 14:47:45 : running : C:0 S:0 F:0 L:0 Q:0 R:0 (52 * * * * *)
kmeans/2 2019-01-30 10:02:40 : dead : C:1 S:0 F:0 L:0 Q:0 R:0
```

Note that short ids are used here; the summary numbers are as explained in example 3.

## Synchronous output

If an analysis follows the convention of returning an output value through the standard output
(standard error could be used for logging in that case), then you can execute an analysis syncrhonously
and obtain its result with this command.

```python
job = analysis.job_by_token('carto-geocoder')
result = job.execute_and_get_output({
    "dataset": "accidentesbicicletas_2018",
    "street": "regexp_replace(trim(lugar_accidente), ' NUM$', '') || '  ' || n",
    "city": "'Madrid'",
    "country": "'Spain'",
    "log_level": "DEBUG",
    "dry": True
}, decodeJson=True)
print(result)
```

Output:
```
{'total_rows': 667, 'required_quota': 667, 'previously_geocoded': 0, 'previously_failed': 0, 'records_with_geometry': 266}
```

For non-JSON output simply omit the `decodeJson` argument: `result = job.execute_and_get_output(params)` and you'll get a bytes string.
For viewing the execution progress as with the *follow* methods, just add a `verbose=True` argument.
