import px
# Get list of pods (even non-HTTP)
df = px.DataFrame(table='process_stats', start_time='-30s')
df.pod = df.ctx['pod']
pods_list = df.groupby('pod').agg()
# Get HTTP events (not all pods will have this)
df = px.DataFrame(table='http_events', start_time='-30s')
df.pod = df.ctx['pod']
df = df.groupby('pod').agg(
    requests=('latency', px.count)
)
df.rps = df.requests / 30;
df = pods_list.merge(df, how='left', left_on='pod', right_on='pod', suffixes=['', '_x'])
px.display(df[['pod', 'rps']], 'pod_stats')