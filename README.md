# LINC Data Platform

![LINC Logo](web/src/assets/linc.logo.color+white.png)

LINC Data Platform is data sharing and visualization platform for the center for Large-scale Imaging of Neural Circuits (LINC). [See here for details](https://connects.mgh.harvard.edu/)

The LINC Data Platform site can be (visited online here)[https://lincbrain.org]

This repository is a fork of the [DANDI Archive](https://github.com/dandi/dandi-archive) project. For more information, please visit the [DANDI Archive](https://dandiarchive.org/)

## Structure

The linc-archive repository contains a Django-based [backend](dandiapi/) to run the LINC REST API, and a
Vue-based [frontend](web/) to provide a user interface to the archive.

## Resources

* To learn how to interact with LINC Data Platform, please refer to the [LINC Documentation](https://docs.lincbrain.org/).

* To get help:
  - File an issue on the relevant [GitHub repository](https://github.com/lincbrain)
  - Reach out on the [LINC Slack](https://mit-lincbrain.slack.com/)

* To understand how to hack on the archive codebase:
  - Django backend: [`DEVELOPMENT.md`](DEVELOPMENT.md)
  - Vue frontend: [`web/README.md`](web/README.md)
