#import "./template.typ": float, template
#import "@preview/muchpdf:0.1.0": muchpdf

#let pmg = `pymatgen`
#let pdf-img(path, ..args) = muchpdf(read(path, encoding: none), ..args)
#show link: underline

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
*@ Janine*

Since 2011, #pmg has enabled both individual and high-throughput computational materials science efforts @ong_python_2013. It started as a central code in the Materials Project@jain_commentary_2013 and nowadays provides tools for setup and analysis of materials simulations, and interfaces to various materials science codes. The library has grown significantly through community efforts, adapting to expanding needs in the field of materials informatics @butler_machine_2018.  // potentially one or two more sentences on the impact it has

On #pmg's 10th anniversary, we review its evolution and impact, sharing challenges and solutions encountered during its growth. We furthermore highlight factors that established #pmg as a cornerstone of materials science software. This retrospective could also serve as a guiding example for other community codes in the materials science domain. Lastly, we outline future developments.

*Pymatgen's place in the community*

= Overview and Design Principles
*@ Janine*
== Background

#pmg was developed in 2011 by Shyue Ping Ong and colleagues at MIT to support the Materials Project @ong_python_2013 @jain_commentary_2013. Initially, #pmg provided essential tools for crystallographic operations, symmetry analysis, integration with the VASP density functional theory (DFT) code, and basic electronic structure and phase diagram analysis. These foundational capabilities enabled researchers to automate and standardize many aspects of computational materials science, laying the groundwork for high-throughput materials discovery.


Since then, #pmg has expanded significantly, incorporating new features and adapting to the evolving landscape of materials informatics @butler_machine_2018. Key trends shaping its development include:

+ The growing importance of research data management
+ The rise of automated workflows for reproducible simulations and experiments
+ Increasing use of machine learning for materials property prediction
+ Greater availability of computational resources, enabling more complex analyses

//#pmg is an open-source Python library for materials analysis, offering tools from basic crystallographic operations to complex electronic structure analysis @ong_python_2013 @jain_commentary_2013. Key features include:

Today, #pmg aims to accelerate materials discovery by providing a comprehensive toolkit for researchers at all levels @curtarolo_highthroughput_2013. While pymatgen’s original goals—such as crystallographic operations and electronic structure analysis—remain central, its capabilities have grown substantially to support a broad spectrum of tasks in computational materials science. Today, pymatgen offers powerful tools for crystallographic and structural analysis, electronic structure parsing, thermodynamic and phase diagram construction, and seamless integration with various DFT codes. Additionally, it includes utilities for machine learning applications in materials property prediction @ward_matminer_2018, reflecting its evolution into a comprehensive platform for materials informatics.



== Statement of Need

The growing complexity of computational materials science requires powerful, flexible, and reliable software tools @horton_promises_2021. #pmg addresses this need by offering:

+ A unified framework for core materials analyses
+ Robust algorithms for diverse materials data
+ Interoperability with popular DFT codes and databases
+ Open-source development encouraging community contributions

#pmg complements other materials science software and we will discuss the package infrastructure and dependent codes below. The closest software of similar popularity is likely ASE @larsen_atomic_2017. However, the design philosophy and use cases of both software are different and partially complementary. #pmg and ASE can be used alongside eachother. Both packages provide parsers for DFT and quantum chemistry codes and general analysis and manipulation tools for molecules and structures. However, ASE enables quantum-chemical simulations by tightly integrating quantum-chemical calculators and MD and other structural optimization capabilities. In contrast, #pmg focuses more on providing materials data analysis functionalities and parsers for quantum-chemical simulations. #pmg's strength lies in its comprehensive coverage of materials analysis tasks and integration capabilities @jain_computational_2016.

= Community Adoption and Impact
*@ Seán*

The growth of #pmg is reflected not only in its feature set but also in its expanding user base and community engagement. Steady growth in downloads and the number of packages requiring #pmg as a dependency over time are evidence of widespread and increasing adoption across the materials science community. Indeed, #pmg has been cited over 4,000 times since 2013 @ong_python_2013 (@fig:citations), poised to reach over 1000 citations in 2025 alone.
These usages span diverse fields, including energy storage and conversion, catalysis, defects, informatics and materials discovery via machine learning @jain_computational_2016 (@fig:mindmap).

#figure(
  image("figs/citations.svg"),
  caption: [Citations of #pmg over time.],
) <fig:citations>

== Package Ecosystem

In addition to direct usage for common materials analyses, many packages which are specialised for various computational materials science research areas have built upon the #pmg framework.
A selection of the most popular downstream packages is shown in @fig:dependent-usage-of-pmg, which includes:

+ #link("https://github.com/materialsproject/atomate2")[`atomate(2)`] @mathew_atomate_2017@ganose_atomate2_2025, #link("https://github.com/materialsproject/custodian")[`custodian`], #link("https://quantum-accelerators.github.io/quacc/")[`quacc`] @rosen_quacc_2025: High-throughput computational materials science workflows . 
// `atomate2`, also published in Digital Discovery, demonstrates #pmg's role as a foundational tool for diverse materials science workflows used across the community for high-throughput studies.
+ #link("https://hackingmaterials.lbl.gov/matminer/")[`matminer`] @ward_matminer_2018: Data mining in materials science
+ #link("https://github.com/materialsvirtuallab/pymatgen-analysis-diffusion")[`pymatgen-analysis-diffusion`] @deng_datadriven_2017: Diffusion analysis suite
+ #link("https://doped.readthedocs.io/en/latest/")[`doped`] @kavanagh_doped_2024, #link("https://shakenbreak.readthedocs.io/en/latest/")[`ShakeNBreak`] @mosquera-lois_shakenbreak_2022: Defect modeling and structure-searching, building on #link("https://materialsproject.github.io/pymatgen-analysis-defects")[`pymatgen-analysis-defects`] @shen_pymatgen-analysis-defects_2024 and #link("https://github.com/mbkumar/pycdt")[`PyCDT`] @broberg_pycdt_2018
+ #link("https://pymatviz.janosh.dev/")[`pymatviz`] @riebesell_pymatviz_2022, #link("https://smact.readthedocs.io/en/latest/")[`SMACT`] @davies_smact_2019: Materials informatics toolkits
+ #link("https://matbench-discovery.materialsproject.org/")[`matbench-discovery`] @riebesell_framework_2025, #link("https://www.air4.science/")[`AIRS`] @zhangArtificialIntelligenceScience2025, #link("https://github.com/materialsvirtuallab/matgl")[`matgl`] @ko_materials_2025: Machine learning for materials science
+ #link("https://pyxtal.readthedocs.io/en/latest/")[`PyXtal`] @fredericksPyXtalPythonLibrary2021: Generation and manipulation of atomic structures with symmetry constraints
\

This zoo of downstream packages demonstrates #pmg's extensibility, serving a foundational role in the materials modelling and informatics ecosystems @butler_machine_2018.
Of course, #pmg itself builds on foundational open-source Python packages, such as `numpy`, `scipy` and `pandas` for numerical operations, `matplotlib` for plotting, `spglib` for symmetry analyses and `monty` for serialization, as shown in @fig:pmg-dependency-usage.

#figure(
  image("figs/pmg_dependency_usage.svg"),
  caption: [Usage of 3rd-party dependencies in #pmg modules. Linewidths are scaled by the number of function usages.],
) <fig:pmg-dependency-usage>
#SK[Along with making this 2-columns, need to remove in-figure titles (by cropping?). The text is currently too small; making them wider (to fill the single-column space) will help, in addition to increasing font size (✅) and possibly cutting some of the entries (✅). At the very end, may want to manually edit.]
#figure(
  image("figs/dependent-usage-of-pmg.svg"),
  caption: [Downstream usage of #pmg modules by dependent packages. Linewidths are scaled by the number of function usages.],
) <fig:dependent-usage-of-pmg>

Cumulatively, #pmg's impact on the materials science community includes:

+ Accelerated research across various domains @butler_machine_2018, including the accelerated development of specialised materials analysis toolkits (@fig:dependent-usage-of-pmg).
+ Standardization of core materials analysis procedures.
+ Improved reproducibility, through user-friendly serialization and analysis tools.
+ Provision of accessible educational tools for students and early-career researchers @ong_python_2013, such as https://github.com/materialsvirtuallab/matgenb.
+ Adoption in industrial research and development workflows @jain_commentary_2013.
+ Promotion of open science and collaborative development @horton_promises_2021.

// integration into platforms like the Materials Project, AFLOW, and OQMD @curtarolo_aflow_2012.

== Case Studies
Below, we discuss case studies of advanced materials analyses that the #pmg framework has enabled.

=== Defect Modeling Tools
Defect modeling is a rapidly growing field, driven by advances in computational power and methods that make these calculations tractable, along with the critical importance of defect species to diverse materials technologies, such as transistors, solar cells, transparent conducting materials, batteries, qubits and more. 
Defect simulation can be a long and complex process, however, requiring many different tasks, including structure manipulations, symmetry analyses, input file generation and output parsing for electronic structure codes, lightweight metadata and serialization for reproducibility, and interfaces with databases such as the Materials Project for phase diagram analysis.
Moreover, many of these tasks have specific requirements for the specialized case of defects, such as efficient and appropriate supercell generation (to balance computational cost and accuracy), determination of defect point symmetries, configurational degeneracies and site multiplicities in symmetry-breaking supercells, efficient algorithms for large and complex structure analyses, calculation parameter consistency checks, targeted distortions for structure-searching, smart algorithms for sub-phase diagrams and more.
\ \

Several open-source toolkits have now been developed which make use of core functionalities in #pmg to implement stages of the defect modeling workflow, including `doped` @kavanagh_doped_2024 (@fig:dependent-usage-of-pmg), `pydefect` @kumagai_insights_2021, `PyCDT` @broberg_pycdt_2018, `pymatgen-analysis-defects` @shen_pymatgen-analysis-defects_2024, `ShakeNBreak` @mosquera-lois_shakenbreak_2022, `AiiDA-defects` @muy_aiida-defects_2023 and `pydecs` @ogawa_extended_2022. 
These toolkits are seeing widespread usage in the defects community, helping to accelerate research in this technologically crucial area, along with reducing human errors and lowering the barrier to entry for new researchers.
Here, the wide functionality, along with a flexible and modular code structure, has been a key enabler of these downstream developments, allowing the tailoring of #pmg functions to specialised use cases.
One promising aspect of these developments, is that they have greatly reduced the burden for data sharing and reproducibility in defect simulations – a particularly challenging task given the many steps involved @squiresGuidelinesRobustReproducible2025.
Through the object-oriented architecture and efficient serialization tools provided by #pmg and its `monty` dependency, the human effort to collate and export complete metadata and calculation provenance is significantly diminished.
It is hoped that these developments will establish clear community standards and expectations for reproducibility, strengthening the quality and impact of defect modelling research while ensuring robust foundations for future database and machine learning efforts in this area @squiresGuidelinesRobustReproducible2025.


=== Data-driven Heuristic Assessment and Machine Learning
*@ Janine*
#pmg is a powerful toolkit that enables large-scale data analysis and machine learning studies in materials science. Through its integration with materials databases such as the Materials Project and OPTIMADE, researchers can easily retrieve extensive datasets, including machine learning targets, which serve as the foundation for data-driven assessments and the development of machine learning modules. When working with other sources like ICSD or MAGNDATA, #pmg’s ability to read (magnetic) Crystallographic Information Files (CIFs) facilitates the creation of large, structured datasets.
Many chemical heuristics—such as those related to stability, synthesizability, defect energetics, and magnetism—rely on accurate determinations of oxidation states and coordination environments, which can both be assessed within #pmg. Additionally, #pmg is deeply integrated within matminer, a library that streamlines the generation of popular features for machine learning workflows, further supporting the derivation and validation of heuristics.
In summary, #pmg provides a framework for materials data handling, feature extraction, and heuristic development, making it an essential tool for modern, data-driven materials informatics.

=== Workflow Packages?


= New Features
*@ Aaron*

Recent additions to #pmg include:

+ Enhanced machine learning integration @butler_machine_2018
+ Support for additional DFT and post-processing codes (e.g., FHI-AIMS, LOBSTER @george_automated_2022, Critic2, Phonopy@petretto_highthroughput_2018)
+ Improved structure prediction and analysis algorithms (including magnetic structure) @waroquiers_chemenv_2020 @pan_benchmarking_2021 @horton_highthroughput_2019
+ Advanced battery materials research tools
+ Quantum chemistry code integration
+ Extension packages?

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
*@ Janosh & Matt*

Maintaining and evolving a project of #pmg's scale presents unique challenges that have shaped its development approach.


Key challenges in #pmg's development:

+ Code Maintenance: Implemented comprehensive unit testing and continuous integration @ong_python_2013
+ Performance: Optimized critical paths and used compiled languages for key sections
+ Documentation: Adopted auto-documentation tools and prioritized documentation contributions
+ Compatibility: Implemented cross-platform testing and version management
+ Community Management: Established clear contribution guidelines and regular community meetings

As shown in @fig:pmg-code-structure, #pmg's test coverage varies significantly across its modules. While the most frequently used functionality like `core`, `io`, and `entries` maintain high coverage (>90%), some harder-to-test and/or specialized modules such as visualization (`vis`), certain analysis tools (`boltztrap`), and advanced diffusion features (`neb`) have low coverage (\<20%). This heterogeneity reflects both the maturity of different components and the ongoing challenge of maintaining comprehensive tests for a large, evolving codebase.

*Elaborate on challenges, in context of figures. Solutions? Mention MP foundation?*

#figure(
  image("figs/py-pkg-treemap-pymatgen-coverage.svg"),
  caption: [#pmg code structure and test coverage. The size of each module represents the number of lines of code, while colors indicate test coverage percentage.],
) <fig:pmg-code-structure>

As shown in @fig:pr-since-1st @fig:active-contributors and @fig:contributors-worldmap, the community has grown organically with contributors from around the world, though maintaining consistent development velocity requires dedicated maintainers.

#figure(
  image("figs/pr-since-1st.svg"),
  caption: [Pull requests per contributor since their first contribution.],
) <fig:pr-since-1st>

#figure(
  image("figs/active-contributors-colored.svg"),
  caption: [Active contributors to #pmg over time],
) <fig:active-contributors>

#figure(
  image("figs/pr_contributors_worldmap.svg"),
  caption: [Geographic distribution of #pmg pull request contributors. Note caveats; pulled from GitHub profiles],
) <fig:contributors-worldmap>

Future considerations include integrating Rust components for improved performance while maintaining Python's ease of use @lunnikivi_transpiling_2020.

= Outlook and Future Developments
*@ Janosh & Matt*

#pmg has evolved from a specialized tool into a cornerstone of computational materials science. Its growth reflects the collaborative spirit of the materials informatics community and the importance of open-source software in scientific research @ong_python_2013 @jain_computational_2016.

Future developments may include:

+ Enhanced machine learning and AI support @butler_machine_2018
+ Improved multi-scale modeling support, bridging atomistic and continuum approaches // TODO add ref(s)
+ More user-friendly interfaces and visualization tools (#link("https://github.com/materialsproject/crystaltoolkit")[`crystaltoolkit`] @horton_crystal_2023 #link("https://github.com/janosh/pymatviz")[`pymatviz`] @riebesell_pymatviz_2022 #link("https://github.com/janosh/matterviz")[`matterviz`] @riebesell_matterviz_2025)
+ Performance optimizations through compiled extensions and algorithmic improvements. E.g. exploration of hybrid Python-Rust bindings @lunnikivi_transpiling_2020. // TODO mention moyo as a successful example of this?
+ Docs?
+ (More) Extension packages / support? Reflecting a change in development scope

We remain committed to fostering an open, collaborative environment that drives innovation in computational materials science.

*TODO: Elaborate*
*Reiterate Pymatgen's place in the community*

= Acknowledgments

We thank the numerous developers, researchers, and users who have contributed to #pmg. We also acknowledge the funding agencies and institutions that have supported its development, including the U.S. Department of Energy, the National Science Foundation, and various academic institutions.

Special thanks to the broader open-source scientific computing community for their invaluable tools and libraries, especially NumFocus and their efforts around `numpy` @harris_array_2020, `pandas` @mckinney_data_2010 @team_pandasdev_2025 and `matplotlib` @hunter_matplotlib_2007, all of which #pmg heavily relies on.

ChatGPT was used to improve the language.

#bibliography("refs.bib", style: "ieee")
