import Component from '@glimmer/component';
import { action } from '@ember/object';
import { service } from '@ember/service';
import type RouterService from '@ember/routing/router-service';
import LogInForm from './log-in-form';
import SignUpForm from './sign-up-form';

/**
 * Log in or create a home (colivo-design/web/WebAuth.html): one above the
 * other on a phone, side by side on a wide screen (checked by eye).
 */
export default class LogInPage extends Component {
  @service declare router: RouterService;

  @action
  goHome(): void {
    this.router.transitionTo('authenticated.index');
  }

  <template>
    <section data-test-log-in aria-labelledby="log-in-title">
      <h1 id="log-in-title">Log in</h1>
      <p>Use the phone or email you signed up with, or the one your home's
        manager added you with. No home code needed.</p>
      <LogInForm @onLoggedIn={{this.goHome}} />
    </section>
    <section data-test-create-home aria-labelledby="create-home-title">
      <h2 id="create-home-title">Create your home</h2>
      <p>For the person who runs the home. You'll be the owner and can add
        members afterwards.</p>
      <SignUpForm @onSignedUp={{this.goHome}} />
    </section>
  </template>
}
