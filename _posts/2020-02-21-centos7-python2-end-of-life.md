---
title:  "CentOS 7, Ansible and the end of Python 2"
author: Dr John A Stevenson
categories:
  - devops
tags:
  - Python
  - CentOS
  - Ansible
  - continuous-integration
---

The [sunsetting of Python 2](https://www.python.org/doc/sunset-python-2/) on 1 January 2020 has started to cause problems with administering our CentOS 7 servers.
We use [Ansible](https://www.ansible.com/) for automatic configuration and
a few of our long-running jobs recently began to fail as a result Python 2 / Python 3 mistmatches.
Officially, CentOS 7 is [supported until
2024-06-30](https://wiki.centos.org/About/Product), but I think the end of
Python 2 will hasten its demise.

The notes below explain how we solved our issues with CentOS 7 and Ansible.
Hopefully they will be helpful to others.


## Background

When you configure a machine with Ansible, it connects to it via SSH and runs
shell scripts and/or Python scripts to apply the settings that you requested.
In CentOS 7, these scripts are run by Python 2.7.
This causes the following problems with Python tools installed using the `pip`
package manager.  


  - An increasing number of packages are Python 3 only, and others e.g. `docker-compose`, are not being updated for Python 2.  As Ansible's `pip` module uses the system Python 2 interpreter by default, it may fail or get an out-of-date version.
  - Other Ansible modules (e.g. `docker-compose, `nsupdate`), rely on Python
    libraries installed on the system.  By default, Ansible will try to use
the Python 2 version.  Again, these may be old or may not even exist.


## Making Ansible work with Python 3

The solution to this is to make Ansible use Python 3 on the target system.  The
following steps allow this:

### Ensure Python 3 and pip are present

The following tasks ensure the server is able to use Python 3.

```yaml
---
- name: Install latest python 3 and pip3
  yum:
    name:
      - python36
      - libselinux-python
    state: present

- name: Install SELinux for Python 3
  pip:
    name:
      - selinux
    state: present
    executable: pip3
  vars:
    ansible_python_interpreter: /usr/bin/python3
```

Note that `pip3` is automatically installed with Python 3.6, and that the
SELinux dependencies are required by some Ansible modules.

### Use pip3 to install packages

The Ansible `pip` module has a flag to specify `pip3`.  Use this to install
packages to the system's Python 3.

```yaml
- name: Install ETLHelper
  pip:
    name:
      - etlhelper
    state: present
    executable: pip3
```

### Tell Ansible to use Python 3 interpreter where required

Ansible uses the `ansible_python_interpreter` variable to define with Python to
use.  This must be specified wherever a module uses a Python 3 dependency e.g.

```yaml
- name: Use dnsupdate to update ip host
  nsupdate:
    server: "{{ dns_server }}"
    zone: "{{ dns_path }}"
    record: "{{ ansible_hostname }}"
    value: "{{ ansible_default_ipv4.address }}"
    ttl: 600
  vars:
    ansible_python_interpreter: /usr/bin/python3
```

Ansible reads variable definitions according to a [defined
hierarchy](https://docs.ansible.com/ansible/latest/user_guide/playbooks_variables.html#variable-precedence-where-should-i-put-a-variable).
In the example above, the variable sets Python 3 as interpreter for a single
task and Python 2 is used elsewhere.  We find this preferable as it is most
explicit and some other modules, most notably `yum`, will only work with Python
2.
