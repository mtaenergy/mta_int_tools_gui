az acr login -n guidocker
docker build -t guidocker.azurecr.io/mta_int_tools_gui:v1 .
docker tag mta_int_tools_gui:v1 guidocker.azurecr.io/mta_int_tools_gui:v1
docker push guidocker.azurecr.io/mta_int_tools_gui:v1
az container delete --name mta_int_tools_gui --resource-group rg-mtaops-prod-001 -y
az container create --resource-group rg-mtaops-prod-001 --name mta_int_tools_gui -f deployment.yml