import { pageTitle } from 'ember-page-title';
import AppShell from '../components/layout/app-shell';

<template>
  {{pageTitle "Colivo"}}

  <AppShell>
    {{outlet}}
  </AppShell>
</template>
