#import "./template.typ": float, template
#import "@preview/muchpdf:0.1.0": muchpdf

#let pmg = "pymatgen"
#let pdf-img(path, ..args) = muchpdf(read(path, encoding: none), ..args)

#let title = "pymatgen: A decade of community growth, new functionality, and future prospects"

// commands for attributed notes in different colors and with initials prefix
#let JG(body) = {
  set text(fill: red)
  [JG: #body]
}
#let MK(body) = {
  set text(fill: blue)
  [MK: #body]
}
#let HY(body) = {
  set text(fill: orange)
  [HY: #body]
}
#let SK(body) = {
  set text(fill: green)
  [SK: #body]
}
#let JR(body) = {
  set text(fill: purple)
  [JR: #body]
}

#show: template.with(
  title: title,
  abstract: (
    [
      Some fancy abstract text.
    ],
    (
      title: "Plain Language Abstract",
      content: [#pmg is a software tool that helps scientists...],
    ),
  ),
  venue: [_Digital Discovery_],
  header: (
    article-color: rgb("#364f66"),
    article-type: "Preprint",
    article-meta: [Not Peer-Reviewed],
  ),
  authors: ((name: "TBD", corresponding: true),),
  // affiliations: affiliations,
  dates: (
    (type: [Received Date], date: datetime.today()),
    (type: [Revised Date], date: datetime.today()),
    (type: [Accepted Date], date: datetime.today()),
  ),
  doi: "00.0000/XXXXXXXXXX",
  citation: [MP et al., _Digital Discovery_, 2025, *1*, 1---2],
)

#figure(
  image("figs/pymatgen-2-logo.svg", width: 20%),
  caption: [Logo for the pymatgen 2 release.],
)






= Abstract

We present the second major release of the Python Materials Genomics (#pmg) library, reflecting on a decade of community growth and established best practices. This version builds on #pmg's robust, open-source foundation, emphasizing its collaborative nature. Over the past decade, #pmg has thrived as one of the largest open-source materials science codebases. We detail how #pmg aids modern computational materials science, its adaptation to changing demands, and lessons learned from its growing community.

#figure(
  image("figs/mindmap.svg"),
  caption: [Topics and tools in the pymatgen ecosystem.],
)




= Introduction

Since 2011, #pmg has enabled both individual and high-throughput computational materials science efforts @ong_python_2013. It started as a central code in the Materials Project@jain_commentary_2013 and nowadays provides tools for setup and analysis of materials simulations, and interfaces to various materials science codes. The library has grown significantly through community efforts, adapting to expanding needs in the field of materials informatics @butler_machine_2018.

On #pmg's 10th anniversary, we review its evolution, sharing challenges and solutions encountered during its growth. We highlight factors that established #pmg as a cornerstone of materials science software.

= Summary

#pmg is an open-source Python library for materials analysis, offering tools from basic crystallographic operations to complex electronic structure analysis @ong_python_2013 @jain_commentary_2013. Key features include:

+ Crystallographic and structural analysis
+ Electronic structure analysis
+ Thermodynamic and phase diagram tools
+ Integration with various DFT codes
+ Machine learning utilities for materials property prediction //@ward2018matminer

#pmg aims to accelerate materials discovery by providing a comprehensive toolkit for researchers at all levels @curtarolo_highthroughput_2013.

= Statement of Need

Computational materials science requires powerful, flexible, and reliable software tools @horton_promises_2021. #pmg addresses this need by offering:

+ A unified framework for materials analysis
+ Robust algorithms for diverse materials data
+ Interoperability with popular DFT codes
+ Open-source development encouraging community contributions

#pmg complements other materials science software like ASE @larsen_atomic_2017, VASP @kresse_efficient_1996, and LAMMPS @plimpton_fast_1995 @thompson_lammps_2022, enhancing accessibility and reproducibility in materials research.


== Literature Usage

#pmg has been cited over 3,000 times since 2013 @ong_python_2013, with usage in:

+ Materials Project research: Large-scale materials analysis and property prediction @jain_commentary_2013.

#pmg has been applied in diverse fields, including battery materials, catalysis, thermoelectrics, and materials discovery using machine learning // @jain2016computational.

#image("figs/Screenshot 2025-09-03 at 18.44.12.png")

== Downstream Packages

#pmg has spawned several downstream packages, including:

+ `atomate1/2`: High-throughput computational materials science workflows @mathew_atomate_2017
+ `custodian`: Job management and error recovery
+ `matminer`: Data mining in materials science //@ward2018matminer
+ `pymatgen-analysis-diffusion`: Diffusion analysis tools @deng_datadriven_2017
+ `pymatgen-analysis-alloys`: Alloy analysis tools
+ `doped`, `ShakeNBreak`: Defect modelling tools, building on `pymatgen-analysis-defects` & `PyCDT`.

These packages demonstrate #pmg's extensibility and its role in the materials informatics ecosystem @butler_machine_2018.


#SK[For instance, the utility of #pmg as a foundational tool in computational materials science workflows is well-illustrated by its usage in the modelling of crystal defects...
  + Defect simulations require many steps, using a wide range of core tools (structure manipulations, symmetry analyses, efficient I/O w/electronic structure codes, lightweight metadata & serialization for reproducibility, interface with Materials Project...)
  + *But*, with specific requirements for their special case (e.g. efficient & appropriate supercell generation, point symmetries of defect sites in symmetry-breaking supercells, efficient algorithms for large structure analyses, calculation parameter consistency checks, targeted distortions, site multiplicities & degeneracies, smart algorithms for sub-phase diagrams...).
  + Defect modelling is a rapidly growing field, due to advances in computational power and methods making these calculations tractable, along with the importance of these species to diverse materials applications. These community tools, facilitated by the foundational toolkit of #pmg, have accelerated and expanded computational defect investigations, and have reducing the barrier to entry for new researchers in this field.
  + (If we want a figure here, could make a diagram showing the workflow: Pull materials from MP -> Oxi-state Guess w/PMG -> Vacancy generation w/`doped` (via PMG etc) -> Electrostatic analysis with PMG (Ewald tools) -> VASP DFT I/O w/PMG -> Energetic & Structural (w/`doped` & PMG) analysis; from 10.1088/2515-7655/ade916, as example).
]





== Similar and Related Software

While #pmg holds a unique position, other valuable tools in the field include:

+ ASE: Python library for atomistic simulations @larsen_atomic_2017
+ spglib: C library for crystal symmetries, used by #pmg //@togo2018texttt
+ GPAW: DFT Python code using PAW method @mortensen_realspace_2005
+ Phonopy: Package for phonon calculations @togo_firstprinciples_2023
+ LAMMPS: Classical molecular dynamics code @plimpton_fast_1995 @thompson_lammps_2022

These tools often complement each other in materials science workflows. #pmg's strength lies in its comprehensive coverage of materials analysis tasks and integration capabilities //@jain2016computational.

= Background

#pmg was developed in 2011 by Shyue Ping Ong and colleagues at MIT to support the Materials Project @ong_python_2013 @jain_commentary_2013. Initial features included:

+ Crystallographic operations and symmetry analysis
+ VASP DFT code integration
+ Basic electronic structure analysis
+ Phase diagram generation

Since then, #pmg has expanded significantly, incorporating new features and adapting to the evolving landscape of materials informatics @butler_machine_2018.

= New Features and Case Study

#figure(
  image("figs/pr-topics-over-time-stacked-bar.svg"),
  caption: [Pull request topics over time in the pymatgen repository.],
)

#figure(
  image("figs/commits_per_package_heatmap.svg"),
  caption: [Monthly commits per pymatgen subpackage (heatmap).],
)


Recent additions to #pmg include:

+ Enhanced machine learning integration //@ward2018matminer
+ Support for additional DFT and post-processing codes (e.g., FHI-AIMS, LOBSTER @george_automated_2022 , Critic2, Phonopy@petretto_highthroughput_2018)
+ Improved structure prediction and analysis algorithms (including magnetic structure) @waroquiers_chemenv_2020 @pan_benchmarking_2021 @horton_highthroughput_2019
+ Advanced battery materials research tools // TODO add ref(s)
+ Quantum chemistry code integration // TODO add ref(s)

Case study: Battery materials research with #pmg

#pmg offers tools for:
- Voltage calculation
- Diffusion analysis @deng_datadriven_2017
- Electrode stability prediction // TODO add ref(s)

/* #figure(
  table(
    columns: (auto, auto, auto, auto, auto),
    inset: 8pt,
    align: horizon,
    [*Module/Submodule*], [*Key Features*], [*Original Implementation*], [*Example Usage / Citation*], [*Change from v1*],
    [`core`], [Fundamental data structures], [@ong_python_2013], [jain_commentary_2013], [Expanded and optimized],
    [`analysis.chemenv`], [Chemical bonding environments], [waroquiers2020chemical], [zhang2017facile], [New],
    [`analysis.diffraction`], [X-ray, neutron, electron diffraction], [ong_python_2013], [yang2020predicting], [Added electron diffraction],
    [`analysis.magnetism`], [Magnetic structure analysis], [pandey2017pymatgen], [wang2021high], [New],
    [`electronic_structure.cohp`], [Crystal Orbital Hamilton Populations], [esters2022lobsterpy], [esters2023lobster], [New],
    [`ext.matproj`], [Materials Project API integration], [ong_python_2013], [jain_commentary_2013], [Adapted for new API versions],
    [`io.vasp`], [VASP input/output handling], [ong_python_2013], [jain_commentary_2013], [Expanded file support],
    [`phonon`], [Phonon calculations and analysis], [petretto2018high], [george2020machine], [New],
    [`transformations`], [Structure manipulations], [ong_python_2013], [wang2021materials], [Expanded transformations],
    [`vis`], [Visualization tools], [ong_python_2013], [horton2023crystal], [New plotly integration]
  ),
  caption: [Key modules of pymatgen and their evolution from v1 to current version]
)

#set text(size: 11pt) */

= Community Impact

#SK[This is a nice figure, though I would say it shows community _involvement_ (which is kind of a step ahead of community _impact_). What about also showing something like downloads over time (which can be quantitatively inaccurate but should show the trend? 'without mirrors'), and packages requiring #pmg over time? (Edit: I see from the GitHub repo that this is in progress)]

#pmg's impact on the materials science community includes:

+ Accelerated research across various domains //@jain2016computational
+ Standardization of materials analysis procedures
+ Educational tool for students and early-career researchers @ong_python_2013
+ Industry adoption in R&D workflows //@jain2013commentary
+ Promotion of open science and collaborative development @horton_promises_2021

The library's impact is evident in its usage in high-impact publications and integration into platforms like the Materials Project, AFLOW, and OQMD //@curtarolo2012aflow @saal2013materials.

= Challenges and Solutions

#figure(
  image("figs/pr-since-1st.svg"),
  caption: [Pull requests per contributor since their first contribution.],
)




#figure(
  image("figs/active-contributors-colored.svg"),
  caption: [Active contributors to #pmg over time.],
)

#figure(
  image("figs/pr_contributors_worldmap.svg"),
  caption: [Geographic distribution of #pmg pull request contributors.],
)


Key challenges in #pmg's development:

+ Code Maintenance: Implemented comprehensive unit testing and continuous integration @ong_python_2013
#SK[Just noting, as an external user/contributor, something I would find insightful as a reader would be hearing about the need/workload for dedicated maintainers, and how this can be minimised (but I guess can never be avoided)]
+ Performance: Optimized critical paths and used compiled languages for key sections
+ Documentation: Adopted auto-documentation tools and prioritized documentation contributions
+ Compatibility: Implemented cross-platform testing and version management
+ Community Management: Established clear contribution guidelines and regular community meetings

Future considerations include integrating Rust components for improved performance while maintaining Python's ease of use @lunnikivi_transpiling_2020.

= Conclusion

#pmg has evolved from a specialized tool into a cornerstone of computational materials science. Its growth reflects the collaborative spirit of the materials informatics community and the importance of open-source software in scientific research @ong_python_2013 //@jain2016computational.

Future developments may include:

+ Enhanced machine learning and AI integration @butler_machine_2018
+ Improved multi-scale modeling support // TODO add ref(s)
+ More user-friendly interfaces and visualization tools //pymatviz, crystaltoolkit?
+ Exploration of hybrid Python-Rust architectures @lunnikivi_transpiling_2020

We remain committed to fostering an open, collaborative environment that drives innovation in computational materials science.

= Acknowledgments

We thank the numerous developers, researchers, and users who have contributed to #pmg. We also acknowledge the funding agencies and institutions that have supported its development, including the U.S. Department of Energy, the National Science Foundation, and various academic institutions.

Special thanks to the broader open-source scientific computing community for their invaluable tools and libraries, especially NumFocus and their efforts around `numpy`, `pandas` and `matplotlib`, all of which #pmg heavily relies on. //corresponding citations should be added

#bibliography("refs.bib", style: "ieee")
