import Component from '@glimmer/component';
import { action } from '@ember/object';
import { service } from '@ember/service';
import type RouterService from '@ember/routing/router-service';
import SignUpForm from './sign-up-form';

/**
 * Log in or create a home (colivo-design/web/WebAuth.html). Group 3 adds
 * the log-in side.
 */
export default class LogInPage extends Component {
  @service declare router: RouterService;

  @action
  goHome(): void {
    this.router.transitionTo('authenticated.index');
  }

  <template>
    <section data-test-create-home aria-labelledby="create-home-title">
      <h1 id="create-home-title">Create your home</h1>
      <p>For the person who runs the home. You'll be the owner and can add
        members afterwards.</p>
      <SignUpForm @onSignedUp={{this.goHome}} />
    </section>
  </template>
}
