TODO
====

- Create more sections:

  - references

    - For archetypes-field managed references, a path resolver would suffice,
      as ReferenceField and ReverseReferenceField take objects or UIDs.

- Define a 'default import pipeline' variable in the transmogrifier section,
  so you can include a default set of sections that'll work for 95% of the
  transmogrifier import cases. The goal is to have a pipeline definition like
  this::

    include = plone.app.transmogrifier.config:ploneimport.cfg
    pipeline =
        my.specific.import.section
        ${ploneimport:importpipeline}

  With a black box section that could even be done without variable
  substitution.
