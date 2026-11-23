import Component from '@glimmer/component';
import { action } from '@ember/object';
import { service } from '@ember/service';
import type RouterService from '@ember/routing/router-service';
import type SessionService from '../../services/session';
import type { HomeChoice } from '../../services/current-home';
import AuthLayout from '../auth/auth-layout';
import HomePicker from './home-picker';

interface ChooseHomePageSignature {
  Args: { homes: HomeChoice[] };
}

/**
 * "Choose a home" (Phase 1b), in the log-in page's layout: the person's
 * homes; choosing one opens its home page in this tab.
 */
export default class ChooseHomePage extends Component<ChooseHomePageSignature> {
  @service declare router: RouterService;
  @service declare session: SessionService;

  @action
  choose(homeId: string): void {
    this.session.chooseHome(homeId);
    this.router.transitionTo('authenticated.index');
  }

  <template>
    <AuthLayout>
      <div class="flex flex-col gap-1.5">
        <h2 class="text-[26px] leading-tight font-semibold">Choose a home</h2>
        <p class="text-sm leading-normal text-muted">You're in more than one
          home. Pick the one to open; you can switch later from the menu.</p>
      </div>
      <HomePicker @homes={{@homes}} @onChoose={{this.choose}} />
    </AuthLayout>
  </template>
}
