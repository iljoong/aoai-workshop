---
title: Azure OpenAI Service quotas and limits
titleSuffix: Azure AI services
description: Quick reference, detailed description, and best practices on the quotas and limits for the OpenAI service in Azure AI services.
#services: cognitive-services
author: mrbullwinkle
manager: nitinme
ms.service: azure-ai-openai
ms.custom:
  - ignite-2023
  - references_regions
ms.topic: conceptual
ms.date: 02/06/2024
ms.author: mbullwin
---

# Azure OpenAI Service quotas and limits

This article contains a quick reference and a detailed description of the quotas and limits for Azure OpenAI in Azure AI services.

## Quotas and limits reference

The following sections provide you with a quick guide to the default quotas and limits that apply to Azure OpenAI:

| Limit Name | Limit Value |
|--|--|
| OpenAI resources per region per Azure subscription | 30 |
| Default DALL-E 2 quota limits | 2 concurrent requests |
| Default DALL-E 3 quota limits| 2 capacity units (6 requests per minute)|
| Maximum prompt tokens per request | Varies per model. For more information, see [Azure OpenAI Service models](./concepts/models.md)|
| Max fine-tuned model deployments | 5 |
| Total number of training jobs per resource | 100 |
| Max simultaneous running training jobs per resource | 1 |
| Max training jobs queued | 20 |
| Max Files per resource (fine-tuning) | 30 |
| Total size of all files per resource (fine-tuning) | 1 GB |
| Max training job time (job will fail if exceeded) | 720 hours |
| Max training job size (tokens in training file) x (# of epochs) | 2 Billion |
| Max size of all files per upload (Azure OpenAI on your data) | 16 MB |
| Max number or inputs in array with `/embeddings` | 2048 |
| Max number of `/chat/completions` messages | 2048 |
| Max number of `/chat/completions` functions | 128 |
| Max number of `/chat completions` tools | 128 |
| Maximum number of Provisioned throughput units per deployment | 100,000 |
| Max files per Assistant/thread | 20 |
| Max file size for Assistants | 512 MB |
| Assistants token limit | 2,000,000 token limit |

## Regional quota limits

The default quota for models varies by model and region. Default quota limits are subject to change.

<table>  
  <tr>  
    <th>Model</th>  
    <th>Regions</th>  
    <th>Tokens per minute</th>  
  </tr>  
  <tr>  
    <td rowspan="2">gpt-35-turbo</td>  
    <td>East US, South Central US, West Europe, France Central, UK South</td>  
    <td>240 K</td>  
  </tr>  
  <tr>  
    <td>North Central US, Australia East, East US 2, Canada East, Japan East, Sweden Central, Switzerland North</td>  
    <td>300 K</td>  
  </tr>  
  <tr>  
    <td rowspan="2">gpt-35-turbo-16k</td>  
    <td>East US, South Central US, West Europe, France Central, UK South</td>  
    <td>240 K</td>  
  </tr>  
  <tr>  
    <td>North Central US, Australia East, East US 2, Canada East, Japan East, Sweden Central, Switzerland North</td>  
    <td>300 K</td>  
  </tr> 
   <tr>  
    <td>gpt-35-turbo-instruct</td>  
    <td>East US, Sweden Central</td>  
    <td>240 K</td>  
  </tr>  
  <tr>  
    <td>gpt-35-turbo (1106)</td>  
    <td> Australia East, Canada East, France Central, South India, Sweden Central, UK South, West US
</td>  
    <td>120 K</td>  
  </tr>  
  <tr>  
    <td rowspan="2">gpt-4</td>  
    <td>East US, South Central US, France Central</td>  
    <td>20 K</td>  
  </tr>  
  <tr>  
    <td>North Central US, Australia East, East US 2, Canada East, Japan East, UK South, Sweden Central, Switzerland North</td>  
    <td>40 K</td>  
  </tr>  
  <tr>  
    <td rowspan="2">gpt-4-32k</td>  
    <td>East US, South Central US, France Central</td>  
    <td>60 K</td>  
  </tr>  
  <tr>  
    <td>North Central US, Australia East, East US 2, Canada East, Japan East, UK South,  Sweden Central, Switzerland North</td>  
    <td>80 K</td>  
  </tr>
  <tr>  
    <td rowspan="2">gpt-4 (1106-preview)<br>GPT-4 Turbo </td>  
    <td>Australia East, Canada East, East US 2, France Central, UK South, West US</td>  
    <td>80 K</td>  
  </tr>  
  <tr>  
    <td>South India, Norway East, Sweden Central</td>  
    <td>150 K</td>  
  </tr>
<tr>  
    <td>gpt-4 (vision-preview)<br>GPT-4 Turbo with Vision</td>  
    <td>Sweden Central, Switzerland North, Australia East, West US</td>  
    <td>30 K</td>  
  </tr>  
  <tr>  
    <td rowspan="2">text-embedding-ada-002</td>  
    <td>East US, South Central US, West Europe, France Central</td>  
    <td>240 K</td>  
  </tr>  
  <tr>  
    <td>North Central US, Australia East, East US 2, Canada East, Japan East, UK South, Switzerland North</td>  
    <td>350 K</td>  
  </tr>  
<tr>  
    <td>Fine-tuning models (babbage-002, davinci-002, gpt-35-turbo-0613)</td>  
    <td>North Central US, Sweden Central</td>  
    <td>50 K</td>  
  </tr>  
  <tr>  
    <td>all other models</td>  
    <td>East US, South Central US, West Europe, France Central</td>  
    <td>120 K</td>  
  </tr>  
</table>  


### General best practices to remain within rate limits

To minimize issues related to rate limits, it's a good idea to use the following techniques:

- Implement retry logic in your application.
- Avoid sharp changes in the workload. Increase the workload gradually.
- Test different load increase patterns.
- Increase the quota assigned to your deployment. Move quota from another deployment, if necessary.

### How to request increases to the default quotas and limits

Quota increase requests can be submitted from the [Quotas](./how-to/quota.md) page of Azure OpenAI Studio. Please note that due to overwhelming demand, quota increase requests are being accepted and will be filled in the order they are received. Priority will be given to customers who generate traffic that consumes the existing quota allocation, and your request may be denied if this condition isn't met.

For other rate limits, please [submit a service request](../cognitive-services-support-options.md?context=/azure/ai-services/openai/context/context).

## Next steps

Explore how to [manage quota](./how-to/quota.md) for your Azure OpenAI deployments.
Learn more about the [underlying models that power Azure OpenAI](./concepts/models.md).
