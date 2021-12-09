---
title:  "Using AI to triage citizen science submissions"
author: Steve Richardson
categories:
  - front end
  - back end
tags:
  - Angular
  - Microsoft Azure
  - AI
  - Citizen Science
---

The British Geological Survey has a [long history](https://www.bgs.ac.uk/geology-projects/citizen-science/) of utilising citizen science and crowdsourcing to gather information about a range of events and phenomena. The term *Citizen Science* is often used for projects where individuals or groups of volunteers, many without specific training, undertake research-related tasks such as observation, measurement, or computation. Through these networks scientists and researchers can often accomplish much greater results and reach a much wider audience than they would otherwise be able to.

## BGS Citizen science projects

<figure class="third">
	<img src="https://www.bgs.ac.uk/wp-content/uploads/2019/12/mySoil_banner-960x529.jpg">
	<img src="https://www.bgs.ac.uk/wp-content/uploads/2020/06/myHAZ-1-960x497.jpg">
	<img src="https://www.bgs.ac.uk/wp-content/uploads/2020/03/myVolcano-960x529.jpg">
	<figcaption>BGS citizen science applications: mySoil, myHAZ-VCT and myVolcano. </figcaption>
</figure>

## Anonymous submissions Vs user accounts

When designing citizen science applications, the decision of whether to allow anonymous observations or to require an element of authentication is integral to the project aims, ambitions and purpose. Allowing anonymous submissions reduces the amount of time it takes to submit an observation, which respects the time of your users and minimises any barriers to entry.

However, anonymous submissions means that there are no checks on who is submitting, what content they are submitting and prevents being able to contact users again for follow-up questions. An open-door policy can maximise the volume of submissions but allows both high and low quality data to be sent. Depending on the research topic of the citizen science project this can be a help or hindrance, but in many cases the [benefits of maximising contribution rates](https://www.researchgate.net/publication/291356235_To_Sign_Up_or_not_to_Sign_Up_Maximizing_Citizen_Science_Contribution_Rates_through_Optional_Registration) outweighs some of the potential risks.

## How BGS manages anonymous submissions

BGS has managed the risk of anonymous submissions by utilising the BGS Enquiries service who receive notifications of new submissions and are able to review their content (text and imagery) before being approved/published or rejected/hidden. This process enabled a real person to assess the quality of the content and make a conscious decision to approve or reject it.

However, this process is inherently manual and relies on a member of the Enquiries team to be available and have the time to process and action each submission. A member of staff is also manually triaging observations which could include imagery and content which is intentionally harmful or offensive. Given the pressures on their time already, the number of submissions and how frequently each submissions needs to be actioned, the burden can become unsustainable.

# Automating the process

In order to optimise the existing process I investigated how submissions could be screened to remove harmful content before a human is required to look at it. Content like free text can be easily processed to detect offensive words (although the process is fallible, see the [Scunthorpe problem](https://en.wikipedia.org/wiki/Scunthorpe_problem)).

Imagery, however, is a more complex computational problem to solve due to the range of material that can be submitted. In order to investigate a solution I utilised the [Microsoft Azure Computer Vision service](https://azure.microsoft.com/en-us/services/cognitive-services/computer-vision/#overview). This tool uses Artificial Intelligence (AI) on the Azure cloud computing system to analyse imagery and video to extract a variety of visual features from the image. For the purposes of my Proof of Concept (PoC) application I wanted to use Computer Vision to analyse imagery submitted through our crowdsourcing applications to:

* Detect visual features in an image e.g. `table`, `person`, or `indoor`
* Analyse the image and describe, in human-readable language, what it contains
* Provide a confidence value to indicate how sure the AI was about its assessment

## Microsoft demo of Computer Vision API
![](../../../assets/images/2021-08-11-autocaption/ms-example.png)

The example above shows how the original image has been analysed by the Computer Vision API and its content is then available for review, alongside a percentage confidence in is accuracy. A plain-text description attempts to provide a human-readable description of the image, which is reasonably accurate.

## Proof of Concept with BGS data

Steps taken create a PoC with BGS data:
* Created a new Microsoft Azure account to access the API free trial
* Created a blank [Angular application](https://angular.io/) to quickly develop a User Interface (UI) for the tool.
* Repurposed [sample code](https://docs.microsoft.com/en-us/azure/cognitive-services/computer-vision/quickstarts-sdk/image-analysis-client-library?pivots=programming-language-javascript&tabs=visual-studio) for communicating with the Computer Vision API

The result was a basic web application allowing a user to manually select an image to run through the Computer Vison API. During testing I was able to return positive results for a variety of images which had previously been submitted to one of our crowdsourcing applications. For example, an image submitted during a [myVolcano](https://www.bgs.ac.uk/technologies/apps/myvolcano/) educational workshop correctly identified the image below:

**Image Input:**

![](../../../assets/images/2021-08-11-autocaption/edu-workshop.png)

**Image Description:**
> Group of people sitting at a table

**Objects tagged in this image:**

`person`, `indoor`, `table`, `sitting`, `people`, `group`, `laptop`

**Confidence of AI assessment:**

95%

Further testing found that the AI is correct more often than not in making an assessment of the image contents, however, it did make occasional mistakes. More thorough testing is required to generate metrics on the accuracy of the AI assessment and quality of generated descriptions, as well as to assess how useful the enquiries team found the results.

The PoC tool relies on manually inputting each image for evaluation and waiting for the results, however a production system would need to integrate into the existing verification process without manual intervention. A pipeline could look like this:

![](../../../assets/images/2021-08-11-autocaption/flow-chart.png)

## Conclusions

As a concept, using machine learning and AI to automate the imagery review process has real potential to protect staff from harmful material, increase response times and therefore increase the quality of crowdsourced data being utilised. The technology exists in various implementations so further work is required to evaluate each option against the available resources of time and budgets.

## Further reading

Although the Microsoft Azure Computer Vision API was used for the purposes of this Proof of Concept demo, there are Open-Source projects available which will be worthwhile investigating for their potential usage.

* [Im2txt](https://github.com/HughKu/Im2txt)
* [NeuralTalk2](https://github.com/karpathy/neuraltalk2)
* [Image Captioning](https://github.com/DeepRNN/image_captioning)