# Contributing to RoboData

RoboData is in an early design phase. Contributions that sharpen semantics,
surface failure modes, or add representative data fixtures are especially
valuable.

## Before opening a change

1. Read the [architecture](docs/architecture.md) and existing
   [decisions](docs/decisions/).
2. Open an issue for changes that affect public semantics, compatibility, or
   project scope.
3. Keep normative requirements separate from research notes and examples.

## Design changes

Use an Architecture Decision Record (ADR) when a change establishes or revises
a durable project-wide choice. Copy `docs/decisions/0000-template.md`, assign the
next number, and include consequences and rejected alternatives.

Any proposed field or transformation should answer:

- What fact does it represent, and what is its epistemic status?
- Which clock, frame, units, axes, and validity interval apply?
- Is it source data or a derivation? If derived, from what and by which version?
- What information is lost when it is converted or omitted?
- Can a consumer validate the result without private implementation knowledge?

## Pull requests

- Keep changes focused and explain their compatibility impact.
- Add or update examples for schema and contract changes.
- Check Markdown links and render modified SVGs before requesting review.
- Do not commit customer data, credentials, recordings, or generated datasets.

By contributing, you agree that your contributions are licensed under the MIT
License.
