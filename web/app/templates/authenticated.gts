import AppShell from '../components/layout/app-shell';

// Logged-in pages sit in the shell; log-in has its own full-page layout.
<template>
  <AppShell>
    {{outlet}}
  </AppShell>
</template>
