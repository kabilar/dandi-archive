# LINC Archive

![Alt text](web/src/assets/linc-logo.svg "LINC Logo")

LINC Archive is cloud infrastructure and data archival platform for the center for Large-scale Imaging of Neural Circuits (LINC). [See here for details](https://connects.mgh.harvard.edu/)

The LINC Archive site can be (visited online here)[https://lincbrain.org]

This repository is a fork of the [DANDI Archive](https://github.com/dandi/dandi-archive) project. For more information, please visit the [DANDI Archive](https://dandiarchive.org/)

## Structure

The linc-archive repository contains a Django-based [backend](dandiapi/) to run the LINC REST API, and a
Vue-based [frontend](web/) to provide a user interface to the archive.

## Resources

* To learn how to interact with LINC Archive, please temporarily refer to the DANDI Handbook,
see [the handbook](https://www.dandiarchive.org/handbook/).

* To get help:
  - ask a question: https://github.com/dandi/helpdesk/discussions
  - file a feature request or bug report: https://github.com/dandi/helpdesk/issues/new/choose
  - contact the DANDI team: help@dandiarchive.org

* To understand how to hack on the archive codebase:
  - Django backend: [`DEVELOPMENT.md`](DEVELOPMENT.md)
  - Vue frontend: [`web/README.md`](web/README.md)
