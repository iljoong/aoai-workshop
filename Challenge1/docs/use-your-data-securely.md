---
title: 'Using your data with Azure OpenAI securely'
titleSuffix: Azure OpenAI
description: Use this article to learn about securely using your data for text generation in Azure OpenAI.
#services: cognitive-services
manager: nitinme
ms.service: azure-ai-openai
ms.topic: how-to
author: aahill
ms.author: aahi
ms.date: 02/13/2024
recommendations: false
---

# Securely use Azure OpenAI On Your Data

Use this article to learn how to use Azure OpenAI On Your Data securely by protecting data and resources with Microsoft Entra ID role-based access control, virtual networks and private endpoints.

This article is only applicable when using [Azure OpenAI On Your Data with text](/azure/ai-services/openai/concepts/use-your-data). It does not apply to [Azure OpenAI On Your Data with images](/azure/ai-services/openai/concepts/use-your-image-data).

## Data ingestion architecture 

When you use Azure OpenAI On Your Data to ingest data from Azure blob storage, local files or URLs into Azure AI Search, the following process is used to process the data.

:::image type="content" source="../media/use-your-data/ingestion-architecture.png" alt-text="A diagram showing the process of ingesting data." lightbox="../media/use-your-data/ingestion-architecture.png":::

* Steps 1 and 2 are only used for file upload.
* Downloading URLs to your blob storage is not illustrated in this diagram. After web pages are downloaded from the internet and uploaded to blob storage, steps 3 onward are the same.
* Two indexers, two indexes, two data sources and a [custom skill](/azure/search/cognitive-search-custom-skill-interface) are created in the Azure AI Search resource.
* The chunks container is created in the blob storage.
* If the ingestion is triggered by a [scheduled refresh](../concepts/use-your-data.md#schedule-automatic-index-refreshes), the ingestion process starts from step 7.
*  Azure OpenAI's `preprocessing-jobs` API implements the [Azure AI Search customer skill web API protocol](/azure/search/cognitive-search-custom-skill-web-api), and processes the documents in a queue. 
* Azure OpenAI:
    1. Internally uses the first indexer created earlier to crack the documents.
    1. Uses a heuristic-based algorithm to perform chunking, honoring table layouts and other formatting elements in the chunk boundary to ensure the best chunking quality.
    1. If you choose to enable vector search, Azure OpenAI uses the selected embedding deployment to vectorize the chunks internally.
* When all the data that the service is monitoring are processed, Azure OpenAI triggers the second indexer.
* The indexer stores the processed data into an Azure AI Search service.

For the managed identities used in service calls, only system assigned managed identities are supported. User assigned managed identities aren't supported.

## Inference architecture

:::image type="content" source="../media/use-your-data/inference-architecture.png" alt-text="A diagram showing the process of using the inference API." lightbox="../media/use-your-data/inference-architecture.png":::

When you send API calls to chat with an Azure OpenAI model on your data, the service needs to retrieve the index fields during inference to perform fields mapping automatically if the fields mapping isn't explicitly set in the request. Therefore the service requires the Azure OpenAI identity to have the `Search Service Contributor` role for the search service even during inference.

If an embedding deployment is provided in the inference request, the rewritten query will be vectorized by Azure OpenAI, and both query and vector are sent Azure AI Search for vector search.

## Document-level access control

> [!NOTE] 
> Document-level access control is supported for Azure AI search only.

Azure OpenAI On Your Data lets you restrict the documents that can be used in responses for different users with Azure AI Search [security filters](/azure/search/search-security-trimming-for-azure-search-with-aad). When you enable document level access, the search results returned from Azure AI Search and used to generate a response will be trimmed based on user Microsoft Entra group membership. You can only enable document-level access on existing Azure AI Search indexes. To enable document-level access:

1. Follow the steps in the [Azure AI Search documentation](/azure/search/search-security-trimming-for-azure-search-with-aad) to register your application and create users and groups.
1. [Index your documents with their permitted groups](/azure/search/search-security-trimming-for-azure-search-with-aad#index-document-with-their-permitted-groups). Be sure that your new [security fields](/azure/search/search-security-trimming-for-azure-search#create-security-field) have the schema below:
        
    ```json
    {"name": "group_ids", "type": "Collection(Edm.String)", "filterable": true }
    ```

    `group_ids` is the default field name. If you use a different field name like `my_group_ids`, you can map the field in [index field mapping](../concepts/use-your-data.md#index-field-mapping).

1. Make sure each sensitive document in the index has the value set correctly on this security field to indicate the permitted groups of the document.
1. In [Azure OpenAI Studio](https://oai.azure.com/portal), add your data source. in the [index field mapping](../concepts/use-your-data.md#index-field-mapping) section, you can map zero or one value to the **permitted groups** field, as long as the schema is compatible. If the **Permitted groups** field isn't mapped, document level access won't be enabled. 

**Azure OpenAI Studio**

Once the Azure AI Search index is connected, your responses in the studio will have document access based on the Microsoft Entra permissions of the logged in user.

**Web app**

If you are using a published [web app](./use-web-app.md), you need to redeploy it to upgrade to the latest version. The latest version of the web app includes the ability to retrieve the groups of the logged in user's Microsoft Entra account, cache it, and include the group IDs in each API request.

**API**

When using the API, pass the `filter` parameter in each API request. For example:

```json
{
    "messages": [
        {
            "role": "user",
            "content": "who is my manager?"
        }
    ],
    "dataSources": [
        {
            "type": "AzureCognitiveSearch",
            "parameters": {
                "endpoint": "'$SearchEndpoint'",
                "key": "'$SearchKey'",
                "indexName": "'$SearchIndex'",
                "filter": "my_group_ids/any(g:search.in(g, 'group_id1, group_id2'))"
            }
        }
    ]
}
```
* `my_group_ids` is the field name that you selected for **Permitted groups** during [fields mapping](../concepts/use-your-data.md#index-field-mapping).
* `group_id1, group_id2` are groups attributed to the logged in user. The client application can retrieve and cache users' groups.


## Resources configuration

Use the following sections to configure your resources for optimal secure usage. Even if you plan to only secure part of your resources, you still need to follow all the steps below.

## Create resource group

Create a resource group, so you can organize all the relevant resources. The resources in the resource group include but are not limited to:
* One Virtual network
* Three key services: one Azure OpenAI, one Azure AI Search, one Storage Account
* Three Private endpoints, each is linked to one key service
* Three Network interfaces, each is associated with one private endpoint
* One Virtual network gateway, for the access from on-premises client machines
* One Web App with virtual network integrated
* One Private DNS zone, so the Web App finds the IP of your Azure OpenAI

## Create virtual network

The virtual network has three subnets. 

1. The first subnet is used for the private IPs of the three private endpoints.
1. The second subnet is created automatically when you create the virtual network gateway.
1. The third subnet is empty, and used for Web App outbound virtual network integration.

:::image type="content" source="../media/use-your-data/virtual-network.png" alt-text="A diagram showing the virtual network architecture." lightbox="../media/use-your-data/virtual-network.png":::

Note the Microsoft managed virtual network is created by Microsoft, and you cannot see it. The Microsoft managed virtual network is used by Azure OpenAI to securely access your Azure AI Search.

## Configure Azure OpenAI

### Enabled custom subdomain

If you created the Azure OpenAI via Azure portal, the [custom subdomain](/azure/ai-services/cognitive-services-custom-subdomains) should have been created already. The custom subdomain is required for Microsoft Entra ID based authentication, and private DNS zone.

### Enable managed identity

To allow your Azure AI Search and Storage Account to recognize your Azure OpenAI service via Microsoft Entra ID authentication, you need to assign a managed identity for your Azure OpenAI service. The easiest way is to toggle on system assigned managed identity on Azure portal.
:::image type="content" source="../media/use-your-data/openai-managed-identity.png" alt-text="A screenshot showing the system assigned managed identity option in the Azure portal." lightbox="../media/use-your-data/openai-managed-identity.png":::

To set the managed identities via the management API, see [the management API reference documentation](/rest/api/cognitiveservices/accountmanagement/accounts/update#identity).

```json

"identity": {
  "principalId": "12345678-abcd-1234-5678-abc123def",
  "tenantId": "1234567-abcd-1234-1234-abcd1234",
  "type": "SystemAssigned, UserAssigned", 
  "userAssignedIdentities": {
    "/subscriptions/1234-5678-abcd-1234-1234abcd/resourceGroups/my-resource-group",
    "principalId": "12345678-abcd-1234-5678-abcdefg1234", 
    "clientId": "12345678-abcd-efgh-1234-12345678"
  }
}
```

### Enable trusted service

To allow your Azure AI Search to call your Azure OpenAI `preprocessing-jobs` as custom skill web API, while Azure OpenAI has no public network access, you need to set up Azure OpenAI to bypass Azure AI Search as a trusted service based on managed identity. Azure OpenAI identifies the traffic from your Azure AI Search by verifying the claims in the JSON Web Token (JWT). Azure AI Search must use the system assigned managed identity authentication to call the custom skill web API. 

Set `networkAcls.bypass` as `AzureServices` from the management API. For more information, see [Virtual networks article](/azure/ai-services/cognitive-services-virtual-networks?tabs=portal#grant-access-to-trusted-azure-services-for-azure-openai).

### Disable public network access

You can disable public network access of your Azure OpenAI resource in the Azure portal. 

To allow access to your Azure OpenAI service from your client machines, like using Azure OpenAI Studio, you need to create [private endpoint connections](/azure/ai-services/cognitive-services-virtual-networks?tabs=portal#use-private-endpoints) that connect to your Azure OpenAI resource.


## Configure Azure AI Search

You can use basic pricing tier and higher for the configuration below. You don’t have to use S2 pricing tier because the configuration doesn't require [private endpoint support for indexers with a skill set](/azure/search/search-limits-quotas-capacity#shared-private-link-resource-limits). See [step 8](#data-ingestion-architecture) of the data ingestion architecture diagram. The networking for custom skill is *bypass trusted service*, not *private endpoint*.

### Enable managed identity

To allow your other resources to recognize the Azure AI Search using Microsoft Entra ID authentication, you need to assign a managed identity for your Azure AI Search. The easiest way is to toggle on the system assigned managed identity in the Azure portal.

:::image type="content" source="../media/use-your-data/outbound-managed-identity-ai-search.png" alt-text="A screenshot showing the managed identity setting for Azure AI Search in the Azure portal." lightbox="../media/use-your-data/outbound-managed-identity-ai-search.png":::

### Enable role-based access control
As Azure OpenAI uses managed identity to access Azure AI Search, you need to enable role-based access control in your Azure AI Search. To do it on Azure portal, select **Both** in the **Keys** tab in the Azure portal.

:::image type="content" source="../media/use-your-data/managed-identity-ai-search.png" alt-text="A screenshot showing the managed identity option for Azure AI search in the Azure portal." lightbox="../media/use-your-data/managed-identity-ai-search.png":::

To enable role-based access control via the REST API, set `authOptions` as `aadOrApiKey`. For more information, see the [Azure AI Search RBAC article](/azure/search/search-security-rbac?tabs=config-svc-rest%2Croles-portal%2Ctest-portal%2Ccustom-role-portal%2Cdisable-keys-portal#configure-role-based-access-for-data-plane).

```json
"disableLocalAuth": false,
"authOptions": { 
    "aadOrApiKey": { 
        "aadAuthFailureMode": "http401WithBearerChallenge"
    }
}
```

To use Azure OpenAI Studio, you can't disable the API key based authentication for Azure AI Search, because Azure OpenAI Studio uses the API key to call the Azure AI Search API from your browser. 

> [!TIP]
> For the best security, when you are ready for production and no longer need to use Azure OpenAI Studio for testing, we recommend that you disable the API key. See the [Azure AI Search RBAC article](/azure/search/search-security-rbac?tabs=config-svc-portal%2Croles-portal%2Ctest-portal%2Ccustom-role-portal%2Cdisable-keys-portal#disable-api-key-authentication) for details. 

### Disable public network access

You can disable public network access of your Azure AI Search resource in the Azure portal. 

To allow access to your Azure AI Search resource from your client machines, like using Azure OpenAI Studio, you need to create [private endpoint connections](/azure/search/service-create-private-endpoint) that connect to your Azure AI Search resource.

> [!NOTE]
> To allow access to your Azure AI Search resource from Azure OpenAI resource, you need to submit an [application form](https://aka.ms/applyacsvpnaoaioyd). The application will be reviewed in 10 business days and you will be contacted via email about the results. If you are eligible, we will provision the private endpoint in Microsoft managed virtual network, and send a private endpoint connection request to your search service, and you will need to approve the request.

:::image type="content" source="../media/use-your-data/approve-private-endpoint.png" alt-text="A screenshot showing private endpoint approval screen." lightbox="../media/use-your-data/approve-private-endpoint.png":::

The private endpoint resource is provisioned in a Microsoft managed tenant, while the linked resource is in your tenant. You can't access the private endpoint resource by just clicking the **private endpoint** link (in blue font) in the **Private access** tab of the **Networking page**. Instead, click elsewhere on the row, then the **Approve**` button above should be clickable.

Learn more about the [manual approval workflow](/azure/private-link/private-endpoint-overview#access-to-a-private-link-resource-using-approval-workflow).


## Configure Storage Account

### Enable trusted service

To allow access to your Storage Account from Azure OpenAI and Azure AI Search, while the Storage Account has no public network access, you need to set up Storage Account to bypass your Azure OpenAI and Azure AI Search as [trusted services based on managed identity](/azure/storage/common/storage-network-security?tabs=azure-portal#trusted-access-based-on-a-managed-identity).

In the Azure portal, navigate to your storage account networking tab, choose "Selected networks", and then select **Allow Azure services on the trusted services list to access this storage account** and click Save.

> [!NOTE]
> The trusted service feature is only available using the command line described above, and cannot be done using the Azure portal.

### Disable public network access

You can disable public network access of your Storage Account in the Azure portal. 

To allow access to your Storage Account from your client machines, like using Azure OpenAI Studio, you need to create [private endpoint connections](/azure/storage/common/storage-private-endpoints) that connect to your blob storage.



## Role assignments

So far you have already setup each resource work independently. Next you need to allow the services to authorize each other.

|Role| Assignee | Resource | Description |
|--|--|--|--|
| `Search Index Data Reader` | Azure OpenAI | Azure AI Search | Inference service queries the data from the index. |
| `Search Service Contributor` | Azure OpenAI | Azure AI Search | Inference service queries the index schema for auto fields mapping. Data ingestion service creates index, data sources, skill set, indexer, and queries the indexer status. |
| `Storage Blob Data Contributor` | Azure OpenAI | Storage Account | Reads from the input container, and writes the preprocess result to the output container. |
| `Cognitive Services OpenAI Contributor` | Azure AI Search | Azure OpenAI | Custom skill |
| `Storage Blob Data Contributor` | Azure AI Search | Storage Account | Reads blob and writes knowledge store |


In the above table, the `Assignee` means the system assigned managed identity of that resource.

The admin needs to have the `Owner` role on these resources to add role assignments.

See the [Azure RBAC documentation](/azure/role-based-access-control/role-assignments-portal) for instructions on setting these roles in the Azure portal. You can use the [available script on GitHub](https://github.com/microsoft/sample-app-aoai-chatGPT/blob/main/scripts/role_assignment.sh) to add the role assignments programmatically.

To enable the developers to use these resources to build applications, the admin needs to add the developers' identity with the following role assignments to the resources.

|Role| Resource | Description |
|--|--|--|
| `Cognitive Services OpenAI Contributor` | Azure OpenAI | Call public ingestion API from Azure OpenAI Studio. The `Contributor` role is not enough, because if you only have `Contributor` role, you cannot call data plane API via Microsoft Entra ID authentication, and Microsoft Entra ID authentication is required in the secure setup described in this article. |
| `Cognitive Services User` | Azure OpenAI | List API-Keys from Azure OpenAI Studio.|
| `Contributor` | Azure AI Search | List API-Keys to list indexes from Azure OpenAI Studio.|
| `Contributor` | Storage Account | List Account SAS to upload files from Azure OpenAI Studio.|
| `Contributor` | The resource group or Azure subscription where the developer need to deploy the web app to | Deploy web app to the developer's Azure subscription.|

## Configure gateway and client

To access the Azure OpenAI service from your on-premises client machines, one of the approaches is to configure Azure VPN Gateway and Azure VPN Client.

Follow [this guideline](/azure/vpn-gateway/tutorial-create-gateway-portal#VNetGateway) to create virtual network gateway for your virtual network.

Follow [this guideline](/azure/vpn-gateway/openvpn-azure-ad-tenant#enable-authentication) to add point-to-site configuration, and enable Microsoft Entra ID based authentication. Download the Azure VPN Client profile configuration package, unzip, and import the `AzureVPN/azurevpnconfig.xml` file to your Azure VPN client.

:::image type="content" source="../media/use-your-data/vpn-client.png" alt-text="A screenshot showing where to import Azure VPN Client profile." lightbox="../media/use-your-data/vpn-client.png":::

Configure your local machine `hosts` file to point your resources host names to the private IPs in your virtual network. The `hosts` file is located at `C:\Windows\System32\drivers\etc` for Windows, and at `/etc/hosts` on Linux. Example:

```
10.0.0.5 contoso.openai.azure.com
10.0.0.6 contoso.search.windows.net
10.0.0.7 contoso.blob.core.windows.net
```

## Azure OpenAI Studio

You should be able to use all Azure OpenAI Studio features, including both ingestion and inference, from your on-premises client machines.

## Web app
The web app communicates with your Azure OpenAI resource. Since your Azure OpenAI resource has public network disabled, the web app needs to be set up to use the private endpoint in your virtual network to access your Azure OpenAI resource.

The web app needs to resolve your Azure OpenAI host name to the private IP of the private endpoint for Azure OpenAI. So, you need to configure the private DNS zone for your virtual network first.

1. [Create private DNS zone](/azure/dns/private-dns-getstarted-portal#create-a-private-dns-zone) in your resource group. 
1. [Add a DNS record](/azure/dns/private-dns-getstarted-portal#create-an-additional-dns-record). The IP is the private IP of the private endpoint for your Azure OpenAI resource, and you can get the IP address from the network interface associated with the private endpoint for your Azure OpenAI.
1. [Link the private DNS zone to your virtual network](/azure/dns/private-dns-getstarted-portal#link-the-virtual-network) so the web app integrated in this virtual network can use this private DNS zone.

When deploying the web app from Azure OpenAI Studio, select the same location with the virtual network, and select a proper SKU, so it can support the [virtual network integration feature](/azure/app-service/overview-vnet-integration). 

After the web app is deployed, from the Azure portal networking tab, configure the web app outbound traffic virtual network integration, choose the third subnet that you reserved for web app.

:::image type="content" source="../media/use-your-data/web-app-configure-outbound-traffic.png" alt-text="A screenshot showing outbound traffic configuration for the web app." lightbox="../media/use-your-data/web-app-configure-outbound-traffic.png":::

## Using the API

Make sure your sign-in credential has `Cognitive Services OpenAI Contributor` role on your Azure OpenAI resource, and run `az login` first.

:::image type="content" source="../media/use-your-data/api-local-test-setup-credential.png" alt-text="A screenshot showing the cognitive services OpenAI contributor role in the Azure portal." lightbox="../media/use-your-data/api-local-test-setup-credential.png":::

### Ingestion API


See the [ingestion API reference article](/azure/ai-services/openai/reference#start-an-ingestion-job) for details on the request and response objects used by the ingestion API.

More notes:

* `JOB_NAME` in the API path will be used as the index name in Azure AI Search.
* Use the `Authorization` header rather than api-key.
* Explicitly set `storageEndpoint` header.
* Use `ResourceId=` format for `storageConnectionString` header, so Azure OpenAI and Azure AI Search use managed identity to authenticate the storage account, which is required to bypass network restrictions.
* **Do not** set the `searchServiceAdminKey` header. The system-assigned identity of the Azure OpenAI resource is used to authenticate Azure AI Search.
* **Do not** set `embeddingEndpoint` or `embeddingKey`. Instead, use the `embeddingDeploymentName` header to enable text vectorization.


**Submit job example**

```bash
accessToken=$(az account get-access-token --resource https://cognitiveservices.azure.com/ --query "accessToken" --output tsv)
curl -i -X PUT https://my-resource.openai.azure.com/openai/extensions/on-your-data/ingestion-jobs/vpn1025a?api-version=2023-10-01-preview \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $accessToken" \
-H "storageEndpoint: https://mystorage.blob.core.windows.net/" \
-H "storageConnectionString: ResourceId=/subscriptions/1234567-abcd-1234-5678-1234abcd/resourceGroups/my-resource/providers/Microsoft.Storage/storageAccounts/mystorage" \
-H "storageContainer: my-container" \
-H "searchServiceEndpoint: https://mysearch.search.windows.net" \
-H "embeddingDeploymentName: ada" \
-d \
'
{
}
'
```

**Get job status example**

```bash
accessToken=$(az account get-access-token --resource https://cognitiveservices.azure.com/ --query "accessToken" --output tsv)
curl -i -X GET https://my-resource.openai.azure.com/openai/extensions/on-your-data/ingestion-jobs/abc1234?api-version=2023-10-01-preview \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $accessToken"
```

### Inference API

See the [inference API reference article](/azure/ai-services/openai/reference#completions-extensions) for details on the request and response objects used by the inference API.   

More notes:

* **Do not** set `dataSources[0].parameters.key`. The service uses system assigned managed identity to authenticate the Azure AI Search.
* **Do not** set `embeddingEndpoint` or `embeddingKey`. Instead, to enable vector search (with `queryType` set properly), use `embeddingDeploymentName`.

Example:

```bash
accessToken=$(az account get-access-token --resource https://cognitiveservices.azure.com/ --query "accessToken" --output tsv)
curl -i -X POST https://my-resource.openai.azure.com/openai/deployments/turbo/extensions/chat/completions?api-version=2023-10-01-preview \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $accessToken" \
-d \
'
{
    "dataSources": [
        {
            "type": "AzureCognitiveSearch",
            "parameters": {
                "endpoint": "https://my-search-service.search.windows.net",
                "indexName": "my-index",
                "queryType": "vector",
                "embeddingDeploymentName": "ada"
            }
        }
    ],
    "messages": [
        {
            "role": "user",
            "content": "Who is the primary DRI for QnA v2 Authoring service?"
        }
    ]
}
'
```
