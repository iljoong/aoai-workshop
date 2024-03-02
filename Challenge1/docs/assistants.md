---
title: Azure OpenAI Service Assistant API concepts
titleSuffix: Azure OpenAI Service
description: Learn about the concepts behind the Azure OpenAI Assistants API.
ms.topic: conceptual
ms.date: 02/05/2023
manager: nitinme
author: mrbullwinkle
ms.author: mbullwin
recommendations: false
---

# Azure OpenAI Assistants API (Preview)

Assistants, a new feature of Azure OpenAI Service, is now available in public preview. Assistants API makes it easier for developers to create applications with sophisticated copilot-like experiences that can sift through data, suggest solutions, and automate tasks.

## Overview

Previously, building custom AI assistants needed heavy lifting even for experienced developers. While the chat completions API is lightweight and powerful, it's inherently stateless, which means that developers had to manage conversation state and chat threads, tool integrations, retrieval documents and indexes, and execute code manually.

The Assistants API, as the stateful evolution of the chat completion API, provides a solution for these challenges.
Assistants API supports persistent automatically managed threads. This means that as a developer you no longer need to develop conversation state management systems and work around a model’s context window constraints. The Assistants API will automatically handle the optimizations to keep the thread below the max context window of your chosen model. Once you create a Thread, you can simply append new messages to it as users respond. Assistants can also access multiple tools in parallel, if needed. These tools include:

- [Code Interpreter](../how-to/code-interpreter.md)
- [Function calling](../how-to/assistant-functions.md)

Assistant API is built on the same capabilities that power OpenAI’s GPT product. Some possible use cases range from AI-powered product recommender, sales analyst app, coding assistant, employee Q&A chatbot, and more. Start building on the no-code Assistants playground on the Azure OpenAI Studio or start building with the API.

> [!IMPORTANT]
> Retrieving untrusted data using Function calling, Code Interpreter with file input, and Assistant Threads functionalities could compromise the security of your Assistant, or the application that uses the Assistant. Learn about mitigation approaches [here](https://aka.ms/oai/assistant-rai).

## Assistants playground

We provide a walkthrough of the Assistants playground in our [quickstart guide](../assistants-quickstart.md). This provides a no-code environment to test out the capabilities of assistants.

## Assistants components

| **Component** | **Description** |
|---|---|
| **Assistant** | Custom AI that uses Azure OpenAI models in conjunction with tools. |
|**Thread** | A conversation session between an Assistant and a user. Threads store Messages and automatically handle truncation to fit content into a model’s context.|
| **Message** | A message created by an Assistant or a user. Messages can include text, images, and other files. Messages are stored as a list on the Thread. |
|**Run** | Activation of an Assistant to begin running based on the contents of the Thread. The Assistant uses its configuration and the Thread’s Messages to perform tasks by calling models and tools. As part of a Run, the Assistant appends Messages to the Thread.|
|**Run Step** | A detailed list of steps the Assistant took as part of a Run. An Assistant can call tools or create Messages during it’s run. Examining Run Steps allows you to understand how the Assistant is getting to its final results. |

## See also

* Learn more about Assistants and [Code Interpreter](../how-to/code-interpreter.md)
* Learn more about Assistants and [function calling](../how-to/assistant-functions.md)
* [Azure OpenAI Assistants API samples](https://github.com/Azure-Samples/azureai-samples/tree/main/scenarios/Assistants)



