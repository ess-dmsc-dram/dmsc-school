# The `EasyScience` framework

`EasyScience` is a framework of software tool that can be used together to build experimental data analysis packages, for example, it has been used in the development of [EasyDiffraction](https://easydiffraction.org) and [EasyReflectometry](https://easyreflectometry.org)
The framework consists of both front- and back-end elements, where the front-end provides a shared library of graphical interface elements and the back-end offers a clear toolset for model-dependent analysis. 
The two parts of the framework are referred to as `EasyApp`, the graphical elements, and `easyCore` the analysis toolset. 

[TODO]: A figure showing the EasyScience framework and how things interact.

In this school, we are looking only at the `easyCore` component, as we want to focus on how we can perform complex model-dependent analysis, from a Python intrerface. 
`easyCore` allows the user to write a mathematical model that can be used to produce model data and take advantage of a range of optimization algorithms to help find the optimal parameters to provide the best agreement between the model and measured data.
