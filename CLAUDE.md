# Colivo

Spec-driven and test-driven. Specs live in `specs/`; each roadmap phase gets
`specs/<date>-<slug>/` written by `/feature-spec`, then is built group by
group with `/tdd`.

Database design is always discussed with the user before it is written
(`/feature-spec` Gate 0). The living schema is `specs/data-model.md`.

`CHANGELOG.md` is kept by `/changelog`. Run it before merging any branch, and
at the end of any session that committed straight to `main`. Remind the user
if they are about to merge without it.

Testing rules, levels and workflow (always follow):

@specs/testing.md
