# The `EasyScience` framework

EasyScience is a framework of software tools that can be used to build experimental data analysis packages.
For example, it has been used in the development of [EasyDiffraction](https://easydiffraction.org) and [EasyReflectometry](https://easyreflectometry.org).
The framework consists of both front- and back-end elements, known as EasyApp and EasyScience, respectively.
The front-end provides a shared library of graphical interface elements that can be used to build a graphical user interface.
The back-end offers a toolset to perform model-dependent analysis, including the ability to plug-in existing calculation engines.
```{figure} ./images/easyscience.png
---
height: 250px
name: easyscience
---
The EasyScience software family and structure.
```

The focus in this school is on the Python library, `easyscience`, which can be used to perform complex model-dependent analysis.
The use of `easyscience` to perform Bayesian sampling, using external libraries, will also be introduced.
