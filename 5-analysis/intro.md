# Model-dependent analysis

There are two common approaches for the analysis of data, there are model-dependent and independent. 
In this summer school, we will focus on the former, however, the latter is worth highlighting. 
A model-independent approach to analysis is where we make no assumptions about the system that we are studying and draw conclusions only from the data that has been observed. 
In many applications, it is desirable to include *what we think we know* about the system, hence the use of model-dependent analysis. 

Model-dependent analysis involved the development of a mathematical model that describes the {term}`model dataset` that would be observed from our system. 
This mathematical model usually has {term}`parameters`, which are linked to the physics/chemistry of our system, that are varied to optimise the model. 
This optimisation is achieved with an {term}`optimisation algorithm` that tries to obtain the best agreement between the model dataset and the measured experimental data. 
Model-dependent analysis is a popular approach to the analysis of neutron scattering data, before applying this to your simulated neutron data, we will investigate some of the properties of model-dependent analysis with some toy examples. 

```{mermaid}
flowchart LR;
    a(Propose model);
    b(Set/change model\nparameter values);
    c{{Calculate\nmodel data}};
    d(Compare model data\nto experimental data);
    e(Stop iteration);
    a-->b;
    b-->c;
    c-->d;
    d-->|Threshold not\nreached|b;
    d-->|Threshold\nreached|e;
```
<figcaption align="center" id="mda">
    <p>
        <span class="caption-number">Diagram 1. </span>
        <span class="caption-text">
            A diagramatic description of the process of model-dependent analysis.
        </span>
        <a class="headerlink" href="#mda" title="Permalink to this diagram">#</a>
    </p>
</figcaption>