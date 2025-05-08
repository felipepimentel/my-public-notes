---
layout: default
title: Test Page
nav_order: 99
permalink: /test/
---

# Test Page

This is a simple test page to verify that Jekyll is working properly.

## Current time

The current time when this page was built: {{ site.time | date_to_string }}

## Site Variables

- Site title: {{ site.title }}
- Base URL: {{ site.baseurl }}
- URL: {{ site.url }}

## Mermaid Test

```mermaid
graph LR
    A[Jekyll] -->|builds| B[Static Site]
    B -->|hosted on| C[GitHub Pages]
    C -->|viewed by| D[User]
    D -->|interacts with| B
``` 