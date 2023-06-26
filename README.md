# Documentation

The blog post that accompanies this repository [can be found here on this website](https://benalexkeen.com/deploying-streamlit-applications-with-azure-app-services/).

# Deployment

[![Deploy To Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fbenalexkeen%2Fstreamlit-azure-app-services%2Fmain%2Fazuredeploy.json)

## Updating ARM template for a new deployment
- Update the files azuredeploy.json and azuredeploy.parameters.json with project specific parameters
- Upload those files to Azure in the template screen

## Redeploying after changes have been made to project
**Note**: Requires Azure extension on Visual Studio Code

- Go to Azure extension in Visual Studio Code
- Select the subscription and then navigate to *App Services*
- Right click the name the web app to redeploy to and select *Deploy to Web App...*
- Select the current repository on the local computer with the updated app and then click *Deploy*
