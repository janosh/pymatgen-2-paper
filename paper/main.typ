#import "./template.typ": float, subfigure, template
#import "./authors.typ": affiliations, authors

#let pmg = `pymatgen`
#show link: set text(fill: blue.darken(20%))

#let title = "pymatgen: 15 years of community growth, new functionality, and future prospects"

#show: template.with(
  title: title,
  abstract: [
    We present a retrospective on the Python Materials Genomics (#pmg) library, reflecting on 15 years of community growth and established best practices.
    The current version of #pmg builds on its robust, open-source foundation, emphasizing its collaborative nature.
    Over this period, #pmg has grown into one of the largest open-source materials science codebases.
    We detail how #pmg supports advanced computational materials science workflows, how it adapts to changing demands, and the lessons learned from its growing community, offering guidance relevant beyond the #pmg community.
    #pmg will continue to evolve in response to the rapidly changing landscape of computational materials science and materials informatics.
    We discuss the challenges and potential solutions to managing the community-driven evolution of #pmg and provide an outlook on its future development.
  ],
  venue: [_Digital Discovery_],
  header: (
    article-color: rgb("#364f66"),
    article-type: "Preprint",
    article-meta: [Not Peer-Reviewed],
  ),
  authors: authors,
  affiliations: affiliations,
  author-notes: (
    [#super[#sym.dagger] These authors contributed equally.],
    [#super[#sym.ast.op] Corresponding author: Shyue Ping Ong (#link("mailto:shyue@nus.edu.sg")[shyue\@nus.edu.sg]).],
  ),
  dates: (
    (type: [Received Date], date: datetime.today()),
    (type: [Revised Date], date: datetime.today()),
    (type: [Accepted Date], date: datetime.today()),
  ),
  doi: "00.0000/XXXXXXXXXX",
  citation: [J. George et al., _Digital Discovery_, 2026, *1*, 1---2],
)

= Introduction

Python Materials Genomics (#pmg) @ong_python_2013 was launched in 2011 to provide a robust, reusable software foundation for materials analysis in high-throughput density functional theory (DFT) workflows. The predecessor infrastructure, built on Java @jain_high-throughput_2011, was showing its age. The ubiquity of Python, its mix of functional and object-oriented design, rapid development cycle, and interoperability established it as an ideal platform for modern computational materials science software. What emerged from that practical need has, over 15 years, grown into one of the most widely used open-source libraries in the field @open_comp_matsci. Today, #pmg is a cornerstone of the Materials Project @jain_commentary_2013 @horton_2025_mp, a dependency for hundreds of downstream packages, and a standard toolkit across research areas spanning battery materials, defect modeling, machine learning interatomic potentials (MLIPs), and materials informatics @butler_machine_2018 (@fig:mindmap and @fig:shells-of-influence).

The trajectory of #pmg offers an opportunity for reflection. Scientific software rarely combines broad, cross-disciplinary adoption (as exemplified for #pmg by @fig:mindmap) with sustained long-term development. #pmg has been actively developed for more than a decade, and the original software publication now receives close to 1000 citations per year. It has catalyzed an ecosystem of tools in computational materials science @mathew_atomate_2017 @ganose_atomate2_2025 @horton_2025_mp. Understanding how and why this happened carries lessons that extend well beyond #pmg itself.

In this retrospective, we review #pmg's design principles and the philosophy of interoperability that enabled its broad adoption. We trace the growth of its contributor community and downstream package ecosystem and examine the technical and organizational challenges of maintaining infrastructure at this scale. Lastly, we outline the directions we believe will matter most in the next phase of its development. Throughout, we aim to extract lessons applicable to the broader challenge of building and sustaining community-driven scientific software---a challenge that grows more consequential as computational methods become increasingly central to materials discovery.

#place(top + center, float: true, scope: "parent")[
  #figure(
    image("figs/mindmap.pdf", width: 75%),
    caption: [Selected research topics among works citing the original #pmg paper, grouped from OpenAlex primary topics into five thematic branches with LLM assistance. Up to four topics are displayed per branch. Node colors and the color bar share a logarithmic count scale; branch counts sum their displayed children, while the root node color is fixed for visual distinction.],
  ) <fig:mindmap>
]

= Overview and Design Principles

== Background

#pmg was originally developed in 2011 to support the Materials Project @ong_python_2013 @jain_commentary_2013 @horton_2025_mp. In this capacity, #pmg provided essential tools for crystallographic operations, symmetry analysis, integration with the Vienna _Ab Initio_ Simulation Package (VASP) DFT code @kresse_efficient_1996, and basic electronic-structure and phase-diagram analysis. These foundational capabilities enabled researchers to automate and standardize many aspects of computational materials science, laying the groundwork for high-throughput materials discovery.

Since then, #pmg has expanded significantly, incorporating new features and adapting to the evolving landscape of materials science and informatics @butler_machine_2018. Key trends shaping its development include:

+ The growing importance of research data management @himanen_data-driven_2019
+ The rise of automated workflows for reproducible simulations and experiments @himanen_data-driven_2019 @flores-leonar_materials_2020 @stier_materials_2024
+ Increasing use of machine learning for materials property prediction @butler_machine_2018 @schmidt_recent_2019
+ Greater availability of computational resources, enabling more complex analyses, machine learning tasks, and simulations

Today, #pmg aims to accelerate materials discovery by providing a comprehensive toolkit for researchers at all levels @curtarolo_highthroughput_2013. While #pmg's original goals---such as crystallographic operations and electronic structure analysis---remain central, its capabilities have expanded substantially in response to evolving community needs. #pmg now offers tools for crystallographic and structural analysis, including coordination environment analysis, electronic structure parsing, thermodynamic and phase diagram construction, analysis of phonon properties, and interfaces to various electronic structure codes. Additionally, it offers reusable utilities for machine learning applications in materials property prediction that underpin materials informatics packages @ward_matminer_2018, reflecting its evolution from a materials analysis library into a broader platform for materials informatics. By implementing these core materials analysis functions in a modular and reusable software framework, #pmg removes the need to repeatedly reimplement common tasks and allows both users and downstream developers to focus on specialized domain-specific analyses and applications. The same modularity and reuse may also prove increasingly valuable for AI-driven workflows, where LLM-based agents can build on established #pmg functionality as trusted building blocks for scientific reasoning and analysis. #pmg therefore aims to be a powerful, flexible, and reliable software tool @horton_promises_2021 for increasingly complex computational materials science and materials informatics research workflows.

A key lesson learned from the wide community adoption and continued growth of the #pmg codebase is that scientific software must continuously evolve to meet emerging demands in its field; without this adaptability, it risks becoming obsolete. It must also continuously onboard and support new developers; without a welcoming environment, we believe that open-source development is not sustainable. #pmg's growth has been supported by a low barrier to contribution and responsive maintainership, which facilitate community participation and the timely integration of new functionality.

== Interoperability and Comparative Tools

One of #pmg's strengths is its interoperability, with the capability to read various molecule and structure file formats and to automatically retrieve molecules and structures from databases. Furthermore, #pmg provides interfaces to a number of electronic structure/DFT codes (e.g., VASP @kresse_efficient_1996, Quantum ESPRESSO @giannozzi_qe_2017, FHI-aims @blum_fhiaims_2009, CP2K @kuhne_cp2k_2020, ABINIT @gonze_abinit_2020, Q-Chem @epifanovsky2021software) and post-processing tools, such as phonopy @togo_firstprinciples_2023 @phonopy-phono3py-JPCM or LOBSTER @nelson_lobster_2020.

A crucial challenge in orchestrating heterogeneous computational workflows is normalization of the data structures used to transfer information between codes.
Separate codes typically have bespoke input and output data structures, which hinder interoperability between related simulation tools: for example, nearly all molecular DFT codes accept `.xyz` files as input to represent molecular geometries, but the precise formats used to configure calculation parameters (self-consistent field convergence criteria, force convergence criteria, basis sets, etc.) and store calculation outputs are unique to each code.

By normalizing the representation of this data, #pmg makes it easy to chain the outputs of different simulation tools when building complex workflows.
Critically, when running complex workflows, the workflow provenance, metadata, and progress are typically stored in an external database. #pmg was built with these requirements in mind, and thus supports JSON-compliant object de-/serialisation for interoperability with databases that can store JSON data.

#pmg also complements other materials science tools, most notably the Atomic Simulation Environment (ASE) @larsen_atomic_2017. While both software packages offer parsers for DFT and quantum chemistry codes, as well as tools for structure and molecule manipulation, their focuses differ. #pmg centers on complex materials data analyses @jain_computational_2016, supporting tasks from oxidation state prediction to thermal conductivity modeling. ASE emphasizes atomistic simulation using normalized crystalline and molecular data, with basic functionality similar to its analogues in #pmg. Its calculator framework integrates quantum-chemical interoperability with built-in geometry optimization and molecular dynamics functionality.

#pmg emphasizes materials-analysis objects and monty-based serialization, while ASE centers on atomistic simulation through its calculator and dynamics interfaces. Both provide persistence facilities, and conversion between their structure representations enables complementary workflows.

This distinction means that #pmg is often used in conjunction with ASE to orchestrate workflows where certain features (e.g., molecular dynamics driven by an interatomic potential) are only available in ASE. To streamline the usage of both codes, #pmg makes it possible to convert between the #pmg `Structure` object representation of a material and the ASE `Atoms` object representation. In a diverse and rapidly evolving research ecosystem, it is unrealistic and undesirable for a single code to dominate community adoption. Rather than striving for exclusivity, the focus should be on interoperability between codes, allowing users to combine the strengths of both software packages. In this way, the onus is on code maintainers to develop and maintain good relationships with their fellow developers and to ensure this interoperability is as smooth as engineering constraints allow.

This high degree of interoperability enables the seamless integration of computational materials analyses within diverse research workflows. To illustrate, one common materials science workflow for phonon calculations could involve:
+ Obtain a crystal structure from the ICSD @zagorac2019recent or Materials Project @jain_commentary_2013 @horton_2025_mp database, either manually or automatically with the #pmg API tools.
+ Use the symmetry and structure transformation tools in #pmg, built upon spglib @togo2024spglib @spglibv2, to reduce to the primitive unit cell.
+ Use #pmg to write the primitive cell to the file format required by the chosen quantum chemistry code, optionally along with other calculation input files.
+ Perform geometry relaxation with the chosen quantum chemistry code.
+ Read the relaxed structure directly into #pmg, and generate a set of supercells with displaced atoms using the `pymatgen.io.phonopy` interface.
+ Calculate forces for each displaced supercell using the chosen quantum chemistry code, keeping the displaced atomic positions fixed.
+ Parse the displaced-atom calculations with phonopy @togo_firstprinciples_2023 @phonopy-phono3py-JPCM and compute atomic force constants.
+ Plot the phonon dispersion with phonopy or the `pymatgen.io.phonopy` interface, which also supports phonon band-structure and density-of-states analysis. Analysis of Grüneisen parameters additionally requires phonon calculations at multiple volumes.

This is a simple example, but one that helps illustrate the utility of #pmg's comprehensive materials analysis functionality and wide-ranging interoperability. Computational materials research workflows now widely employ #pmg as both a core analysis toolkit and a seamless glue between quantum chemistry codes and advanced research software packages.

While #pmg supports interfaces to many codes, it should be noted that these are driven in large part by the research directions pursued within the Materials Project.
Thus, the interfaces to VASP and Q-Chem have been thoroughly developed, as they are regularly used in the Materials Project.
Other interfaces to PACKMOL @packmol, ATAT @atat, or Zeo++ @zeopp have been developed to support workflows studying non-crystalline materials, configurationally disordered crystalline materials, or material porosity, respectively.
These interfaces may overlap with those available in ASE or pyiron @janssen_pyiron_2019, but they are more often disjoint.
We make no attempt to provide a (necessarily outdated) list of codes to which #pmg natively interfaces, but we list a few which have been added or significantly enhanced since the first #pmg publication @ong_python_2013 (alphabetically): ABINIT @verstraete_Abinit2025_2025, CP2K @kuhne_cp2k_2020, icet @angqvist_icet_2019, JDFTx @sundararaman_jdftx_2017, LAMMPS @thompson_lammps_2022, LOBSTER @nelson_lobster_2020, OpenFF @wang_openff_2024, phonopy @togo_firstprinciples_2023 @phonopy-phono3py-JPCM, and Q-Chem @krylov_qchem_2020.
The extensibility of #pmg allows for rapid development of interfaces to codes as needs arise.

= Community Adoption and Impact

The growth of #pmg is reflected not only in its feature set but also in its expanding user base and community engagement across multiple materials sub-fields (@fig:mindmap). Its applications span diverse fields, including energy storage and conversion, catalysis, defects, informatics, and materials discovery via machine learning @jain_computational_2016.
Further, the influence of #pmg extends across multiple layers of the materials informatics community, from maintainers and contributors to developers of downstream software packages, direct users of #pmg, and indirect users who benefit from its functionality through the Materials Project (@fig:shells-of-influence).
This broad impact is mirrored by sustained growth in adoption: the steadily increasing numbers of downloads and of packages that require #pmg as a dependency are evidence of widespread adoption across the materials science community.
Since its publication in 2013, #pmg has been cited over 4000 times @ong_python_2013, with just under 1000 citations in 2025 alone (Google Scholar, accessed September 2026).
#pmg had approximately 23.2 million downloads from the Python Package Index (PyPI) between August 2018 and December 2025 and over 0.5 million per month in 2026, though we note that these numbers are likely inflated by automated continuous integration (CI) testing.

#figure(
  image("figs/shells-of-influence.pdf"),
  caption: [Different levels of influence within the #pmg ecosystem. From the center outward: maintainers, contributors, developers of downstream packages, direct users of #pmg, and indirect users via the Materials Project. See Supporting Information Section S2 for data sources and collection dates.],
) <fig:shells-of-influence>

== Package Ecosystem

In addition to direct usage for common materials analyses as discussed in the previous section, many packages specialized for various computational materials science research areas have been built upon the #pmg framework.
Notable downstream packages, some of which are shown in @fig:dependent-usage-of-pmg, include:

+ #link("https://github.com/materialsproject/atomate2")[atomate2] @ganose_atomate2_2025, #link("https://github.com/materialsproject/custodian")[custodian], #link("https://quantum-accelerators.github.io/quacc/")[quacc] @rosen_quacc_2025: High-throughput computational materials science workflows.
+ #link("https://github.com/materialsvirtuallab/pymatgen-analysis-diffusion")[pymatgen-analysis-diffusion] @deng_datadriven_2017: Diffusion analysis suite.
+ #link("https://doped.readthedocs.io/en/latest/")[doped] @kavanagh_doped_2024, #link("https://shakenbreak.readthedocs.io/en/latest/")[ShakeNBreak] @mosquera-lois_shakenbreak_2022: Defect modeling and structure-searching, building on #link("https://materialsproject.github.io/pymatgen-analysis-defects")[pymatgen-analysis-defects] @shen_pymatgen-analysis-defects_2024 and #link("https://github.com/mbkumar/pycdt")[PyCDT] @broberg_pycdt_2018.
+ #link("https://pymatviz.janosh.dev/")[pymatviz] @riebesell_pymatviz_2022, #link("https://smact.readthedocs.io/en/latest/")[SMACT] @davies_smact_2019, #link("https://hackingmaterials.lbl.gov/matminer/")[matminer] @ward_matminer_2018: Materials informatics toolkits.
+ #link("https://matbench-discovery.materialsproject.org/")[matbench-discovery] @riebesell_framework_2025, #link("https://www.air4.science/")[AIRS] @zhangArtificialIntelligenceScience2025, #link("https://github.com/materialsvirtuallab/matgl")[MatGL] @ko_materials_2025, #link("https://github.com/torchsim/torch-sim")[torch-sim] @cohen_torchsim_2025: Machine learning for materials science.
+ #link("https://pyxtal.readthedocs.io/en/latest/")[PyXtal] @fredericksPyXtalPythonLibrary2021: Generation and manipulation of atomic structures with symmetry constraints.
+ #link("https://jageo.github.io/LobsterPy/")[LobsterPy] @naik_LobsterPypackage_2024: Automatic analysis of LOBSTER outputs for summarized bonding information.
+ #link("https://hackingmaterials.lbl.gov/amset/")[AMSET] @Ganose2021: Electronic transport property modeling.

This diversity of downstream packages demonstrates #pmg's extensibility and its foundational role in the materials modeling and informatics ecosystems @butler_machine_2018.
Of course, #pmg itself builds on foundational open-source Python packages, such as NumPy @harris_array_2020, SciPy @virtanen_scipy_2020, and pandas @team_pandasdev_2025 @mckinney_data_2010 for numerical operations, Matplotlib @hunter_matplotlib_2007 and Plotly @plotly for plotting, spglib @togo2024spglib @spglibv2 for symmetry analyses, NetworkX @hagberg2007exploring for graph analysis, and monty for serialization, as shown in @fig:package-ecosystem.

#place(top + center, float: true, scope: "parent")[
  #figure(
    {
      grid(
        columns: 2,
        gutter: 2em,
        subfigure(
          pad(left: -5em, image("figs/pmg-dependency-usage.pdf")),
          caption: [Upstream usage of third-party Python packages (left) by #pmg subpackages (middle).],
          dy: -1em,
          label: <fig:pmg-dependency-usage>,
        ),
        subfigure(
          pad(right: -5em, image("figs/dependent-usage-of-pmg.pdf")),
          caption: [Downstream usage of #pmg subpackages (middle) by dependent packages (right).],
          dy: 3pt,
          label: <fig:dependent-usage-of-pmg>,
        ),
      )
      place(center + horizon, dy: -5%, image("figs/pymatgen-2-logo.pdf", width: 8em))
    },
    caption: [Upstream and downstream usage relationships of #pmg subpackages. Link width indicates the number of statically detected API call sites in the analyzed source code. The panels show selected dependencies and downstream repositories; repository selection and filtering are described in Supporting Information Section S3. These subpackages broadly correspond to three common modes of #pmg usage: input/output (`io`), manipulation of materials objects (`core`), and analysis or simulation-enabling functionality (`analysis`).],
  ) <fig:package-ecosystem>
]

Cumulatively, #pmg's impact on the materials science community includes:

+ Accelerated research across various domains @butler_machine_2018, including the rapid development of specialized materials analysis toolkits (@fig:dependent-usage-of-pmg).
+ Standardization of core materials analysis procedures.
+ Improved reproducibility through user-friendly serialization and analysis tools.
+ Provision of accessible educational tools for students and early-career researchers @ong_python_2013, such as https://github.com/materialsvirtuallab/matgenb and https://github.com/sp8rks/MaterialsInformatics.
+ Adoption in industrial research and development workflows @jain_commentary_2013 @horton_2025_mp.
+ Promotion of open science and collaborative development @horton_promises_2021.

== Case Studies

As discussed above, many advanced materials analysis packages have been built upon the #pmg codebase to enable complex domain-specific research workflows.
Below, we briefly discuss two such cases where the #pmg framework has facilitated advanced, complex materials analyses.

=== Defect Modeling Tools

Defect modeling is a rapidly growing field, driven by advances in computational power and methods which make these calculations increasingly tractable, along with the critical importance of defect species to diverse materials technologies, such as transistors, solar cells, transparent conducting materials, batteries, qubits and more @Yan2024.
Defect simulation can be a long and complex process, as it requires many different tasks @kumagai_insights_2021 @kavanagh_doped_2024 @freysoldt_firstprinciples_2014, including structure manipulations, symmetry analyses, input file generation and output parsing for electronic structure codes, lightweight metadata and serialization for reproducibility, and interfaces with databases such as the Materials Project for phase diagram analysis.
Moreover, many of these tasks have specific requirements in the specialized case of defects.
These include efficient and appropriate supercell generation (to balance computational cost and accuracy), determination of defect point symmetries, configurational degeneracies, and site multiplicities (in symmetry-breaking supercells), targeted distortions for structure-searching, efficient algorithms for large and complex structure analyses, smart algorithms for sub-phase diagrams, and more @squires_guidelines_2026.

Several open-source toolkits have now been developed which make use of core functionalities in #pmg to implement stages of the defect modeling workflow, including doped @kavanagh_doped_2024 (@fig:dependent-usage-of-pmg), pydefect @kumagai_insights_2021, PyCDT @broberg_pycdt_2018, pymatgen-analysis-defects @shen_pymatgen-analysis-defects_2024, ShakeNBreak @mosquera-lois_shakenbreak_2022, AiiDA-defects @muy_aiida-defects_2023 and pydecs @ogawa_extended_2022.
These toolkits are seeing widespread usage in the defect modeling community, helping to accelerate research in this technologically crucial area, while reducing human errors and lowering the barrier to entry for new researchers.
Here, the wide functionality and flexible, modular structure of #pmg has been a key enabler of these downstream developments, allowing #pmg functions to be tailored to specialized use cases.

One particularly promising aspect of these developments is that they have greatly reduced the burden of data sharing and reproducibility in defect simulations---a particularly challenging task given the many steps involved @squires_guidelines_2026.
Through the object-oriented architecture and efficient serialization tools provided by #pmg and its monty dependency for JSON (de)serialization, the human effort to collate and export complete metadata and calculation provenance is significantly diminished.
These developments are helping to establish clear community standards and expectations for reproducibility, strengthening the quality of defect modeling research while ensuring robust foundations for future database and machine learning efforts in this area @squires_guidelines_2026.

=== Data-Driven Heuristic Assessment and Machine Learning <sec:heuristics>

#pmg is a powerful toolkit that enables large-scale data analysis and machine learning studies in materials science.
These capabilities are essential for uncovering new design principles for specific material properties and for developing feature-based machine learning models, the latter frequently serving as a core component in Materials Acceleration Platforms (MAPs) and self-driving labs @flores-leonar_materials_2020 @stier_materials_2024.

Through #pmg's direct interfaces to materials databases (the Materials Project API, now spun off as its own package, or the OPTIMADE API @andersen2021optimade), researchers can easily retrieve extensive datasets, including machine learning targets, which serve as the foundation for data-driven assessments of design principles and heuristics, as well as the development of machine learning models.
When working with other crystal structure sources such as the Cambridge Structural Database @groom2016cambridge, Inorganic Crystal Structure Database @zagorac2019recent or MAGNDATA @gallego2016magndata, #pmg's ability to parse (magnetic) Crystallographic Information Files (CIFs) directly into the input objects needed for atomistic simulation facilitates the creation of large, structured datasets.
#pmg allows simplified filtering by composition or crystal symmetry, depending on requirements.
Additionally, many post-processing features are available in #pmg, simplifying the generation of targets.

Chemical heuristics have frequently been used to inspire design principles or features in machine learning models. Such features are extremely valuable, as they provide physically and chemically interpretable descriptors that not only improve model interpretability but can also serve as scientific consistency checks for machine learning outputs.
Many such descriptors and design principles---such as those related to stability, synthesisability, defect energetics, and magnetism---rely on accurate determinations of oxidation states and coordination environments, both of which can be assessed within #pmg.
#pmg implements several heuristics to determine oxidation states (e.g., based on bond valence sums or simple composition-based guessing methods) and to determine coordination environments (e.g., based on minimum distances or Hoppe's effective coordination numbers, and more advanced approaches implemented in the `local_env` and `chemenv` modules) @pan_benchmarking_2021 @waroquiers_chemenv_2020.
Additionally, #pmg is deeply integrated with matminer @ward_matminer_2018, a library that streamlines the generation of popular features for machine learning workflows, further supporting the derivation and validation of heuristics.
Here, #pmg objects are used directly as input for creating machine learning features.

In summary, #pmg provides a framework for materials data handling, feature extraction, and heuristic development, making it an essential tool for modern, data-driven materials informatics.
By codifying chemical, crystallographic, and physical knowledge into reusable data structures, descriptors, and analysis workflows, #pmg transforms expert domain knowledge into a scalable resource for data-driven materials discovery.

=== Transferability and Lessons Learned <sec:addnl>

Numerous other case studies demonstrate the impact of #pmg across materials modeling sub-fields, including low-dimensional materials, surface slab generation and analysis, high-throughput materials discovery and automated workflows, and magnetic structure enumeration.

The success of sub-field-specific modeling packages built on #pmg demonstrates that providing robust functionality for common tasks---such as structure manipulations, oxidation state estimation or input/output for DFT codes---allows domain experts to readily extend it to more specialized research workflows.
By implementing these core materials analysis functions in a modular code structure, which can be readily imported into downstream packages, #pmg removes the need to re-implement common tasks and allows practitioners to focus on specialized domain-specific analyses (e.g., predicting defect concentrations). In this way, some functionalities have effectively become community reference points for specific tasks within the field (e.g., `StructureMatcher`), with methodological choices and default parameters adopted broadly through the software's widespread use. Packages such as #pmg, through their widespread use and expert oversight, can serve as important touchstones for the community, helping to promote consistent practices and methodologies. As a result, a natural form of standardization can emerge, with widely adopted implementations shaping common approaches to computational materials analysis.
Another aspect that has proven important to the success of these advanced simulation workflows is the use of computationally efficient implementations in core #pmg modules, through intelligent algorithms, vectorisation, Cython code, or other methods.
This ensures efficiency and scalability in downstream uses, enabling complex workflows built on #pmg, such as high-throughput screening across immense materials search spaces or structural analyses of large, low-symmetry defect supercells. At the same time, performance optimizations must be balanced against code readability, maintainability, and ease of understanding, as these are essential to encouraging community contributions and ensuring the project's long-term sustainability.

Finally, clear communication about code deprecations and breaking changes is crucial for the smooth, uninterrupted development and maintenance of the many downstream scientific packages that rely on #pmg.

= New Features <sec:new-features>

The growth of #pmg closely follows trends in materials science research, reflecting its critical role in advancing science.

Modeling of Li- and Co-alternative battery electrodes has long driven atomistic analysis tools in #pmg.
The pymatgen-analysis-diffusion extension @shen_topological_2023 grew out of a smaller submodule of diffusivity analysis tools, which were eventually migrated to a separate namespace package.
These tools enable faster estimates of ionic mobility from molecular dynamics trajectories.
They also include tools to identify likely topotactic ion insertion defect sites based on electronic charge densities @shen_charge_2020, used when estimating ionic mobility from transition-state type mappings of the potential energy surface.

More recently, machine learning (ML) methods @butler_machine_2018, particularly MLIPs @chen_universal_2022, have emerged as practical ways to rapidly estimate atomic structure without more costly recourse to electronic structure methods.
#pmg has integrated some of these structural prediction tools via the external MatGL Python package @ko_materials_2025.
This allows users to, e.g., quickly relax crystal structures using common graph neural network MLIPs such as M3GNet @chen_universal_2022, CHGNet @deng_chgnet_2023, TensorNet @simeon_tensornet_2023, and MatPES-derived models @kaplan2025matpes.
MLIPs can also be used directly in #pmg to estimate small-cell ordered representations of disordered materials by enumerating possible orderings and selecting the predicted minimum-energy configuration.

Analysis of local coordination environments has also been of critical importance in understanding the connections between atomic structure and materials characteristics.
These insights help identify structural motifs that lead to similar performance, e.g., frameworks which favor ionic mobility.
#pmg facilitates the analysis of electronic charge densities and electronic bonding by interfacing with LOBSTER @nelson_lobster_2020.
#pmg allows for computationally tractable analysis of local atomic coordination environments using, e.g., the ChemEnv @waroquiers_chemenv_2020 and CrystalNN @zimmermann_crystalnn_2020 methods (see also @sec:heuristics).
CrystalNN can be further used to generate structural embeddings similar to the feature vectors of MLIPs, which in turn allow for rapid estimates of structural similarity @zimmermann_crystalnn_2020 and automatic generation of human-readable descriptions of materials with the robocrys package @ganose_robocrys_2019.
Local coordination environment analysis from ChemEnv, CrystalNN similarity estimates, and CrystalNN-based generated descriptions of materials are now standard analysis products of the Materials Project's build pipelines, and are currently distributed as part of its core data.

Other extensions to #pmg that can be separately installed under the `io` and `analysis` namespaces include, but are not limited to: validation of VASP @kresse_ultrasoft_1999 calculations for compatibility with the Materials Project @horton_2025_mp via pymatgen-io-validation; orchestration and parsing of FHI-aims @blum_fhiaims_2009, Quantum ESPRESSO @giannozzi_qe_2017, and FLEUR @wortmann_fleur_2023 electronic structure calculations via pymatgen-io-aims, pymatgen-io-espresso, and pymatgen-io-fleur, respectively; orchestration of classical molecular dynamics calculations with OpenMM @eastman_openmm_2023 via pymatgen-io-openmm; and core defect functions in pymatgen-analysis-defects @shen_pymatgen-analysis-defects_2024.
A more complete list of extensions to #pmg is maintained in the add-ons section of the documentation.

As illustrated in @fig:pr-topics and @fig:commits-heatmap, development activity has been sustained across multiple subpackages for over a decade, with contributions spanning bug fixes and refactoring, structural and I/O functionality, testing and code quality, documentation, and performance improvements.

#place(top + center, float: true, scope: "parent")[
  #figure(
    grid(
      columns: (1fr, 2fr),
      gutter: 1em,
      subfigure(
        image("figs/pr-topics-over-time-stacked-bar.pdf"),
        caption: [Merged non-bot pull requests by merger year and title-based theme.],
        dy: 2.4em,
        label: <fig:pr-topics>,
      ),
      subfigure(
        image("figs/commits-per-package-heatmap.png"),
        caption: [Commits per #pmg package over time, aggregated into calendar half-years on a logarithmic color scale.],
        dy: 1.5em,
        label: <fig:commits-heatmap>,
      ),
    ),
    caption: [Development activity in the #pmg repository. (a) All 2,494 non-bot pull requests merged through 31 December 2025, each assigned once by ordered keyword rules; unmatched titles are retained as Other / unclassified. Themes are approximate title-based categories. (b) Commits per package in calendar half-years (January--June and July--December) from 2012 through 2025.],
    gap: 3em, // room for the placed subfigure captions
  ) <fig:development-activity>
]

= Challenges and Solutions

Maintaining and evolving a project of #pmg's scale over more than a decade presents unique technical, organizational, and community challenges that offer valuable lessons for the broader scientific software community. Our experience highlights the importance of balancing sustainability, interoperability, governance, contributor onboarding, and community growth. We discuss key challenges encountered and possible approaches to addressing them.

== Sustainability and Maintainer Resources

Perhaps the most critical challenge facing mature open-source scientific software is long-term sustainability.
Unlike commercial software with dedicated development teams, #pmg has evolved primarily through volunteer contributions from academic researchers, for whom software development competes with research publications, teaching, and other career pressures.
This model, while fostering community ownership, introduces structural tensions in maintenance, code review capacity, and long-term feature development.

The Materials Project has provided crucial institutional support, including dedicated development and engineering staff, computational resources, and organizational infrastructure.
By providing infrastructure and maintenance, #pmg has established itself as a host for analysis- and application-specific materials science code that might otherwise never have been made public or reusable.
This hybrid model (combining institutional backing with community contributions) has proven essential for #pmg's longevity.
Yet acquiring funding for software maintenance remains challenging, as grant agencies strongly favor novel research over infrastructure upkeep.
Projects like FAIRmat @fairmat_web_2025, as part of the German national research data infrastructure, and the Molecular Sciences Software Institute (MolSSI) @molssi_web_2025 represent important steps toward recognizing computational and data infrastructure as crucial research infrastructure deserving of sustained investment.

#pmg has cultivated a globally distributed contributor base (@fig:contributors-worldmap) with a continual influx of new contributors (@fig:pr-since-1st), which affords some resilience to changing resource situations at any one institution.
However, the concentration of maintenance burden on a small number of core developers remains an ongoing concern.
We hope that clear contribution guidelines, responsive code review, and explicit recognition of contributors (through authorship opportunities, acknowledgements in papers, and community visibility) can help sustain engagement and grow the pool of active maintainers.

This incremental-development perspective aligns with _Digital Discovery_'s recent Commit article concept @aspuru_commit_2025, which formalizes citable reporting of improvements to prior software, data, and hardware publications.
While the present manuscript contains a full retrospective, the underlying motivation is similar: to incentivize and reward sustainable scientific software development through transparent, community-driven iteration.
Sustained progress still depends on stable funding, explicit onboarding pathways, and incentive structures that recognize maintenance work. We outline some strategies in the following sections.

== Backwards Compatibility and API Evolution

A fundamental tension in mature software libraries is balancing API stability against the need for improvements.
#pmg has accumulated technical debt from early design decisions, e.g., inconsistent syntax for parsing Python objects from files, inefficient JSON representations of Python objects, complex object-oriented inheritance, and a proliferation of similar objects.
These challenges are known to #pmg developers, and addressing them requires careful assessment to preserve backwards compatibility without impeding further development.
Because #pmg uses calendar versioning (`YYYY.MM.DD`), which does not encode the magnitude of changes, users currently need to consult the release notes to assess the upgrade impact.

With thousands of users and hundreds of dependent packages, #pmg bears significant responsibility for API stability.
Breaking changes can cascade through the ecosystem, disrupting research workflows and requiring coordinated updates across multiple projects.
To manage this, #pmg is adopting established deprecation best practices: deprecated features emit a `FutureWarning` with clear removal timelines (typically 6--12 months), giving downstream maintainers time to adapt.
Major changes are communicated through release notes, GitHub discussions, and the matsci.org forum.
The namespace package architecture (`pymatgen-io-*`, `pymatgen-analysis-*`) further enables specialized APIs to evolve independently, reducing the impact of breaking changes on the core library.

For mature infrastructure libraries, backwards compatibility is a community contract. Incremental deprecations with predictable removal timelines are imperative for evolving a codebase with a user base as large as #pmg's while minimizing the impact on downstream research.

== Test Coverage and Code Quality

As shown in @fig:pmg-code-structure, the 31 July 2025 coverage report records 60,242 covered statements out of 76,389 executable Python statements (78.9%), though coverage varies significantly by module. Coverage is 90.2% for `core`, 85.8% for `entries`, and 83.6% for `io`, while visualization (`vis`) has 13.9% coverage. Both cell areas and coverage percentages are derived from this report, with package coverage calculated from summed covered and executable statements.
This heterogeneity reflects genuine trade-offs: some modules require licensed external executables (VASP, Gaussian) for meaningful testing, others involve long-running operations, and visualization code requires rendering backends that complicate headless CI.
Testing resources have been strategically focused on core modules serving the largest user bases.

CI via GitHub Actions has been an important quality-control mechanism.
The specifics of the CI have varied over time, but have typically included running the pytest test suite (or a comparable test suite) on every pull request across multiple Python versions.
Test coverage is also tracked and reported.
CI has benefited from the Python ecosystem's rapid migration of developer tools to Rust, which has significantly accelerated #pmg's CI pipelines and local development workflows.
In particular, static type analysis (e.g., mypy, Pyright) has helped catch subtle bugs at development time that would otherwise only surface during testing or production.
Looking ahead, the Rust-based type checker ty (once a stable release is available) is fast enough to run in tight feedback loops with LLM coding agents, catching type errors in seconds rather than minutes, even for codebases as large as #pmg.
This could enable rapid iteration toward correct code without waiting for much slower test suites to complete.
Pre-commit hooks enforce these checks locally.
However, unit tests are still necessary, and the test suite's slow execution time, currently over half an hour despite parallelisation, still creates friction for contributors.
Improving test efficiency remains an ongoing priority.

The emergence of frontier large language models (LLMs) is significantly reducing #pmg's maintenance burden.
Tasks like writing tests, adding type annotations, improving docstrings, and refactoring legacy code can now be accelerated with LLM assistance.
This is particularly valuable given the backlog of technical debt accumulated over 15 years.
AI-powered code review tools like #link("https://coderabbit.ai")[CodeRabbit], #link("https://cursor.com/bugbot")[Cursor Bugbot] or #link("https://code.claude.com/docs/en/code-review")[Claude Code] can further reduce maintainer workload by providing automated first-pass reviews on pull requests.
While early attempts at LLM-based code review on large codebases often introduced noise (e.g., overly verbose reviews) due to limited context windows and model capabilities, these tools have matured significantly and now handle complex change sets reliably, catching real issues that would otherwise require slow and arduous manual inspection.
LLMs also lower contribution barriers by helping newcomers navigate unfamiliar code.
These AI-assisted tools have meaningfully increased throughput for #pmg's small maintainer team. At the same time, careful review remains critical to ensure that AI-assisted contributions meet community standards for correctness, maintainability, and scientific reliability, and that contributors retain sufficient understanding of the resulting code to support its long-term stewardship.

Quality at scale is best achieved through layered safeguards rather than any single metric.
Fast static type and format checks, targeted issue-driven unit tests, and human-reviewed AI assistance together provide better reliability per maintainer-hour than focusing on any subset of these tools.

== Governance and Onboarding of Contributors and Users

As a core component of the Materials Project's analysis tools, #pmg is governed according to principles established by the Materials Project stakeholders, which are in turn inspired by the best practices adopted by established community organizations like NumPy @harris_array_2020 and NumFOCUS.
Collectively, the Materials Project (MP) members and software stakeholders responsible for adopting and enforcing codes of conduct were known as the Materials Project Software Foundation (MPSF). The MPSF worked to establish a democratic governance structure for the MP software ecosystem and, for example, facilitated the inclusion of MP software in the NumFOCUS foundation index.

These codes of conduct foster a welcoming environment for new contributors, aiming to cultivate longer-term community engagement that, in turn, benefits #pmg.
As #pmg continues to expand in scope beyond the means of a small team of core maintainers, community engagement in maintaining its more niche feature sets is imperative, and welcoming new contributors is vital to #pmg's long-term sustainability.
Over the last 10 years, the number of active contributors has generally ranged between approximately 30 and 75 per year, peaking in 2019 (@fig:active-contributors). The last 5 years have shown a slight decline in active contributors, making governance and onboarding strategies even more important. The annual number of commits shows a similar trend, although commit sizes vary significantly.

Our experience suggests that successful community growth depends not only on attracting contributors but also on establishing processes that make it easy to submit, review, reproduce, and maintain contributions. We believe that #pmg's broad adoption cannot be attributed solely to its technical capabilities. A comparatively low barrier to contribution and a culture of responsive code review have played important roles in growing and sustaining the contributor community. Structured issue reporting, contribution templates, automated testing, and layered code review have all been important in enabling #pmg to scale beyond what could be supported by a small number of maintainers. Together, these practices help ensure that new functionality developed by the community can be incorporated efficiently, reducing friction for contributors and encouraging long-term engagement.

As junior community members contribute to #pmg, they will eventually be invited to take on maintainer roles for sections of #pmg.
Junior maintainers who express interest in maintaining the core feature set will be deputized by more experienced maintainers to handle day-to-day maintenance.
This ensures both that community-submitted issues are addressed in a timely fashion and that more experienced maintainers can address larger questions of software direction, optimization, etc.
Because the analysis tools of #pmg are integral to MP's workflows and data pipelines, these features are virtually guaranteed to be maintained as long as MP continues its mission.
However, the more peripheral features of #pmg will require this kind of community-driven maintenance structure to prevent them from becoming unmaintained and non-functional.

An important lesson from #pmg's growth is that a healthy open-source ecosystem extends beyond code contributors. Community discussion forums and support channels such as the matsci.org forum play a critical role in user onboarding, dissemination of best practices, and the identification of future contributors and maintainers. These resources help scale support beyond the core development team's capacity while strengthening community engagement.

Equally important has been the transfer of expertise through academic mentorship and research networks. Many new contributors and users were trained in groups that already had experience with #pmg, allowing knowledge, development practices, and community norms to be passed on to students, postdoctoral researchers, and collaborators. As these researchers moved to new institutions and established their own groups, they acted as multipliers, broadening adoption and cultivating the next generation of contributors and maintainers. This combination of formal community support structures and person-to-person knowledge transfer has been a key factor in sustaining #pmg's growth and impact.

== Dependencies and Dependents

As discussed in previous sections, a large ecosystem of materials science codes depends on #pmg (see @fig:dependent-usage-of-pmg), while #pmg itself depends on the open-source ecosystem for scientific computing, plotting, and data science (@fig:pmg-dependency-usage).
As a core component of the base layer of computational materials science infrastructure, sitting between foundational packages and hundreds of downstream dependents, #pmg's dependency management has ecosystem-wide implications.
#pmg follows the Scientific Python community's SPEC 0 policy @spec0_minimum_supported_dependencies, specifying minimum-version constraints but avoiding upper-version caps to prevent resolver conflicts in downstream packages.
When upstream libraries introduce breaking changes---as occurred with the NumPy 2.0 C API transition #cite(<harris_array_2020>)---#pmg must adapt promptly, often ahead of its own dependents, to avoid blocking the wider ecosystem.
This bidirectional responsibility is a recurring theme in maintaining community infrastructure: changes propagate both up and down the dependency graph, and delayed adaptation in either direction compounds across the ecosystem, underscoring that widely adopted software like #pmg requires a responsive maintainer team to avoid becoming a bottleneck for the broader ecosystem.

#figure(
  image("figs/pr-since-1st.pdf"),
  caption: [Annual merged non-bot #pmg pull requests grouped by contributor tenure at merger, measured from the author's first PR submission, including unmerged submissions. Years denote merger dates; all 2,494 PRs merged through 31 December 2025 are included, matching @fig:pr-topics. Tenure bins are disjoint, with one year defined as 365.25 days.],
) <fig:pr-since-1st>

#place(top + center, float: true, scope: "parent")[
  #figure(
    pad(x: -3em, image("figs/pr-contributors-worldmap.pdf", width: 90%)),
    caption: [Geographic distribution of #pmg pull requests by contributor country. Countries were inferred from GitHub profile and affiliation snapshots, supplemented by manually curated mappings; these do not necessarily represent locations at the time of each contribution. The map omits 67 of 276 contributors with no country assignment, accounting for 136 of 2,498 merged PRs. See Supporting Information Section S6 for data sources and collection dates.],
  ) <fig:contributors-worldmap>
]

#place(top + center, float: true, scope: "parent")[
  #figure(
    pad(right: -2em, image("figs/py-pkg-treemap-pymatgen-coverage.pdf")),
    caption: [#pmg Python code structure and line coverage in the 31 July 2025 coverage.py report. Cell area represents executable statements and color represents the fraction covered by tests. Parent percentages use summed covered and executable statements. Modules are grouped to at most three path components, with groups below 1,500 statements combined into `other` cells and subpackages below 5,000 statements shown as single cells.],
  ) <fig:pmg-code-structure>
]

#figure(
  image("figs/active-contributors-colored.pdf"),
  caption: [Number of active contributors and non-merge commits per year to #pmg from 2012 through 2025.],
) <fig:active-contributors>

= Outlook and Future Developments

#pmg has evolved from a specialized tool into a cornerstone of computational materials science.
Its growth reflects the collaborative spirit of the materials informatics community and the importance of open-source software in scientific research.

While the core features of #pmg are relatively stable, more peripheral features require constant community review beyond the stewardship of a small team of maintainers.
Improving the performance of the most essential #pmg libraries is key to its growth.
#pmg introduced namespace packages in #link("https://github.com/materialsproject/pymatgen/commit/f462d35c")[v2022.0.0] (March 2021), which allowed the independent installation and maintenance of #pmg "add-on" packages within the #pmg "namespace", i.e., importable from `pymatgen.io` and `pymatgen.analysis`.
Critically, this decouples the release cadence of add-on packages from that of the core library---enabling the higher release frequency often needed during a package's early development without being blocked by the slower, more deliberate release cycle of #pmg itself.
This is further supported by the standalone `pymatgen-core` package, now a dependency of #pmg, which provides fundamental materials science data structures together with I/O and analysis functionality for other developers to build upon.

At its current scope, expanding and refining the feature set of #pmg would benefit from a larger development team to ensure effective stewardship.
As #pmg continues to grow in scope and adoption, we frame the next steps as high-impact community opportunities.
In particular, broader shared ownership of maintenance tasks (code review, issue triage, and bug fixes in niche submodules) can strengthen participation and long-term stewardship.
As contributors gain experience in these roles, they can naturally grow into deputy reviewer and maintainer positions.

There are many active areas of materials science that could benefit from extensions of #pmg's key feature set.
These include a wider variety and greater depth of control over `io` extensions for popular electronic structure (e.g., Quantum ESPRESSO), atomistic (e.g., LAMMPS, GROMACS), and continuum, phase-field and multiphysics codes.
However, as noted previously, any extension of functionality that is not in a separately installable namespace package would require concomitant community review.

While community forums such as #link("https://matsci.org")[matsci.org] and the #pmg issue tracker provide important support, there is significant opportunity to scale the documentation to match the library's breadth. A promising direction for this expansion is a community-reviewed, LLM-assisted workflow, which could improve coverage without increasing the burden on core maintainers.

High-impact development opportunities informed by community needs and emerging trends in materials science include:

*Machine learning integration* is likely to remain important as ML methods increasingly enter materials discovery and design @butler_machine_2018. High-value contributions include native support for modern frameworks (PyTorch, JAX), efficient structure-to-graph conversions for neural network architectures, and stronger integration with benchmarking frameworks like Matbench Discovery @riebesell_framework_2025.

*Visualization and user experience* improvements through tighter integration with Crystal Toolkit @horton_crystal_2023, pymatviz @riebesell_pymatviz_2022, and MatterViz @riebesell_matterviz_2025 could lower barriers to entry. Useful community efforts include enhanced Jupyter notebook support, interactive structure manipulation, and publication-ready figure generation.

*Performance optimizations* remain a major opportunity, especially via strategic use of compiled extensions. #pmg now operates in a different regime than at its inception: in early development, #pmg was used to orchestrate much slower DFT calculations, and the additional overhead from Python and its heavily object-oriented software structure was negligible. Today, however, with the rise of very fast MLIP simulations, this overhead is significant, and deeper optimization is increasingly valuable. A successful example is the moyo project @moyo, which migrated the symmetry analysis tools of spglib to Rust while maintaining an easy-to-use Python API via bindings. Similar approaches could accelerate frequently used, compute-intensive operations such as structure matching, neighbor searching, convex hull calculations, and more.

*Extension package ecosystem* growth will strengthen #pmg's federated architecture: a stable core supplemented by domain-specific namespace packages (e.g., pymatgen-analysis-diffusion @deng_datadriven_2017, pymatgen-io-openmm) maintained by experts. Increasing the number and quality of these extensions distributes the maintenance burden while enabling rapid iteration in specialized domains. New functionality areas---such as multi-scale modeling bridging atomistic and mesoscale simulations---are best developed as extension packages rather than by expanding the core.

*GPU compatibility:* A promising direction is broader support for tensor backends (e.g., PyTorch) in array-heavy code paths, enabling GPU acceleration and potential speedups for large-scale analyses.

*Agentic AI tools:* #pmg functions could be exposed to LLM-based agents through tool interfaces, including Model Context Protocol (MCP) servers. monty serialization can facilitate data exchange, while explicit tool implementations, schemas, and input validation support reliable tool use. These tools can provide access to chemistry, materials science, and physical analysis capabilities to support agent workflows.

We invite contributions at all levels---from bug reports and documentation improvements to new features and extension packages. The project's GitHub repository, documentation site, and community forums provide entry points for new contributors.

#heading(numbering: none)[Use of AI tools]

Large language models were used in parts of the analysis: OpenAI GPT-5 grouped OpenAlex topics into thematic branches for @fig:mindmap (Supporting Information Section S1), and OpenAI GPT-4o mapped institutional affiliations to countries for contributors without a GitHub profile location in @fig:contributors-worldmap (Supporting Information Section S6). Copilot GPT-5.6 was used to unify the author contribution statements drafted by each co-author. Copilot was also used for brainstorming, translation, language editing, text revision, and proofreading during manuscript preparation. The authors reviewed, edited where necessary, and verified all text. LLM coding assistants, including Anthropic's Claude, helped write the figure and analysis scripts and were used to check consistency between the main text, figures, and Supporting Information. All outputs were checked by the authors.

#heading(numbering: none)[Data availability]

Code to reproduce the analysis and figures presented in this manuscript is available at https://github.com/janosh/pymatgen-2-paper.

#heading(numbering: none)[Author contributions]

Writing -- Original Draft, Writing -- Review & Editing: Janine George, Matthew K. Horton, Aaron D. Kaplan, Seán R. Kavanagh, Janosh Riebesell, Andrew S. Rosen, Haoyu Yang, Anubhav Jain, Shyue Ping Ong. Methodology and Software: all authors. Software contributions were made to the openly accessible repository on GitHub. For details on the software contributions of all authors, please refer to the Supporting Information.

#heading(numbering: none)[Conflicts of interest]

Anthony Onwuli is currently an employee of MatNex and holds options in the company. His software contributions to #pmg were made prior to joining MatNex. Michael Wolloch is an employee of VASP Software GmbH.

#heading(numbering: none)[Acknowledgements]

We thank the numerous developers, researchers, and users who have contributed to #pmg over the years. We also acknowledge the funding agencies and institutions that have supported its development, including the U.S. Department of Energy, the National Science Foundation, and various academic institutions.

Special thanks go to the broader open-source scientific computing community for their invaluable tools and libraries, especially NumFOCUS and their efforts around NumPy @harris_array_2020, pandas @mckinney_data_2010 @team_pandasdev_2025 and Matplotlib @hunter_matplotlib_2007, all of which #pmg heavily relies on.

This work was intellectually led and primarily supported by the Materials Project, funded by the U.S. Department of Energy under award DE-AC02-05CH11231 (Materials Project program KC23MP).
Tom Demeyere, Janine George and Aakash Naik were supported by ERC Grant MultiBonds (grant agreement Nº 101161771; funded by the European Union. Views and opinions expressed are, however, those of the author(s) only and do not necessarily reflect those of the European Union or the European Research Council Executive Agency. Neither the European Union nor the granting authority can be held responsible for them). Furthermore, Tom Demeyere, Janine George, Aakash Naik and Katharina Ueltzen acknowledge the Gauss Centre for Supercomputing e.V. (www.gauss-centre.eu) for funding the code developments by providing generous computing time on the GCS Supercomputer SuperMUC-NG at Leibniz Supercomputing Centre (www.lrz.de) (Project No. pn73da). Janine George is also part of the NFDI consortium FAIRmat, funded by the Deutsche Forschungsgemeinschaft (DFG, German Research Foundation), project 460197019.
Seán R. Kavanagh acknowledges membership of the UK's HEC Materials Chemistry Consortium, which is funded by EPSRC (EP/X035859) and provided access to the ARCHER2 UK National Supercomputing Service (http://www.archer2.ac.uk) for code developments.
Andrew S. Rosen acknowledges support from the Princeton Office of the Dean for Research (ODFR) and Meta. Gian-Marco Rignanese is Research Director of the Fonds de la Recherche Scientifique -- FNRS.
Haoyu Yang was supported by the NFDI consortium FAIRmat, funded by the Deutsche Forschungsgemeinschaft (DFG), project 460197019.
Noam Bernstein's work was supported by the U.S. Naval Research Laboratory's base program.
Brandon Bocklund's work was performed under the auspices of the U.S. Department of Energy by Lawrence Livermore National Laboratory (LLNL) under Contract DE-AC52-07NA27344.
Part of the work at LLNL was funded by the Laboratory Directed Research and Development Program under project tracking code 26-SI-001.
Matthew C. Kuner was supported by the National Science Foundation Graduate Research Fellowship Program under Grant No. DGE-2146752.
Ihor Radchenko was supported by a KEYTECH grant (project number WPC3/2022/50/KEYTECH/2024, National Centre for Research and Development, Poland) and by the Teaming Horizon 2020 programme (GA No. 857543) of the European Commission.
Nav Nidhi Rajput's work was supported by the U.S. National Science Foundation (CSSI-2514002).
Kaifeng Zheng was supported as part of the Molten Salts in Extreme Environments Energy Frontier Research Center, funded by the U.S. Department of Energy (DOE), Office of Science, through a subcontract from Brookhaven National Laboratory, which is operated under DOE Contract No. DE-SC0012704.
Shyue Ping Ong also acknowledges funding support from the National University of Singapore Materialyze.AI Startup Grant under WBS No. A-0010359-00-00.

#bibliography("refs.bib", style: "ieee")
