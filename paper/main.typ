#import "./template.typ": float, subfigure, template

#let pmg = `pymatgen`
#show link: underline

#let title = "pymatgen: A decade of community growth, new functionality, and future prospects"


// TODO think about concluding/outlook/perspective paragraphs at the end of each subsection

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
We present the second major release of the Python Materials Genomics (#pmg) library, reflecting on a decade of community growth and established best practices. This version builds on #pmg's robust, open-source foundation, emphasizing its collaborative nature. Over the past decade, #pmg has thrived as one of the largest open-source materials science codebases. We detail how #pmg aids modern computational materials science, its adaptation to changing demands, and lessons learned from its growing community.
#pmg will continue to evolve based on current developments and requirements in the rapidly changing landscape of computational materials science and materials informatics.
We discuss the challenges and potential solutions to managing the community-driven evolution of #pmg, providing an outlook on its future development.
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
#align(center, image("figs/pymatgen-2-logo.pdf", width: 20%))


// Notes from May 16
// = List of Figures (6 max allowed in DD)

// // Issues have been added to repo to track figure progress
// 1. Community usage of pymatgen. Filter a list of downstream packages via GitHub (tree structure? graph?) - get year of first commit, show growth over time. OpenAlex - retrieve citing articles, sort by citations, topics (https://openalex.org/works?page=1&filter=cites%3Aw2015197254). Show community beyond solid state (MOF)?
// 2. pymatgen layout + pymatgen add-on packages (https://github.com/janosh/pymatviz?tab=readme-ov-file#treemap)
// 3. Functionality figure (existing data): centered around composition, chemical space, crystal structure - interface generation, defects, phase diagram, magnetism (spin), tensor operations(how?), k-path, lattice?
// 4. Contributors (anonymized, over time, e.g. LOC or num PRs, num comments, num of contributors per module)


// TODOs
// Sustainability section?
// * Discuss code standards (+ also challenges, evolving best practices balanced with backwards compat, funding, maintenance vs new features, churn and people leaving and joining, incentives to document + structured documentation)
// * Test coverage https://app.codecov.io/gh/materialsproject/pymatgen/tree/master/pymatgen (trade-off between test coverage and choice of tests)
// * Highlight uniqueness in cover letter (not many codes developed over ten+ years!)

= Introduction
*@ Janine*


#figure(
  image("figs/mindmap.pdf"),
  caption: [#pmg functionality grouped into research topics, colored by number of papers in each topic citing #pmg.],
) <fig:mindmap>

Since 2011, #pmg has enabled both individual and high-throughput computational materials science efforts @ong_python_2013. It started as a central code in the Materials Project@jain_commentary_2013 and nowadays provides tools for setup and analysis of materials simulations, and interfaces to various materials science codes. #pmg stands out for its exceptionally broad range of analysis capabilities across elemental, compositional, crystallographic, and material property levels. The library has grown significantly through community efforts, adapting to expanding needs in the fields of materials informatics @butler_machine_2018 and computational materials science. Due to its broad capabilities, #pmg is used in diverse research areas spanning from battery materials to machine learning applications, as shown in @fig:mindmap.


After more than 14 years of development, we review the evolution and impact of #pmg, sharing challenges and solutions encountered during its growth. We furthermore highlight factors that established #pmg as a cornerstone of materials science software. This retrospective could also serve as a guiding example for other community codes in the materials science domain. Lastly, we outline future developments.


//*Pymatgen's place in the community* (I hope I covered it)

= Overview and Design Principles
*@ Janine*
== Background

#pmg was developed in 2011 by Shyue Ping Ong and colleagues at MIT to support the Materials Project @ong_python_2013 @jain_commentary_2013. Initially, #pmg provided essential tools for crystallographic operations, symmetry analysis, integration with the Vienna _Ab Initio_ Simulation Package (VASP) density functional theory (DFT) code @kresse_efficient_1996 and basic electronic structure and phase diagram analysis. These foundational capabilities enabled researchers to automate and standardize many aspects of computational materials science, laying the groundwork for high-throughput materials discovery. Many of these efforts were linked to the development of the Materials Project. @jain_commentary_2013 @horton_accelerated_2025


Since then, #pmg has expanded significantly, incorporating new features and adapting to the evolving landscape of materials informatics @butler_machine_2018. Key trends shaping its development include:

+ The growing importance of research data management
+ The rise of automated workflows for reproducible simulations and experiments
+ Increasing use of machine learning for materials property prediction
+ Greater availability of computational resources, enabling more complex analyses, machine learning tasks, and simulations

//#pmg is an open-source Python library for materials analysis, offering tools from basic crystallographic operations to complex electronic structure analysis @ong_python_2013 @jain_commentary_2013. Key features include:

Today, #pmg aims to accelerate materials discovery by providing a comprehensive toolkit for researchers at all levels @curtarolo_highthroughput_2013. While #pmg’s original goals—such as crystallographic operations and electronic structure analysis—remain central, its capabilities have grown substantially to support a broad spectrum of tasks in computational materials science and materials informatics. #pmg offers powerful tools for crystallographic and structural analysis, including coordination environment analysis, electronic structure parsing, thermodynamic and phase diagram construction, analysis of phonon properties, and interfaces to  various DFT codes. Additionally, it includes utilities for machine learning applications in materials property prediction @ward_matminer_2018, reflecting its evolution into a comprehensive platform for materials informatics. #pmg therefore aims to be a powerful, flexible, and reliable software tool @horton_promises_2021, in the growing complexity of computational materials science and materials informatics.

// I had a language bug here. I used "is integrated with" in the wrong way. It wasn't that I did not know what was integrated with what but rather I somehow used the phrase incorrectly. I think the with threw me off. Sorry. Should be correct now.

== Interoperability and Comparative Tools

One of #pmg's strengths is its interoperability, as it has the capability to read various molecule and structure file formats and to retrieve molecules and structures from databases. Furthermore, #pmg provides interfaces to DFT codes (e.g., VASP, Quantum Espresso) or post-processing tools, such as `Phonopy`.
#pmg also complements other materials science tools, most notably the Atomic Simulation Environment (ASE) @larsen_atomic_2017. While both software packages offer parsers for DFT and quantum chemistry codes, as well as tools for structure and molecule manipulation, their focuses differ. #pmg centers on materials data analysis,@jain_computational_2016 supporting tasks from oxidation state prediction to thermal conductivity modeling. ASE emphasizes simulation workflows, integrating quantum-chemical calculators and molecular dynamics. The two are thus complementary and often used together. To streamline the usage of both codes, #pmg makes it possible to convert between the #pmg `Structure` object representation of a material and the ASE `Atoms` object representation.

// Maybe rephrase to be a bit more succinct in comparing pymatgen and ASE
// Again, I tried. I hope I succeeded

= Community Adoption and Impact
*@ Seán*

The growth of #pmg is reflected not only in its feature set but also in its expanding user base and community engagement. Steady growth in downloads and the number of packages requiring #pmg as a dependency over time are evidence of widespread and increasing adoption across the materials science community. Indeed, #pmg has been cited over 4000 times since 2013 @ong_python_2013 (@fig:citations) and is poised to reach over 1000 citations in 2025 alone.
// , with usage spanning:
// + Materials Project research: Large-scale materials analysis and property prediction @jain_commentary_2013.
These usages span diverse fields, including energy storage and conversion, catalysis, defects, informatics and materials discovery via machine learning @jain_computational_2016 (@fig:mindmap).

#figure(
  image("figs/citations.pdf"),
  caption: [Citations of #pmg over time.],
) <fig:citations>

== Package Ecosystem


In addition to direct usage for common materials analyses, many packages which are specialized for various computational materials science research areas have built upon the #pmg framework.
A selection of the most popular downstream packages is shown in @fig:dependent-usage-of-pmg, which includes:

+ #link("https://github.com/materialsproject/atomate2")[`atomate(2)`] @ganose_atomate2_2025, #link("https://github.com/materialsproject/custodian")[`custodian`], #link("https://quantum-accelerators.github.io/quacc/")[`quacc`] @rosen_quacc_2025: High-throughput computational materials science workflows.
// `atomate2`, also published in Digital Discovery, demonstrates #pmg's role as a foundational tool for diverse materials science workflows used across the community for high-throughput studies.
+ #link("https://hackingmaterials.lbl.gov/matminer/")[`matminer`] @ward_matminer_2018: Data mining in materials science
+ #link("https://github.com/materialsvirtuallab/pymatgen-analysis-diffusion")[`pymatgen-analysis-diffusion`] @deng_datadriven_2017: Diffusion analysis suite *-- TODO: Fuse with later discussion of extension/namespace packages*
+ #link("https://doped.readthedocs.io/en/latest/")[`doped`] @kavanagh_doped_2024, #link("https://shakenbreak.readthedocs.io/en/latest/")[`ShakeNBreak`] @mosquera-lois_shakenbreak_2022: Defect modeling and structure-searching, building on #link("https://materialsproject.github.io/pymatgen-analysis-defects")[`pymatgen-analysis-defects`] @shen_pymatgen-analysis-defects_2024 and #link("https://github.com/mbkumar/pycdt")[`PyCDT`] @broberg_pycdt_2018
+ #link("https://pymatviz.janosh.dev/")[`pymatviz`] @riebesell_pymatviz_2022, #link("https://smact.readthedocs.io/en/latest/")[`SMACT`] @davies_smact_2019: Materials informatics toolkits
+ #link("https://matbench-discovery.materialsproject.org/")[`matbench-discovery`] @riebesell_framework_2025, #link("https://www.air4.science/")[`AIRS`] @zhangArtificialIntelligenceScience2025, #link("https://github.com/materialsvirtuallab/matgl")[`matgl`] @ko_materials_2025, #link("https://github.com/Radical-AI/torch-sim")[`torch-sim`] @cohen_torchsim_2025: Machine learning for materials science
+ #link("https://pyxtal.readthedocs.io/en/latest/")[`PyXtal`] @fredericksPyXtalPythonLibrary2021: Generation and manipulation of atomic structures with symmetry constraints
+ #link("https://jageo.github.io/LobsterPy/")[`LobsterPy`]: @naik_LobsterPypackage_2024 Automatic analysis of `LOBTSER` outputs for summarized bonding information.
\

This diversity of downstream packages demonstrates #pmg's extensibility, serving a foundational role in the materials modeling and informatics ecosystems @butler_machine_2018.
Of course, #pmg itself builds on foundational open-source Python packages, such as `numpy` @harris_array_2020, `scipy` @virtanen_scipy_2020, and `pandas` @team_pandasdev_2025 @mckinney_data_2010 for numerical operations, `matplotlib` @hunter_matplotlib_2007 for plotting, `spglib` @togo2024spglib for symmetry analyses and `monty` for serialization, as shown in @fig:package-ecosystem.

#place(top + center, float: true, scope: "parent")[
  #figure(
    {
      grid(
        columns: 2,
        gutter: 2em,
        subfigure(
          pad(left: -5em, image("figs/pmg-dependency-usage.pdf")),
          caption: [Usage of 3rd-party Python packages in #pmg.],
          dy: -1em,
          label: <fig:pmg-dependency-usage>,
        ),
        subfigure(
          pad(right: -5em, image("figs/dependent-usage-of-pmg.pdf")),
          caption: [Downstream usage of #pmg modules by dependent packages.],
          dy: 3pt,
          label: <fig:dependent-usage-of-pmg>,
        ),
      )
      place(center + horizon, dy: -5%, image("figs/pymatgen-2-logo.pdf", width: 8em))
    },
    caption: [Package dependency ecosystem. Linewidths are scaled by the number of function usages.],
  ) <fig:package-ecosystem>
]

Cumulatively, #pmg's impact on the materials science community includes:

+ Accelerated research across various domains @butler_machine_2018, including the accelerated development of specialized materials analysis toolkits (@fig:dependent-usage-of-pmg).
+ Standardization of core materials analysis procedures.
+ Improved reproducibility, through user-friendly serialization and analysis tools.
+ Provision of accessible educational tools for students and early-career researchers @ong_python_2013, such as https://github.com/materialsvirtuallab/matgenb and https://github.com/sp8rks/MaterialsInformatics.
// Andrew notebook potentially live soon
+ Adoption in industrial research and development workflows @jain_commentary_2013.
+ Promotion of open science and collaborative development @horton_promises_2021.

// integration into platforms like the Materials Project, AFLOW, and OQMD @curtarolo_aflow_2012.
// SK: Well it's that pymatgen's API can be used with these material databases (except ofc Materials Project which it supports/'is integrated to')

== Case Studies
Below, we discuss case studies of advanced materials analyses that the #pmg framework has enabled.

=== Defect Modeling Tools
Defect modeling is a rapidly growing field, driven by advances in computational power and methods that make these calculations tractable, along with the critical importance of defect species to diverse materials technologies, such as transistors, solar cells, transparent conducting materials, batteries, qubits and more.
Defect simulation can be a long and complex process, however, requiring many different tasks, including structure manipulations, symmetry analyses, input file generation and output parsing for electronic structure codes, lightweight metadata and serialization for reproducibility, and interfaces with databases such as the Materials Project for phase diagram analysis.
Moreover, many of these tasks have specific requirements for the specialized case of defects, such as efficient and appropriate supercell generation (to balance computational cost and accuracy), determination of defect point symmetries, configurational degeneracies and site multiplicities in symmetry-breaking supercells, efficient algorithms for large and complex structure analyses, calculation parameter consistency checks, targeted distortions for structure-searching, smart algorithms for sub-phase diagrams and more.

Several open-source toolkits have now been developed which make use of core functionalities in #pmg to implement stages of the defect modeling workflow, including `doped` @kavanagh_doped_2024 (@fig:dependent-usage-of-pmg), `pydefect` @kumagai_insights_2021, `PyCDT` @broberg_pycdt_2018, `pymatgen-analysis-defects` @shen_pymatgen-analysis-defects_2024, `ShakeNBreak` @mosquera-lois_shakenbreak_2022, `AiiDA-defects` @muy_aiida-defects_2023 and `pydecs` @ogawa_extended_2022.
These toolkits are seeing widespread usage in the defects community, helping to accelerate research in this technologically crucial area, along with reducing human errors and lowering the barrier to entry for new researchers.
Here, the wide functionality, along with a flexible and modular code structure, has been a key enabler of these downstream developments, allowing the tailoring of #pmg functions to specialized use cases.
One promising aspect of these developments, is that they have greatly reduced the burden for data sharing and reproducibility in defect simulations---a particularly challenging task given the many steps involved @squiresGuidelinesRobustReproducible2025.
Through the object-oriented architecture and efficient serialization tools provided by #pmg and its `monty` dependency for (de)serialization, the human effort to collate and export complete metadata and calculation provenance is significantly diminished.
It is hoped that these developments will establish clear community standards and expectations for reproducibility, strengthening the quality and impact of defect modeling research while ensuring robust foundations for future database and machine learning efforts in this area @squiresGuidelinesRobustReproducible2025.

// + (If we want a figure here, could make a diagram showing the workflow: Pull materials from MP -> Oxi-state Guess w/PMG -> Vacancy generation w/`doped` (via PMG etc) -> Electrostatic analysis with PMG (Ewald tools) -> VASP DFT I/O w/PMG -> Energetic & Structural (w/`doped` & PMG) analysis; from 10.1088/2515-7655/ade916, as example).

=== Data-Driven Heuristic Assessment and Machine Learning
*@ Janine*

#pmg is a powerful toolkit that enables large-scale data analysis and machine learning studies in materials science. These are typical tasks required when finding new design principles for certain materials properties or when developing feature-based machine learning models. The latter is frequently a core component in Materials Acceleration Platforms or self-driving labs.@stier_materials_2024
Through #pmg's direct interfaces to material databases (Materials Project API or OPTIMADE API @andersen2021optimade), researchers can easily retrieve extensive datasets, including machine learning targets, which serve as the foundation for data-driven assessments of design principles and heuristics and the development of machine learning models. When working with other crystal structure sources such as the Cambridge Structural Database @groom2016cambridge, Inorganic Crystal Structure Database @zagorac2019recent or MAGNDATA @gallego2016magndata, #pmg’s ability to read (magnetic) Crystallographic Information Files (CIFs) facilitates the creation of large, structured datasets. #pmg allows simplified filtering by composition or crystal symmetry, depending on requirements. Additionally, many post-processing features exist in pymatgen as well, enabling simpler generation of targets.

Chemical heuristics have been frequently used to inspire design principles or features in machine learning models. Many of them—such as those related to stability, synthesizability, defect energetics, and magnetism—rely on accurate determinations of oxidation states and coordination environments, which can both be assessed within #pmg.@george_limited_2020 @ueltzen_can_2025 #pmg implements several heuristics to determine oxidation states (e.g., based on bond valence sums or simple composition-based guessing methods) and to determine coordination environments (e.g., based on minimum distances or Hoppe's effective coordination numbers)@pan_benchmarking_2021, @waroquiers_chemenv_2020. Additionally, #pmg is deeply integrated within matminer, a library that streamlines the generation of popular features for machine learning workflows, further supporting the derivation and validation of heuristics. Here, #pmg formats are directly used as an input for creating machine-learning features.
In summary, #pmg provides a framework for materials data handling, feature extraction, and heuristic development, making it an essential tool for modern, data-driven materials informatics.

= New Features
*@ Aaron*

The growth of #pmg closely follows trends in materials science research, reflecting its critical role in advancing science.

Modeling of Li- and Co-alternative battery electrodes has long driven atomistic analysis tools in #pmg.
The `pymatgen-analysis-diffusion` extension @shen_topological_2023 grew out of a smaller submodule of diffusivity analysis tools which were eventually migrated to a separate namespace package.
These tools enable faster estimates of ionic mobility from molecular dynamics trajectories.
They also include tools to identify likely topotactic ion insertion defect sites based on electronic charge densities @shen_charge_2020, used when estimating ionic mobility from transition-state type mappings of the potential energy surface.

More recently, machine learning (ML) methods @butler_machine_2018, particularly ML interatomic potentials (MLIPs) @chen_universal_2022, have emerged as practical ways to rapidly estimate atomic structure without more costly recourse to electronic structure methods.
#pmg has integrated some of these structural prediction tools via the external `matgl` python package @ko_materials_2025.
This allows users to, e.g., quickly relax crystal structures using common graph neural-network MLIPs such as M3GNet @chen_universal_2022, CHGNet @deng_chgnet_2023, and TensorNet @simeon_tensornet_2023.
MLIPs can also be directly used in #pmg to estimate small-cell ordered representations of disordered materials by enumeration of ordered representation, and selecting the minimum energy configuration.

Analysis of local coordination environments has also been of critical importance in understanding the roles of atomic and electronic structure shape materials characteristics.
These insights help identify structural motifs that lead to similar performance, e.g., frameworks which favor ionic mobility.
#pmg aids in analysis of electronic charge densities and electronic bonding by interfacing with LOBSTER @nelson_lobster_2020.
#pmg makes possible analysis of local atomic coordination environments using the ChemEnv @waroquiers_chemenv_2020 and CrystalNN @zimmermann_crystalnn_2020 methods, among others.
CrystalNN can be further used to generate structural embeddings similar to the feature vectors of MLIPs, which in turn allow for rapid estimates of structural similarity @zimmermann_fingerprint_2020 and automatic generation of human-readable descriptions of materials with the `robocrys` package @ganose_robocrys_2019.
Local coordination environment analysis from ChemEnv, CrystalNN similarity estimates, and CrystalNN-based generated descriptions of materials are now standard analysis products of the Materials Project's build pipelines, and are currently distributed as part of its core data.

Other extensions to #pmg which can be separately installed under the `io` and `analysis` namespaces include, but are not limited to: validation of VASP @kresse_ultrasoft_1999 calculations for compatibility with the Materials Project @horton_accelerated_2025 via `pymatgen-io-validation`; orchestration and parsing of FHI-aims @blum_fhiaims_2009, Quantum Espresso @giannozzi_qe_2017, and FLEUR @wortmann_fleur_2023 electronic structure calculations via `pymatgen-io-aims`, `pymatgen-io-espresso`, and `pymatgen-io-fleur`, respectively; orchestration of classical molecular dynamics calculations with OpenMM @eastman_openmm_2023 via `pymatgen-io-openmm`; orchestration of insertion defect electronic structure calculations with `pymatgen-analysis-defects` @shen_pmgdefects_2024.
A more complete list of extensions to #pmg is maintained in the add-ons section of the documentation.

// Recent additions to #pmg to include:

// + Enhanced machine learning integration @butler_machine_2018
// + Support for additional DFT and post-processing codes (e.g., FHI-AIMS, LOBSTER @george_automated_2022, Critic2, Phonopy@petretto_highthroughput_2018)
// + Improved structure prediction and analysis algorithms (including magnetic structure) @waroquiers_chemenv_2020 @pan_benchmarking_2021 @horton_highthroughput_2019
// + Advanced battery materials research tools
// + Quantum chemistry code integration
// + Extension packages?

As illustrated in @fig:pr-topics and @fig:commits-heatmap, the development activity has been sustained across multiple subpackages, with contributions spanning bug fixes, new features, and performance improvements.

#place(top + center, float: true, scope: "parent")[
  #figure(
    grid(
      columns: (1fr, 2fr),
      gutter: 1em,
      subfigure(
        pad(x: -1em, image("figs/pr-topics-over-time-stacked-bar.pdf")),
        caption: [Pull request topics over time in the pymatgen repository.],
        dy: 12%,
        label: <fig:pr-topics>,
      ),
      subfigure(
        pad(x: -1em, image("figs/commits-per-package-heatmap.pdf")),
        caption: [Monthly commits per pymatgen subpackage (heatmap).],
        label: <fig:commits-heatmap>,
      ),
    ),
    caption: [Development activity in the pymatgen repository over time.],
  ) <fig:development-activity>
]

//Case study: Battery materials research with #pmg

//#pmg offers tools for:
//- Voltage calculation
//- Diffusion analysis @deng_datadriven_2017
//- Electrode stability prediction // TODO add ref(s)


= Challenges and Solutions

Maintaining and evolving a project of #pmg's scale over more than a decade presents unique challenges that offer valuable lessons for the broader scientific software community. We discuss key challenges encountered and the possible solutions to address them.

== Sustainability and Maintainer Resources
Janosh: adds section on commit and motivation for it


Perhaps the most critical challenge facing long-lived open-source scientific software is sustainability. Unlike commercial software with dedicated development teams, #pmg has evolved primarily through volunteer contributions from academic researchers, where software development competes with research publications, teaching, and other career pressures. This model, while fostering community ownership, creates inherent tensions around maintenance, code review capacity, and long-term feature development.

The Materials Project has provided crucial institutional support, offering paid developer time, computational resources, and organizational infrastructure. This hybrid model (combining institutional backing with community contributions) has proven essential for #pmg's longevity. Yet acquiring funding for software maintenance remains challenging, as grant agencies strongly favor novel research over infrastructure upkeep. Projects like FAIRmat @fairmat_web_2025, as part of the German national research data infrastructure, and the Molecular Sciences Software Institute (MolSSI) @molssi_web_2025 represent important steps toward recognizing computational infrastructure as a research infrastructure deserving sustained investment.

As shown in @fig:pr-since-1st and @fig:contributors-worldmap, #pmg has cultivated a globally distributed contributor base which affords some amount of resilience to changing resource situations at any one institution. However, the concentration of maintenance burden on a small number of core developers remains an ongoing concern. We hope that clear contribution guidelines, responsive code review, and explicit recognition of contributors (through authorship opportunities, acknowledgments in papers, and community visibility) can help sustain engagement and grow the pool of active maintainers.

== Backwards Compatibility and API Evolution

A fundamental tension in mature software libraries is balancing API stability for existing users against the need for improvements and corrections. #pmg has accumulated substantial technical debt from early design decisions made before certain use cases were anticipated. For example, in some cases, the classes to parse ab initio code outputs are used to return objects representing electronic structure properties (```
io.vasp.outputs.Vasprun.complete_dos
```). In other cases, the classes representing electronic structure properties can be used to parse such files (e.g., ```
electronic_structure.cohp.CompleteCohp.from_file()
```). This leads to inconsistencies in the API logic.
The development of #pmg has generally sought to avoid breaking changes to minimize downstream impact on its end users, thereby allowing for extensive deprecation periods when a breaking change to the API is planned.
These choices follow best practices established in other open-source software libraries.

== Test Coverage and Code Quality

As shown in @fig:pmg-code-structure, #pmg's test coverage varies significantly across its modules. While the most frequently used functionality like `core`, `io`, and `entries` maintain high coverage (>90%), some harder-to-test and/or specialized modules such as visualization (`vis`), certain analysis tools (`boltztrap`), and advanced diffusion features (`neb`) have low coverage (\<20%). This heterogeneity reflects both the maturity of different components and the ongoing challenge of maintaining comprehensive tests for a large, evolving codebase.

This heterogeneity is not merely neglect but reflects genuine trade-offs. Some modules require external executables and/or long-running operations for meaningful testing, making comprehensive continuous integration (CI) difficult. Visualization code often requires rendering backends that complicate automated testing. #pmg has focused testing resources on core modules that attract the largest user bases, accepting lower coverage for specialized and infrequently used features.

Continuous integration via GitHub Actions, along with tools like `pytest`, `coverage.py`, `ruff` (for linting) and `ty` for type checking, form the backbone of our quality assurance. Pre-commit hooks automate formatting and catch common issues before review. However, the test suite's growing execution time creates friction for contributors. Some efforts need to be directed towards improving test efficiency and parallelization beyond the current use of `pytest-split` spreading tests across multiple 4 concurrent runners.

== Governance and Contributor Onboarding

// @Aaron
// Shyue may not like this section at all. What I have here is the perspective of MP / MPSF

As a core component of the Materials Project's analysis tools, #pmg is governed according to principles established by the Materials Project stakeholders, which are in turn inspired by the best practices adopted by established community organizations like Numpy @harris_array_2020 and NumFOCUS.
Collectively, the MP members and MP software stakeholders which are responsible for the adoption and enforcement of codes of conduct are known as the Materials Project Software Foundation (MPSF).
MPSF works to democratically establish a governance structure for MP's software ecosystem and has, e.g., ensured the inclusion of MP software in the NumFOCUS foundation index.

These codes of conduct ensure a welcoming environment for new contributors, with the goal of fostering longer term community engagement that in turn benefits #pmg.
As #pmg continues to expand in scope beyond the means of a small team of core maintainers, community engagement in maintaining its more niche feature sets is imperative.
Ensuring that new contributors feel welcome in engaging with the development of #pmg then helps ensure its longevity.

As more junior community maintainers contribute to #pmg, they will eventually be invited to take on maintainer roles for sections of #pmg.
Junior maintainers who express interest in maintaining the core feature set will be deputized by more experienced maintainers to handle quotidian maintenance.
This simultaneously ensures that community-submitted issues are addressed in a timely fashion, and that more experienced maintainers can address larger questions of software direction, optimization, etc.
Because the analysis tools of #pmg are integral to MP's workflows and data pipelines, these features are virtually guaranteed to be maintained as long as MP continues its mission.
However, the more peripheral features of #pmg will require this kind of community-driven maintenance structure to prevent them becoming vaporware.

== Dependencies and Dependents
TODO: extend?

As discussed in previous sections, a large ecosystem of material science codes depends on #pmg (see package ecosystem and Figure 3b).
However, #pmg also depends on the Python ecosystem for scientific computing, plotting and data science (Figure 3a). This includes numpy,  scipy, matplotlib, plotly, pandas and sympy. networkx supports graph-based analysis within #pmg. For serialization, #pmg, for example, uses monty and orjson. Monty itself has been developed to support pymatgen in such tasks.

#place(top + center, float: true, scope: "parent")[
  #figure(
    pad(right: -2em, image("figs/py-pkg-treemap-pymatgen-coverage.pdf")),
    caption: [#pmg code structure and test coverage. The size of each module represents the number of lines of code, while colors indicate test coverage percentage.],
    // TODO: check that the namespace add-ons (pymatgen-io-espresso, pymatgen-analysis-diffusion, and pymatgen-analysis-defects are being accounted for correctly in test coverage)
  ) <fig:pmg-code-structure>
]

#figure(
  image("figs/pr-since-1st.pdf"),
  caption: [Pull requests per contributor since their first contribution.],
) <fig:pr-since-1st>

#figure(
  image("figs/active-contributors-colored.pdf"),
  caption: [Active contributors to #pmg over time – SK: Could potentially cut, somewhat duplicating info from other figures],
) <fig:active-contributors>

#place(top + center, float: true, scope: "parent")[
  #figure(
    pad(x: -3em, top: -2em, bottom: -5em, image("figs/pr-contributors-worldmap.pdf")),
    caption: [Geographic distribution of #pmg pull request contributors. Note caveats; pulled from GitHub profiles],
  ) <fig:contributors-worldmap>
]

Future considerations include performance improvements in the #pmg core submodule, as well as for submodules for interoperability with electronic structure codes.
These improvements may require partial rewriting of code with compiled languages, or partitioning into namespace modules.
This latter approach has already been taken with the `analysis` and `io` namespaces of #pmg, which permit integration with external python libraries with more niche functionality.
// Future considerations include integrating Rust components for improved performance while maintaining Python's ease of use @lunnikivi_transpiling_2020. // is this fine with all maintainers?
// JR: rust migration is probably a personal hobby horse of mine and something Shyue would reject outright...
// AK: Rewrote to make it more generic

= Outlook and Future Developments

#pmg has evolved from a specialized tool into a cornerstone of computational materials science. Its growth reflects the collaborative spirit of the materials informatics community and the importance of open-source software in scientific research.

While the core features of pymatgen are relatively stable, more peripheral features require constant community review beyond the stewardship of a small team of maintainers.
Improving performance of the most essential #pmg libraries is key to its growth.
Division of #pmg into namespaces, with separately installable #pmg`-core` and `-io` namespace modules, would greatly help this goal.

At its current scope, the feature set of #pmg is beyond the expertise of any one person and would ideally require a larger team for maintenance.
The development team will try to use its standing in the community to better assign maintenance tasks, such as code review, issue closure, and bug fixes, for more niche submodules of #pmg.
This will also ensure that a new group of active users are included in the development process of #pmg, ensuring its constant stewardship.
As newer deputy code reviewers gain experience, they can also rise to fill maintainer roles.

There are many active areas of materials science which could benefit from extensions of #pmg key feature set.
These include a wider variety and depth of control for `io` extensions to popular electronic structure (e.g., Quantum Espresso), atomistic (e.g., LAMMPS, GROMACS), and continuum, phase field, and multiphysics codes.
However, as noted previously, any extension of functionality that is not in a separately-installable namespace would require concomitant community review.

While community fora such as `matsci.org` exist alongside the issue tracker for #pmg, the documentation of #pmg is very sparse given its breadth.
We plan to use large language models with review from the user community to generate better documentation.

Future development priorities informed by community needs and emerging trends in materials science include:

*Machine learning integration* will be important as ML methods increasingly enter materials discovery and design @butler_machine_2018. Future development should emphasize native support for modern frameworks (PyTorch, JAX) and efficient structure-to-graph conversions for neural network architectures. Better integration with benchmarking frameworks like Matbench Discovery @riebesell_framework_2025 will standardize evaluation and accelerate method development.

*Visualization and user experience* improvements through tighter integration with `crystal-toolkit` @horton_crystal_2023, `pymatviz` @riebesell_pymatviz_2022, and `matterviz` @riebesell_matterviz_2025 will lower barriers to entry. Enhanced Jupyter notebook support, interactive structure manipulation, and publication-ready figure generation remain priorities.

*Performance optimizations* will target bottlenecks through strategic use of compiled extensions. The `moyo` project demonstrates successful Rust migration of symmetry analysis while maintaining an easy-to-use Python API via bindings. Similar approaches could accelerate oft-used compute-intensive operations such as structure matching, neighbor searching, convex hull calculations, and more. Meanwhile Python's new and improved no-GIL (global interpreter lock) multi-processing available from Python 3.14+ could serve as a middle ground, enabling faster processing of large datasets without the need to rewrite in compiled languages.

*Extension package ecosystem* growth will strengthen #pmg's federated architecture: a stable core supplemented by domain-specific namespace packages (e.g., `pymatgen-analysis-diffusion` @deng_datadriven_2017, `pymatgen-analysis-defects` @shen_pymatgen-analysis-defects_2024) maintained by experts. Increasing the number and quality of these extensions distributes maintenance burden while enabling rapid iteration in specialized domains. New functionality areas—such as multi-scale modeling bridging atomistic and mesoscale simulations—are best developed as extension packages rather than expanding the core.

We invite contributions at all levels---from bug reports and documentation improvements to new features and extension packages. The project's GitHub repository, documentation site, and community forums provide entry points for new contributors.

= Acknowledgments

We thank the numerous developers, researchers, and users who have contributed to #pmg. We also acknowledge the funding agencies and institutions that have supported its development, including the U.S. Department of Energy, the National Science Foundation, and various academic institutions.

Special thanks to the broader open-source scientific computing community for their invaluable tools and libraries, especially NumFocus and their efforts around `numpy` @harris_array_2020, `pandas` @mckinney_data_2010 @team_pandasdev_2025 and `matplotlib` @hunter_matplotlib_2007, all of which #pmg heavily relies on.

ChatGPT was used to improve the language and to make additional literature queries. Everything was checked carefully afterwards.

#bibliography("refs.bib", style: "ieee")
