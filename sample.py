import px

 # The dns_events table pairs DNS requests with their responses.
# df = px.DataFrame(table='dns_events', start_time='-30m')
df = px.DataFrame(table='dns_events', start_time=px.plugin.start_time, end_time=px.plugin.end_time)

# Parse the DNS response to determine if it was successfully resolved.
df.resp_body = px.pluck(df.resp_body, 'answers')
df.request_resolved = px.contains(df.resp_body, 'name')

# Filter for resolved requests.
df = df[df.request_resolved]

# Parse the DNS request for query name.
# TODO: cleanup this logic when we support object types.
df.req_body = px.pluck(df.req_body, 'queries')
df.idx1 = px.find(df.req_body, '\"name\":')
df.idz = px.length(df.req_body) - (df.idx1 + 8) - 3
df.fqdn_partial = px.substring(df.req_body, df.idx1 + 8, df.idz)
df.idx2 = px.find(df.fqdn_partial, ',')
df.fqdn = px.substring(df.fqdn_partial, 0, df.idx2 - 1)

# Filter out local domain queries:
# If your k8s cluster uses a different internal domain suffix, add it here.
df = df[not px.contains(df.fqdn, '.local')]
df = df[not px.contains(df.fqdn, '.internal')]

# Add link to script that will show all requests for specific query.
df.link = px.script_reference('All DNS requests containing FQDN as substring',
                              'sotw/dns_queries_filtered', {
                                  'start_time': '-30m',
                                  'query_name_filter': df.fqdn
                              })

# Group by (fqdn, link) and count number of requests.
df = df.groupby(['fqdn', 'link']).agg(
    num_requests=('request_resolved', px.count)
)

# px.display(df)

# export
px.export(
  df, px.otel.Data(
    resource={
      'service.name': 'dns_fqdn_stats',
      'instrumentation.provider': 'pixie',
      'pixie.cluster.id': 'pixiecluster',
    },
    data=[
      px.otel.metric.Gauge(
        name='pixie.fqdn',
        value=df.num_requests,
        attributes={'fqdn': df.fqdn},
      ),
    ],
  ),
)
