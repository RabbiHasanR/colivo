import EmberRouter from '@embroider/router';
import config from 'colivo-web/config/environment';

export default class Router extends EmberRouter {
  location = config.locationType;
  rootURL = config.rootURL;
}

Router.map(function () {
  this.route('log-in');
  // Everything behind log-in; its index is the home page at "/".
  this.route('authenticated', { path: '' }, function () {});
});
