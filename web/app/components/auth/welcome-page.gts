import Component from '@glimmer/component';
import { action } from '@ember/object';
import { service } from '@ember/service';
import type RouterService from '@ember/routing/router-service';
import type SessionService from '../../services/session';
import FirstLogInCheck from './first-log-in-check';

/** The first log-in check, then the member's home. */
export default class WelcomePage extends Component {
  @service declare router: RouterService;
  @service declare session: SessionService;

  @action
  goHome(): void {
    this.router.transitionTo('authenticated.index');
  }

  <template>
    {{#if this.session.me}}
      <FirstLogInCheck @me={{this.session.me}} @onChecked={{this.goHome}} />
    {{/if}}
  </template>
}
