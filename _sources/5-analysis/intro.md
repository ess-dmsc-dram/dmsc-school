# Model-dependent analysis

There are two general approaches to the analysis of data; model-dependent and model-independent.
In this summer school, we are going to focus on the former; however, the latter is worth briefly highlighting.
A model-independent approach to analysis is where no assumptions are made about the system that is being studied and conclusions are drawn **only** from the data that has been observed.
In many applications, it is desirable to include *what we think we know* about the system, and hence the use of model-dependent analysis.

Model-dependent analysis involves the development of a mathematical model that describes the model dataset that would be found for our system.
This mathematical model usually has parameters that are linked to the physics and chemistry of our system.
These parameters are varied to optimise the model, using an optimisation algorithm, with respect to the experimental data, i.e., to get the best agreement between the model data and the experimental data.
Model-dependent analysis is popular in the analysis of neutron scattering data, but before we apply this to your simulated neutron data, let us investigate some of the properties of model-dependent analysis through some toy examples.

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
            A diagrammatic description of the process of model-dependent analysis.
        </span>
        <a class="headerlink" href="#mda" title="Permalink to this diagram">#</a>
    </p>
</figcaption>
