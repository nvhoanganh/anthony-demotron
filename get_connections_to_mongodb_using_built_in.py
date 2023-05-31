# Import Pixie's module for querying data
import px

# Load the last 30 seconds of Pixie's `conn_stats` table into a Dataframe.
df = px.DataFrame(table='conn_stats', start_time=px.plugin.start_time, end_time=px.plugin.end_time)
# df = px.DataFrame(table='conn_stats', start_time='-30s')

# select column you want, you can run `px live px/schemas` to get the column list of tables and column names
# in this case we just want remote_addr,remote_port,conn_open,conn_close
# df = df[['remote_addr','remote_port','conn_open', 'conn_close']]

# attach Context information
ns_prefix = df.ctx['namespace'] + '/'
df.container = df.ctx['container_name']
df.pod = px.strip_prefix(ns_prefix, df.ctx['pod'])
df.service = px.strip_prefix(ns_prefix, df.ctx['service'])
df.namespace = df.ctx['namespace']
df.cluster_name = 'pixiedemo'
df.cluster_id = px.vizier_id()
df.pixie = 'pixie'

# filter by port 27017 only
df = df[df['remote_port'] == 27017]

# px.display(df)

df.open = 'open'
df.close = 'close'

# export
px.export(
  df, px.otel.Data(
    resource={
      'service.name': df.service,
      'k8s.container.name': df.container,
      'service.instance.id': df.pod,
      'k8s.pod.name': df.pod,
      'k8s.namespace.name': df.namespace,
      'pixie.cluster.id': df.cluster_id,
      'k8s.cluster.name': df.cluster_name,
      'instrumentation.provider': df.pixie,
    },
    data=[
      px.otel.metric.Gauge(
        name='pixie.mongodb.connection',
        value=df.conn_open,
        attributes={'type': df.open, 'area': df.bytes_sent},
      ),
      px.otel.metric.Gauge(
        name='pixie.mongodb.connection',
        description='Number of connection open to the MongoDB service',
        value=df.conn_close,
        attributes={'type': df.close, 'area': df.bytes_sent},
      ),
    ],
  ),
)
