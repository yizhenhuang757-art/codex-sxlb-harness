# Bilingual GitHub Pages Documentation Design

## Goal

Make the public SXLB harness immediately usable while giving interested readers a rigorous, accessible explanation of the 三省六部 model that inspired its governance design.

## Audience and language model

- English and Simplified Chinese readers receive complete, corresponding documentation.
- Chinese is a first-class documentation language for researchers who work with Chinese institutional history.
- The Chinese and English pages must carry the same claims, information architecture, and navigation targets; neither is a summary of the other.

## Publishing approach

Use a dependency-free GitHub Pages site built from Markdown in `docs/`, with Jekyll collection-style pages and a small shared stylesheet. Configure Pages to deploy from the `docs/` directory on `main`, avoiding a custom build workflow and its additional token scope requirement.

## Information architecture

The site has English and Chinese roots, each with the same order:

1. Installation and quick start
2. Expected outcomes and when to use SXLB
3. Feature overview
4. Workflow and command reference
5. Historical background: the three departments and six ministries
6. SXLB mapping and extended design rationale

The home page gives newcomers an installation path and example outcome first. The historical material is intentionally later in the flow, so conceptual depth is available without blocking adoption.

## Historical explanation

The documentation explains the conventional high-level model:

- 中书省: policy drafting and formulation
- 门下省: deliberation, review, and remonstrance
- 尚书省: coordinated administration and execution
- 吏、户、礼、兵、刑、工部: personnel; finance and households; rites, education, and diplomacy; military administration; justice; public works

It also states that institutional responsibilities varied across periods and that this is a pedagogical model rather than a claim that SXLB recreates an imperial government.

## SXLB mapping

The site describes SXLB as a contemporary harness that borrows a sequence of proposal, independent review, accountable execution, verification, and recordkeeping. It explicitly distinguishes conceptual inspiration from one-to-one historical equivalence and explains the optional multi-agent conversion path.

## Validation

- Verify that all English/Chinese navigation targets exist and cross-link correctly.
- Check that language-pair pages contain equivalent sections.
- Preserve the existing public-source unit suite and privacy scan.
- Confirm the static Pages source is deployable from `docs/` on `main`.
