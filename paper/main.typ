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

As shown in @fig:mindmap, #pmg has evolved into a comprehensive ecosystem spanning diverse research areas from battery materials to machine learning applications.

#figure(
  image("figs/mindmap.svg"),
  caption: [#pmg functionality grouped into research topics, colored by number of papers in each topic citing #pmg.],
) <fig:mindmap>

= Introduction

Since 2011, #pmg has enabled both individual and high-throughput computational materials science efforts @ong_python_2013. It started as a central code in the Materials Project@jain_commentary_2013 and nowadays provides tools for setup and analysis of materials simulations, and interfaces to various materials science codes. The library has grown significantly through community efforts, adapting to expanding needs in the field of materials informatics @butler_machine_2018.  // potentially one or two more sentences on the impact it has

On #pmg's 10th anniversary, we review its evolution and impact, sharing challenges and solutions encountered during its growth. We furthermore highlight factors that established #pmg as a cornerstone of materials science software. This retrospective could also serve as a guiding example for other community codes in the materials science domain. Lastly, we outline future developments.

= Overview and Design Principles

== Background

#pmg was developed in 2011 by Shyue Ping Ong and colleagues at MIT to support the Materials Project @ong_python_2013 @jain_commentary_2013. Initially, #pmg provided essential tools for crystallographic operations, symmetry analysis, integration with the VASP density functional theory (DFT) code, and basic electronic structure and phase diagram analysis. These foundational capabilities enabled researchers to automate and standardize many aspects of computational materials science, laying the groundwork for high-throughput materials discovery.


Since then, #pmg has expanded significantly, incorporating new features and adapting to the evolving landscape of materials informatics @butler_machine_2018. Key trends shaping its development include:

+ The growing importance of research data management
+ The rise of automated workflows for reproducible simulations and experiments
+ Increasing use of machine learning for materials property prediction
+ Greater availability of computational resources, enabling more complex analyses

//#pmg is an open-source Python library for materials analysis, offering tools from basic crystallographic operations to complex electronic structure analysis @ong_python_2013 @jain_commentary_2013. Key features include:

Today, #pmg aims to accelerate materials discovery by providing a comprehensive toolkit for researchers at all levels @curtarolo_highthroughput_2013. While pymatgen’s original goals—such as crystallographic operations and electronic structure analysis—remain central, its capabilities have grown substantially to support a broad spectrum of tasks in computational materials science. Today, pymatgen offers powerful tools for crystallographic and structural analysis, electronic structure parsing, thermodynamic and phase diagram construction, and seamless integration with various DFT codes. Additionally, it includes utilities for machine learning applications in materials property prediction [@ward_matminer_2018], reflecting its evolution into a comprehensive platform for materials informatics.



== Statement of Need

The growing complexity of computational materials science requires powerful, flexible, and reliable software tools @horton_promises_2021. #pmg addresses this need by offering:

+ A unified framework for materials analysis
+ Robust algorithms for diverse materials data
+ Interoperability with popular DFT codes
+ Open-source development encouraging community contributions

#pmg complements other materials science software and we will discuss the package infrastructure and dependent codes below. The closest software of similar popularity is likely ASE @larsen_atomic_2017. However, the design philosophy and use cases of both software are different and partially complementary. #pmg can also be used alongside ASE. Both packages provide parsers for DFT and quantum chemistry codes and general analysis and manipulation tools for molecules and structures. However, ASE enables quantum-chemical simulations by tightly integrating quantum-chemical calculators and MD and other structural optimization capabilities. In contrast, #pmg focuses more on providing materials data analysis functionalities and parsers for quantum-chemical simulations. #pmg's strength lies in its comprehensive coverage of materials analysis tasks and integration capabilities @jain_computational_2016.

= Community Adoption

== Package Ecosystem

#pmg has spawned several downstream packages, including:

+ `atomate1/2`: High-throughput computational materials science workflows @mathew_atomate_2017. `atomate2`, also published in Digital Discovery, demonstrates #pmg's role as a foundational tool for diverse materials science workflows used across the community for high-throughput studies.
+ `custodian`: Job management and error recovery
+ `matminer`: Data mining in materials science @ward_matminer_2018
+ `pymatgen-analysis-diffusion`: Diffusion analysis tools @deng_datadriven_2017
+ `pymatgen-analysis-alloys`: Alloy analysis tools
+ `doped`, `ShakeNBreak`: Defect modeling tools, building on `pymatgen-analysis-defects` & `PyCDT`

These packages demonstrate #pmg's extensibility and its role in the materials informatics ecosystem @butler_machine_2018.

#figure(
  image("figs/pmg_dependency_usage.svg"),
  caption: [3rd-party dependency usage of #pmg modules.],
) <fig:pmg-dependency-usage>

#figure(
  image("figs/dependent-usage-of-pmg.svg"),
  caption: [Dependent repositories' usage of #pmg submodules.],
) <fig:dependent-usage-of-pmg>

#SK[What about also showing something like downloads over time (which can be quantitatively inaccurate but should show the trend? 'without mirrors'), and packages requiring #pmg over time?]

The growth of #pmg is reflected not only in its feature set but also in its expanding user base and community engagement. Steady growth in package downloads and the number of packages requiring #pmg as a dependency over time are evidence of #pmg's increasing adoption across the materials science community, as shown in @fig:pmg-dependency-usage and @fig:dependent-usage-of-pmg.

#pmg's impact on the materials science community includes:

+ Accelerated research across various domains @butler_machine_2018
+ Standardization of materials analysis procedures
+ Educational tool for students and early-career researchers @ong_python_2013
+ Industry adoption in R&D workflows @jain_commentary_2013
+ Promotion of open science and collaborative development @horton_promises_2021

The library's impact is evident in its usage in high-impact publications and integration into platforms like the Materials Project, AFLOW, and OQMD @curtarolo_aflow_2012.

== Literature Usage

#pmg has been cited over 4,000 times since 2013 @ong_python_2013, poised to reach over 1000 citations in 2025 alone, with usage spanning:

+ Materials Project research: Large-scale materials analysis and property prediction @jain_commentary_2013.

#pmg has been applied in diverse fields, including battery materials, catalysis, thermoelectrics, and materials discovery using machine learning @jain_computational_2016.

#figure(
  image("figs/citations.svg"),
  caption: [Citations of #pmg over time.],
) <fig:citations>

== Case Studies

=== Defect Modeling Tools

#SK[
  The utility of #pmg as a foundational tool in computational materials science workflows is well-illustrated by its usage in the modeling of crystal defects. Defect simulations require many steps, utilizing a wide range of core tools including structure manipulations, symmetry analyses, efficient I/O with electronic structure codes, lightweight metadata and serialization for reproducibility, and interfaces with the Materials Project. However, defect modeling also has specific requirements for specialized cases, such as efficient and appropriate supercell generation, point symmetries of defect sites in symmetry-breaking supercells, efficient algorithms for large structure analyses, calculation parameter consistency checks, targeted distortions, site multiplicities and degeneracies, and smart algorithms for sub-phase diagrams.

  Defect modeling is a rapidly growing field, driven by advances in computational power and methods that make these calculations tractable, along with the critical importance of defect species to diverse materials applications. Community tools facilitated by the foundational functionality in #pmg, have accelerated and expanded computational defect investigations while reducing the barrier to entry for new researchers in this field.
  + (If we want a figure here, could make a diagram showing the workflow: Pull materials from MP -> Oxi-state Guess w/PMG -> Vacancy generation w/`doped` (via PMG etc) -> Electrostatic analysis with PMG (Ewald tools) -> VASP DFT I/O w/PMG -> Energetic & Structural (w/`doped` & PMG) analysis; from 10.1088/2515-7655/ade916, as example).
]

=== Data-driven Heuristic Assessment and Machine Learning
#pmg is a powerful toolkit that enables large-scale data analysis and machine learning studies in materials science. Through its integration with materials databases such as the Materials Project and OPTIMADE, researchers can easily retrieve extensive datasets, including machine learning targets, which serve as the foundation for data-driven assessments and the development of machine learning modules. When working with other sources like ICSD or MAGNDATA, #pmg’s ability to read (magnetic) Crystallographic Information Files (CIFs) facilitates the creation of large, structured datasets.
Many chemical heuristics—such as those related to stability, synthesizability, defect energetics, and magnetism—rely on accurate determinations of oxidation states and coordination environments, which can both be assessed within #pmg. Additionally, #pmg is deeply integrated within matminer, a library that streamlines the generation of popular features for machine learning workflows, further supporting the derivation and validation of heuristics.
In summary, #pmg provides a framework for materials data handling, feature extraction, and heuristic development, making it an essential tool for modern, data-driven materials informatics.




= New Features

Recent additions to #pmg include:

+ Enhanced machine learning integration @butler_machine_2018
+ Support for additional DFT and post-processing codes (e.g., FHI-AIMS, LOBSTER @george_automated_2022, Critic2, Phonopy@petretto_highthroughput_2018)
+ Improved structure prediction and analysis algorithms (including magnetic structure) @waroquiers_chemenv_2020 @pan_benchmarking_2021 @horton_highthroughput_2019
+ Advanced battery materials research tools
+ Quantum chemistry code integration

As illustrated in @fig:pr-topics and @fig:commits-heatmap, the development activity has been sustained across multiple subpackages, with contributions spanning bug fixes, new features, and performance improvements.

#figure(
  image("figs/pr-topics-over-time-stacked-bar.svg"),
  caption: [Pull request topics over time in the pymatgen repository.],
) <fig:pr-topics>

#figure(
  image("figs/commits_per_package_heatmap.svg"),
  caption: [Monthly commits per pymatgen subpackage (heatmap).],
) <fig:commits-heatmap>

Case study: Battery materials research with #pmg

#pmg offers tools for:
- Voltage calculation
- Diffusion analysis @deng_datadriven_2017
- Electrode stability prediction // TODO add ref(s)


= Challenges and Solutions

Maintaining and evolving a project of #pmg's scale presents unique challenges that have shaped its development approach.


Key challenges in #pmg's development:

+ Code Maintenance: Implemented comprehensive unit testing and continuous integration @ong_python_2013
+ Performance: Optimized critical paths and used compiled languages for key sections
+ Documentation: Adopted auto-documentation tools and prioritized documentation contributions
+ Compatibility: Implemented cross-platform testing and version management
+ Community Management: Established clear contribution guidelines and regular community meetings

As shown in @fig:pr-since-1st @fig:active-contributors and @fig:contributors-worldmap, the community has grown organically with contributors from around the world, though maintaining consistent development velocity requires dedicated maintainers.

#figure(
  image("figs/pr-since-1st.svg"),
  caption: [Pull requests per contributor since their first contribution.],
) <fig:pr-since-1st>

#figure(
  image("figs/active-contributors-colored.svg"),
  caption: [Active contributors to #pmg over time.],
) <fig:active-contributors>

#figure(
  image("figs/pr_contributors_worldmap.svg"),
  caption: [Geographic distribution of #pmg pull request contributors.],
) <fig:contributors-worldmap>

Future considerations include integrating Rust components for improved performance while maintaining Python's ease of use @lunnikivi_transpiling_2020.

= Outlook and Future Developments

#pmg has evolved from a specialized tool into a cornerstone of computational materials science. Its growth reflects the collaborative spirit of the materials informatics community and the importance of open-source software in scientific research @ong_python_2013 @jain_computational_2016.

Future developments may include:

+ Enhanced machine learning and AI integration @butler_machine_2018
+ Improved multi-scale modeling support, bridging atomistic and continuum approaches // TODO add ref(s)
+ More user-friendly interfaces and visualization tools (#link("https://github.com/materialsproject/crystaltoolkit")[`crystaltoolkit`] @horton_crystal_2023 #link("https://github.com/janosh/pymatviz")[`pymatviz`] @riebesell_pymatviz_2022 #link("https://github.com/janosh/matterviz")[`matterviz`] @riebesell_matterviz_2025)
+ Performance optimizations through compiled extensions and algorithmic improvements. E.g. exploration of hybrid Python-Rust bindings @lunnikivi_transpiling_2020. // TODO mention moyo as a successful example of this?

We remain committed to fostering an open, collaborative environment that drives innovation in computational materials science.

= Acknowledgments

We thank the numerous developers, researchers, and users who have contributed to #pmg. We also acknowledge the funding agencies and institutions that have supported its development, including the U.S. Department of Energy, the National Science Foundation, and various academic institutions.

Special thanks to the broader open-source scientific computing community for their invaluable tools and libraries, especially NumFocus and their efforts around `numpy` @harris_array_2020, `pandas` @mckinney_data_2010 @team_pandasdev_2025 and `matplotlib` @hunter_matplotlib_2007, all of which #pmg heavily relies on.

ChatGPT was used to improve the language.

#bibliography("refs.bib", style: "ieee")
