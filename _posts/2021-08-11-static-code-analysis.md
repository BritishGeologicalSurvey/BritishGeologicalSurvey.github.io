## Static Code Analysis with SonarQube
The use of _static code analysis tools_ can help developers identify code quality issues and security vulnerabilities early in the software development lifecycle, and so helps in the effort to *Shift-Left*. 

Whilst many IDEs (and IDE plugins) can carry out code linting, and even spot potential security issues, the ability to configure them is often restircted to local development environments and the analysis detached from the build process.


### Continuous Inspection
The ideal approach to static code analysis would be to have it automated and placed within the CI/CD pipelines. If either the code does not meet some pre-defined level of quality or it contains possible security vulnerabilities then the pipeline could be failed.
This has the advantage of alerting the developer to issues early, ensuring they get addressed before being picked up in code reviews, *Dynamic Analysis Security Tests (DAST)*, or manual pen testing. When picked up in these later activities the time required to remedy them is likley to be much greater, and of course they could miss some issues otherwise detected by static code analysis.

### SonarQube
[SonarQube](https://www.sonarsource.com/plans-and-pricing/community/) is a platform that can help provide a *Continuous Inspection* solution, supporting a number of languages (including Python, Java, JavaScript, TypeScript, PL/SQL, and PHP). It has a web-based admin console where you can configure profiles for code quality/vulnerability severity as well as threshold criteria for test failure.
These profiles and test criteria can then be applied at the project level and used within the CI/CD pipeline; failing the pipeline if the quality threshold has not been met.

#### Quality Profiles
SonarQube lets you associate what it calls _Quality Profiles_ to your project. There are default ones to pick from or you can create your own.
They serve as buckets for rules/issues that should be considered during analysis.

There is a comprehensive list of rules/issues that are maintained that are categorised as **bug**, **vulnerability**, **security hotspot**, or **code smell**. The descriptions for these categories in the table below are my interpretations.

| Categroy | Description |
|--|--|
| Bug | General coding error |
| Vulnerability  | Security-specific bug |
| Security hotspot | Parts of the code identified as having the potential to be insecure but SonarQube is unable to determine whether it constitutes a genuine vulnerability |
| Code smell | Unconventional, possibly confusing style of coding |

What is particularly good is that the issue descriptions often contain guidance on how to fix the issue and relevant links to entries on the various standards lists, including security lists such as _CWE_, _Sans-25_, and _OWASP Top 10_.

![alt text](./issue_desc.PNG "security vulnerability issue description")
_Example issue description_

#### Quality Gates
SonarQube also has the concept of a _Quality Gate_. This defines the criteria that will be applied when carrying out a pass/fail test at the end of an analysis. Associating a _Quality Gate_ to a project gives the CI/CD pipeline an opportunity to fail if the desired quality level is not met.
Its configuration can be based on various metrics. As well as categorising issues by type they are also assigned severity ratings (**Blocker**, **Critical**, **Major**, **Minor**, **Info**) and these can also be used to configure _Quality Gates_.

![alt text](./quality_gate.PNG "example of a strict Quality Gate")
_Example Quality Gate configuration_

#### IDE integration
SonarQube also provides linting plugins for some IDEs, including _VS Code_, _Eclipse_, and _Intelij_ (and third-party plugins are available for some others).
The advantage of using these is they enable you to bind the project you are working on to a centrally maintained configuration (i.e. _Quality Profile_). Any local analysis that is run will therefore match that done during the CI/CD pipeline or by any other developer subsequently checking the code out.

### Final Remarks
Recently, in the tech media, there has been an increased focus on vulnerabilities introduced into applications via third-party dependencies, and an appreciation that an application’s main code base is just the tip of its potential attack surface.
Whilst this may be the case, the ease with which _Static Analysis Security Testing (SAST)_ and code quality testing can now be applied to your code base means there is little reason not to use automated static code analysis to gain some security benefit.

And it is probably even more important for open source projects (especially those used as library dependencies) as any security vulnerabilities within them, if not identified prior to release, could be identifiable to others using automated SAST tools.

