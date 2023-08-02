# Model-dependent analysis

**Model-dependent analysis** is the process where a mathematical model is constructed that provides a {term}`model dataset` that would be observed, if our mathematical model precisely described the system.
The {term}`parameters` of this model are then optimised, using some {term}`optimisation algorithm` to obtain the best agreement between the model dataset and our measured experimental data. 
The use of model-dependent analysis is popular in neutron scattering analysis, however, before working with our simulated neutron data, we will look at some toy examples. 

```{mermaid}
flowchart LR;
    a(Propose model);
    b(Set/change model\nparameter values);
    c{{Calculate model\ndata}};
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