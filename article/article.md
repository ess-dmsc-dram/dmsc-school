# The First European Spallation Source Data Management and Software Centre Summer School

[Andrew R. McCluskey](https://orcid.org/0000-0003-3381-5911)<sup>a,</sup>&Dagger;\*, 
Petra Aulin<sup>a</sup>, 
Fredrik Bolmsten<sup>a</sup>, 
Mads Bertelsen<sup>a</sup>, 
[Carina M. C. Lobley](https://orcid.org/0000-0003-3673-2767)<sup>b</sup>, 
Joanna Lewis<sup>b</sup>, 
[Massimiliano Novelli](https://orcid.org/0000-0003-2818-0368)<sup>a</sup>, 
Cosmina Somani<sup>a</sup>, 
Alexandre Stefanov<sup>a</sup>, 
Martin Trajanovski<sup>a</sup>, 
[Neil Vaytet](https://ocrid.org/0000-0002-6843-0037)<sup>a</sup>, 
Peter K. Willendrup<sup>a</sup>, 
[Jan-Lukas Wynen](https://orcid.org/0000-0002-3761-3201)<sup>a</sup>, 
Sunyoung Yoo<sup>a</sup>, and
Thomas Holm Rod<sup>a</sup>\* 

a. Data Management and Scientific Computing Division, European Spallation Source ERIC, Copenhagen, Denmark.
b. Research Coordination Office, European Spallation Source ERIC, Lund, Sweden.

&Dagger; Current Address: School of Chemistry, University of Bristol, Cantock's Close, Bristol, BS8 1TS, United Kingdom 

* [andrew.mccluskey@bristol.ac.uk](mailto:andrew.mccluskey@bristol.ac.uk)/[thomas.holmrod@ess.eu](mailto:thomas.holmrod@ess.eu)

From the fourth to the eight of September 2023, the Data Management and Software Centre (DMSC) of the European Spallation Source (ESS) hosted the first DMSC Summer School.
The focus of this school was to introduce "students" (ranging from Master's-level to staff scientist) to the growing importance of data in the neutron scattering landscape.
The summer school covered aspects of Python programming, experimental simulation, data reduction, analysis and cataloguing -- with a focus on FAIR data practices throughout.
The material from the summer school is available online at [ess-dmsc-dram.github.io/dmsc-school](https://ess-dmsc-dram.github.io/dmsc-school) and the school was generously supported by the Carlsberg Foundation and the Danish Scattering Association (DanScatt).

The role of data in the neutron scattering landscape is changing, with more impetus being placed on the role of complex data reduction and analysis, as well as the importance of FAIR (findable, accessible, interoperable, and reusable) and open data [10.1140/epjp/s13360-023-04189-6](https://doi.org/10.1140/epjp/s13360-023-04189-6).
The European Spallation Source (ESS) has recognised this, leading to the creation of the Data Management and Software Cente (DMSC) division, based in Copenhagen and linked to the ESS Lund site for fast data transfer.
This makes ESS unique in the neutron scattering landscape, coming online with data as a primary partner in user experiments, alongside the instrumentation itself.

It was identified that training future users of ESS in neutron data simulation, reducation, analysis and handling would be important to enable the best science.
Therefore, the first DMSC Summer School was organised, to provide an in-depth discussion of these aspects.
The school was hosted at the Niels Bohr Institute of the University of Copenhagen (with some workshops taking place in the historic Auditorium A, where Niels Bohr himself had taught), the ESS site in Lund, and the DMSC offices in Copenhagen.

Modern data skills in neutron scattering require modern computational practices, in particular the use of the Python programming language and Jupyter Notebooks [10.1109/MCSE.2021.3059263](https://doi.org/10.1109/MCSE.2021.3059263).
Therefore, the first day of the summer school focused on introducing the Python programming language and plotting within Jupyter.
This gave the students a firm grounding in Python and ensured that all students were capable of working confidently on the material in later days.
This day ended with a presentation introducing the ESS viewpoint on the subject of data management plans and the importance of FAIR data, concepts that would be consolidated throughout the school.

Tuesday was spent in Lund, first to visit the MAX IV synchrotron source, which is a close neighbour of the ESS. 
After a tour of MAX IV, the students were introduced to the neutron instrumentation software McStas [REF FOR MCSTAS]. 
At this point, the students were asked if they would prefer to simulate a small-angle neutron scattering (SANS) instrument or a backscattering quasi-elastic neutron scattering (QENS) instrument. 
In the end, the fourteen students split approximately 50:50 between the two. 
Additionally, while at the ESS site, the students where given a tour of the ESS construction site and participated in a poster session, where they were able to discuss their shared interests in the importance of data in neutron scattering. 

The following day, the group returned to the Niels Bohr Institute to continue working with their simulated data. 
Now, the task was to reduce their raw, simulated data to something that can be analysed with traditional methods. 
For this, the `scipp` package [REF FOR SCIPP] was used, enabling informative visualisations and most importantly the ability to efficiently manipulate and histogram the data. 
Using `scipp` the students were able to reduce their raw detector data from the McStas simulations to a 1D dataset of intensity as a function of either wavevector (SANS) or energy transfer (QENS). 

On Thursday, the students were introduced to the EasyScience framework [REF FOR EASYSCIENCE] and tested with analysing their reduced data using a model-dependent approach. 
For the SANS datasets, this meant fitting a spherical model to the "experimental" data, while for those working with QENS a simple diffusion model was used. 
Beyond standard fitting, the students were shown Bayesian methods; Markov chain Monte Carlo and nested sampling, to probe the correlations in the model parameters and compare different analytical models. 

The week ended with an discussion of the importance of data storage and cataloguing, in this case using the SciCat service. 
The students were asked to consider what parts of their experiments constituted "data" and tasked with using the `scitacean` package to upload their complied datasets to the SciCat instance. 
This session was particularly informative as it helped the students think again about the introduction to proposals, DMPs and FAIR data given at the start of the week. 

Alongside the teaching, there was a range of social activities that the students were invited to participate in -- with the aim to build a cohort of data-focused neutron scatterers. 
This started the Sunday before the school started with a visit to a board game café in central Copenhagen, where the group were welcomed. 
On the Wednesday evening, the students (and many of the teachers) participated in an programming competition, a game that regularly takes place between staff of the DMSC, where they were tasked with writing a Python program to compete in a tournement, with one "AI" named as the winner. 
Finally, there was a summer school dinner on the Thursday evening, which took place within the Tivoli Gardens in central Copenhagen. 

All in all, the first DMSC Summer School was successful in its aim to introduce members of the neutron scattering community to the growing importance of data in the field. 
The feedback from the participants has been extremely positive and given that the event itself was 300 % oversubscribed, there is ambition to run it again in the future. 
Hopefully, we will be able to welcome you to Copenhagen in the future for another DMSC Summer School. 
