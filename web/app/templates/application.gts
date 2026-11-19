import { pageTitle } from 'ember-page-title';

// The Colivo shell (sidebar, menu button) arrives with Phase 0 group 4 (B12).
<template>
  {{pageTitle "Colivo"}}

  {{outlet}}
</template>
