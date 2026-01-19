<a id="readme-top"></a>
<br />
<div align="center">
    <img src="https://www.eraneos.com/wp-content/themes/expedition-theme/images/eraneos-logo-black.svg" alt="eraneos-logo" width="300">

  <h3 align="center">Dropzone Challenge</h3>

</div>


Dear candidate,

Thank you for taking the time to demonstrate your technical skills solving our Dropzone challenge. It is inspired by a former customer project and intended to simulate various expectations towards <b>Cloud- and Data Engineers</b> at Eraneos Analytics. 

> **Recruiting Process**
> 
> - You will have received access to a sandbox in Google Cloud Platform or AWS as per your preference.
> - [Implement this challenge](#dropzone-challenge) on the provided cloud sandbox.
> - Prepare a presentation (~15 min) of your implementation
> - Please upload your solution (source code, scripts, resources,...) as well as your presentation into this Gitlab Repo **at the latest 24 hours before** the scheduled interview meeting.
> - We meet virtually for the [technical interview](#interview-agenda) (~2h) at the scheduled time
> - You will have a final meeting with our CEO likely on the next day after internal alignments have been completed.

**Table of Contents**

- [Interview Agenda](#interview-agenda)
- [Dropzone Challenge](#dropzone-challenge)
  - [Objectives](#objectives)
  - [Mandatory System Tasks](#mandatory-system-tasks)
    - [01 | Data ingestion](#01--data-ingestion)
    - [02 | Storing raw data](#02--storing-raw-data)
    - [03 | Data transformation](#03--data-transformation)
    - [04 | Storing transformed data](#04--storing-transformed-data)
  - [Optional Features](#optional-features)
    - [API design](#api-design)
    - [Scalability](#scalability)
    - [Security](#security)
    - [Lineage](#lineage)
    - [Testing](#testing)
    - [CI/CD](#cicd)

# Interview Agenda

Our interview will take about 2 hours. You will be talking about your solution with two of our senior data engineers from Eraneos. 

We love our interviews to be more like a nerdy tech talk than a test examination. We are much more interested in finding out who you are as techie, and what you are capable of, than finding what you can't do (yet).

The agenda will roughly follow these items:

- Getting to know each other (10-15 min) 
- Data Case Presentation + Discussion (15-20 min) 
- Data Case Code Walkthrough + Discussion (45 min) 
- Q&A - ask us anything (30 min) 
- Feedback (5 min)   

---
# Dropzone Challenge

The time allocation for this case should be approximately between eight to twelve hours. The challenge does not demand a perfect implementation; rather, the focus should be on showcasing the depth of your understanding of common engineering issues, and your ability to deliver a functional solution under time constraint. 

## Objectives

Your **first objective is to design and present a system architecture**. The system provides a REST API service to ingest JSON data, process that data, and make the processed data available for further analysis. 

The presentation of your architecture shall consider all [mandatory system tasks](#mandatory-system-tasks). In addition, elaborate your ideas and strategies on as many [optional features](#optional-features) as possible.

The **second objective is to implement as much of your architecture** on your chosen cloud sandbox as your time permits. Prefer Python to implement the services where possible.

Feel free to use GenAI coding assistants to create and improve your architecture and jobs. We are looking forward to an open discussion what you used, and how it improved your efficiency.

Here are some some things will impress us during the interview later:

* A well structured and understandable presentation of your approach and system architecture
* A demonstrable working deployment of your implementation of the end-to-end dropzone service
* Beautiful code design
* You have a good understanding of the strengths and weaknesses of your solution
* Thoughtful use of modern and clean development practices

## Mandatory System Tasks

### 01 | Data ingestion

A JSON file's contents is a timestamped array of measuring points. Check out the sample file:
- [json_payload/file.json](../json_payload/file.json)

The JSON data will be submitted as a POST request with a command equivalent to:

```shell
curl -X POST -d @file.json http://service.com/endpoint
```

> Note: Assume that there may be up to 1000 requests per minute under maximum load.

### 02 | Storing raw data

The raw JSON data should be stored **immediately** using an appropriate storage option.

### 03 | Data transformation

Each json contains a `time_stamp` and `data` keys. 

- Timestamps must contain timezone offsets (e.g. "-04:00" for US/Eastern)
- Timestamps must be converted to UTC. 
- Data points are aggregated calculating the mean and standard deviation.

Please ensure that data quality checks are performed and handle failures appropriately.

### 04 | Storing transformed data

For each processed json the service should store the UTC timestamp, mean, standard deviation for further analytics in an appropriate storage options.

The UTC timestamp is a primary key. If the same UTC timestamp is received twice, the existing data should be replaced by the mean and standard deviation of the newly ingested data.

## Optional Features

The following features are considered optional for the dropzone challenge. However, in a real life scenario these features are anything but optional. Please try to elaborate on them during your presentation if only in theory. Implementation of some or even all features is considered a big bonus.

### API design

Build the API to come complete with standardized documentation. Consider using OpenAPI.

### Scalability

Select technologies and/or services that scale well horizontally. Design software components also in a scalable way. For example, you may consider decoupling ingestion from transformation.

### Security

APIs exposed to the internet should be secured enforcing authentication. Think about common ways to authenticate and secure communication.

### Lineage

Think about how you could track data lineage from ingestion to analysis, so you could confirm transformed data in retrospect.

### Testing

Well tested code is usually more stable, secure, and easier to maintain. Implement tests using a testing framework of your choice. Elaborate on the concept of test coverage.

### CI/CD

Automated deployment makes day to day operations much easier and more reproducible. Implement common CI/CD tasks to deploy your system artefacts to the cloud.
