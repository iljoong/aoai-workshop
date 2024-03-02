---
title: 'Using the Azure OpenAI web app'
titleSuffix: Azure OpenAI
description: Use this article to learn about using the available web app to chat with Azure OpenAI models.
manager: nitinme
ms.service: azure-ai-openai
ms.topic: how-to
author: aahill
ms.author: aahi
ms.date: 02/09/2024
recommendations: false
---


# Use the Azure OpenAI web app

Along with Azure OpenAI Studio, APIs and SDKs, you can also use the available standalone web app to interact with Azure OpenAI models using a graphical user interface, which you can deploy using either Azure OpenAI studio or a [manual deployment](https://github.com/microsoft/sample-app-aoai-chatGPT). 

![A screenshot of the web app interface.](../media/use-your-data/web-app.png)

## Important considerations

- Publishing creates an Azure App Service in your subscription. It might incur costs depending on the [pricing plan](https://azure.microsoft.com/pricing/details/app-service/windows/) you select. When you're done with your app, you can delete it from the Azure portal.
- By default, the app will be deployed with the Microsoft identity provider already configured, restricting access to the app to members of your Azure tenant. To add or modify authentication:

    1. Go to the [Azure portal](https://portal.azure.com/#home) and search for the app name you specified during publishing. Select the web app, and go to the **Authentication** tab on the left navigation menu. Then select **Add an identity provider**. 
    
        :::image type="content" source="../media/quickstarts/web-app-authentication.png" alt-text="Screenshot of the authentication page in the Azure portal." lightbox="../media/quickstarts/web-app-authentication.png":::

    1. Select Microsoft as the identity provider. The default settings on this page will restrict the app to your tenant only, so you don't need to change anything else here. Then select **Add**
    
    Now users will be asked to sign in with their Microsoft Entra ID account to be able to access your app. You can follow a similar process to add another identity provider if you prefer. The app doesn't use the user's sign-in information in any other way other than verifying they are a member of your tenant.

## Web app customization

You can customize the app's frontend and backend logic. For example, you could change the icon that appears in the center of the app by updating `/frontend/src/assets/Contoso.svg` and then redeploying the app [using the Azure CLI](https://github.com/microsoft/sample-app-aoai-chatGPT#deploy-with-the-azure-cli).  See the source code for the web app, and more information on [GitHub](https://github.com/microsoft/sample-app-aoai-chatGPT).

When customizing the app, we recommend:

- Resetting the chat session (clear chat) if the user changes any settings. Notify the user that their chat history will be lost.

- Clearly communicating how each setting you implement will affect the user experience.

- When you rotate API keys for your Azure OpenAI or Azure AI Search resource, be sure to update the app settings for each of your deployed apps to use the new keys.

### Updating the web app

We recommend pulling changes from the `main` branch for the web app's source code frequently to ensure you have the latest bug fixes, API version, and improvements.

> [!NOTE]
> After February 1, 2024, the web app requires the app startup command to be set to `python3 -m gunicorn app:app`. When updating an app that was published prior to February 1, 2024, you need to manually add the startup command from the **App Service Configuration** page.

## Chat history

You can enable chat history for your users of the web app. When you enable the feature, your users will have access to their individual previous queries and responses. 

To enable chat history, deploy or redeploy your model as a web app using [Azure OpenAI Studio](https://oai.azure.com/portal)

:::image type="content" source="../media/use-your-data/enable-chat-history.png" alt-text="A screenshot of the chat history enablement button on Azure OpenAI studio." lightbox="../media/use-your-data/enable-chat-history.png":::

> [!IMPORTANT]
> Enabling chat history will create a [Cosmos DB](/azure/cosmos-db/introduction) instance in your resource group, and incur [additional charges](https://azure.microsoft.com/pricing/details/cosmos-db/autoscale-provisioned/) for the storage used. 

Once you've enabled chat history, your users will be able to show and hide it in the top right corner of the app. When the history is shown, they can rename, or delete conversations. As they're logged into the app, conversations will be automatically ordered from newest to oldest, and named based on the first query in the conversation. 

:::image type="content" source="../media/use-your-data/web-app-chat-history.png" alt-text="A screenshot of the chat history in the web app." lightbox="../media/use-your-data/web-app-chat-history.png":::

## Deleting your Cosmos DB instance

Deleting your web app does not delete your Cosmos DB instance automatically. To delete your Cosmos DB instance, along with all stored chats, you need to navigate to the associated resource in the [Azure portal](https://portal.azure.com) and delete it. If you delete the Cosmos DB resource but keep the chat history option enabled on the studio, your users will be notified of a connection error, but can continue to use the web app without access to the chat history.

## Next steps
* [Prompt engineering](../concepts/prompt-engineering.md)
* [Azure openAI on your data](../concepts/use-your-data.md)