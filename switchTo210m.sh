Sub1=76d03a17-20be-4175-bbed-ca6d7819c68f
Sub2=789b2037-d4c7-40c7-99e8-f36aed4f3f00

# start the Cluster at $210/month subscriptionp
az account set --subscription $Sub1
az aks get-credentials --resource-group pixiedemo --name pixiecluster --overwrite-existing
az aks stop --name pixiecluster --resource-group pixiedemo
az aks start --name pixiecluster --resource-group pixiedemo

# stop the the Cluster at $210/m subscription
az account set --subscription $Sub2
az aks get-credentials --resource-group pixiedemo --name pixiecluster --overwrite-existing
az aks stop --name pixiecluster --resource-group pixiedemo

#switch back to the old cluster
az account set --subscription $Sub1
az aks get-credentials --resource-group pixiedemo --name pixiecluster --overwrite-existing
kubectl get service --watch --namespace=sock-shop

kubectl get pod --watch --namespace=sock-shop