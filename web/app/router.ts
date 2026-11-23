import EmberRouter from '@embroider/router';
import config from 'colivo-web/config/environment';

export default class Router extends EmberRouter {
  location = config.locationType;
  rootURL = config.rootURL;
}

Router.map(function () {
  this.route('log-in');
  // Which home to act in, for a person in several (Phase 1b).
  this.route('choose-home');
  // Everything behind log-in; its index is the home page at "/".
  this.route('authenticated', { path: '' }, function () {
    this.route('members');
    this.route('welcome');
  });
});
