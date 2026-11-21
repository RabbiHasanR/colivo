import Service from '@ember/service';

// For components, which don't import the data layer.
export type { Setup, SetupStep } from '../data/builders/home';

/** The logged-in member's home: its setup checklist. */
export default class CurrentHomeService extends Service {}

declare module '@ember/service' {
  interface Registry {
    'current-home': CurrentHomeService;
  }
}
