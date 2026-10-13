---
title: 'Nexus quarantines & PNPM (caching)'
author: Janusz Lavrnja-Czapski
categories:
  - Development
tags:
  - javascript
  - security
  - nexus
---

# Nexus quarantines & PNPM (caching)

As we have given more consideration to security practices in software development over recent weeks and months, some interesting quirks have appeared in how we manage the security of external dependencies in the JavaScript ecosystem. This post explores how the interaction between pnpm's security features and Nexus quarantines can be managed to keep everything as synchronised as possible and avoid potential security holes in our development pipelines.

## Background

Most of our software developers will be familiar with Nexus quarantines, and frontend developers with how they get caught out when working with pnpm:

```bash
Error: ERR_PNPM_TARBALL_HTTP_STATUS
  × fetching dependencies
  ╰─▶ Tarball server returned HTTP 403 for https://our-internal-registry.org/
repository/npm-all/@whatwg-node/node-fetch/-/node-fetch-0.9.1.tgz
```

This particular package is a sub-dependency of various other packages in the npm ecosystem, and currently requires an override to a different version to allow the install to pass.

Nexus lists it with a High Risk CVSS score that requires immediate attention:

```text
9	Security-High-NPM	High Risk CVSS score

Found security vulnerability sonatype-2026-008747 with severity >= 7 (severity = 8.7)

Found security vulnerability sonatype-2026-008747 with severity < 9 (severity = 8.7)

Component format is 'npm'
```

## The problem

There will be situations where packages are not quarantined and can be freely installed via package managers, as was the case with this dependency, but are subsequently quarantined after being found to have exploitable vulnerabilities.

What happens when we run `pnpm install` in a local project after the dependency has been quarantined? It still succeeds. Why?

- **pnpm keeps package files in its store.** Once the contents are in the store, pnpm can link them into node_modules without network access to the registry.
- **The lockfile pins the integrity hash.** pnpm-lock.yaml records the package. If the lockfile is present and the store contains the record, pnpm sees "I already have this" and doesn't request the tarball, so Nexus never gets the chance to block it.

### The security gap

- Developer machines with warm stores keep using the quarantined version.
- Long-lived CI runners with persistent caches keep installing it.
- Docker layers or build caches that contain node_modules do the same.
- Behaviour becomes inconsistent: "works on my machine" vs "fails in CI".

## How to approach a solution

Due to the nature of pnpm and how it differs from npm, there is no equivalent of `npm cache clean --force` to run in CI environments to force a fresh fetch from the registry. You can run `pnpm store prune` to remove unreferenced packages that are no longer used by any projects, or run `pnpm store path` and then `rm -rf` the entire directory. However, doing either on every CI run would quickly destroy the efficiency savings the store provides, so neither is ideal.

A preliminary solution is to create a new job in our shared GitLab deployment template that performs a cold registry check. The job creates temporary directories for both the pnpm store and cache, which start completely empty and force pnpm to fetch all required dependencies from the internal Nexus registry:

```yaml
cold-registry-check:
  stage: app-tests
  image: ${NODE_DOCKER_IMAGE}
  extends: .pnpm-install
  cache: []
  variables:
    PNPM_STORE_DIR: /tmp/pnpm-store # overrides the global value for this job only
  rules:
    - if: $SKIP_COLD_REGISTRY_CHECK == "true"
      when: never
    - if: $COLD_REGISTRY_CHECK == "true" && ($CI_PIPELINE_SOURCE == "schedule" || $CI_PIPELINE_SOURCE == "web")
  script:
    - pnpm config set cache-dir /tmp/pnpm-cache
    - pnpm config get cache-dir # confirm it took effect
    - |
      pnpm fetch || {
        echo "COLD REGISTRY CHECK FAILED: a locked package could not be fetched from Nexus."
        echo "Likely quarantined or removed. Find the package named above, check its status in the Nexus component view."
        exit 1
      }
  allow_failure: false
```

Caching is disabled, and the `COLD_REGISTRY_CHECK` environment variable ensures the job only runs on a pipeline schedule or manual web trigger, not on default pipelines. The job can be included in the same way as other parts of the deployment template:

```yaml
- project: 'devops/ci-kube-deploy'
  ref: next
  file: 'node-template/cold-registry-check.yml'
```

It can also be disabled or re-enabled whenever needed:

```yaml
SKIP_COLD_REGISTRY_CHECK: 'false'
```

## The output

This job can be run on a recurring schedule for a project's CI pipeline, either weekly or nightly depending on what we feel is most useful. Any pipeline failures can be configured to notify the repository owners that a package has been quarantined and needs updating within the project. It is quite light-touch initially, but it gives us a way to tell developers that packages need updating, and it stops quarantined packages from being quietly installed without anyone noticing.

## Moving forward

Ideally, this scheduled task will be expanded into a more robust reporting system, or linked to default pipelines that run each time we push changes to an application. Teams notifications, emails, webhooks and the like could all be good ways of ensuring that emerging issues are picked up quickly and not allowed to drift out of notice.
