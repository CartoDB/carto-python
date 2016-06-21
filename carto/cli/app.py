from carto import CartoException, APIKeyAuthClient, SQLCLient, FileImport
import click


class CartoDBUser(object):

    def __init__(self, user_name=None, api_key=None):
        self.user_name = user_name
        self.client = APIKeyAuthClient(api_key=api_key, user=user_name)
        self.sql_client = SQLCLient(self.client)

    def execute_sql(self, query):
        try:
            res = self.sql_client.send(query)
            if 'rows' in res:
                return res.get('rows')
            else:
                print(dir(res))
                raise CartoException("Your query does not return any row")
        except CartoException as e:
            raise


@click.group()
@click.option('--user-name',
              help='Your CartoDB user, you can use also ' +
              'the environment variable CARTODB_USER_NAME')
@click.option('--api-key',
              help='API KEY, you can use also the environment ' +
              'variable CARTODB_API_KEY')
@click.pass_context
def cli(ctx, user_name, api_key):
    ctx.obj = CartoDBUser(user_name, api_key)


@click.command(help="Gets the number of records of a table")
@click.argument('table_name')
@click.pass_obj
def count(cartodb, table_name):
    rows = cartodb.execute_sql(
        'select count(*) from {}'.format(table_name))
    count = rows[0].get('count')
    click.echo(count)


@click.command(help='Gets the BBOX of a table')
@click.argument('table_name')
@click.pass_obj
def bbox(cartodb, table_name):
    rows = cartodb.execute_sql(
        '''
        with data as (select ST_Extent(the_geom) as bbox from {} )
        select
            ST_XMax(bbox) xmax, ST_XMin(bbox) xmin,
            ST_YMax(bbox) ymax, ST_YMin(bbox) ymin
        from data'''.format(table_name))

    xmax = rows[0].get('xmax')
    ymax = rows[0].get('ymax')
    xmin = rows[0].get('xmin')
    ymin = rows[0].get('ymin')

    click.echo("SW: {:+9.4f} | {:+9.4f}".format(xmin, ymin))
    click.echo("NE: {:+9.4f} | {:+9.4f}".format(xmax, ymax))


@click.command(help='List schemas')
@click.pass_obj
def schema_list(cartodb):
    rows = cartodb.execute_sql('''
        select nspname as user
        from pg_catalog.pg_namespace
        where not nspowner = 10 order by nspname
        ''')

    for row in rows:
        click.echo(row.get('user'))


@click.command(help='List users tables')
@click.pass_obj
def table_list(cartodb):
    rows = cartodb.execute_sql('''
        select table_name
        from information_schema.tables
        where table_schema in (\'public\',\'{}\')
        order by table_name
        '''.format(cartodb.user_name))

    for row in rows:
        click.echo(row.get('table_name'))


@click.command(help='Import a local file')
@click.argument('file_path')
@click.option('--create-vis', type=bool, default=True,
              help="Create a visualization too?")
@click.option('--privacy', type=click.Choice(['private', 'link', 'public']),
              default='private', help="Define dataset privacy")
@click.pass_obj
def import_file(cartodb, file_path, create_vis, privacy):
    fi = FileImport(
        file_path, cartodb.client, create_vis=create_vis, privacy=privacy)
    fi.run()
    click.echo('Id:{}'.format(fi.id))
    click.echo('Status:{}'.format(fi.success))


'''
More ideas on commands to add:

- Describe table
- CartoDBfy a table
- Import dataset/URL
- Export dataset
- Execute SQL via normal and batch APIs

  - Check batch API job status

- Work on named maps:

  - list templates
  - add/update/delete template

- Work with Static Maps API

- Debug levels?
'''


cli.add_command(count)
cli.add_command(bbox)
cli.add_command(table_list)
cli.add_command(schema_list)
cli.add_command(import_file)


if __name__ == '__main__':
    # Use environment variables starting as CARTODB
    cli(auto_envvar_prefix='CARTODB')
