# Colivo

Spec-driven and test-driven. Specs live in `specs/`; each roadmap phase gets
`specs/<date>-<slug>/` written by `/feature-spec`, then is built group by
group with `/tdd`.

Every screen follows its design in `colivo-design/` (`web/` for the web,
`mobile/` for the Flutter app): layout, cards, colours, spacing and words.
The design is the target, not a suggestion. Any difference (a field the
phase can't have yet, a changed word, an extra control) is asked about
first, then recorded in the phase's `requirements.md → Screens`. Choices
already made: the product is called "Colivo", not "Mess Manager".

Database design is always discussed with the user before it is written
(`/feature-spec` Gate 0). The living schema is `specs/data-model.md`.

`CHANGELOG.md` is kept by `/changelog`. Run it before merging any branch, and
at the end of any session that committed straight to `main`. Remind the user
if they are about to merge without it.

Testing rules, levels and workflow (always follow):

@specs/testing.md
