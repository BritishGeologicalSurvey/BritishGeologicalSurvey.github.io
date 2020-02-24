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

Python 2 vs 3 mismatches have been causing problems in our
CentOS 7 server adminstration.
We use [Ansible](https://www.ansible.com/) for automatic configuration and
continuous integration deployments.
A few of our long-used jobs recently broke because Python 2 dependencies were out-of-date.
CentOS 7 itself depends on Python 2.
It is officially [supported until
June 2024](https://wiki.centos.org/About/Product), but I think that the [sunsetting
of Python 2](https://www.python.org/doc/sunset-python-2/) will hasten its
demise.

The notes below explain how we solved our issues with CentOS 7 and Ansible.
Hopefully they will be helpful to others.


## Background

Ansible configures servers by connecting via SSH and running
shell scripts and/or Python scripts to apply the requested settings.
In CentOS 7, these scripts are run by Python 2.7.
This causes two main problems with Python tools installed using the `pip`
package manager:

  - An increasing number of packages are Python 3 only, and others are not receiving updates for Python 2.  Ansible's `pip` module uses the system Python 2 interpreter by default, so it may fail or get an out-of-date version.
  - Other Ansible modules rely on Python libraries installed on the system.  By default, Ansible will try to use
the Python 2 version.  Again, these may be missing or old.


## Making Ansible work with Python 3

The solution to this is to make Ansible use Python 3 on the target system.  The
following steps are required:

### Ensure Python 3 and pip are present

The following tasks ensure the server is able to use Python 3.

```yaml
---
- name: Install python 3.6 and pip3
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

Note that Python 3 is not available in the default repositories, so it is
necessary to [enable the EPEL repo](https://fedoraproject.org/wiki/EPEL) or
similar.  EPEL has Python 3.6, which automatically includes `pip3`.  The
SELinux dependencies are required by some Ansible modules.

### Use pip3 to install packages

The Ansible `pip` module has a `executable` option to specify which `pip` to
use.  Use this to install
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

Ansible uses the `ansible_python_interpreter` variable to define which Python to
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

Without this setting, the task will fail with an `ImportError` as the Python
2 interpreter fails to find the library installed via `pip3`.

Ansible reads variable definitions according to a [defined
hierarchy](https://docs.ansible.com/ansible/latest/user_guide/playbooks_variables.html#variable-precedence-where-should-i-put-a-variable).
In the example above, the variable only applies for a single
task and Python 2 is used elsewhere.  We find this preferable to setting for
an entire host or play as the intention is most
explicit and some modules, notably `yum`, will only work with Python
2.

Trivia: `yum` ("Yellowdog updater, modified") is the package manager in CentOS 7.  It requires Python 2.  CentOS 8 uses `dnf` package manager ("Dandified Yum"), which can use Python 3.
