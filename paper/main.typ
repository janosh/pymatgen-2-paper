#import "./template.typ": float, subfigure, template

#let pmg = `pymatgen`
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
      We present a retrospective on the Python Materials Genomics (#pmg) library, reflecting on a decade of community growth and established best practices. This version builds on #pmg's robust, open-source foundation, emphasizing its collaborative nature. Over the past decade, #pmg has thrived as one of the largest open-source materials science codebases. We detail how #pmg aids modern computational materials science, its adaptation to changing demands, and lessons learned from its growing community.
      #pmg will continue to evolve based on current developments and requirements in the rapidly changing landscape of computational materials science and materials informatics.
      We discuss the challenges and potential solutions to managing the community-driven evolution of #pmg, providing an outlook on its future development.
    ],
    (
      title: "Plain Language Abstract",
      content: [#pmg is an open-source Python library that helps materials scientists analyze crystal structures, run computational simulations, and discover new materials. Over 14 years of development, it has grown into one of the most widely used tools in the field, with contributions from hundreds of researchers worldwide. This paper reviews how #pmg has evolved, the challenges of maintaining large community-driven scientific software, and where the project is headed next.],
    ),
  ),
  venue: [_Digital Discovery_],
  header: (
    article-color: rgb("#364f66"),
    article-type: "Preprint",
    article-meta: [Not Peer-Reviewed],
  ),
  // MH: we have plenty of time to figure out author list - still want to focus on content -
  //     but I would like us to consider Janine as first author since Janine has really driven
  //     this paper development and would not have happened without her diligent efforts. Maybe
  //     the team can share a co-author credit with a to-be-determined author ordering after this?
  // MH: also left a comment that I need to reach out to folks who were invited to participate the
  //     first time I tried to kick-off this paper ~2 yrs ago. I want to make sure they know they
  //     were not forgotten and have opportunity to provide input.

  // JG: I am completely fine with being one of the first authors. I think this reflects the work that we have done here much better. I think the paper wouldn't have been possible without all of your contributions (figures, code, draft)!
  // My main wish is that we finally get it done and then provide easy options for future updates!
  authors: (
    (name: "Janine George", corresponding: false),
    (name: "Matthew Horton", corresponding: false),
    (name: "Seán Kavanagh", corresponding: false),
    (name: "Aron Kaplan", corresponding: false),
    (name: "Janosh Riebesell", corresponding: false),
    (name: "Andrew S. Rosen", corresponding: false),
    (name: "Haoyu Yang", corresponding: false),
    (name: "***", corresponding: false),
  ), // indicate that all of them are co-first authors
  // affiliations: affiliations,
  dates: (
    (type: [Received Date], date: datetime.today()),
    (type: [Revised Date], date: datetime.today()),
    (type: [Accepted Date], date: datetime.today()),
  ),
  doi: "00.0000/XXXXXXXXXX",
  citation: [MP et al., _Digital Discovery_, 2026, *1*, 1---2],
)
//#align(center, image("figs/pymatgen-2-logo.pdf", width: 20%))


// Notes from May 16
// = List of Figures (6 max allowed in DD)

// TODOs
// Sustainability section?
// * Discuss code standards (+ also challenges, evolving best practices balanced with backwards compat, funding, maintenance vs new features, churn and people leaving and joining, incentives to document + structured documentation)
// * Test coverage https://app.codecov.io/gh/materialsproject/pymatgen/tree/master/pymatgen (trade-off between test coverage and choice of tests)
// * Highlight uniqueness in cover letter (not many codes developed over ten+ years!)

// * Check Digital Discovery rules on hyperlinks - raised by SK [Feb 2026]


// Lessons learned to each section: structures the paper -> everyone
= Introduction
// *@ Janine* *@ Matt*


#figure(
  image("figs/mindmap.pdf"),
  caption: [#pmg functionality grouped into research topics, colored by number of papers in each topic citing #pmg.],
) <fig:mindmap>

Since 2011, #pmg has enabled both individual and high-throughput computational materials science efforts @ong_python_2013. It started as a central code in the Materials Project @jain_commentary_2013 and nowadays provides many tools for setup and analysis of materials simulations, along with interfaces to various materials science codes. #pmg stands out for its exceptionally broad range of analysis capabilities across elemental, compositional, crystallographic, and material property levels. The library has grown significantly through community efforts, adapting to expanding needs in the fields of materials informatics @butler_machine_2018 and computational materials science. Due to its broad capabilities, #pmg is used in diverse research areas spanning from battery materials to machine learning applications, as shown in @fig:mindmap.


After more than 14 years of development, we review the evolution and impact of #pmg, sharing challenges and solutions encountered during its growth. We furthermore highlight factors that established #pmg as a cornerstone of materials science software. This retrospective could also serve as a guiding example for other community codes in the materials science domain. Lastly, we outline future developments and associated challenges.


//*Pymatgen's place in the community* (I hope I covered it)

= Overview and Design Principles
// *@ Janine*
== Background

#pmg was developed in 2011 by Shyue Ping Ong and colleagues at MIT to support the Materials Project @ong_python_2013 @jain_commentary_2013. Initially, #pmg provided essential tools for crystallographic operations, symmetry analysis, integration with the Vienna _Ab Initio_ Simulation Package (VASP) density functional theory (DFT) code @kresse_efficient_1996 and basic electronic structure and phase diagram analysis. These foundational capabilities enabled researchers to automate and standardize many aspects of computational materials science, laying the groundwork for high-throughput materials discovery. Many of these efforts were linked to the development of the Materials Project. @jain_commentary_2013 @horton_accelerated_2025

Since then, #pmg has expanded significantly, incorporating new features and adapting to the evolving landscape of materials science and informatics @butler_machine_2018. Key trends shaping its development include:

+ The growing importance of research data management
+ The rise of automated workflows for reproducible simulations and experiments
+ Increasing use of machine learning for materials property prediction
+ Greater availability of computational resources, enabling more complex analyses, machine learning tasks, and simulations

//#pmg is an open-source Python library for materials analysis, offering tools from basic crystallographic operations to complex electronic structure analysis @ong_python_2013 @jain_commentary_2013. Key features include:

Today, #pmg aims to accelerate materials discovery by providing a comprehensive toolkit for researchers at all levels @curtarolo_highthroughput_2013. While #pmg’s original goals—such as crystallographic operations and electronic structure analysis—remain central, its capabilities have grown substantially to support a broad spectrum of tasks in computational materials science and materials informatics, shaped by the previously listed trends.

#pmg offers powerful tools for crystallographic and structural analysis, including coordination environment analysis, electronic structure parsing, thermodynamic and phase diagram construction, analysis of phonon properties, and interfaces to various electronic structure codes. Additionally, it includes utilities for machine learning applications in materials property prediction @ward_matminer_2018, reflecting its evolution into a comprehensive platform for materials informatics. #pmg therefore aims to be a powerful, flexible, and reliable software tool @horton_promises_2021 for increasingly complex computational materials science and materials informatics research workflows. A key lesson learned from the wide community adoption and continued growth of the #pmg codebase, is that scientific software must continuously evolve to meet emerging demands in its field; without this adaptability, it risks becoming obsolete. It also must continuously onboard new developers; without a welcoming development environment, it is not sustainable. //maybe strongly worded but I indeed believe that this is true – SK 👍



== Interoperability and Comparative Tools

One of #pmg's strengths is its interoperability, having the capability to read various molecule and structure file formats and to automatically retrieve molecules and structures from databases. Furthermore, #pmg provides interfaces to a number of electronic structure / DFT codes (e.g., VASP @kresse_efficient_1996, Quantum Espresso @giannozzi_qe_2017, FHI-aims @blum_fhiaims_2009, CP2K @kuhne_cp2k_2020, Abinit @gonze_abinit_2020) or post-processing tools, such as `Phonopy` @togo_firstprinciples_2023 or `LOBSTER` @nelson_lobster_2020.

A crucial challenge in orchestrating heterogeneous computational workflows is normalization of the data structures used to transfer information between codes.
By "heterogeneous", we refer to workflows which may need separate codes to run, as exemplified by the phonon workflow example below.
Separate codes typically have bespoke input and output data structures, which hinder interoperability between related simulation tools: ex., nearly all molecular DFT codes accept `.xyz` files as input to represent molecular geometries, but the precise format of simulation input (self-consistent field convergence criteria, force convergence criteria, basis sets, etc.) and logging of calculation progress are unique to each code.

By normalizing the representation of this data, #pmg makes it easier to chain the outputs of different simulation tools when building complex workflows.
Critically, when running complex workflows, the workflow provenance, metadata, and progress are typically stored in an external database. #pmg was built with this in mind, and thus supports JSON-compliant object de-/serialization for interoperability with databases that can store JSON data.

#pmg also complements other materials science tools, most notably the Atomic Simulation Environment (ASE) @larsen_atomic_2017. While both software packages offer parsers for DFT and quantum chemistry codes, as well as tools for structure and molecule manipulation, their focuses differ. #pmg centers on complex materials data analyses, @jain_computational_2016 supporting tasks from oxidation state prediction to thermal conductivity modeling. ASE emphasizes atomistic simulation using normalization of crystalline and molecular data with similar basic functionality as their analogues in #pmg. Its `calculator` framework integrates quantum-chemical interoperability and in-built geometry optimization and molecular dynamics functionality.

Perhaps critically, the representations of atomistic data and operations used in ASE are not natively converted to a database-friendly representation, and require additional engineering to perform this conversion when orchestrating ASE-based workflows.
This distinction means that #pmg is often used in conjunction with ASE to orchestrate workflows where certain features (e.g., molecular dynamics driven by a classical forcefield) are only available in ASE. To streamline the usage of both codes, #pmg makes it possible to convert between the #pmg `Structure` object representation of a material and the ASE `Atoms` object representation. In a diverse and rapidly evolving research ecosystem, it is unrealistic and not desirable to expect a single code to dominate community adoption. Rather than striving for exclusivity, the focus should be on interoperability between codes, allowing users to combine the strengths of both software packages. In this way, it is on the code maintainers to develop and maintain good relationships with their fellow developers, and ensure this interoperability is as smooth as engineering constraints allow.
// Maybe rephrase to be a bit more succinct in comparing pymatgen and ASE
// Again, I tried. I hope I succeeded
// SK: I think this is very nice

Overall, this 'shameless' interoperability of #pmg enables seamless integration of various computational materials analyses within diverse research workflows. To illustrate, one common materials science workflow for phonon calculations could involve:
1. Obtain a crystal structure from the ICSD @zagorac2019recent or Materials Project @jain_commentary_2013 database, either manually or automatically with the #pmg API tools.
2. Use the symmetry and structure transformation tools in #pmg, built upon `spglib` @togo2024spglib, to reduce to the primitive unit cell.
3. Write the primitive cell to the file format required by the chosen quantum chemistry code, as well as other calculation input files (optionally), using #pmg.
4. Perform geometry relaxation with the chosen quantum chemistry code.
5. Directly read in the relaxed structure to #pmg, and generate a set of supercells with displaced atoms using the `pymatgen.io.phonopy` interface.
6. Parse the displaced-atom calculations with `phonopy` @togo_firstprinciples_2023 and compute atomic force constants.
7. Plot the phonon dispersion with `phonopy` or the `pymatgen.io.phonopy` interface, which additionally allows further analyses of Grüneisen parameters, phonon band structure and density of states manipulations etc.

This is a simple example, but one that helps illustrate the utility of #pmg's comprehensive materials analysis functionality and wide-ranging interoperability. Computational materials research workflows now widely employ #pmg as both a core analysis toolkit and a seamless glue between quantum chemistry codes and advanced research software packages.

// SK: I added this example to try illustrate, but possibly too verbose / not worth including; please feel free to trim as you see fit @Matt!
// JG: I am a bit worried that this repeats our use cases later on.

While #pmg supports interfaces to many codes, it should be noted that these are driven in large part by the research routes pursued within the Materials Project. Thus the interfaces to VASP and QChem have been thoroughly developed, as they are regularly used in the Materials Project.
Other interfaces to `packmol`, `atat`, or `zeo++` have been developed to support workflows studying non-crystalline materials, configurationally disordered crystalline materials, or material porosity, respectively. These interfaces may overlap with those available in ASE or `pyiron`, but they are more often disjoint.
We make no attempt to make a (necessarily outdated) list of codes to which #pmg natively interfaces, but we list a few which have been added or significantly enhanced since the first #pmg publication @ong_python_2013 (alphabetically): ABINIT @verstraete_Abinit2025_2025, CP2K @kuhne_cp2k_2020, icet @angqvist_icet_2019, JDFTx @sundararaman_jdftx_2017, LAMMPS @thompson_lammps_2022, LOBSTER @nelson_lobster_2020, OpenFF @wang_openff_2024, phonopy @togo_firstprinciples_2023, and QChem @krylov_qchem_2020.
The extensibility of #pmg allows for rapid development of interfaces to codes as needs arise.

= Community Adoption and Impact
// *@ Seán*

The growth of #pmg is reflected not only in its feature set but also in its expanding user base and community engagement. Steady growth in downloads and the number of packages requiring #pmg as a dependency over time are evidence of widespread and increasing adoption across the materials science community. Indeed, #pmg has been cited over 4000 times since 2013 @ong_python_2013, reaching just under 1000 citations in 2025 alone.
#pmg now averages over 1 million downloads per month on the Python Package Index (PyPI), though we note that these numbers are somewhat inflated due to automated continuous integration (CI) testing.
These usages span diverse fields, including energy storage and conversion, catalysis, defects, informatics, and materials discovery via machine learning @jain_computational_2016 (@fig:mindmap).

// #figure(
//   image("figs/citations.pdf"),
//   caption: [Citations of #pmg over time.],
// ) <fig:citations>

== Package Ecosystem

In addition to direct usage for common materials analyses, many packages, which are specialized for various computational materials science research areas, have built upon the #pmg framework.
A selection of the most popular downstream packages is shown in @fig:dependent-usage-of-pmg, which includes:

+ #link("https://github.com/materialsproject/atomate2")[`atomate(2)`] @ganose_atomate2_2025, #link("https://github.com/materialsproject/custodian")[`custodian`], #link("https://quantum-accelerators.github.io/quacc/")[`quacc`] @rosen_quacc_2025: High-throughput computational materials science workflows.
// `atomate2`, also published in Digital Discovery, demonstrates #pmg's role as a foundational tool for diverse materials science workflows used across the community for high-throughput studies.
+ #link("https://hackingmaterials.lbl.gov/matminer/")[`matminer`] @ward_matminer_2018: Data mining in materials science
+ #link("https://github.com/materialsvirtuallab/pymatgen-analysis-diffusion")[`pymatgen-analysis-diffusion`] @deng_datadriven_2017: Diffusion analysis suite (discussed further in #link(<sec:new-features>)[New Features])
+ #link("https://doped.readthedocs.io/en/latest/")[`doped`] @kavanagh_doped_2024, #link("https://shakenbreak.readthedocs.io/en/latest/")[`ShakeNBreak`] @mosquera-lois_shakenbreak_2022: Defect modeling and structure-searching, building on #link("https://materialsproject.github.io/pymatgen-analysis-defects")[`pymatgen-analysis-defects`] @shen_pymatgen-analysis-defects_2024 and #link("https://github.com/mbkumar/pycdt")[`PyCDT`] @broberg_pycdt_2018
+ #link("https://pymatviz.janosh.dev/")[`pymatviz`] @riebesell_pymatviz_2022, #link("https://smact.readthedocs.io/en/latest/")[`SMACT`] @davies_smact_2019: Materials informatics toolkits
+ #link("https://matbench-discovery.materialsproject.org/")[`matbench-discovery`] @riebesell_framework_2025, #link("https://www.air4.science/")[`AIRS`] @zhangArtificialIntelligenceScience2025, #link("https://github.com/materialsvirtuallab/matgl")[`matgl`] @ko_materials_2025, #link("https://github.com/Radical-AI/torch-sim")[`torch-sim`] @cohen_torchsim_2025: Machine learning for materials science
+ #link("https://pyxtal.readthedocs.io/en/latest/")[`PyXtal`] @fredericksPyXtalPythonLibrary2021: Generation and manipulation of atomic structures with symmetry constraints
+ #link("https://jageo.github.io/LobsterPy/")[`LobsterPy`]: @naik_LobsterPypackage_2024 Automatic analysis of `LOBSTER` outputs for summarized bonding information.
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
    caption: [Package dependency ecosystem. Linewidths represent the frequency of function invocations.],
  ) <fig:package-ecosystem>
]

Cumulatively, #pmg's impact on the materials science community includes:

+ Accelerated research across various domains @butler_machine_2018, including the accelerated development of specialized materials analysis toolkits (@fig:dependent-usage-of-pmg).
+ Standardization of core materials analysis procedures.
+ Improved reproducibility through user-friendly serialization and analysis tools.
+ Provision of accessible educational tools for students and early-career researchers @ong_python_2013, such as https://github.com/materialsvirtuallab/matgenb and https://github.com/sp8rks/MaterialsInformatics.
// Andrew notebook potentially live soon
+ Adoption in industrial research and development workflows @jain_commentary_2013.
+ Promotion of open science and collaborative development @horton_promises_2021.

// integration into platforms like the Materials Project, AFLOW, and OQMD @curtarolo_aflow_2012.
// SK: Well it's that pymatgen's API can be used with these material databases (except ofc Materials Project which it supports/'is integrated to')

== Case Studies
As discussed above, many advanced materials analysis packages have built upon the #pmg codebase to enable complex domain-specific research workflows.
Below, we briefly discuss two such cases where the #pmg framework has facilitated advanced materials analyses.

// MH: let's keep 350 word limit for case studies to keep tight, Seán to move some lessons learned to end to cover both

=== Defect Modeling Tools
Defect modeling is a rapidly growing field, driven by advances in computational power and methods which make these calculations increasingly tractable, along with the critical importance of defect species to diverse materials technologies, such as transistors, solar cells, transparent conducting materials, batteries, qubits and more.
Defect simulation can be a long and complex process, however, requiring many different tasks, including structure manipulations, symmetry analyses, input file generation and output parsing for electronic structure codes, lightweight metadata and serialization for reproducibility, and interfaces with databases such as the Materials Project for phase diagram analysis.
Moreover, many of these tasks have specific requirements for the specialized case of defects, such as efficient and appropriate supercell generation (to balance computational cost and accuracy), determination of defect point symmetries, configurational degeneracies and site multiplicities in symmetry-breaking supercells, efficient algorithms for large and complex structure analyses, calculation parameter consistency checks, targeted distortions for structure-searching, smart algorithms for sub-phase diagrams and more @squires_guidelines_2026.

Several open-source toolkits have now been developed which make use of core functionalities in #pmg to implement stages of the defect modeling workflow, including `doped` @kavanagh_doped_2024 (@fig:dependent-usage-of-pmg), `pydefect` @kumagai_insights_2021, `PyCDT` @broberg_pycdt_2018, `pymatgen-analysis-defects` @shen_pymatgen-analysis-defects_2024, `ShakeNBreak` @mosquera-lois_shakenbreak_2022, `AiiDA-defects` @muy_aiida-defects_2023 and `pydecs` @ogawa_extended_2022.
These toolkits are seeing widespread usage in the defects community, helping to accelerate research in this technologically crucial area, along with reducing human errors and lowering the barrier to entry for new researchers.
Here, the wide functionality and flexible, modular structure of #pmg has been a key enabler of these downstream developments, allowing the tailoring of #pmg functions to specialized use cases.

One particularly promising aspect of these developments, is that they have greatly reduced the burden for data sharing and reproducibility in defect simulations---a particularly challenging task given the many steps involved @squires_guidelines_2026.
Through the object-oriented architecture and efficient serialization tools provided by #pmg and its `monty` dependency for (de)serialization, the human effort to collate and export complete metadata and calculation provenance is significantly diminished.
These developments are helping to establish clear community standards and expectations for reproducibility, strengthening the quality of defect modeling research while ensuring robust foundations for future database and machine learning efforts in this area @squires_guidelines_2026.

// + (If we want a figure here, could make a diagram showing the workflow: Pull materials from MP -> Oxi-state Guess w/PMG -> Vacancy generation w/`doped` (via PMG etc) -> Electrostatic analysis with PMG (Ewald tools) -> VASP DFT I/O w/PMG -> Energetic & Structural (w/`doped` & PMG) analysis; from 10.1088/2515-7655/ade916, as example).

=== Data-Driven Heuristic Assessment and Machine Learning
// *@ Janine*
// remove? add other publications to make it fairer
#pmg is a powerful toolkit that enables large-scale data analysis and machine learning studies in materials science. These are typical tasks required when finding new design principles for certain materials properties or when developing feature-based machine learning models. The latter is frequently a core component in Materials Acceleration Platforms or self-driving labs.@stier_materials_2024
Through #pmg's direct interfaces to material databases (Materials Project API or OPTIMADE API @andersen2021optimade), researchers can easily retrieve extensive datasets, including machine learning targets, which serve as the foundation for data-driven assessments of design principles and heuristics, as well as the development of machine learning models. When working with other crystal structure sources such as the Cambridge Structural Database @groom2016cambridge, Inorganic Crystal Structure Database @zagorac2019recent or MAGNDATA @gallego2016magndata, #pmg’s ability to read (magnetic) Crystallographic Information Files (CIFs) facilitates the creation of large, structured datasets. #pmg allows simplified filtering by composition or crystal symmetry, depending on requirements. Additionally, many post-processing features are available in pymatgen, enabling the simpler generation of targets.

Chemical heuristics have been frequently used to inspire design principles or features in machine learning models. Many of them—such as those related to stability, synthesizability, defect energetics, and magnetism—rely on accurate determinations of oxidation states and coordination environments, which can both be assessed within #pmg. #pmg implements several heuristics to determine oxidation states (e.g., based on bond valence sums or simple composition-based guessing methods) and to determine coordination environments (e.g., based on minimum distances or Hoppe's effective coordination numbers)@pan_benchmarking_2021, @waroquiers_chemenv_2020. Additionally, #pmg is deeply integrated within matminer,@ward_matminer_2018 a library that streamlines the generation of popular features for machine learning workflows, further supporting the derivation and validation of heuristics. Here, #pmg formats are used directly as input for creating machine-learning features.
In summary, #pmg provides a framework for materials data handling, feature extraction, and heuristic development, making it an essential tool for modern, data-driven materials informatics. The codification transforms chemical and crystallographic knowledge into a resource that accelerates data-driven materials discovery.

//SMACT? (From Walsh group) -> I decided to remove my own publication in this context. In this way, i believe, the citations are fairer (i.e., mostly the publications actually implementing the heuristics are cited)

=== Additional Case Studies and Lessons
*Note to self (Matt): mention additional possible case studies we have _not_ written here*
There are many other possible case studies we could discuss, which illustrate the impact of #pmg in a variety of different materials modeling sub-fields, such as in low-dimensional materials, surface slicing and analyses, high-throughput materials discovery and automated workflows, magnetic structure enumerations and more.
// SK: Rough draft something here based on MH's comment

A key lesson we can extract from the success of subfield-specific modeling packages built on #pmg is that the provision of robust functionality for common tasks (such as structure manipulations, oxidation state estimation or input/output to DFT codes) allows the ready extension to more specialized research workflows by domain experts.
By implementing these core materials analysis functions in a modular code structure, which can be readily imported into downstream packages, #pmg removes the need to re-implement common tasks and allows practitioners to focus on specialized domain-specific analyses (e.g., predicting defect concentrations).
Another aspect which has proven important to the success of these advanced simulation workflows is the use of computationally-efficient implementations (e.g. through intelligent algorithms, vectorisation or CPython code) in the #pmg core modules.
This ensures efficiency and scalability in downstream usages, allowing, for instance, high-throughput screening across immense materials search spaces, or structural analyses of large defect supercells with low symmetry.
Finally, the clear communication of code deprecations and breaking changes is crucial for the smooth and uninterrupted development and maintenance of the many downstream scientific packages which rely on #pmg.


= New Features <sec:new-features>
// *@ Aaron*
// Subsections?
// add other io modules as a subsection -> standard parameters for metals, insulators etc. (but pros and cons); Codified Materials Intelligence
// Standardization of Materials Science Data -> Alexandria database

The growth of #pmg closely follows trends in materials science research, reflecting its critical role in advancing science.

Modeling of Li- and Co-alternative battery electrodes has long driven atomistic analysis tools in #pmg.
The `pymatgen-analysis-diffusion` extension @shen_topological_2023 grew out of a smaller submodule of diffusivity analysis tools, which were eventually migrated to a separate namespace package.
These tools enable faster estimates of ionic mobility from molecular dynamics trajectories.
They also include tools to identify likely topotactic ion insertion defect sites based on electronic charge densities @shen_charge_2020, used when estimating ionic mobility from transition-state type mappings of the potential energy surface.

More recently, machine learning (ML) methods @butler_machine_2018, particularly ML interatomic potentials (MLIPs) @chen_universal_2022, have emerged as practical ways to rapidly estimate atomic structure without more costly recourse to electronic structure methods.
#pmg has integrated some of these structural prediction tools via the external `matgl` python package @ko_materials_2025.
This allows users to, e.g., quickly relax crystal structures using common graph neural-network MLIPs such as M3GNet @chen_universal_2022, CHGNet @deng_chgnet_2023, and TensorNet @simeon_tensornet_2023.
MLIPs can also be directly used in #pmg to estimate small-cell ordered representations of disordered materials by enumeration of possible orderings, and selecting the predicted minimum energy configuration.

Analysis of local coordination environments has also been of critical importance in understanding the roles of atomic and electronic structure in shaping materials characteristics.
These insights help identify structural motifs that lead to similar performance, e.g., frameworks which favor ionic mobility.
#pmg aids in analysis of electronic charge densities and electronic bonding by interfacing with LOBSTER @nelson_lobster_2020.
#pmg makes possible analysis of local atomic coordination environments using the ChemEnv @waroquiers_chemenv_2020 and CrystalNN @zimmermann_crystalnn_2020 methods, among others.
CrystalNN can be further used to generate structural embeddings similar to the feature vectors of MLIPs, which in turn allow for rapid estimates of structural similarity @zimmermann_fingerprint_2020 and automatic generation of human-readable descriptions of materials with the `robocrys` package @ganose_robocrys_2019.
Local coordination environment analysis from ChemEnv, CrystalNN similarity estimates, and CrystalNN-based generated descriptions of materials are now standard analysis products of the Materials Project's build pipelines, and are currently distributed as part of its core data.

Other extensions to #pmg which can be separately installed under the `io` and `analysis` namespaces include, but are not limited to: validation of VASP @kresse_ultrasoft_1999 calculations for compatibility with the Materials Project @horton_accelerated_2025 via `pymatgen-io-validation`; orchestration and parsing of FHI-aims @blum_fhiaims_2009, Quantum Espresso @giannozzi_qe_2017, and FLEUR @wortmann_fleur_2023 electronic structure calculations via `pymatgen-io-aims`, `pymatgen-io-espresso`, and `pymatgen-io-fleur`, respectively; orchestration of classical molecular dynamics calculations with OpenMM @eastman_openmm_2023 via `pymatgen-io-openmm`; core defect functions with `pymatgen-analysis-defects` @shen_pmgdefects_2024.
A more complete list of extensions to #pmg is maintained in the add-ons section of the documentation.

// Recent additions to #pmg to include:

// + Enhanced machine learning integration @butler_machine_2018
// + Support for additional DFT and post-processing codes (e.g., FHI-AIMS, LOBSTER @george_automated_2022, Critic2, Phonopy@petretto_highthroughput_2018)
// + Improved structure prediction and analysis algorithms (including magnetic structure) @waroquiers_chemenv_2020 @pan_benchmarking_2021 @horton_highthroughput_2019
// + Advanced battery materials research tools
// + Quantum chemistry code integration
// + Extension packages?

As illustrated in @fig:pr-topics and @fig:commits-heatmap, development activity has been sustained across multiple subpackages for over a decade, with contributions spanning bug fixes, new features, and performance improvements.

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
        pad(x: -1em, image("figs/commits-per-package-heatmap.png")),
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

Perhaps the most critical challenge facing long-lived open-source scientific software is sustainability. Unlike commercial software with dedicated development teams, #pmg has evolved primarily through volunteer contributions from academic researchers, where software development competes with research publications, teaching, and other career pressures. This model, while fostering community ownership, creates inherent tensions around maintenance, code review capacity, and long-term feature development.

The Materials Project has provided crucial institutional support, offering paid developer time, computational resources, and organizational infrastructure. This hybrid model (combining institutional backing with community contributions) has proven essential for #pmg's longevity. Yet acquiring funding for software maintenance remains challenging, as grant agencies strongly favor novel research over infrastructure upkeep. Projects like FAIRmat @fairmat_web_2025, as part of the German national research data infrastructure, and the Molecular Sciences Software Institute (MolSSI) @molssi_web_2025 represent important steps toward recognizing computational infrastructure as crucial research infrastructure deserving of sustained investment.

As shown in @fig:pr-since-1st and @fig:contributors-worldmap, #pmg has cultivated a globally distributed contributor base which affords some amount of resilience to changing resource situations at any one institution. However, the concentration of maintenance burden on a small number of core developers remains an ongoing concern. We hope that clear contribution guidelines, responsive code review, and explicit recognition of contributors (through authorship opportunities, acknowledgments in papers, and community visibility) can help sustain engagement and grow the pool of active maintainers.
This incremental-development perspective aligns with Digital Discovery's recent `Commit` article concept @aspuru_commit_2025, which formalizes citable reporting of improvements to prior software, data, and hardware publications. While the present manuscript contains a full retrospective, the underlying motivation is similar: incentivize and reward sustainable scientific software development through transparent, community-driven iteration.
Sustained progress still depends on stable funding, explicit onboarding pathways, and incentive structures that recognize maintenance work.

== Backwards Compatibility and API Evolution

// Inconsistent APIs: dataclass vs. monty conflicts
// Versioning issues: less possibility of release candidates for testing new features/deprec

A fundamental tension in mature software libraries is balancing API stability against the need for improvements. #pmg has accumulated technical debt from early design decisions—for example, parsing classes sometimes return property objects (`io.vasp.outputs.Vasprun.complete_dos`), while elsewhere property classes parse files directly (`electronic_structure.cohp.CompleteCohp.from_file()`).

#pmg uses Calendar Versioning (CalVer) with the format `YYYY.MM.DD`, providing immediate insight into release recency. Unlike Semantic Versioning, CalVer does not encode change magnitude in the version number, so users need to consult release notes to assess upgrade impact.

With thousands of users and hundreds of dependent packages, #pmg bears significant responsibility for API stability. Breaking changes can cascade through the ecosystem, disrupting research workflows and requiring coordinated updates across multiple projects. To manage this, #pmg follows established deprecation best practices: deprecated features raise `DeprecationWarning` with clear removal timelines (typically 6--12 months), giving downstream maintainers time to adapt. Major changes are communicated through release notes, GitHub discussions, and the matsci.org forum. The namespace package architecture (`pymatgen-io-*`, `pymatgen-analysis-*`) further enables specialized APIs to evolve independently, reducing the blast radius of breaking changes on the core library.

For mature infrastructure libraries, backward compatibility is a community contract. Incremental deprecations with predictable removal timelines are imperative for evolving a codebase with a user base as large as #pmg while minimizing the impact on downstream research.

== Test Coverage and Code Quality
// @Janosh: expanded 13 Jan 2026 - Rust tooling (ruff/ty/uv), LLMs for maintenance, AI code review (CodeRabbit/Cursorbot)

As shown in @fig:pmg-code-structure, #pmg achieves approximately 79% test coverage across its 150,000+ lines of code, though coverage varies significantly by module. Core functionality (`core`, `io`, `entries`) maintains >90% coverage, while specialized modules like visualization (`vis`) and certain analysis tools (`boltztrap`) have lower coverage (\<20%). This heterogeneity reflects genuine trade-offs: some modules require licensed external executables (VASP, Gaussian) for meaningful testing, others involve long-running operations, and visualization code requires rendering backends that complicate headless CI. Testing resources have been strategically focused on core modules serving the largest user bases.

Continuous integration via GitHub Actions runs the `pytest` test suite on every pull request across multiple Python versions. Coverage is tracked via `coverage.py` and reported to Codecov. The Python ecosystem's rapid migration of developer tools to Rust—including #link("https://docs.astral.sh/ruff")[`ruff`] (linting and formatting), #link("https://github.com/astral-sh/ty")[`ty`] (type checking), and #link("https://docs.astral.sh/uv")[`uv`] (package management)—has dramatically accelerated #pmg's CI pipelines and local development workflows. In particular, static type analysis with tools like `mypy` and the much faster Rust-native `ty` catches subtle bugs at development time that would otherwise only surface during testing or production. `ty` is fast enough to run in tight feedback loops with LLM coding agents, catching type errors in seconds rather than minutes even in large codebases like #pmg — enabling rapid iteration toward correct code without waiting for slow test suites. Pre-commit hooks enforce these checks locally. However, the test suite's ~45 minute execution time (despite `pytest-split` parallelization across 4 runners) creates friction for contributors, and improving test efficiency remains an ongoing priority.

The emergence of frontier large language models (LLMs) has significantly reduced #pmg's maintenance burden. Tasks like writing tests, adding type annotations, improving docstrings, and refactoring legacy code can now be accelerated with LLM assistance—particularly valuable given the backlog of technical debt accumulated over 14 years. AI-powered code review tools like #link("https://coderabbit.ai")[CodeRabbit] and #link("https://cursor.com/bugbot")[Cursorbot] further reduce maintainer workload by providing automated first-pass reviews on pull requests. While early attempts at LLM-based code review on large codebases often added noise due to limited context windows and model capabilities, these tools have matured significantly—now handling complex changesets reliably and catching real issues that would otherwise require slow and arduous manual testing. LLMs also lower contribution barriers by helping newcomers navigate unfamiliar code. While human oversight remains essential, these AI-assisted tools have meaningfully increased throughput for #pmg's small maintainer team.

Quality at scale is best achieved through layered safeguards rather than any single metric. Fast static type and format checks, targeted issue-driven unit tests, and human-reviewed AI assistance together provide better reliability-per-maintainer-hour than focusing any subset of these tools.

== Governance and Contributor Onboarding

// @Aaron
// Shyue may not like this section at all. What I have here is the perspective of MP / MPSF

As a core component of the Materials Project's analysis tools, #pmg is governed according to principles established by the Materials Project stakeholders, which are in turn inspired by the best practices adopted by established community organizations like NumPy @harris_array_2020 and NumFOCUS.
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

As discussed in previous sections, a large ecosystem of materials science codes depends on #pmg (see @fig:dependent-usage-of-pmg).
However, #pmg also depends on the open source ecosystem for scientific computing, plotting, and data science (@fig:pmg-dependency-usage). This includes `numpy`, `scipy`, `spglib`, `matplotlib`, `plotly`, `pandas`, and `sympy`. `networkx` supports graph-based analysis within #pmg. For serialization, #pmg uses `monty` and `orjson`. `monty` itself has been developed to support #pmg in such tasks.

As a core component of the base layer of the computational materials science infrastructure layer that sits between foundational packages and hundreds of downstream dependents, #pmg's dependency management has ecosystem-wide implications. #pmg follows the Scientific Python community's SPEC 0 policy @spec0_minimum_supported_dependencies, specifying minimum-version constraints but avoiding upper-version caps to prevent resolver conflicts in downstream packages. When upstream libraries introduce breaking changes---as occurred with the NumPy 2.0 C API transition @harris_array_2020 ---#pmg must adapt promptly, often ahead of its own dependents, to avoid blocking the wider ecosystem. This bidirectional responsibility is a recurring theme in maintaining community infrastructure: changes propagate both up and down the dependency graph, and delayed adaptation in either direction compounds across the ecosystem, underscoring that widely adopted software like #pmg requires a responsive maintainer team to avoid becoming a bottleneck for the broader ecosystem.

#place(top + center, float: true, scope: "parent")[
  #figure(
    pad(right: -2em, image("figs/py-pkg-treemap-pymatgen-coverage.pdf")),
    caption: [#pmg code structure and test coverage. The size of each module represents lines of code, while colors indicate test coverage percentage.],
  ) <fig:pmg-code-structure>
]

#figure(
  image("figs/pr-since-1st.pdf"),
  caption: [Pull requests per contributor since their first contribution.],
) <fig:pr-since-1st>

#figure(
  image("figs/active-contributors-colored.pdf"),
  caption: [Active contributors to #pmg over time.],
  // SK: Could potentially cut, somewhat duplicating info from other figures
) <fig:active-contributors>

#place(top + center, float: true, scope: "parent")[
  #figure(
    pad(x: -3em, top: -2em, bottom: -5em, image("figs/pr-contributors-worldmap.pdf")),
    caption: [Geographic distribution of #pmg pull request contributors. Note caveats; pulled from GitHub profiles],
  ) <fig:contributors-worldmap>
]

= Outlook and Future Developments
// Agents? - @Aaron: added a brief bit at the end
// Make it less committing for us: open it up to other developers
#pmg has evolved from a specialized tool into a cornerstone of computational materials science. Its growth reflects the collaborative spirit of the materials informatics community and the importance of open-source software in scientific research.

While the core features of pymatgen are relatively stable, more peripheral features require constant community review beyond the stewardship of a small team of maintainers.
Improving performance of the most essential #pmg libraries is key to its growth. #pmg introduced namespace packages in #link("https://github.com/materialsproject/pymatgen/commit/f462d35c")[v2022.0.3] (March 2021, see also #link("https://github.com/materialsproject/pymatgen/commit/8f097cf7")[`8f097cf`], #link("https://github.com/materialsproject/pymatgen/commit/711edf42")[`711edf4`], #link("https://github.com/materialsproject/pymatgen/commit/9f86ea4e")[`9f86ea4`], and the #link("https://github.com/materialsproject/pymatgen-addon-template")[addon template]), which allowed the independent installation and maintenance of pymatgen "add-on" packages within the pymatgen "namespace", i.e. importable from `pymatgen.io` and `pymatgen.analysis`. Critically, this decouples the release cadence of add-on packages from that of the core library---enabling the higher release frequency often needed during a package's early development without being blocked by the slower, more deliberate release cycle of #pmg itself. This can be furthered with a separately-installable `pymatgen-core` to deliver just the fundamental materials science object primitives for other developers to build upon.

At its current scope, expanding and refining the feature set of #pmg would ideally require a large development team to ensure effective stewardship.
As #pmg continues to grow in scope and adoption, we frame the next steps as high-impact community opportunities.
In particular, broader shared ownership of maintenance tasks (code review, issue triage, and bug fixes in niche submodules) can strengthen participation and long-term stewardship.
As contributors gain experience in these roles, they can naturally grow into deputy reviewer and maintainer positions.

There are many active areas of materials science which could benefit from extensions of #pmg key feature set.
These include a wider variety and depth of control for `io` extensions to popular electronic structure (e.g., Quantum Espresso), atomistic (e.g., LAMMPS, GROMACS), and continuum, phase field, and multiphysics codes.
However, as noted previously, any extension of functionality that is not in a separately-installable namespace would require concomitant community review.

While community fora such as `matsci.org` exist alongside the issue tracker for #pmg, the documentation of #pmg is very sparse given its breadth.
One promising direction is community-reviewed, LLM-assisted documentation expansion to improve coverage without increasing burden on core maintainers.

High-impact development opportunities informed by community needs and emerging trends in materials science include:

// Comment from JG: "phrase as invitation" to help/support
// MH: maybe we can make each point similar length - again keep focused
// AR: Instead of "we will do X", these are areas that should be areas of focus (by the community)
*Machine learning integration* is likely to remain important as ML methods increasingly enter materials discovery and design @butler_machine_2018. High-value contributions include native support for modern frameworks (PyTorch, JAX), efficient structure-to-graph conversions for neural network architectures, and stronger integration with benchmarking frameworks like Matbench Discovery @riebesell_framework_2025.
// Mention agentic AI able to take advantage of pymatgen platform

*Visualization and user experience* improvements through tighter integration with `crystal-toolkit` @horton_crystal_2023, `pymatviz` @riebesell_pymatviz_2022, and `matterviz` @riebesell_matterviz_2025 could lower barriers to entry. Useful community efforts include enhanced Jupyter notebook support, interactive structure manipulation, and publication-ready figure generation.

*Performance optimizations* remain a major opportunity, especially via strategic use of compiled extensions. #pmg now operates in a different regime to when it started: in early development, #pmg was used to orchestrate much-slower DFT calculations, and the additional overhead from Python and its heavily object-oriented software structure was negligible. However, today, with the rise of very rapid ML forcefield simulation capability, this overhead is now significant and deeper optimization is increasingly valuable. A successful example is given by the `moyo` project, which involved a Rust migration of symmetry analysis tools in `spglib` while maintaining an easy-to-use Python API via bindings. Similar approaches could accelerate oft-used compute-intensive operations such as structure matching, neighbor searching, convex hull calculations, and more.
// Previously discussed integrating Rust components more broadly @lunnikivi_transpiling_2020, but this may not have consensus among all maintainers.
// JR: rust migration is probably a personal hobby horse of mine and something Shyue would reject outright...
// AK: Rewrote to make it more generic (focus on compiled extensions generally, not Rust specifically)

*Extension package ecosystem* growth will strengthen #pmg's federated architecture: a stable core supplemented by domain-specific namespace packages (e.g., `pymatgen-analysis-diffusion` @deng_datadriven_2017, `pymatgen-io-openmm`) maintained by experts. Increasing the number and quality of these extensions distributes maintenance burden while enabling rapid iteration in specialized domains. New functionality areas—such as multi-scale modeling bridging atomistic and mesoscale simulations—are best developed as extension packages rather than expanding the core.

*GPU compatibility*: A promising direction is broader support for tensor backends (e.g., PyTorch) in array-heavy code paths, enabling GPU acceleration and potential speedups for large-scale analyses.

*Agentic AI tools* Large language models (LLMs) can naturally run `python` code using the architecture-agnostic model context protocol (MCP) framework, provided that the data structures operated on by the MCP are (mostly) JSONable. #pmg naturally supports this interface via the de-/serialization procedures defined within `monty`. While this has naturally positioned #pmg to support MCP-type tools, to better facilitate the construction of analysis tools that LLMs can use, #pmg will need to enforce clearer type annotations and reduce the complexity of the JSON-serialized representations of objects. Both of these efforts would also likely strengthen the reliability and lower the memory usage of #pmg.

//MH: *Provenance and units*: [want to highlight a weakness in pmg, our abandoned TransformedStructure concept, the way de/re-serialization best practices have shifted, the risks of unit errors: in other words, how can we drive scientific correctness forwards. Highlight other good work here, eg AiiDA's provenance graph, while a usability nightmare [won't mention this part], is an inspiration.]

//MH: maybe some community mention here - OPTIMADE API - unsure.... will think about this aspect.

//- suggestion from Shyue "would say most of the code that works with numpy arrays should be adapted such that they can seamlessly work with torch tensors. I am working with NVIDIA’s team on incorporating their alchemi NN code which can speed up distance computations for large cells (it is not that useful for small cells). So in future analysis of million-atom simulation cells over 10s or even 100s of ns of trajectories would be possible and efficient."

We invite contributions at all levels---from bug reports and documentation improvements to new features and extension packages. The project's GitHub repository, documentation site, and community forums provide entry points for new contributors.

= Acknowledgments

We thank the numerous developers, researchers, and users who have contributed to #pmg over the years. We also acknowledge the funding agencies and institutions that have supported its development, including the U.S. Department of Energy, the National Science Foundation, and various academic institutions.

Special thanks is given to the broader open-source scientific computing community for their invaluable tools and libraries, especially NumFocus and their efforts around `numpy` @harris_array_2020, `pandas` @mckinney_data_2010 @team_pandasdev_2025 and `matplotlib` @hunter_matplotlib_2007, all of which #pmg heavily relies on.

// MH: will make sure to have a callout / appendix for all our developers.
// JG: can we get most of them be authors? [hopefully! I have a notebook too, I will need to make sure I have all author information, may need to reach out to latest developers]
// ChatGPT was utilized to enhance the language and facilitate additional literature queries. Everything was checked carefully afterwards. -- not needed for language improvements

// Author contributions
// Noting CREDIT taxonomy https://credit.niso.org we could think about adopting before submission
// JG: organized meetings, re-wrote introduction, overview and design principles, case study on chemical heuristics, contributed to backwards compatibility and api evolution, gave feedback to all sections and figures, contacted Digital Discovery for initial feedback on our publication, started with one draft for a figure
// MH: primarily feedback and comments, guidance on structure, writing some small sections, tbd if more. Very early organization/co-ordination - JG has done this almost exclusively for this iteration. Developer outreach.
// SK: case study on defect modeling, community adoption and impact section, minor editing to all (particularly early) sections, feedback to all sections/figures. Attended all meetings.
// JR (LLM-assisted summary of commit history):
// + 26 commits by 2026-02-17 with ~7,223 lines added, ~3,373 removed
// + Wrote the "Challenges and Solutions" sections on sustainability, backward compatibility/API evolution, and test coverage/code quality; added framing around maintainer resources, deprecation policy, CalVer implications/downsides compared to SemVer, wrote section on Rust-native tooling, and AI-assisted maintenance.
// + manuscript infra setup (repo, git repo, CI, initial bibliography), Digital Discovery Typst template, subfigure support
// + created and/or contributed to all figures (PR-topic trend plotting, contributors-over-time tooling, world-map/contributor data pipeline support, dependent/dependency usage analysis scaffolding)
// + Contributions to pymatgens (from `fig_scripts/pr_contributors_bar_plot/_pr_contributors.json`): 421 PRs attributed to `janosh` (out of 2,449 total PRs; 269 unique contributors) from 2021-03-09 to 2025-02-06
// + pymatgen contribution profile: sustained multi-year activity with major emphasis on bug fixes/reliability, API design, developer tooling and CI modernization, code quality improvements, targeted feature additions, and better docs.
// AR: I think I added a paragraph or two somewhere at some point, but I've more been just editing more recently. Certainly I am not expecting to be among the lead authors.
// ADK: new features of pmg including io and use in workflows; some bigger picture stuff on direction of pymatgen development wrt MP + MPSF
// we decided on everyone attending these meetings regularly to be joint

#bibliography("refs.bib", style: "ieee")
